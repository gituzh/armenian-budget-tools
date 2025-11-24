"""Parser output verification tests.

These tests verify that the parser produces correctly structured output
from real Excel files. They are integration tests that check:
- Non-empty CSV output
- Correct data types (integer codes, etc.)
- Correct structural relationships (code/name pairing, etc.)

These tests use actual parsed data from data/processed/csv/ and verify
parser output quality, not semantic validation rules.
"""
