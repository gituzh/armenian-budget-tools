import re
import logging
import os
import pandas as pd
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def flatten_budget_excel_2024(excel_path: str) -> tuple[pd.DataFrame, float]:
    """
    Reads the 2024 budget Excel file (.xlsx) with its multi-line hierarchical structure and
    flattens it into a table with one row per subprogram. The output table includes:

      - state_body, state_body_total
      - program_code, program_name, program_goal, program_result_desc, program_total
      - subprogram_code, subprogram_name, subprogram_desc, subprogram_type, subprogram_total

    Steps:
      1. Read all rows from the Excel file (no header or row skipping).
      2. Locate the "ԸՆԴԱՄԵՆԸ" row in col2; its total (grand_total) is in col3.
         Processing starts from the row after this.
      3. Iterate over rows (with a progress bar), detecting:
         - **State Body Row**: if col0 and col1 are empty, col2 is non-empty, and col3 is
           numeric. This sets the current state body context.
         - **Program Row**: if col0 is non-empty and numeric and col3 is numeric.
           Look ahead for additional program details (name, goal, result) from rows with
           empty col0 (skipping label rows ending with "`").
         - **Subprogram Block**: a row with col0 equal to "Ծրագրի միջոցառումներ" signals the
           start of subprograms.
         - **Subprogram Row**: in the subprogram block, if col1 is non-empty and numeric and
           col3 is numeric, then it is a subprogram row. A forward-looking loop collects extra
           lines from col2 for subprogram description and type. It now also stops if a new
           program row is detected.
      4. Each subprogram record is built using the current state body and program context.
      5. All numeric totals are converted to floats.
      6. Returns (flattened DataFrame, grand_total).
    """
    # 1. Read entire Excel file (no header).
    df = pd.read_excel(excel_path, sheet_name=0, header=None)
    df = df.fillna("")

    # Helper: check if value is numeric.
    def is_numeric(val):
        try:
            float(val)
            return True
        except:
            return False

    # 2. Locate "ԸՆԴԱՄԵՆԸ" row in col2; grand total is in col3.
    grand_total = None
    start_idx = None
    for i in range(len(df)):
        col2_val = str(df.loc[i, 2]).strip().lower()
        if col2_val == "ընդամենը":
            if not is_numeric(df.loc[i, 3]):
                raise ValueError(f"Grand total in row {i} is not numeric.")
            grand_total = float(df.loc[i, 3])
            start_idx = i + 1  # Begin after grand total row.
            break
    if start_idx is None:
        raise ValueError("Could not find a row where col2 is 'ԸՆԴԱՄԵՆԸ'.")

    # 3. Initialize context variables.
    current_state_body = ""
    current_state_body_total = None
    current_program_code = ""
    current_program_name = ""
    current_program_goal = ""
    current_program_result_desc = ""
    current_program_total = None
    in_subprogram_block = False

    results = []  # To store flat records.
    n = len(df)
    i = start_idx

    # Set up progress bar for the main loop.
    pbar = tqdm(total=(n - start_idx), desc="Flattening rows")

    while i < n:
        # Read current row's columns 0 to 3.
        col0 = str(df.loc[i, 0]).strip()
        col1 = str(df.loc[i, 1]).strip()
        col2 = str(df.loc[i, 2]).strip()
        col3 = str(df.loc[i, 3]).strip()
        pbar.update(1)

        # -- State Body Row --
        # If col0 and col1 are empty, col2 non-empty, and col3 numeric.
        if col0 == "" and col1 == "" and col2 and is_numeric(col3):
            current_state_body = col2
            current_state_body_total = float(col3)
            # Reset program context.
            current_program_code = ""
            current_program_name = ""
            current_program_goal = ""
            current_program_result_desc = ""
            current_program_total = None
            in_subprogram_block = False
            i += 1
            continue

        # -- Detect start of Subprogram Block --
        if col0.lower().replace(" ", "") == "ծրագրիմիջոցառումներ":
            in_subprogram_block = True
            i += 1
            continue

        # -- Program Row and Details --
        if not in_subprogram_block:
            # If col0 is non-empty and numeric and col3 is numeric, it's a new program.
            if col0 and is_numeric(col0) and is_numeric(col3):
                current_program_code = col0
                current_program_total = float(col3)
                # Look ahead to collect extra program details from rows with empty col0.
                prog_name = ""
                prog_goal = ""
                prog_result = ""
                j = i + 1
                while j < n:
                    next_row = df.loc[j]
                    next_col0 = str(next_row[0]).strip()
                    next_col2 = str(next_row[2]).strip()
                    # Break if a new program or state body starts.
                    if next_col0:
                        break
                    if next_col2:
                        # If row is a label (ends with "`"), skip and use the following row.
                        if next_col2.endswith("`"):
                            if j + 1 < n:
                                potential = str(df.loc[j + 1, 2]).strip()
                                if potential and (not potential.endswith("`")):
                                    if not prog_name:
                                        prog_name = potential
                                    elif not prog_goal:
                                        prog_goal = potential
                                    elif not prog_result:
                                        prog_result = potential
                                    j += 2
                                    continue
                        else:
                            if not prog_name:
                                prog_name = next_col2
                            elif not prog_goal:
                                prog_goal = next_col2
                            elif not prog_result:
                                prog_result = next_col2
                    j += 1
                if not prog_name:
                    prog_name = col2
                current_program_name = prog_name
                current_program_goal = prog_goal
                current_program_result_desc = prog_result
                pbar.update(j - i - 1)
                i = j
                continue
            else:
                i += 1
                continue

        # -- Subprogram Block Processing --
        if in_subprogram_block:
            # A subprogram row is detected if col1 is non-empty and numeric and col3 is numeric.
            if col1 and is_numeric(col1) and is_numeric(col3):
                subprogram_code = col1
                subprogram_total = float(col3)
                subprogram_name = col2  # Use col2 as initial subprogram name.
                subprogram_desc = ""
                subprogram_type = ""
                j = i + 1
                extra_lines = []
                while j < n:
                    next_row = df.loc[j]
                    next_col0 = str(next_row[0]).strip()
                    next_col1 = str(next_row[1]).strip()
                    next_col2 = str(next_row[2]).strip()
                    # Break if the next row qualifies as a state body row.
                    if (
                        next_col0 == ""
                        and next_col1 == ""
                        and next_col2
                        and is_numeric(str(next_row[3]).strip())
                    ):
                        in_subprogram_block = False
                        break
                    # Break if next row is a new program row.
                    if (
                        next_col0
                        and is_numeric(next_col0)
                        and is_numeric(str(next_row[3]).strip())
                    ):
                        in_subprogram_block = False
                        break
                    # Also break if a new subprogram starts (col1 non-empty).
                    if next_col1:
                        break

                    if next_col2:
                        extra_lines.append(next_col2)
                    j += 1
                if extra_lines:
                    subprogram_desc = extra_lines[0]
                if len(extra_lines) > 1:
                    subprogram_type = extra_lines[1]
                results.append(
                    {
                        "state_body": current_state_body,
                        "state_body_total": current_state_body_total,
                        "program_code": current_program_code,
                        "program_name": current_program_name,
                        "program_goal": current_program_goal,
                        "program_result_desc": current_program_result_desc,
                        "program_total": current_program_total,
                        "subprogram_code": subprogram_code,
                        "subprogram_name": subprogram_name,
                        "subprogram_desc": subprogram_desc,
                        "subprogram_type": subprogram_type,
                        "subprogram_total": subprogram_total,
                    }
                )
                pbar.update(j - i - 1)
                i = j
                continue

        # Default: move to next row.
        i += 1
    pbar.close()

    # 4. Build final DataFrame with required column order.
    col_order = [
        "state_body",
        "state_body_total",
        "program_code",
        "program_name",
        "program_goal",
        "program_result_desc",
        "program_total",
        "subprogram_code",
        "subprogram_name",
        "subprogram_desc",
        "subprogram_type",
        "subprogram_total",
    ]

    result_df = pd.DataFrame(results, columns=col_order)
    return result_df, grand_total


