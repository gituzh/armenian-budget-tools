"""Core enumerations used across the package."""

from __future__ import annotations

from enum import Enum


class SourceType(str, Enum):
    """Types of supported data sources.

    Values are strings to ease serialization and CLI interchange.
    """

    BUDGET_LAW = "BUDGET_LAW"
    SPENDING_Q1 = "SPENDING_Q1"
    SPENDING_Q12 = "SPENDING_Q12"
    SPENDING_Q123 = "SPENDING_Q123"
    SPENDING_Q1234 = "SPENDING_Q1234"


__all__ = ["SourceType"]
