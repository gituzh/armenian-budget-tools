import argparse
import logging
from pathlib import Path
from typing import Optional, List
import importlib
import colorlog
import yaml

from armenian_budget.core.enums import SourceType

# Source type choices for argparse - used across all commands
SOURCE_TYPE_CHOICES = list(SourceType.__members__.keys())

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


def cmd_process(args: argparse.Namespace) -> int:
    """Process one or more years of budget data.

    When multiple years are provided, any missing year/source-type inputs
    only emit warnings and the command succeeds if at least one dataset
    was processed overall.
    """

    # Resolve roots
    extracted_root = Path(args.extracted_root or Path("data/extracted")).resolve()
    processed_root_arg = getattr(args, "processed_root", None)
    input_provided = bool(getattr(args, "input", None))
    # When discovery is used, extracted_root must exist; if explicitly provided, processed_root must be provided too
    if not input_provided:
        if not extracted_root.exists() or not extracted_root.is_dir():
            logging.error("Extracted root not found or not a directory: %s", extracted_root)
            return 2
        if getattr(args, "extracted_root", None) is not None and processed_root_arg is None:
            logging.error("--processed-root is required when --extracted-root is provided")
            return 2
    # Determine processed output directory (csv is written under this root)
    if processed_root_arg is not None:
        processed_root = Path(processed_root_arg).resolve()
    else:
        # Default to ./data/processed (sibling of default extracted root)
        processed_root = Path("data/processed").resolve()
    out_dir = (processed_root / "csv").resolve()
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
        logging.error(
            "When --input is provided, only a single year may be specified in --years."
        )
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

    total_successes = 0
    # Collect per year/source results for end-of-run report
    report_entries: list[dict] = []
    for year in years:
        year_successes = 0
        for st_name in source_types:
            try:
                st_enum = SourceType[st_name]
            except KeyError:
                logging.warning("Skipping unknown source type: %s", st_name)
                report_entries.append(
                    {
                        "year": year,
                        "source": st_name,
                        "status": "FAIL",
                        "reason": "unknown source type",
                    }
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
                        st_name,
                        input_path,
                    )
                    report_entries.append(
                        {
                            "year": year,
                            "source": st_name,
                            "status": "FAIL",
                            "reason": msg,
                        }
                    )
                    continue
            else:
                try:
                    input_path = discover_best_file(
                        extracted_root=extracted_root,
                        year=year,
                        source_type=st_name,
                        parsers_config_path=parsers_yaml,
                        force_discover=bool(getattr(args, "force_discover", False)),
                        deep_validate=bool(getattr(args, "deep_validate", False)),
                    )
                except (
                    AssertionError,
                    FileNotFoundError,
                    RuntimeError,
                    ValueError,
                    KeyError,
                    OSError,
                ) as e:
                    logging.warning("Discovery failed for %s/%s: %s", year, st_name, e)
                    report_entries.append(
                        {
                            "year": year,
                            "source": st_name,
                            "status": "FAIL",
                            "reason": f"discovery: {e}",
                        }
                    )
                    continue

            # Run appropriate parser
            try:
                if st_enum.name == "MTEP":
                    df, overall, _, _ = flatten_mtep_excel(str(input_path), year=int(year))
                elif year == 2025:
                    # Use 2025 parser for all 2025 sources, passing source_type for spending
                    df, overall, _, _ = flatten_budget_excel_2025(
                        str(input_path), source_type=st_enum
                    )
                else:
                    df, overall, _, _ = flatten_budget_excel_2019_2024(
                        str(input_path), source_type=st_enum, year=int(year)
                    )
            except SystemExit:
                # Strict parser exit is treated as a failure for this type only
                logging.error("Parsing failed for %s/%s", year, st_name)
                report_entries.append(
                    {
                        "year": year,
                        "source": st_name,
                        "status": "FAIL",
                        "reason": "parse error (see logs)",
                    }
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
                logging.error("Error parsing %s/%s: %s", year, st_name, e)
                report_entries.append(
                    {
                        "year": year,
                        "source": st_name,
                        "status": "FAIL",
                        "reason": f"parse error: {type(e).__name__}: {e}",
                    }
                )
                continue

            # Write outputs
            csv_name = f"{year}_{st_name}.csv"
            overall_name = f"{year}_{st_name}_overall.json"
            try:
                df.to_csv(out_dir / csv_name, index=False, encoding="utf-8-sig")
                import json

                with open(out_dir / overall_name, "w", encoding="utf-8") as f:
                    json.dump(overall, f, ensure_ascii=False, indent=2)
            except (OSError, ValueError) as e:
                logging.error("Failed writing outputs for %s/%s: %s", year, st_name, e)
                report_entries.append(
                    {
                        "year": year,
                        "source": st_name,
                        "status": "FAIL",
                        "reason": f"write error: {type(e).__name__}: {e}",
                    }
                )
                continue

            logging.info("Processed %s/%s", year, st_name)
            logging.info("Saved CSV: %s", out_dir / csv_name)
            logging.info("Saved overall JSON: %s", out_dir / overall_name)
            year_successes += 1
            total_successes += 1
            report_entries.append({"year": year, "source": st_name, "status": "OK", "reason": ""})

        if year_successes == 0:
            logging.warning("No datasets processed for year %s.", year)

    # End-of-run processing report
    if report_entries:
        # Optional JSON report path
        report_path = getattr(args, "report_json", None)
        if report_path:
            try:
                import json

                ordered = sorted(report_entries, key=lambda r: (int(r["year"]), str(r["source"])))
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(ordered, f, ensure_ascii=False, indent=2)
                logging.info("Saved processing report JSON: %s", report_path)
            except (OSError, ValueError) as e:
                logging.error("Failed to write report JSON %s: %s", report_path, e)

        logging.info("Processing report:")
        # Stable order: by year, then by source name
        for entry in sorted(report_entries, key=lambda r: (int(r["year"]), str(r["source"]))):
            if entry["status"] == "OK":
                logging.info("%s %s: OK", entry["year"], entry["source"])
            else:
                logging.info(
                    "%s %s: FAIL (%s)",
                    entry["year"],
                    entry["source"],
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
    from armenian_budget.core.utils import get_processed_paths

    registry = importlib.import_module("armenian_budget.validation.registry")

    # Parse years argument
    years: List[int] = []
    if getattr(args, "years", None):
        parsed = _parse_years_arg(args.years)
        years = parsed or []
    else:
        logging.error("--years is required")
        return 2

    # Parse source type
    try:
        source_type = SourceType[args.source_type]
    except KeyError:
        valid_types = ", ".join(t.value for t in SourceType)
        logging.error(
            "Unknown source type: '%s'. Valid types: %s",
            args.source_type,
            valid_types,
        )
        return 2

    # Determine processed_root
    processed_root_arg = getattr(args, "processed_root", None)
    if processed_root_arg is not None:
        processed_root = Path(processed_root_arg).resolve()
    else:
        processed_root = Path("data/processed").resolve()

    # Check that processed_root exists
    if not processed_root.exists():
        logging.error(
            "Processed root not found: %s. Run 'armenian-budget process' first.",
            processed_root,
        )
        return 2

    # Track results for end-of-run summary
    validation_results: List[dict] = []
    total_errors = 0
    successful_validations = 0

    # Validate each year
    for year in years:
        logging.info("Validating %s/%s...", year, source_type.value)

        try:
            # Run validation for this year
            report = registry.run_validation(year, source_type, processed_root)

            # Track results
            has_errors = report.has_errors(strict=False)
            error_count = report.get_error_count()
            warning_count = report.get_warning_count()

            if has_errors:
                total_errors += error_count
                logging.warning(
                    "Validation failed for %s/%s: %d errors, %d warnings",
                    year,
                    source_type.value,
                    error_count,
                    warning_count,
                )
            else:
                logging.info(
                    "Validation passed for %s/%s",
                    year,
                    source_type.value,
                )

            # Print console report
            registry.print_report(report)

            # Generate markdown report if requested
            if args.report:
                if args.report is True:
                    # Default location: next to CSV file
                    csv_path, _ = get_processed_paths(year, source_type, processed_root)
                    report_dir = csv_path.parent
                    report_path = report_dir / f"{year}_{source_type.value}_validation.md"
                else:
                    # Custom directory provided - create per-year files
                    report_dir = Path(args.report)
                    report_dir.mkdir(parents=True, exist_ok=True)
                    report_path = report_dir / f"{year}_{source_type.value}_validation.md"

                # Write markdown report
                markdown_content = report.to_markdown()
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                logging.info("Markdown report saved: %s", report_path)

            # Generate JSON report if requested
            if args.report_json:
                if args.report_json is True:
                    # Default location: next to CSV file
                    csv_path, _ = get_processed_paths(year, source_type, processed_root)
                    report_dir = csv_path.parent
                    report_path = report_dir / f"{year}_{source_type.value}_validation.json"
                else:
                    # Custom directory provided - create per-year files
                    report_dir = Path(args.report_json)
                    report_dir.mkdir(parents=True, exist_ok=True)
                    report_path = report_dir / f"{year}_{source_type.value}_validation.json"

                # Write JSON report
                json_content = report.to_json()
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(json_content)

                logging.info("JSON report saved: %s", report_path)

            # Track success
            successful_validations += 1
            validation_results.append({
                "year": year,
                "source_type": source_type.value,
                "status": "FAIL" if has_errors else "OK",
                "errors": error_count,
                "warnings": warning_count,
            })

        except FileNotFoundError as e:
            logging.warning(
                "Dataset not found for %s/%s: %s",
                year,
                source_type.value,
                e,
            )
            validation_results.append({
                "year": year,
                "source_type": source_type.value,
                "status": "MISSING",
                "errors": 0,
                "warnings": 0,
                "reason": str(e),
            })
            continue
        except (ValueError, OSError) as e:
            logging.error(
                "Error validating %s/%s: %s",
                year,
                source_type.value,
                e,
            )
            validation_results.append({
                "year": year,
                "source_type": source_type.value,
                "status": "ERROR",
                "errors": 0,
                "warnings": 0,
                "reason": str(e),
            })
            continue

    # Print summary if multiple years
    if len(years) > 1 and validation_results:
        logging.info("Validation Summary:")
        for entry in validation_results:
            if entry["status"] == "OK":
                logging.info("%s %s: PASSED", entry["year"], entry["source_type"])
            elif entry["status"] == "FAIL":
                logging.info(
                    "%s %s: FAILED (%d errors, %d warnings)",
                    entry["year"],
                    entry["source_type"],
                    entry["errors"],
                    entry["warnings"],
                )
            else:
                logging.info(
                    "%s %s: %s (%s)",
                    entry["year"],
                    entry["source_type"],
                    entry["status"],
                    entry.get("reason", ""),
                )

    # Determine exit code (strict: fail if ANY errors found)
    if successful_validations == 0:
        logging.error("No datasets were validated.")
        return 1

    if total_errors > 0:
        logging.error("Validation found %d errors across all datasets.", total_errors)
        return 2

    return 0


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
    original_root = Path(args.original_root or Path("data/original")).resolve()
    extracted_root = Path(args.extracted_root or Path("data/extracted")).resolve()
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
    if getattr(args, "source_type", None):
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
    if not sources:
        logging.warning("No matching sources to download.")
        return 0

    results = download_sources(
        sources,
        original_root,
        skip_existing=(not bool(args.force)),
        overwrite_existing=bool(getattr(args, "overwrite", False)),
    )
    # Always record checksums for successful results into config/checksums.yaml
    import hashlib
    from datetime import datetime, timezone

    checksums_path = Path(cfg_path).with_name("checksums.yaml")
    existing_index: dict[tuple, dict] = {}
    try:
        if checksums_path.exists():
            with checksums_path.open("r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}
            for item in existing.get("checksums", []) or []:
                key = (
                    item.get("name"),
                    int(item.get("year", 0)),
                    item.get("source_type"),
                    item.get("url"),
                )
                existing_index[key] = item
    except (OSError, ValueError, yaml.YAMLError, TypeError):
        existing_index = {}

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
        key = (
            source_def.name,
            int(source_def.year),
            source_def.source_type,
            source_def.url,
        )
        prev = existing_index.get(key)
        if not prev or prev.get("checksum") != digest:
            existing_index[key] = {
                "name": source_def.name,
                "year": int(source_def.year),
                "source_type": source_def.source_type,
                "url": source_def.url,
                "checksum": digest,
                "checksum_updated_at": ts,
            }
            recorded += 1

    try:
        with checksums_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                {"checksums": list(existing_index.values())},
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
        years_to_extract = sorted({r.year for r in results if r.ok})
        for y in years_to_extract:
            # Extract spending reports
            input_dir = original_root / "spending_reports" / str(y)
            output_dir = extracted_root / "spending_reports" / str(y)
            extract_rar_files(input_dir, output_dir)
            extract_zip_files(input_dir, output_dir)

            # Extract MTEP files
            mtep_input_dir = original_root / "mtep" / str(y)
            mtep_output_dir = extracted_root / "mtep" / str(y)
            extract_rar_files(mtep_input_dir, mtep_output_dir)
            extract_zip_files(mtep_input_dir, mtep_output_dir)

            # Extract budget law files
            budget_law_input_dir = original_root / "budget_laws" / str(y)
            budget_law_output_dir = extracted_root / "budget_laws" / str(y)
            extract_rar_files(budget_law_input_dir, budget_law_output_dir)
            extract_zip_files(budget_law_input_dir, budget_law_output_dir)

    return 0 if fail == 0 else 1


def cmd_extract(args: argparse.Namespace) -> int:
    # Import dynamically to avoid static import resolution problems in some IDEs
    organizer_mod = importlib.import_module("armenian_budget.sources.organizer")
    extract_rar_files = getattr(organizer_mod, "extract_rar_files")
    extract_zip_files = getattr(organizer_mod, "extract_zip_files")

    original_root = Path(args.original_root or Path("data/original")).resolve()
    extracted_root = Path(args.extracted_root or Path("data/extracted")).resolve()
    years = _parse_years_arg(args.years)

    # Determine which source types to extract
    source_type_filter = getattr(args, "source_type", None)
    source_type_dirs = []
    if source_type_filter:
        # Map the filter to directory name
        # argparse already uppercased it via type=str.upper, so convert to lowercase
        type_to_dir = {
            "BUDGET_LAW": "budget_laws",
            "SPENDING_Q1": "spending_reports",
            "SPENDING_Q12": "spending_reports",
            "SPENDING_Q123": "spending_reports",
            "SPENDING_Q1234": "spending_reports",
            "MTEP": "mtep",
        }
        dir_name = type_to_dir.get(source_type_filter)
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
                    if p.is_dir() and p.name.isdigit():
                        years_set.add(int(p.name))
        if years_set:
            years = sorted(years_set)
        else:
            logging.warning("No original source directories found in: %s", original_root)
            return 0

    if not years:
        logging.warning("No years to extract.")
        return 0

    # Extract from each source type directory
    for y in years:
        for dir_name in source_type_dirs:
            input_dir = original_root / dir_name / str(y)
            output_dir = extracted_root / dir_name / str(y)
            extract_rar_files(input_dir, output_dir)
            extract_zip_files(input_dir, output_dir)

    return 0


def cmd_mcp_server(args: argparse.Namespace) -> int:
    """Start the MCP server.

    Default: stdio. If --port is set, run HTTP transport at host:port.
    """
    try:
        mcp_server = importlib.import_module("armenian_budget.interfaces.mcp.server")
    except (ModuleNotFoundError, AttributeError, ImportError) as e:
        logging.error(
            "Failed to import MCP server. Ensure 'mcp' is installed. Error: %s",
            e,
        )
        return 3
    data_path = args.data_path or "data/processed"
    try:
        rel = Path(data_path).resolve().relative_to(Path.cwd().resolve())
        display_path = rel.as_posix()
    except (ValueError, OSError):
        display_path = str(Path(data_path))
    port = getattr(args, "port", None)
    host = getattr(args, "host", None) or "127.0.0.1"
    https = bool(getattr(args, "https", False))
    certfile = getattr(args, "certfile", None)
    keyfile = getattr(args, "keyfile", None)
    if port and https:
        logging.info(
            "Starting MCP HTTPS server on %s:%s (data path: %s)",
            host,
            port,
            display_path,
        )
    elif port:
        logging.info(
            "Starting MCP HTTP server on %s:%s (data path: %s)",
            host,
            port,
            display_path,
        )
    else:
        logging.info("Starting MCP stdio server with data path: %s", display_path)
    try:
        if port and https:
            getattr(mcp_server, "run_https")(
                data_path,
                host=host,
                port=int(port),
                certfile=certfile or "config/certs/localhost.pem",
                keyfile=keyfile or "config/certs/localhost-key.pem",
            )
        elif port:
            getattr(mcp_server, "run_http")(data_path, host=host, port=int(port))
        else:
            mcp_server.run(data_path)
    except KeyboardInterrupt:
        pass
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

    extracted_root = Path(args.extracted_root or Path("data/extracted")).resolve()
    if not extracted_root.exists() or not extracted_root.is_dir():
        logging.error("Extracted root not found or not a directory: %s", extracted_root)
        return 2
    parsers_yaml = Path(args.parsers_config or Path("config/parsers.yaml").resolve())
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
    ok = 0
    for y in years:
        for st in src_types:
            try:
                path = discover_best_file(
                    extracted_root=extracted_root,
                    year=int(y),
                    source_type=st,
                    parsers_config_path=parsers_yaml,
                    force_discover=bool(getattr(args, "force_discover", False)),
                    deep_validate=bool(getattr(args, "deep_validate", False)),
                )
                logging.info("Discovered %s/%s → %s", y, st, path)
                ok += 1
            except (
                AssertionError,
                FileNotFoundError,
                RuntimeError,
                ValueError,
                KeyError,
            ) as e:
                logging.warning("No match for %s/%s: %s", y, st, e)
                continue
    return 0 if ok > 0 else 1


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
        help="Force re-download even if file already exists",
    )
    p_download.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files after successful download (even if same size)",
    )
    p_download.add_argument(
        "--source-type",
        type=str.upper,
        choices=SOURCE_TYPE_CHOICES,
        help="Limit download to a specific source type (case insensitive)",
    )
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
    p_discover.set_defaults(func=cmd_discover)

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
        help="Processed outputs root (CSV written under <processed-root>/csv). Defaults to ./data/processed",
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
    p_process.set_defaults(func=cmd_process)

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
        required=True,
        type=str.upper,
        choices=SOURCE_TYPE_CHOICES,
        help="Source type to validate (case insensitive).",
    )
    p_validate.add_argument(
        "--processed-root",
        required=False,
        default=None,
        help="Processed data root (CSV read from <processed-root>/csv). Defaults to ./data/processed",
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
    p_validate.set_defaults(func=cmd_validate)

    p_mcp = sub.add_parser("mcp-server", help="Run minimal MCP server (stdio or HTTP)")
    p_mcp.add_argument(
        "--data-path",
        default=None,
        help="Path to data/processed directory (defaults to ./data/processed)",
    )
    p_mcp.add_argument(
        "--port",
        default=None,
        help="If set, run HTTP/HTTPS transport on the given port",
    )
    p_mcp.add_argument(
        "--host",
        default=None,
        help="Host to bind for HTTP transport (default 127.0.0.1)",
    )
    p_mcp.add_argument("--https", action="store_true", help="Enable HTTPS (requires cert and key)")
    p_mcp.add_argument(
        "--certfile",
        default=None,
        help="Path to TLS cert PEM (default config/certs/localhost.pem)",
    )
    p_mcp.add_argument(
        "--keyfile",
        default=None,
        help="Path to TLS key PEM (default config/certs/localhost-key.pem)",
    )
    p_mcp.set_defaults(func=cmd_mcp_server)

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
