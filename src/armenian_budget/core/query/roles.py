from __future__ import annotations

from typing import Dict


def get_column_roles(source_type: str) -> Dict[str, str]:
    """Return standardized role→column mapping for known source types.

    Mirrors README/architecture docs and MCP surface.
    """
    st = str(source_type).upper()
    if st == "BUDGET_LAW":
        return {"allocated": "subprogram_total"}
    if st in {"SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"}:
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
            "execution_rate": "subprogram_actual_vs_rev_annual_plan",
        }
    if st == "SPENDING_Q1234":
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
        }
    return {}


