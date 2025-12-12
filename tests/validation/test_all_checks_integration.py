"""Integration tests for all validation checks.

This module ensures that all individual validation checks can be instantiated
and run against real budget data without raising unhandled exceptions,
confirming their basic compatibility and functionality within the framework.
"""

import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.models import CheckResult
from armenian_budget.validation.checks.required_fields import RequiredFieldsCheck
from armenian_budget.validation.checks.empty_identifiers import EmptyIdentifiersCheck
from armenian_budget.validation.checks.missing_financial_data import MissingFinancialDataCheck
from armenian_budget.validation.checks.hierarchical_totals import HierarchicalTotalsCheck
from armenian_budget.validation.checks.negative_totals import NegativeTotalsCheck
from armenian_budget.validation.checks.period_vs_annual import PeriodVsAnnualCheck
from armenian_budget.validation.checks.negative_percentages import NegativePercentagesCheck
from armenian_budget.validation.checks.execution_exceeds_100 import ExecutionExceeds100Check
from armenian_budget.validation.checks.percentage_calculation import PercentageCalculationCheck

# List of all check classes to be tested
ALL_CHECKS = [
    RequiredFieldsCheck,
    EmptyIdentifiersCheck,
    MissingFinancialDataCheck,
    HierarchicalTotalsCheck,
    NegativeTotalsCheck,
    PeriodVsAnnualCheck,
    NegativePercentagesCheck,
    ExecutionExceeds100Check,
    PercentageCalculationCheck,
]


@pytest.mark.parametrize("CheckClass", ALL_CHECKS)
def test_check_runs_on_real_data(all_budget_data, CheckClass):
    """
    Integration test to ensure each validation check runs without errors on real data.

    This test does not validate the correctness of the data itself, but rather
    confirms that the checks are compatible with the data schema and do not
    exception during execution.

    Args:
        all_budget_data: Fixture providing real budget data (df, overall, source_type).
        CheckClass: The validation check class to be tested.
    """
    df = all_budget_data.df
    overall = all_budget_data.overall_values
    source_type = SourceType(all_budget_data.source_type)

    check_instance = CheckClass()

    # Skip checks that don't apply to the current source type
    if not check_instance.applies_to_source_type(source_type):
        pytest.skip(f"{CheckClass.__name__} does not apply to {source_type.value}")

    # Execute the validation
    try:
        results = check_instance.validate(df, overall, source_type)

        # Assert that the result is a list of CheckResult objects
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, CheckResult)

    except Exception as e:
        pytest.fail(f"{CheckClass.__name__} raised an exception on {source_type.value} data: {e}")