def flatten_budget_excel(excel_path: str) -> tuple[pd.DataFrame, float]:
    """
    Reads a multi-level Armenian state budget Excel file and flattens it into a single table
    with one row per subprogram and contextual info from its parent program and state body.

    The function:
    1. Reads all rows (no skipping)
    2. Identifies the "ԸՆԴԱՄԵՆԸ" row and stores the grand total from its last column
    3. Starts parsing data from the row *after* "ԸՆԴԱՄԵՆԸ"
    4. Detects state body, program, and subprogram rows using specific structural rules
    5. Collects subprogram rows into a flat table with 12 columns
    6. Converts all financial total fields into floats
    7. Returns the resulting DataFrame and the grand total separately

    Parameters:
        excel_path (str): Path to the Excel file to parse

    Returns:
        pd.DataFrame: Flattened table with subprogram records
        float: The grand total from the "ԸՆԴԱՄԵՆԸ" row
    """
    # 1. Read the Excel file as-is (no header or skipping)
    df = pd.read_excel(excel_path, sheet_name=0, header=None)

    # 2. Replace NaN values with empty strings for easier string operations
    df = df.fillna("")

    # Helper function to check if a value is numeric
    def is_numeric(val):
        try:
            float(val)
            return True
        except ValueError:
            return False

    # 3. Locate the "ԸՆԴԱՄԵՆԸ" row and extract the grand total from column 6
    grand_total = None
    start_idx = None
    for i in range(len(df)):
        c0 = str(df.loc[i, 0]).strip().lower()
        if c0 == "ընդամենը":
            try:
                grand_total = float(df.loc[i, 6])
            except ValueError as exc:
                raise ValueError(
                    f"Grand total at row {i}, column 6 is not a valid number."
                ) from exc
            start_idx = i + 1  # start reading actual data from the next row
            break

    if start_idx is None:
        raise ValueError("Could not find a row where column 0 is 'ԸՆԴԱՄԵՆԸ'.")

    # 4. Initialize "current" values to track state body and program context
    current_state_body = ""
    current_state_body_total = ""
    current_program_code = ""
    current_program_name = ""
    current_program_goal = ""
    current_program_result_desc = ""
    current_program_total = ""

    # 5. Prepare container for final flattened records
    rows = []

    # 6. Iterate over all rows after the grand total marker with a progress bar
    for i in tqdm(range(start_idx, len(df)), desc="Flattening rows"):
        c0 = str(df.loc[i, 0]).strip()  # potential state body name
        c1 = str(df.loc[i, 1]).strip()  # potential program code
        c2 = str(df.loc[i, 2]).strip()  # potential subprogram code
        c3 = str(df.loc[i, 3]).strip()  # name / goal / desc
        c4 = str(df.loc[i, 4]).strip()
        c5 = str(df.loc[i, 5]).strip()
        c6 = str(df.loc[i, 6]).strip()  # numeric total field

        # A. Detect and store a new state body row
        #    - column 0 has text
        #    - column 6 has numeric value (total)
        if c0 and is_numeric(c6):
            current_state_body = c0
            current_state_body_total = float(c6)
            # Reset program-level state
            current_program_code = ""
            current_program_name = ""
            current_program_goal = ""
            current_program_result_desc = ""
            current_program_total = ""
            continue

        # B. Detect and store a new program row
        #    - column 1 is numeric (program code)
        #    - columns 3–6 are all non-empty
        if is_numeric(c1) and all([c3, c4, c5, c6]):
            current_program_code = c1
            current_program_name = c3
            current_program_goal = c4
            current_program_result_desc = c5
            current_program_total = float(c6)
            continue

        # C. Detect a subprogram row
        #    - column 2 contains a dash (e.g. "1154 - 11001")
        #    - columns 3–6 are all non-empty
        if "-" in c2 and all([c3, c4, c5, c6]):
            try:
                subprogram_total = float(c6)
            except ValueError:
                continue  # skip row if total is invalid

            rows.append(
                {
                    "state_body": current_state_body,
                    "state_body_total": (
                        float(current_state_body_total)
                        if current_state_body_total
                        else ""
                    ),
                    "program_code": current_program_code,
                    "program_name": current_program_name,
                    "program_goal": current_program_goal,
                    "program_result_desc": current_program_result_desc,
                    "program_total": (
                        float(current_program_total)
                        if current_program_total
                        else ""
                    ),
                    "subprogram_code": c2,
                    "subprogram_name": c3,
                    "subprogram_desc": c4,
                    "subprogram_type": c5,
                    "subprogram_total": subprogram_total,
                }
            )

    # 7. Define output column order as specified in the original requirement
    column_order = [
        "state_body",
        "state_body_total",
        "program_code",
        "program_name",
        "program_goal",
        "program_result_desc",
        "program_total",
        "subprogram_code",
        "subprogram_name",
        "subprogram_desc",
        "subprogram_type",
        "subprogram_total",
    ]

    # 8. Build DataFrame with the correct column order
    result_df = pd.DataFrame(rows, columns=column_order)

    return result_df, grand_total


