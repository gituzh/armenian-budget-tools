import pandas as pd
from tqdm import tqdm
import re


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
            except ValueError:
                raise ValueError(
                    f"Grand total at row {i}, column 6 is not a valid number."
                )
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


# Run the function
df, grand_total = flatten_budget_excel(
    "raw_data/budget_laws/2025/օրենքի հավելվածներ/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների.xlsx"
)

# df, grand_total = flatten_budget_excel(
#     "raw_data/budget_laws/2024/ORENQ HAVELVACNER/2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների+.xls"
# )


# Print total for verification
print(f"Grand total from 'ԸՆԴԱՄԵՆԸ': {grand_total:,.2f} AMD")

# Save to CSV
df.to_csv(
    "output/2025/budget_by_program_and_subprogram.csv",
    index=False,
    encoding="utf-8-sig",
)


df[df["program_code"] == "1162"]["subprogram_total"].sum()


df[df["subprogram_code"] == "1220 - 11001"]["subprogram_total"].sum()