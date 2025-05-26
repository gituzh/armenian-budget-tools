#! /usr/bin/env python3
import logging
import os
from tqdm import tqdm
import colorlog
import json
from budget import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    SourceType,
)

# Configure logging with colorlog
logger = logging.getLogger()
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# "%(log_color)s%(asctime)s - %(levelname)s - %(message)s"
log_format = (
    "%(asctime)s:%(levelname)s:%(name)s in "
    "%(filename)s:%(funcName)s:%(lineno)d: %(message)s"
)
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}
stream_handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    f"%(log_color)s{log_format}",
    log_colors=log_colors,
    reset=True,
    style="%",
)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

# Configure child loggers to propagate to root
# logging.getLogger('budget').propagate = True


if __name__ == "__main__":
    # Load sources from JSON
    with open("sources.json", "r", encoding="utf-8") as f:
        budget_files = json.load(f)

    # Process each year
    for year, source_types in budget_files.items():
        logger.info("\nProcessing year %s", year)

        # Process each source type
        for source_type, file_path in source_types.items():
            if not file_path.strip():
                logger.info(
                    "Skipping %s for year %s (no file path)", source_type, year
                )
                continue

            logger.info("\nProcessing source type %s", source_type)

            # Choose appropriate function based on year/source type
            if year == "2025":
                flatten_func = flatten_budget_excel_2025
                df, overall, rowtype_stats, statetrans_stats = flatten_func(
                    file_path
                )
            else:
                flatten_func = flatten_budget_excel_2019_2024
                df, overall, rowtype_stats, statetrans_stats = flatten_func(
                    file_path,
                    source_type=SourceType[source_type],
                )

            logger.info("State machine function completed successfully!")
            logger.info("Processed %d subprograms", len(df))
            logger.info("Overall values: %s", overall)
            logger.info("Columns: %s", list(df.columns))
            logger.info("Sample data:\n%s", df.head())
            logger.info(df.info())
            logger.info(
                "Number of unique program codes: %d",
                len(df["program_code"].unique()),
            )
            logger.info(
                "Number of unique program names: %d",
                len(df["program_name"].unique()),
            )
            logger.info("Overall values (%s): %s", year, overall)

            # Create output directory if it doesn't exist
            output_dir = f"output/{year}/{source_type}"
            os.makedirs(output_dir, exist_ok=True)

            # Save to CSV
            df.to_csv(
                f"{output_dir}/{year}_{source_type}.csv",
                index=False,
                encoding="utf-8-sig",
            )

            # Save grand total as JSON
            with open(
                f"{output_dir}/{year}_{source_type}_overall.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(overall, f, ensure_ascii=False, indent=2)