# Define file paths and corresponding years
budget_files = {
    2020: "raw_data/budget_laws/2020/2.1.Havelvacner_Orenq/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xlsx",
    2021: "raw_data/budget_laws/2021/Orenqo havelvacner/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xls",
    2022: "raw_data/budget_laws/2022/1.1.ORENQI_HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xls",
    2023: "raw_data/budget_laws/2023/1.1.ORENQI HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների..xls",
    2024: "raw_data/budget_laws/2024/ORENQ HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների+.xls",
    2025: "raw_data/budget_laws/2025/օրենքի հավելվածներ/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների.xlsx",
}

# Process each year
for year, file_path in budget_files.items():
    logger.info(f"\nProcessing year {year}")

    # Choose appropriate function based on year
    if year == 2025:
        flatten_func = flatten_budget_excel
    else:
        flatten_func = flatten_budget_excel_2024

    # Process the file
    df, grand_total = flatten_func(file_path)

    # Log information
    logger.info(df.info())
    logger.info(
        "Number of unique program codes: %d", len(df["program_code"].unique())
    )
    logger.info(
        "Number of unique program names: %d", len(df["program_name"].unique())
    )
    logger.info(f"Grand total ({year}): {grand_total}")

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
    with open(f"{output_dir}/grand_total.txt", "w") as f:
        f.write(f"Grand total: {grand_total}")
