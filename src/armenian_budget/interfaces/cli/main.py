import argparse
import logging
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Optional, List
import importlib
import colorlog
import yaml

from armenian_budget.core.enums import SourceType
from armenian_budget.core.utils import (
    dataset_stem,
    list_version_dirs,
    validate_label,
    year_dir_name,
)

logger = logging.getLogger(__name__)

# Source type choices for argparse - used across all commands
SOURCE_TYPE_CHOICES = list(SourceType.__members__.keys())

# Year folder of a version under data/original: "2026" or "2026_EDRAFT"
_YEAR_DIR_RE = re.compile(r"^(\d+)(_[A-Z0-9]+)?$")

# Folder under data/original and data/extracted that holds each source type
_CATEGORY_DIRS = {
    "BUDGET_LAW": "budget_laws",
    "SPENDING_Q1": "spending_reports",
    "SPENDING_Q12": "spending_reports",
    "SPENDING_Q123": "spending_reports",
    "SPENDING_Q1234": "spending_reports",
    "MTEP": "mtep",
}


def _select_versions(
    available: Sequence[str | None], label: str | None, unlabelled: bool
) -> list[str | None]:
    """Versions a command works on; None is the unlabelled version.

    ``available`` are the labels registered in sources.yaml. --label selects
    that version whether or not it is registered, so the caller can report it
    as missing instead of skipping it. Without flags the unlabelled version is
    always attempted, followed by every registered labelled version.
    """
    if label:
        return [label]
    if unlabelled:
        return [None]
    return [None] + [lb for lb in available if lb is not None]


def _load_source_registry(config_arg: str | None):
    """Load sources.yaml, the list of labelled versions, for a command.

    Returns None when the file is missing or cannot be loaded, with one warning:
    unlabelled work went on without it before labels existed, so it goes on, and
    no labelled version is then run.
    """
    sources_config = resolve_path_with_default(config_arg, "config/sources.yaml")
    if not sources_config.exists():
        logger.warning(
            "Sources config %s not found: labelled versions are not run", sources_config
        )
        return None
    registry_mod = importlib.import_module("armenian_budget.sources.registry")
    try:
        return registry_mod.SourceRegistry(sources_config)
    except (yaml.YAMLError, ValueError, TypeError) as e:
        logger.warning(
            "Ignoring sources config %s: %s; labelled versions are not run",
            sources_config,
            e,
        )
        return None


def _registered_labels(source_registry, year: int, *source_types: str) -> list[str]:
    """Labels registered in sources.yaml for a year and source types, sorted."""
    if source_registry is None:
        return []
    return sorted(
        {
            label
            for source_type in source_types
            for label in source_registry.published_by_label(year, source_type.lower())
            if label is not None
        }
    )


def _category_types(category: str) -> list[str]:
    """Source types whose files live in a category folder."""
    return [st for st, name in _CATEGORY_DIRS.items() if name == category]


def _warn_unregistered_folders(
    source_registry,
    root: Path,
    category: str,
    year: int,
    warned: set[Path],
) -> None:
    """Warn, once per folder, about labelled folders of a category not in sources.yaml.

    ``root`` is data/original or data/extracted. Such a folder is ignored.
    Without a registry every labelled version is already reported as not run,
    so there is nothing to add.
    """
    if source_registry is None:
        return
    category_root = root / category
    registered = _registered_labels(source_registry, year, *_category_types(category))
    for label in list_version_dirs(category_root, year):
        folder = category_root / year_dir_name(year, label)
        if label is None or label in registered or folder in warned:
            continue
        warned.add(folder)
        logger.warning(
            "Ignoring %s: %s is not registered for %s in sources.yaml",
            folder,
            label,
            year,
        )


def _not_registered(label: str, year: int, source_type: str | None = None) -> str:
    version = f"{year} {source_type}" if source_type else str(year)
    return f"{label} is not registered for {version} in sources.yaml"


def _label_arg(value: str) -> str:
    try:
        return validate_label(value.upper())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _add_version_options(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--label",
        type=_label_arg,
        help=(
            "Only the version with this source label, e.g. EDRAFT (case "
            "insensitive). By default the unlabelled version and every "
            "labelled version are covered."
        ),
    )
    group.add_argument(
        "--unlabelled",
        action="store_true",
        help="Only the unlabelled version (for a budget law: the adopted law).",
    )


def _with_label(text: str, label: str | None) -> str:
    return f"{text} {label}" if label else text


def _report_entry(
    year: int, source: str, status: str, reason: str, label: str | None
) -> dict:
    entry = {"year": year, "source": source, "status": status, "reason": reason}
    if label:
        entry["label"] = label
    return entry


def _checksum_key(item: dict) -> tuple[int, str | None, str | None]:
    return (
        int(item.get("year", 0)),
        item.get("source_type"),
        item.get("url"),
    )


def _source_checksum_key(source: object) -> tuple[int, str | None, str | None]:
    return (
        int(getattr(source, "year")),
        getattr(source, "source_type"),
        getattr(source, "url"),
    )


def _checksum_record(
    source: object,
    checksum: str,
    previous: dict | None,
    timestamp: str,
) -> dict:
    return {
        "name": getattr(source, "name"),
        "year": int(getattr(source, "year")),
        "source_type": getattr(source, "source_type"),
        "url": getattr(source, "url"),
        "checksum": checksum,
        "checksum_updated_at": (
            previous.get("checksum_updated_at")
            if previous and previous.get("checksum") == checksum
            else timestamp
        ),
    }


def _ordered_checksum_items(checksums_by_key: dict[tuple, dict], sources: list) -> list[dict]:
    ordered: list[dict] = []
    emitted: set[tuple] = set()
    for source in sources:
        key = _source_checksum_key(source)
        item = checksums_by_key.get(key)
        if item is None:
            continue
        ordered.append(item)
        emitted.add(key)
    ordered.extend(item for key, item in checksums_by_key.items() if key not in emitted)
    return ordered


def _merge_checksum_item(
    index: dict[tuple, dict],
    item: dict,
    source_names_by_key: dict[tuple, set[str]],
) -> None:
    key = _checksum_key(item)
    active_names = source_names_by_key.get(key, set())
    current_name = index.get(key, {}).get("name")
    item_name = item.get("name")
    if (
        key not in index
        or (item_name in active_names and current_name not in active_names)
    ):
        index[key] = item


try:
    # Prefer package-defined version
    from armenian_budget import __version__ as _PACKAGE_VERSION
