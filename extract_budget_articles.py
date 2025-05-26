#! /usr/bin/env python3
import logging
import os
from tqdm import tqdm
import colorlog
from budget import flatten_budget_excel_2019_2024, flatten_budget_excel_2025

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
    # Define file paths and corresponding years
    budget_files = {
        2019: "raw_data/budget_laws/2019/Orenqi havelvacner_Excel/2.Հավելված N1 աղյուսակ N2 ծախսերն ըստ ծրագրերի և միջոցառումների.xls",
        2020: "raw_data/budget_laws/2020/2.1.Havelvacner_Orenq/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xlsx",
        2021: "raw_data/budget_laws/2021/Orenqo havelvacner/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xls",
        2022: "raw_data/budget_laws/2022/1.1.ORENQI_HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xls",
        2023: "raw_data/budget_laws/2023/1.1.ORENQI HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xls",
        2024: "raw_data/budget_laws/2024/ORENQ HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների+.xls",
        2025: "raw_data/budget_laws/2025/օրենքի հավելվածներ/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների.xlsx",
    }

    # Process each year
    for year, file_path in budget_files.items():
        logger.info("\nProcessing year %d", year)

        # Choose appropriate function based on year
        if year == 2025:
            flatten_func = flatten_budget_excel_2025
            df, grand_total, rowtype_stats, statetrans_stats = flatten_func(
                file_path
            )
        else:
            flatten_func = flatten_budget_excel_2019_2024
            df, grand_total, rowtype_stats, statetrans_stats = flatten_func(
                file_path
            )

        logger.info("State machine function completed successfully!")
        logger.info("Processed %d subprograms", len(df))
        logger.info("Grand total: %f", grand_total)
        logger.info("Columns: %s", list(df.columns))
        logger.info("Sample data:\n%s", df.head())
        for row_type, count in rowtype_stats.items():
            logger.info("Row type %s: %d", row_type.name, count)
        for state, count in statetrans_stats.items():
            logger.info("State %s: %d", state.name, count)

        # Log information
        logger.info(df.info())
        logger.info(
            "Number of unique program codes: %d",
            len(df["program_code"].unique()),
        )
        logger.info(
            "Number of unique program names: %d",
            len(df["program_name"].unique()),
        )
        logger.info("Grand total (%d): %f", year, grand_total)

        # Create output directory if it doesn't exist
        output_dir = f"output/{year}"
        os.makedirs(output_dir, exist_ok=True)

        # Save to CSV
        df.to_csv(
            f"{output_dir}/budget_by_program_and_subprogram.csv",
            index=False,
            encoding="utf-8-sig",
        )

        # Save grand total
        with open(f"{output_dir}/grand_total.txt", "w", encoding="utf-8") as f:
            f.write(f"Grand total: {grand_total}")
