"""Tests for the data schema functions in armenian_budget.core.schemas.

This module verifies that the schema functions correctly return required fields,
financial fields, amount fields, and percentage fields for different source types.
"""

import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import (
    get_required_fields,
    get_financial_fields,
    get_amount_fields,
    get_percentage_fields,
)

ALL_SOURCE_TYPES = list(SourceType)


@pytest.mark.parametrize("source_type", ALL_SOURCE_TYPES)
def test_get_required_fields(source_type):
    csv_fields, json_fields = get_required_fields(source_type)
    assert isinstance(csv_fields, list)
    assert isinstance(json_fields, list)
    assert "state_body" in csv_fields
    assert "program_code" in csv_fields
    assert "program_name" in csv_fields

    if source_type == SourceType.BUDGET_LAW:
        assert "subprogram_total" in csv_fields
        assert "overall_total" in json_fields
    elif source_type == SourceType.MTEP:
        assert "program_total_y0" in csv_fields
        assert "overall_total_y0" in json_fields
    elif source_type in (SourceType.SPENDING_Q1, SourceType.SPENDING_Q12, SourceType.SPENDING_Q123):
        assert "subprogram_period_plan" in csv_fields
        assert "overall_period_plan" in json_fields
    elif source_type == SourceType.SPENDING_Q1234:
        assert "subprogram_annual_plan" in csv_fields
        assert "overall_annual_plan" in json_fields
        assert "subprogram_period_plan" not in csv_fields
        assert "overall_period_plan" not in json_fields


@pytest.mark.parametrize("source_type", ALL_SOURCE_TYPES)
def test_get_financial_fields(source_type):
    csv_fields, json_fields = get_financial_fields(source_type)
    assert isinstance(csv_fields, list)
    assert isinstance(json_fields, list)

    if source_type == SourceType.BUDGET_LAW:
        assert "state_body_total" in csv_fields
        assert "overall_total" in json_fields
    elif source_type == SourceType.MTEP:
        assert "state_body_total_y1" in csv_fields
        assert "overall_total_y1" in json_fields
    elif source_type in (SourceType.SPENDING_Q1, SourceType.SPENDING_Q12, SourceType.SPENDING_Q123):
        assert "program_actual" in csv_fields
        assert "program_actual_vs_rev_period_plan" in csv_fields
        assert "overall_actual" in json_fields
        assert "overall_actual_vs_rev_period_plan" in json_fields
    elif source_type == SourceType.SPENDING_Q1234:
        assert "program_actual" in csv_fields
        assert "program_actual_vs_rev_annual_plan" in csv_fields
        assert "overall_actual" in json_fields
        assert "overall_actual_vs_rev_annual_plan" in json_fields
        assert "program_actual_vs_rev_period_plan" not in csv_fields
        assert "overall_actual_vs_rev_period_plan" not in json_fields


@pytest.mark.parametrize("source_type", ALL_SOURCE_TYPES)
def test_get_amount_fields(source_type):
    csv_fields, json_fields = get_amount_fields(source_type)
    assert isinstance(csv_fields, list)
    assert isinstance(json_fields, list)

    # Amount fields should not contain percentage fields
    for field in csv_fields + json_fields:
        assert "vs" not in field
        assert "plan_years" not in field

    if source_type == SourceType.BUDGET_LAW:
        assert "program_total" in csv_fields
        assert "overall_total" in json_fields
    elif source_type == SourceType.MTEP:
        assert "program_total_y2" in csv_fields
        assert "overall_total_y2" in json_fields
    elif source_type in (SourceType.SPENDING_Q1, SourceType.SPENDING_Q12, SourceType.SPENDING_Q123):
        assert "subprogram_rev_period_plan" in csv_fields
        assert "overall_rev_period_plan" in json_fields
    elif source_type == SourceType.SPENDING_Q1234:
        assert "subprogram_rev_annual_plan" in csv_fields
        assert "overall_rev_annual_plan" in json_fields
        assert "subprogram_rev_period_plan" not in csv_fields
        assert "overall_rev_period_plan" not in json_fields


@pytest.mark.parametrize("source_type", ALL_SOURCE_TYPES)
def test_get_percentage_fields(source_type):
    csv_fields, json_fields = get_percentage_fields(source_type)
    assert isinstance(csv_fields, list)
    assert isinstance(json_fields, list)

    if source_type in (SourceType.BUDGET_LAW, SourceType.MTEP):
        assert not csv_fields
        assert not json_fields
    else:
        assert csv_fields
        assert json_fields
        for field in csv_fields + json_fields:
            assert "vs" in field

    if source_type in (SourceType.SPENDING_Q1, SourceType.SPENDING_Q12, SourceType.SPENDING_Q123):
        assert "program_actual_vs_rev_period_plan" in csv_fields
        assert "overall_actual_vs_rev_period_plan" in json_fields
    elif source_type == SourceType.SPENDING_Q1234:
        assert "program_actual_vs_rev_annual_plan" in csv_fields
        assert "overall_actual_vs_rev_annual_plan" in json_fields
        assert "program_actual_vs_rev_period_plan" not in csv_fields
        assert "overall_actual_vs_rev_period_plan" not in json_fields