except ImportError:  # pragma: no cover - defensive fallback
    _PACKAGE_VERSION = None  # type: ignore[assignment]
    try:
        # Fallback to installed package metadata
        from importlib.metadata import version as _pkg_version, PackageNotFoundError

        _PACKAGE_VERSION = _pkg_version("armenian-budget-tools")  # type: ignore[assignment]
    except PackageNotFoundError:
        _PACKAGE_VERSION = "unknown"  # type: ignore[assignment]


def setup_logging(
    verbose: bool = False, warnings_only: bool = False, errors_only: bool = False
) -> None:
    logger = logging.getLogger()
    for h in list(logger.handlers):
        logger.removeHandler(h)
    log_format = (
        "%(asctime)s:%(levelname)s:%(name)s in %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
    )
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
    stream_handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(f"%(log_color)s{log_format}", log_colors=log_colors)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if errors_only:
        logger.setLevel(logging.ERROR)
    elif warnings_only:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)


def resolve_path_with_default(arg_value: Optional[str], default: str) -> Path:
    """Resolve optional path argument with default fallback.

    Args:
        arg_value: The argument value from argparse (may be None)
        default: Default path to use if arg_value is None

    Returns:
        Resolved absolute Path object
    """
    return Path(arg_value or default).resolve()


def _report_order(entry: dict) -> tuple[int, str, str]:
    return (int(entry["year"]), str(entry["source"]), entry.get("label") or "")


