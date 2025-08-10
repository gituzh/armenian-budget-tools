import argparse
import logging
from pathlib import Path
from typing import Optional, List

import colorlog
import importlib
import yaml
## Avoid static import resolution issues in different environments
# We'll import the runner dynamically when needed


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

    Supports either --year or --years; when multiple years are provided,
    any missing year/source-type inputs only emit warnings and the
    command succeeds if at least one dataset was processed overall.
    """

    # Resolve output directory with default
    out_dir = Path(args.out or Path("data/processed/csv")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Dynamic import of parsers to avoid static resolution issues in some IDEs
    # Predeclare for linters
    flatten_budget_excel_2019_2024 = None  # type: ignore[assignment]
    flatten_budget_excel_2025 = None  # type: ignore[assignment]
    SourceType = None  # type: ignore[assignment]
    try:
        parsers_pkg = importlib.import_module("armenian_budget.ingestion.parsers")
        flatten_budget_excel_2019_2024 = getattr(parsers_pkg, "flatten_budget_excel_2019_2024")
        flatten_budget_excel_2025 = getattr(parsers_pkg, "flatten_budget_excel_2025")
        SourceType = getattr(parsers_pkg, "SourceType")
    except (ModuleNotFoundError, AttributeError, ImportError) as e:
        logging.error("Failed to import parsers: %s", e)
        return 3

    # Determine years
    years: List[int] = []
    if getattr(args, "years", None):
        parsed = _parse_years_arg(args.years)
        years = parsed or []
    elif getattr(args, "year", None):
        years = [int(args.year)]
    else:
        logging.error("One of --year or --years is required")
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
        ]

    # If user provided a single explicit input, require a single source type
    if getattr(args, "input", None) and len(source_types) > 1:
        logging.error("When --input is provided, --source-type must be specified to disambiguate.")
        return 2

    # If user provided --input and multiple years, reject as ambiguous
    if getattr(args, "input", None) and len(years) != 1:
        logging.error(
            "When --input is provided, only a single --year may be specified (not --years)."
        )
        return 2

    # Lazy import discovery if needed
    discover_best_file = None
    if not getattr(args, "input", None):
        try:
            ingestion_pkg = importlib.import_module("armenian_budget.ingestion")
            discover_best_file = getattr(ingestion_pkg, "discover_best_file")
        except (ModuleNotFoundError, AttributeError, ImportError) as e:
            logging.error("Discovery unavailable: %s", e)
            return 1

    parsers_yaml = Path(args.parsers_config or Path("config/parsers.yaml").resolve())
    dest_root = Path(args.dest_root or Path.cwd() / "data")

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
            if getattr(args, "input", None):
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
                        dest_root=dest_root,
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
                if year == 2025 and st_enum == SourceType.BUDGET_LAW:
                    df, overall, _, _ = flatten_budget_excel_2025(str(input_path))
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
    # Validation: run structural and financial checks
    csv_path = Path(args.csv)
    if not csv_path.exists():
        logging.error("CSV not found: %s", csv_path)
        return 2

    import pandas as pd

    df = pd.read_csv(csv_path)

    # Dynamic import to avoid path resolution issues during dev
    runner = importlib.import_module("armenian_budget.validation.runner")
    report = runner.run_all_checks(df, csv_path)
    runner.print_report(report)
    return 2 if report.has_errors(strict=False) else 0


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
    dest_root = Path(args.dest_root or Path.cwd() / "data")

    try:
        registry = SourceRegistry(cfg_path)
    except (FileNotFoundError, yaml.YAMLError, ValueError) as e:
        logging.error("Failed to load sources: %s", e)
        return 3

    years = _parse_years_arg(args.years)
    sources = registry.all() if years is None else registry.for_years(years)
    # Keep budget laws and spending sources
    sources = [
        s for s in sources if s.source_type.startswith("spending_") or s.source_type == "budget_law"
    ]
    if not sources:
        logging.warning("No matching sources to download.")
        return 0

    results = download_sources(
        sources,
        dest_root,
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
            input_dir = dest_root / "original" / "spending_reports" / str(y)
            output_dir = dest_root / "extracted" / "spending_reports" / str(y)
            extract_rar_files(input_dir, output_dir)
            extract_zip_files(input_dir, output_dir)

    return 0 if fail == 0 else 1


def cmd_extract(args: argparse.Namespace) -> int:
    # Import dynamically to avoid static import resolution problems in some IDEs
    organizer_mod = importlib.import_module("armenian_budget.sources.organizer")
    extract_rar_files = getattr(organizer_mod, "extract_rar_files")
    extract_zip_files = getattr(organizer_mod, "extract_zip_files")

    dest_root = Path(args.dest_root or Path.cwd() / "data")
    years = _parse_years_arg(args.years)
    if years is None:
        # Auto-detect years from data/original/spending_reports/*
        base = dest_root / "original" / "spending_reports"
        if base.exists():
            years = sorted(int(p.name) for p in base.iterdir() if p.is_dir() and p.name.isdigit())
        else:
            logging.warning("No original spending_reports directory found: %s", base)
            return 0

    if not years:
        logging.warning("No years to extract.")
        return 0

    for y in years:
        input_dir = dest_root / "original" / "spending_reports" / str(y)
        output_dir = dest_root / "extracted" / "spending_reports" / str(y)
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
        logging.info("Starting MCP HTTPS server on %s:%s (data path: %s)", host, port, display_path)
    elif port:
        logging.info("Starting MCP HTTP server on %s:%s (data path: %s)", host, port, display_path)
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

    dest_root = Path(args.dest_root or Path.cwd() / "data")
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
                    dest_root=dest_root,
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
    p = argparse.ArgumentParser(prog="armenian-budget", description="Armenian Budget Tools (v0.1)")
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

    p_process = sub.add_parser("process", help="Process one or more source Excels and write CSV")
    p_process.add_argument("--year", required=False, help="Year, e.g., 2023")
    p_process.add_argument(
        "--years",
        required=False,
        help=(
            "Comma-separated years (e.g. 2019,2020) or range (2019-2024). "
            "When provided, processes all listed years."
        ),
    )
    p_process.add_argument(
        "--source-type",
        required=False,
        choices=[
            "BUDGET_LAW",
            "SPENDING_Q1",
            "SPENDING_Q12",
            "SPENDING_Q123",
            "SPENDING_Q1234",
        ],
        help=(
            "Source type. If omitted, all supported source types for the year will be processed."
        ),
    )
    p_process.add_argument("--input", required=False, help="Path to source Excel file")
    p_process.add_argument(
        "--out",
        required=False,
        default=None,
        help="Output directory for CSV/JSON (defaults to ./data/processed/csv)",
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
        "--dest-root",
        default=None,
        help="Data root (defaults to ./data) where original/ and extracted/ live",
    )
    p_process.set_defaults(func=cmd_process)

    p_validate = sub.add_parser("validate", help="Validate a processed CSV (minimal checks)")
    p_validate.add_argument("--csv", required=True, help="Path to CSV produced by process")
    p_validate.set_defaults(func=cmd_validate)

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
        "--dest-root",
        default=None,
        help="Destination root (defaults to ./data) containing original/ and extracted/",
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
    p_download.set_defaults(func=cmd_download)

    p_extract = sub.add_parser("extract", help="Extract already downloaded spending archives")
    p_extract.add_argument(
        "--years",
        help="Comma-separated years (e.g. 2019,2020) or range (2019-2024). If omitted, auto-detect from data/original.",
    )
    p_extract.add_argument(
        "--dest-root",
        default=None,
        help="Destination root (defaults to ./data) containing original/ and extracted/",
    )
    p_extract.set_defaults(func=cmd_extract)

    p_mcp = sub.add_parser("mcp-server", help="Run minimal MCP server (stdio or HTTP)")
    p_mcp.add_argument(
        "--data-path",
        default=None,
        help="Path to data/processed directory (defaults to ./data/processed)",
    )
    p_mcp.add_argument(
        "--port", default=None, help="If set, run HTTP/HTTPS transport on the given port"
    )
    p_mcp.add_argument(
        "--host", default=None, help="Host to bind for HTTP transport (default 127.0.0.1)"
    )
    p_mcp.add_argument("--https", action="store_true", help="Enable HTTPS (requires cert and key)")
    p_mcp.add_argument(
        "--certfile", default=None, help="Path to TLS cert PEM (default config/certs/localhost.pem)"
    )
    p_mcp.add_argument(
        "--keyfile",
        default=None,
        help="Path to TLS key PEM (default config/certs/localhost-key.pem)",
    )
    p_mcp.set_defaults(func=cmd_mcp_server)

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
        choices=[
            "BUDGET_LAW",
            "SPENDING_Q1",
            "SPENDING_Q12",
            "SPENDING_Q123",
            "SPENDING_Q1234",
        ],
        help="Limit discovery to a specific source type",
    )
    p_discover.add_argument(
        "--dest-root",
        default=None,
        help="Data root (defaults to ./data) where original/ and extracted/ live",
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