def cmd_process(args: argparse.Namespace) -> int:
    """Process one or more years of budget data.

    When multiple years are provided, any missing year/source-type inputs
    only emit warnings and the command succeeds if at least one dataset
    was processed overall.
    """

    # Resolve roots
    extracted_root = resolve_path_with_default(args.extracted_root, "data/extracted")
    input_provided = args.input is not None
    # When discovery is used, extracted_root must exist; if explicitly provided, processed_root must be provided too
    if not input_provided:
        if not extracted_root.exists() or not extracted_root.is_dir():
            logging.error("Extracted root not found or not a directory: %s", extracted_root)
            return 2
        if args.extracted_root is not None and args.processed_root is None:
            logging.error("--processed-root is required when --extracted-root is provided")
            return 2
    # Determine processed output directory (processed files are written to this root)
    processed_root = resolve_path_with_default(args.processed_root, "data/processed")
    out_dir = processed_root.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Dynamic import of parsers to avoid static resolution issues in some IDEs
    # Predeclare for linters
    flatten_budget_excel_2019_2024 = None  # type: ignore[assignment]
    flatten_budget_excel_2025 = None  # type: ignore[assignment]
    flatten_mtep_excel = None  # type: ignore[assignment]
    SourceType = None  # type: ignore[assignment]
    try:
        parsers_pkg = importlib.import_module("armenian_budget.ingestion.parsers")
        flatten_budget_excel_2019_2024 = getattr(parsers_pkg, "flatten_budget_excel_2019_2024")
        flatten_budget_excel_2025 = getattr(parsers_pkg, "flatten_budget_excel_2025")
        flatten_mtep_excel = getattr(parsers_pkg, "flatten_mtep_excel")
        SourceType = getattr(parsers_pkg, "SourceType")
    except (ModuleNotFoundError, AttributeError, ImportError) as e:
        logging.error("Failed to import parsers: %s", e)
        return 3

    # Determine years
    years: List[int] = []
    if getattr(args, "years", None):
        parsed = _parse_years_arg(args.years)
        years = parsed or []
    else:
        logging.error("--years is required")
        return 2

    # Determine which source types to process
    if args.source_type:
        source_types: list[str] = [args.source_type]
    else:
        # Process all supported types when not specified
        source_types = [
            "BUDGET_LAW",
            "SPENDING_Q1",
            "SPENDING_Q12",
            "SPENDING_Q123",
            "SPENDING_Q1234",
            "MTEP",
        ]

    # If user provided a single explicit input, require a single source type
    if getattr(args, "input", None) and len(source_types) > 1:
        logging.error("When --input is provided, --source-type must be specified to disambiguate.")
        return 2

    # If user provided --input and multiple years, reject as ambiguous
    if getattr(args, "input", None) and len(years) != 1:
        logging.error("When --input is provided, only a single year may be specified in --years.")
        return 2

    # Lazy import discovery if needed
    discover_best_file = None
    if not input_provided:
        try:
            ingestion_pkg = importlib.import_module("armenian_budget.ingestion")
            discover_best_file = getattr(ingestion_pkg, "discover_best_file")
        except (ModuleNotFoundError, AttributeError, ImportError) as e:
            logging.error("Discovery unavailable: %s", e)
            return 1

    parsers_yaml = Path(args.parsers_config or Path("config/parsers.yaml").resolve())

    label_arg = getattr(args, "label", None)
    unlabelled_arg = bool(getattr(args, "unlabelled", False))
    # The labelled versions of a year are the ones registered in sources.yaml
    source_registry = (
        None if input_provided else _load_source_registry(getattr(args, "config", None))
    )
    warned: set[Path] = set()

    total_successes = 0
    # Collect per year/source results for end-of-run report
    report_entries: list[dict] = []
    for year in years:
        year_successes = 0
        jobs: list[tuple[str, str | None]] = []
        for st_name in source_types:
            if input_provided or st_name not in _CATEGORY_DIRS:
                # An explicit input is one version: the labelled one if asked
                versions = [label_arg]
            else:
                _warn_unregistered_folders(
                    source_registry,
                    extracted_root,
                    _CATEGORY_DIRS[st_name],
                    year,
                    warned,
                )
                versions = _select_versions(
                    _registered_labels(source_registry, year, st_name),
                    label_arg,
                    unlabelled_arg,
                )
            jobs.extend((st_name, label) for label in versions)
        for st_name, label in jobs:
            st_display = _with_label(st_name, label)
            try:
                st_enum = SourceType[st_name]
            except KeyError:
                logging.warning("Skipping unknown source type: %s", st_name)
                report_entries.append(
                    _report_entry(year, st_name, "FAIL", "unknown source type", label)
                )
                continue

            # Determine input path: prefer explicit, else discover
            if input_provided:
                input_path = Path(args.input)
                if not input_path.exists():
                    msg = f"input file missing: {input_path}"
                    logging.warning(
                        "Input file does not exist for %s/%s: %s",
                        year,
                        st_display,
                        input_path,
                    )
                    report_entries.append(
                        _report_entry(year, st_name, "FAIL", msg, label)
                    )
                    continue
            else:
                if label and label not in _registered_labels(
                    source_registry, year, st_name
                ):
                    msg = _not_registered(label, year, st_name)
                    logger.warning("%s/%s: %s", year, st_display, msg)
                    report_entries.append(
                        _report_entry(year, st_name, "FAIL", msg, label)
                    )
                    continue
                try:
                    input_path = discover_best_file(
                        extracted_root=extracted_root,
                        year=year,
                        source_type=st_name,
                        parsers_config_path=parsers_yaml,
                        force_discover=args.force_discover,
                        deep_validate=args.deep_validate,
                        label=label,
                    )
                except (
                    AssertionError,
                    FileNotFoundError,
                    RuntimeError,
                    ValueError,
                    KeyError,
                    OSError,
                ) as e:
                    logging.warning(
                        "Discovery failed for %s/%s: %s", year, st_display, e
                    )
                    report_entries.append(
                        _report_entry(year, st_name, "FAIL", f"discovery: {e}", label)
                    )
                    continue

            # Run appropriate parser
            try:
                if st_enum.name == "MTEP":
                    df, overall, _, _ = flatten_mtep_excel(str(input_path), year=int(year))
                elif year >= 2025:
                    # Use 2025+ parser for all 2025 and later sources, passing source_type for spending
                    df, overall, _, _ = flatten_budget_excel_2025(
                        str(input_path), source_type=st_enum, year=int(year)
                    )
                else:
                    df, overall, _, _ = flatten_budget_excel_2019_2024(
                        str(input_path), source_type=st_enum, year=int(year)
                    )
            except SystemExit:
                # Strict parser exit is treated as a failure for this type only
                logging.error("Parsing failed for %s/%s", year, st_display)
                report_entries.append(
                    _report_entry(
                        year, st_name, "FAIL", "parse error (see logs)", label
                    )
                )
                continue
            except (
                AssertionError,
                ValueError,
                KeyError,
                IndexError,
                OSError,
                RuntimeError,
            ) as e:
                logging.error("Error parsing %s/%s: %s", year, st_display, e)
                report_entries.append(
                    _report_entry(
                        year,
                        st_name,
                        "FAIL",
                        f"parse error: {type(e).__name__}: {e}",
                        label,
                    )
                )
                continue

            # Write outputs
            stem = dataset_stem(year, st_name, label)
            csv_name = f"{stem}.csv"
            overall_name = f"{stem}_overall.json"
            try:
                df.to_csv(out_dir / csv_name, index=False, encoding="utf-8-sig")
                import json

                with open(out_dir / overall_name, "w", encoding="utf-8") as f:
                    json.dump(overall, f, ensure_ascii=False, indent=2)
            except (OSError, ValueError) as e:
                logging.error(
                    "Failed writing outputs for %s/%s: %s", year, st_display, e
                )
                report_entries.append(
                    _report_entry(
                        year,
                        st_name,
                        "FAIL",
                        f"write error: {type(e).__name__}: {e}",
                        label,
                    )
                )
                continue

            logging.info("Processed %s/%s", year, st_display)
            logging.info("Saved CSV: %s", out_dir / csv_name)
            logging.info("Saved overall JSON: %s", out_dir / overall_name)
            year_successes += 1
            total_successes += 1
            report_entries.append(_report_entry(year, st_name, "OK", "", label))

        if year_successes == 0:
            logging.warning("No datasets processed for year %s.", year)

    # End-of-run processing report
    if report_entries:
        # Optional JSON report path
        if args.report_json:
            try:
                import json

                ordered = sorted(report_entries, key=_report_order)
                with open(args.report_json, "w", encoding="utf-8") as f:
                    json.dump(ordered, f, ensure_ascii=False, indent=2)
                logging.info("Saved processing report JSON: %s", args.report_json)
            except (OSError, ValueError) as e:
                logging.error("Failed to write report JSON %s: %s", args.report_json, e)

        logging.info("Processing report:")
        # Stable order: by year, then by source name, then by label
        for entry in sorted(report_entries, key=_report_order):
            source = _with_label(entry["source"], entry.get("label"))
            if entry["status"] == "OK":
                logging.info("%s %s: OK", entry["year"], source)
            else:
                logging.info(
                    "%s %s: FAIL (%s)",
                    entry["year"],
                    source,
                    entry.get("reason", ""),
                )

    if total_successes == 0:
        logging.error("No datasets processed.")
        return 1
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate one or more years of processed budget data.

    When multiple years are provided, validation runs for each year independently.
    Any missing year/source-type combinations emit warnings, and the command
    succeeds if at least one dataset was validated successfully (with or without errors).

    Returns:
        0 if all validations passed without errors
        1 if no datasets were validated
        2 if any validation errors were found
    """
    # Import validation module and utilities
    from armenian_budget.core.enums import SourceType

    registry = importlib.import_module("armenian_budget.validation.registry")
    label_arg = getattr(args, "label", None)
    unlabelled_arg = bool(getattr(args, "unlabelled", False))

    # Parse years argument
    years: List[int] = []
    if getattr(args, "years", None):
        parsed = _parse_years_arg(args.years)
        years = parsed or []
    else:
        logging.error("--years is required")
        return 2

    # Determine which source types to validate
    if args.source_type:
        source_types: list[str] = [args.source_type]
    else:
        # Validate all supported types when not specified
        source_types = [
            "BUDGET_LAW",
            "SPENDING_Q1",
            "SPENDING_Q12",
            "SPENDING_Q123",
            "SPENDING_Q1234",
            "MTEP",
        ]

    # Determine processed_root
    processed_root = resolve_path_with_default(args.processed_root, "data/processed")

    # Check that processed_root exists
    if not processed_root.exists():
        logging.error(
            "Processed root not found: %s. Run 'armenian-budget process' first.",
            processed_root,
        )
        return 2

    # Registered labels, and published dates for the identical-data note
    source_registry = _load_source_registry(getattr(args, "config", None))

    # Track results for end-of-run summary
    validation_results: List[dict] = []
    total_errors = 0
    successful_validations = 0

    # Validate each year and source type combination
    for year in years:
        for st_name in source_types:
            try:
                source_type = SourceType[st_name]
            except KeyError:
                valid_types = ", ".join(SourceType.__members__.keys())
                logging.error(
                    "Invalid source type: %s. Valid types: %s",
                    st_name,
                    valid_types,
                )
                total_errors += 1
                validation_results.append(
                    {
                        "year": year,
                        "source_type": st_name,
                        "status": "ERROR",
                        "errors": 1,
                        "warnings": 0,
                        "reason": "invalid source type",
                    }
                )
                continue

            registered = _registered_labels(source_registry, year, st_name)
            versions = _select_versions(
                registered,
                label_arg,
                unlabelled_arg,
            )
            published = (
                source_registry.published_by_label(year, st_name.lower())
                if source_registry
                else {}
            )
            for label in versions:
                if label and label not in registered:
                    reason = _not_registered(label, year, st_name)
                    logger.warning(
                        "%s/%s: %s", year, _with_label(st_name, label), reason
                    )
                    validation_results.append(
                        {
                            "year": year,
                            "source_type": st_name,
                            "status": "MISSING",
                            "errors": 0,
                            "warnings": 0,
                            "reason": reason,
                            "label": label,
                        }
                    )
                    continue
                result = _validate_version(
                    registry, args, year, source_type, processed_root, label, published
                )
                if label:
                    result["label"] = label
                validation_results.append(result)
                total_errors += result["errors"]
                if result["status"] in ("OK", "FAIL"):
                    successful_validations += 1

    _log_validation_summary(validation_results)

    # Determine exit code (strict: fail if ANY errors found)
    if total_errors > 0:
        logging.error("Validation found %d errors across all datasets.", total_errors)
        return 2

    if successful_validations == 0:
        logging.error("No datasets were validated.")
        return 1

    return 0


def _validate_version(
    registry,
    args: argparse.Namespace,
    year: int,
    source_type: SourceType,
    processed_root: Path,
    label: str | None,
    published: dict,
) -> dict:
    """Validate one version of a dataset and return its summary entry."""
    st_display = _with_label(source_type.value, label)
    stem = dataset_stem(year, source_type.value, label)
    logging.info("Validating %s/%s...", year, st_display)

    try:
        report = registry.run_validation(
            year, source_type, processed_root, label=label, published=published
        )

        has_errors = report.has_errors(strict=False)
        error_count = report.get_error_count()
        warning_count = report.get_warning_count()

        if has_errors:
            logging.warning(
                "Validation failed for %s/%s: %d errors, %d warnings",
                year,
                st_display,
                error_count,
                warning_count,
            )
        else:
            logging.info("Validation passed for %s/%s", year, st_display)

        # Print console report
        registry.print_report(report)

        # Write Markdown / JSON reports if requested: next to the CSV by default,
        # or into the custom directory given with the flag
        for flag, kind, suffix, render in (
            (args.report, "Markdown", "md", report.to_markdown),
            (args.report_json, "JSON", "json", report.to_json),
        ):
            if not flag:
                continue
            report_dir = processed_root if flag is True else Path(flag)
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = report_dir / f"{stem}_validation.{suffix}"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(render())
            logging.info("%s report saved: %s", kind, report_path)

        return {
            "year": year,
            "source_type": source_type.value,
            "status": "FAIL" if has_errors else "OK",
            "errors": error_count,
            "warnings": warning_count,
        }
    except FileNotFoundError as e:
        logging.warning("Dataset not found for %s/%s: %s", year, st_display, e)
        return {
            "year": year,
            "source_type": source_type.value,
            "status": "MISSING",
            "errors": 0,
            "warnings": 0,
            "reason": str(e),
        }
    except (ValueError, OSError) as e:
        logging.error("Error validating %s/%s: %s", year, st_display, e)
        return {
            "year": year,
            "source_type": source_type.value,
            "status": "ERROR",
            "errors": 0,
            "warnings": 0,
            "reason": str(e),
        }


def _log_validation_summary(validation_results: list[dict]) -> None:
    """Log one line per dataset when a run covered more than one."""
    if len(validation_results) < 2:
        return
    logging.info("Validation Summary:")
    for entry in validation_results:
        source = _with_label(entry["source_type"], entry.get("label"))
        if entry["status"] == "OK":
            logging.info("%s %s: PASSED", entry["year"], source)
        elif entry["status"] == "FAIL":
            logging.info(
                "%s %s: FAILED (%d errors, %d warnings)",
                entry["year"],
                source,
                entry["errors"],
                entry["warnings"],
            )
        else:
            logging.info(
                "%s %s: %s (%s)",
                entry["year"],
                source,
                entry["status"],
                entry.get("reason", ""),
            )


def _parse_years_arg(years_arg: Optional[str]) -> Optional[List[int]]:
    if not years_arg:
        return None
    years_arg = years_arg.strip()
    if "-" in years_arg and "," not in years_arg:
        start, end = years_arg.split("-", 1)
        return list(range(int(start), int(end) + 1))
    years: List[int] = []
    for part in years_arg.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            s, e = part.split("-", 1)
            years.extend(range(int(s), int(e) + 1))
        else:
            years.append(int(part))
    return sorted(set(years))


def cmd_download(args: argparse.Namespace) -> int:
    # Import dynamically to avoid static import resolution problems in some IDEs
    registry_mod = importlib.import_module("armenian_budget.sources.registry")
    downloader_mod = importlib.import_module("armenian_budget.sources.downloader")
    organizer_mod = importlib.import_module("armenian_budget.sources.organizer")

    SourceRegistry = getattr(registry_mod, "SourceRegistry")
    download_sources = getattr(downloader_mod, "download_sources")
    extract_rar_files = getattr(organizer_mod, "extract_rar_files")
    extract_zip_files = getattr(organizer_mod, "extract_zip_files")

    cfg_path = Path(args.config)
    original_root = resolve_path_with_default(args.original_root, "data/original")
    extracted_root = resolve_path_with_default(args.extracted_root, "data/extracted")
    if not original_root.exists():
        original_root.mkdir(parents=True, exist_ok=True)

    try:
        registry = SourceRegistry(cfg_path)
    except (FileNotFoundError, yaml.YAMLError, ValueError) as e:
        logging.error("Failed to load sources: %s", e)
        return 3

    years = _parse_years_arg(args.years)
    sources = registry.all() if years is None else registry.for_years(years)

    # Filter by source type if specified
    if args.source_type:
        # argparse already uppercased it via type=str.upper
        requested_type = args.source_type.lower()  # Convert to lowercase for source comparison
        sources = [s for s in sources if s.source_type == requested_type]
    else:
        # Keep budget laws, spending sources, and MTEP sources
        sources = [
            s
            for s in sources
            if s.source_type.startswith("spending_")
            or s.source_type == "budget_law"
            or s.source_type == "mtep"
        ]
    if args.label:
        sources = [s for s in sources if s.label == args.label]
        for year in years or []:
            if not any(s.year == year for s in sources):
                logger.warning(
                    "%s", _not_registered(args.label, year, args.source_type)
                )
    elif args.unlabelled:
        sources = [s for s in sources if s.label is None]
    if not sources:
        logging.warning("No matching sources to download.")
        # A requested label that nothing registers counts as a failure
        return 1 if args.label else 0

    results = download_sources(
        sources,
        original_root,
        skip_existing=(not args.force),
    )
    # Always record checksums for successful results into config/checksums.yaml
    import hashlib
    from datetime import datetime, timezone

    checksums_path = Path(cfg_path).with_name("checksums.yaml")
    checksum_history_path = Path(cfg_path).with_name("checksum_history.yaml")
    existing_index: dict[tuple, dict] = {}
    checksum_history: list[dict] = []
    source_names_by_key: dict[tuple, set[str]] = {}
    for source in registry.all():
        source_names_by_key.setdefault(_source_checksum_key(source), set()).add(source.name)
    try:
        if checksums_path.exists():
            with checksums_path.open("r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}
            for item in existing.get("checksums", []) or []:
                _merge_checksum_item(existing_index, item, source_names_by_key)
    except (OSError, ValueError, yaml.YAMLError, TypeError):
        existing_index = {}
    try:
        if checksum_history_path.exists():
            with checksum_history_path.open("r", encoding="utf-8") as f:
                history = yaml.safe_load(f) or {}
            checksum_history = list(history.get("changes", []) or [])
    except (OSError, ValueError, yaml.YAMLError, TypeError):
        checksum_history = []

    recorded = 0
    for source_def, dl_result in zip(sources, results):
        if not dl_result.ok:
            continue
        sha = hashlib.sha256()
        try:
            with open(dl_result.output_path, "rb") as checksum_file:
                while True:
                    block = checksum_file.read(1024 * 1024)
                    if not block:
                        break
                    sha.update(block)
            digest = sha.hexdigest()
        except (OSError, ValueError):
            continue
        ts = datetime.now(timezone.utc).isoformat()
        key = _source_checksum_key(source_def)
        prev = existing_index.get(key)
        if not prev or prev.get("checksum") != digest:
            if prev and prev.get("checksum"):
                change_record = {
                    "name": source_def.name,
                    "year": int(source_def.year),
                    "source_type": source_def.source_type,
                    "url": source_def.url,
                    "previous_checksum": prev.get("checksum"),
                    "new_checksum": digest,
                    "previous_checksum_updated_at": prev.get("checksum_updated_at"),
                    "changed_detected_at": ts,
                }
                archived_path = getattr(dl_result, "archived_path", None)
                if archived_path:
                    change_record["archived_path"] = str(archived_path)
                checksum_history.append(change_record)
            recorded += 1
        existing_index[key] = _checksum_record(source_def, digest, prev, ts)

    try:
        with checksums_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                {"checksums": _ordered_checksum_items(existing_index, registry.all())},
                f,
                sort_keys=False,
                allow_unicode=True,
                indent=2,
            )
        if checksum_history:
            with checksum_history_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    {"changes": checksum_history},
                    f,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=2,
                )
    except (OSError, ValueError, yaml.YAMLError, TypeError):
        pass
    ok = sum(1 for r in results if r.ok)
    fail = len(results) - ok
    # Per-item summary for visibility
    for r in results:
        if r.ok and r.reason == "skipped_existing":
            status = "OK (skipped)"
        else:
            status = "OK" if r.ok else f"FAIL ({r.reason})"
        q = f"/{r.quarter}" if getattr(r, "quarter", None) else ""
        logging.info(
            "%s — %s [%s%s] → %s",
            status,
            r.name,
            r.year,
            q,
            r.output_path,
        )
    logging.info("Downloads: %d ok, %d failed, %d checksums recorded", ok, fail, recorded)

    if args.extract:
        versions_to_extract = sorted(
            {(s.year, s.label or "") for s, r in zip(sources, results) if r.ok}
        )
        for y, label in versions_to_extract:
            year_dir = year_dir_name(y, label or None)
            # Spending reports, MTEP files and budget law files
            for dir_name in ("spending_reports", "mtep", "budget_laws"):
                input_dir = original_root / dir_name / year_dir
                output_dir = extracted_root / dir_name / year_dir
                if not input_dir.is_dir():
                    # Nothing downloaded for this version: leave no empty folder
                    continue
                extract_rar_files(input_dir, output_dir)
                extract_zip_files(input_dir, output_dir)

    return 0 if fail == 0 else 1


def cmd_extract(args: argparse.Namespace) -> int:
    # Import dynamically to avoid static import resolution problems in some IDEs
    organizer_mod = importlib.import_module("armenian_budget.sources.organizer")
    extract_rar_files = getattr(organizer_mod, "extract_rar_files")
    extract_zip_files = getattr(organizer_mod, "extract_zip_files")

    original_root = resolve_path_with_default(args.original_root, "data/original")
    extracted_root = resolve_path_with_default(args.extracted_root, "data/extracted")
    years = _parse_years_arg(args.years)

    # Determine which source types to extract
    source_type_filter = args.source_type
    source_type_dirs = []
    if source_type_filter:
        # Map the filter to directory name
        dir_name = _CATEGORY_DIRS.get(source_type_filter)
        if dir_name:
            source_type_dirs = [dir_name]
    else:
        # Extract all types
        source_type_dirs = ["spending_reports", "mtep", "budget_laws"]

    if years is None:
        # Auto-detect years from all source type directories
        years_set = set()
        for dir_name in source_type_dirs:
            base = original_root / dir_name
            if base.exists():
                for p in base.iterdir():
                    year_match = _YEAR_DIR_RE.match(p.name)
                    if p.is_dir() and year_match:
                        years_set.add(int(year_match.group(1)))
        if years_set:
            years = sorted(years_set)
        else:
            logging.warning("No original source directories found in: %s", original_root)
            return 0

    if not years:
        logging.warning("No years to extract.")
        return 0

    source_registry = _load_source_registry(args.config)
    warned: set[Path] = set()
    extracted_any = False
    # Extract from each source type directory
    for y in years:
        for dir_name in source_type_dirs:
            _warn_unregistered_folders(
                source_registry, original_root, dir_name, y, warned
            )
            registered = _registered_labels(
                source_registry, y, *_category_types(dir_name)
            )
            for label in _select_versions(registered, args.label, args.unlabelled):
                year_dir = year_dir_name(y, label)
                input_dir = original_root / dir_name / year_dir
                output_dir = extracted_root / dir_name / year_dir
                if label and label not in registered:
                    reason = _not_registered(label, y, args.source_type)
                    logger.warning("%s/%s: %s", dir_name, year_dir, reason)
                    continue
                if not input_dir.is_dir():
                    # Nothing to extract; do not leave an empty version folder
                    if label:
                        logger.warning(
                            "No original folder for %s: %s", label, input_dir
                        )
                    continue
                extract_rar_files(input_dir, output_dir)
                extract_zip_files(input_dir, output_dir)
                extracted_any = True

    if args.label and not extracted_any:
        logger.error("Nothing extracted for label %s.", args.label)
        return 1
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    try:
        ingestion_pkg = importlib.import_module("armenian_budget.ingestion")
        discover_best_file = getattr(ingestion_pkg, "discover_best_file")
    except (ModuleNotFoundError, AttributeError) as e:
        logging.error("Unable to load discovery module: %s", e)
        return 3

    years = _parse_years_arg(args.years)
    if not years:
        logging.error("--years is required for discover")
        return 2

    extracted_root = resolve_path_with_default(args.extracted_root, "data/extracted")
    if not extracted_root.exists() or not extracted_root.is_dir():
        logging.error("Extracted root not found or not a directory: %s", extracted_root)
        return 2
    parsers_yaml = resolve_path_with_default(args.parsers_config, "config/parsers.yaml")
    src_types: List[str]
    if args.source_type:
        src_types = [args.source_type]
    else:
        src_types = [
            "BUDGET_LAW",
            "SPENDING_Q1",
            "SPENDING_Q12",
            "SPENDING_Q123",
            "SPENDING_Q1234",
        ]
    source_registry = _load_source_registry(args.config)
    warned: set[Path] = set()
    ok = 0
    jobs = []
    for y in years:
        for st in src_types:
            _warn_unregistered_folders(
                source_registry, extracted_root, _CATEGORY_DIRS[st], int(y), warned
            )
            registered = _registered_labels(source_registry, int(y), st)
            jobs.extend(
                (y, st, label)
                for label in _select_versions(registered, args.label, args.unlabelled)
            )
    for y, st, label in jobs:
        st_display = _with_label(st, label)
        if label and label not in _registered_labels(source_registry, int(y), st):
            logger.warning(
                "No match for %s/%s: %s",
                y,
                st_display,
                _not_registered(label, int(y), st),
            )
            continue
        try:
            path = discover_best_file(
                extracted_root=extracted_root,
                year=int(y),
                source_type=st,
                parsers_config_path=parsers_yaml,
                force_discover=args.force_discover,
                deep_validate=args.deep_validate,
                label=label,
            )
            logging.info("Discovered %s/%s → %s", y, st_display, path)
            ok += 1
        except (
            AssertionError,
            FileNotFoundError,
            RuntimeError,
            ValueError,
            KeyError,
        ) as e:
            logging.warning("No match for %s/%s: %s", y, st_display, e)
            continue
    return 0 if ok > 0 else 1


def cmd_gdp_extract(args: argparse.Namespace) -> int:
    try:
        gdp_mod = importlib.import_module("armenian_budget.ingestion.gdp_indicators")
    except (ModuleNotFoundError, AttributeError) as e:
        logging.error("Unable to load GDP extractor: %s", e)
        return 3

    years = _parse_years_arg(args.years)
    if not years:
        logging.error("--years is required for gdp-extract")
        return 2

    original_root = resolve_path_with_default(args.original_root, "data/original")
    extracted_root = resolve_path_with_default(args.extracted_root, "data/extracted")
    processed_root = resolve_path_with_default(args.processed_root, "data/processed")
    sources_config = resolve_path_with_default(args.config, "config/sources.yaml")

    source_types = [args.source_type] if args.source_type else list(gdp_mod.GDP_SOURCE_TYPES)
    ok = 0
    failed = 0
    # One warning per run when the registry cannot be read
    registry_usable = "BUDGET_LAW" in source_types and (
        _load_source_registry(args.config) is not None
    )
    for year in years:
        note_labels: dict[str, bool] = {}
        if registry_usable:
            note_labels = gdp_mod.budget_law_note_labels(sources_config, int(year))
        jobs: list[tuple[str, str | None]] = []
        for source_type in source_types:
            if source_type == "BUDGET_LAW":
                # Every labelled version registered for the year, by default
                versions = _select_versions(
                    sorted(note_labels), args.label, args.unlabelled
                )
            else:
                # Labels apply to budget laws only
                versions = [] if args.label else [None]
            jobs.extend((source_type, label) for label in versions)
        for source_type, label in jobs:
            if label and label not in note_labels:
                reason = _not_registered(label, year, source_type)
                logger.warning("%s %s: %s", year, source_type, reason)
                failed += 1
                continue
            if label and not note_labels[label]:
                # Reported, not an error: this version has no budget message
                logger.info(
                    "%s %s %s: skipped, no budget message registered",
                    year,
                    source_type,
                    label,
                )
                continue
            try:
                snapshot = gdp_mod.extract_gdp_snapshot(
                    year=int(year),
                    source_type=source_type,
                    original_root=original_root,
                    extracted_root=extracted_root,
                    sources_config=sources_config,
                    label=label,
                )
                output_path = gdp_mod.write_gdp_snapshot(snapshot, processed_root)
                logging.info("Saved GDP snapshot: %s", output_path)
                ok += 1
            except (
                FileNotFoundError,
                ValueError,
                KeyError,
                OSError,
                yaml.YAMLError,
            ) as exc:
                logging.warning("%s %s: %s", year, _with_label(source_type, label), exc)
                failed += 1

    if ok == 0:
        logging.error("No GDP snapshots extracted.")
        return 1
    return 0 if failed == 0 else 1


def cmd_gdp_report(args: argparse.Namespace) -> int:
    try:
        gdp_mod = importlib.import_module("armenian_budget.ingestion.gdp_indicators")
    except (ModuleNotFoundError, AttributeError) as e:
        logging.error("Unable to load GDP reporter: %s", e)
        return 3

    years = _parse_years_arg(args.years) if args.years else None
    processed_root = resolve_path_with_default(args.processed_root, "data/processed")
    snapshots = gdp_mod.load_gdp_snapshots(
        processed_root,
        years=years,
        source_type=args.source_type,
    )
    if not snapshots:
        logging.error("No GDP JSON snapshots found.")
        return 1

    has_filter = bool(args.years or args.source_type)
    default_output = (
        "data/reports/gdp_report_partial.html"
        if has_filter
        else "data/reports/gdp_report.html"
    )
    output_path = resolve_path_with_default(args.output, default_output)
    gdp_mod.write_gdp_html_report(snapshots, output_path)
    logging.info("Saved GDP report: %s", output_path)
    return 0


def cmd_minfin_spending_reports(args: argparse.Namespace) -> int:
    try:
        reports_mod = importlib.import_module(
            "armenian_budget.sources.minfin_spending_reports"
        )
    except (ModuleNotFoundError, AttributeError) as e:
        logging.error("Unable to load MinFin spending report lister: %s", e)
        return 3

    years = set(_parse_years_arg(args.years) or []) if args.years else None
    reports = reports_mod.list_minfin_spending_reports(years)
    if args.quarter:
        reports = [report for report in reports if report["quarter"] == args.quarter]
    if args.downloads_only:
        downloads = []
        for report in reports:
            for item in report["downloads"]:
                downloads.append(
                    {
                        "year": report["year"],
                        "quarter": report["quarter"],
                        **item,
                    }
                )
        import json

        print(json.dumps(downloads, ensure_ascii=False, indent=2))
        return 0

    import json

    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 0


def cmd_minfin_budget(args: argparse.Namespace) -> int:
    try:
        budget_mod = importlib.import_module("armenian_budget.sources.minfin_budget")
    except (ModuleNotFoundError, AttributeError) as e:
        logging.error("Unable to load MinFin budget lister: %s", e)
        return 3

    years = set(_parse_years_arg(args.years) or []) if args.years else None
    records = budget_mod.list_minfin_budget(years)
    if args.downloads_only:
        downloads = []
        for record in records:
            for item in record["downloads"]:
                downloads.append(
                    {
                        "year": record["year"],
                        "source_type": record["source_type"],
                        "page_url": record["page_url"],
                        **item,
                    }
                )
        import json

        print(json.dumps(downloads, ensure_ascii=False, indent=2))
        return 0

    import json

    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="armenian-budget",
        description=f"Armenian Budget Tools (v{_PACKAGE_VERSION})",
    )
    p.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    p.add_argument(
        "--warnings-only",
        action="store_true",
        help="Show only warnings and errors (overrides --verbose)",
    )
    p.add_argument(
        "--errors-only",
        action="store_true",
        help="Show only errors (overrides --warnings-only and --verbose)",
    )

    sub = p.add_subparsers(dest="command", required=True)

    p_download = sub.add_parser("download", help="Download spending reports from sources.yaml")
    p_download.add_argument(
        "--years",
        help="Comma-separated years (e.g. 2019,2020) or range (2019-2024). Defaults to all in YAML.",
    )
    p_download.add_argument(
        "--config",
        default=str(Path("config/sources.yaml").resolve()),
        help="Path to sources.yaml",
    )
    p_download.add_argument(
        "--original-root",
        default=None,
        help="Original sources root (defaults to ./data/original)",
    )
    p_download.add_argument(
        "--extracted-root",
        default=None,
        help="Extracted data root for --extract (defaults to ./data/extracted)",
    )
    p_download.add_argument(
        "--extract",
        action="store_true",
        help="Extract downloaded RAR archives into data/extracted/spending_reports/{year}",
    )
    p_download.add_argument(
        "--force",
        action="store_true",
        help="Re-download existing files and archive changed prior copies",
    )
    p_download.add_argument(
        "--source-type",
        type=str.upper,
        choices=SOURCE_TYPE_CHOICES,
        help="Limit download to a specific source type (case insensitive)",
    )
    _add_version_options(p_download)
    p_download.set_defaults(func=cmd_download)

    p_extract = sub.add_parser("extract", help="Extract already downloaded spending archives")
    p_extract.add_argument(
        "--years",
        help="Comma-separated years (e.g. 2019,2020) or range (2019-2024). If omitted, auto-detect from data/original.",
    )
    p_extract.add_argument(
        "--source-type",
        type=str.upper,
        choices=SOURCE_TYPE_CHOICES,
        help="Limit extraction to a specific source type (case insensitive). If omitted, all types are extracted.",
    )
    p_extract.add_argument(
        "--original-root",
        default=None,
        help="Original sources root (defaults to ./data/original)",
    )
    p_extract.add_argument(
        "--extracted-root",
        default=None,
        help="Extracted data root (defaults to ./data/extracted)",
    )
    _add_version_options(p_extract)
    p_extract.add_argument(
        "--config",
        default=None,
        help=(
            "Path to sources.yaml (defaults to config/sources.yaml). Only read "
            "for the labelled versions registered there."
        ),
    )
    p_extract.set_defaults(func=cmd_extract)

    p_discover = sub.add_parser(
        "discover",
        help="Discover and cache input files from extracted archives",
    )
    p_discover.add_argument(
        "--years",
        required=True,
        help="Comma-separated years (e.g. 2019,2020) or range (2019-2024)",
    )
    p_discover.add_argument(
        "--source-type",
        type=str.upper,
        choices=SOURCE_TYPE_CHOICES,
        help="Limit discovery to a specific source type",
    )
    p_discover.add_argument(
        "--extracted-root",
        default=None,
        help="Extracted data root (defaults to ./data/extracted)",
    )
    p_discover.add_argument(
        "--parsers-config",
        default=None,
        help="Path to parsers.yaml (defaults to config/parsers.yaml)",
    )
    p_discover.add_argument(
        "--force-discover",
        action="store_true",
        help="Force re-discovery even if a cached mapping exists",
    )
    p_discover.add_argument(
        "--deep-validate",
        action="store_true",
        help="Probe-parse candidates during discovery to validate content (slower)",
    )
    p_discover.add_argument(
        "--config",
        default=None,
        help=(
            "Path to sources.yaml (defaults to config/sources.yaml). Only read "
            "for the labelled versions registered there."
        ),
    )
    _add_version_options(p_discover)
    p_discover.set_defaults(func=cmd_discover)

    p_minfin = sub.add_parser(
        "minfin-spending-reports",
        help="List spending report files advertised on minfin.am",
    )
    p_minfin.add_argument(
        "--years",
        help=(
            "Comma-separated years (e.g. 2024,2025) or range (2024-2025). "
            "Defaults to all listed years."
        ),
    )
    p_minfin.add_argument(
        "--quarter",
        choices=["Q1", "Q12", "Q123", "Q1234"],
        help="Limit output to one spending report period.",
    )
    p_minfin.add_argument(
        "--downloads-only",
        action="store_true",
        help="Return a flat list of downloadable items instead of period records.",
    )
    p_minfin.set_defaults(func=cmd_minfin_spending_reports)

    p_minfin_budget = sub.add_parser(
        "minfin-budget",
        help="List budget files advertised on minfin.am",
    )
    p_minfin_budget.add_argument(
        "--years",
        help=(
            "Comma-separated years (e.g. 2024,2025) or range (2024-2025). "
            "Defaults to all listed years."
        ),
    )
    p_minfin_budget.add_argument(
        "--downloads-only",
        action="store_true",
        help="Return a flat list of downloadable items instead of year records.",
    )
    p_minfin_budget.set_defaults(func=cmd_minfin_budget)

    p_process = sub.add_parser("process", help="Process one or more source Excels and write CSV")
    p_process.add_argument(
        "--years",
        required=True,
        help=(
            "Comma-separated years (e.g. 2019,2020) or range (2019-2024). "
            "For a single year, use --years 2023. When provided, processes all listed years."
        ),
    )
    p_process.add_argument(
        "--source-type",
        choices=SOURCE_TYPE_CHOICES,
        help=(
            "Source type (case insensitive). If omitted, all supported source types for the year will be processed."
        ),
    )
    p_process.add_argument(
        "--input",
        required=False,
        help="Path to source Excel file (when provided, discovery is bypassed and --extracted-root is ignored)",
    )
    p_process.add_argument(
        "--processed-root",
        required=False,
        default=None,
        help="Processed outputs root. Defaults to ./data/processed",
    )
    p_process.add_argument(
        "--auto",
        action="store_true",
        help=("Deprecated: discovery now runs automatically when --input is not provided."),
    )
    p_process.add_argument(
        "--force-discover",
        action="store_true",
        help="Force re-discovery even if a cached mapping exists",
    )
    p_process.add_argument(
        "--deep-validate",
        action="store_true",
        help="Probe-parse candidates during discovery to validate content (slower)",
    )
    p_process.add_argument(
        "--parsers-config",
        default=None,
        help="Path to parsers.yaml (defaults to config/parsers.yaml)",
    )
    p_process.add_argument(
        "--report-json",
        default=None,
        help="Write end-of-run processing report to this JSON file",
    )
    p_process.add_argument(
        "--extracted-root",
        default=None,
        help="Extracted data root (defaults to ./data/extracted). Required if discovery is used and you provide a non-default location.",
    )
    p_process.add_argument(
        "--config",
        default=None,
        help=(
            "Path to sources.yaml (defaults to config/sources.yaml). Only read "
            "for the labelled versions registered there, so that one with "
            "nothing extracted is reported."
        ),
    )
    _add_version_options(p_process)
    p_process.set_defaults(func=cmd_process)

    p_gdp_extract = sub.add_parser(
        "gdp-extract",
        help="Extract GDP indicator JSON snapshots from budget source documents",
    )
    p_gdp_extract.add_argument(
        "--years",
        required=True,
        help="Comma-separated years (e.g. 2024,2025) or range (2024-2025)",
    )
    p_gdp_extract.add_argument(
        "--source-type",
        type=str.upper,
        choices=["BUDGET_LAW", "SPENDING_Q1234"],
        help="Limit extraction to one GDP-supported source type",
    )
    p_gdp_extract.add_argument(
        "--config",
        default=None,
        help="Path to sources.yaml (defaults to config/sources.yaml)",
    )
    p_gdp_extract.add_argument(
        "--original-root",
        default=None,
        help="Original sources root (defaults to ./data/original)",
    )
    p_gdp_extract.add_argument(
        "--extracted-root",
        default=None,
        help="Extracted data root (defaults to ./data/extracted)",
    )
    p_gdp_extract.add_argument(
        "--processed-root",
        default=None,
        help="Processed outputs root (defaults to ./data/processed)",
    )
    _add_version_options(p_gdp_extract)
    p_gdp_extract.set_defaults(func=cmd_gdp_extract)

    p_gdp_report = sub.add_parser(
        "gdp-report",
        help="Render an HTML report from GDP JSON snapshots",
    )
    p_gdp_report.add_argument(
        "--years",
        help="Comma-separated years (e.g. 2024,2025) or range (2024-2025)",
    )
    p_gdp_report.add_argument(
        "--source-type",
        type=str.upper,
        choices=["BUDGET_LAW", "SPENDING_Q1234"],
        help="Limit report to one GDP-supported source type",
    )
    p_gdp_report.add_argument(
        "--processed-root",
        default=None,
        help="Processed data root (defaults to ./data/processed)",
    )
    p_gdp_report.add_argument(
        "--output",
        default=None,
        help=(
            "HTML output path. Defaults to ./data/reports/gdp_report.html without "
            "filters and ./data/reports/gdp_report_partial.html with filters."
        ),
    )
    p_gdp_report.set_defaults(func=cmd_gdp_report)

    p_validate = sub.add_parser("validate", help="Validate processed budget data")
    p_validate.add_argument(
        "--years",
        required=True,
        help=(
            "Comma-separated years (e.g. 2019,2020) or range (2019-2024). "
            "For a single year, use --years 2023."
        ),
    )
    p_validate.add_argument(
        "--source-type",
        type=str.upper,
        choices=SOURCE_TYPE_CHOICES,
        help="Source type to validate (case insensitive). If omitted, all supported source types will be validated.",
    )
    p_validate.add_argument(
        "--processed-root",
        required=False,
        default=None,
        help="Processed data root. Defaults to ./data/processed",
    )
    p_validate.add_argument(
        "--config",
        default=None,
        help=(
            "Path to sources.yaml (defaults to config/sources.yaml). Only read "
            "for the labelled versions registered there and the published "
            "dates shown in the identical-data note."
        ),
    )
    p_validate.add_argument(
        "--report",
        nargs="?",
        const=True,
        default=False,
        help="Generate detailed Markdown report (one per year). Optionally specify custom directory path.",
    )
    p_validate.add_argument(
        "--report-json",
        nargs="?",
        const=True,
        default=False,
        help="Generate detailed JSON report (one per year). Optionally specify custom directory path.",
    )
    _add_version_options(p_validate)
    p_validate.set_defaults(func=cmd_validate)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(
        verbose=bool(args.verbose),
        warnings_only=bool(getattr(args, "warnings_only", False)),
        errors_only=bool(getattr(args, "errors_only", False)),
    )
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
