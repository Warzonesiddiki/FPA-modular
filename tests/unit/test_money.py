from decimal import Decimal
import pytest
from app.core.money import parse_major, to_minor, format_major, largest_remainder_allocate, variance

def test_parse_and_float_ban():
    assert parse_major("₹1,25,000.50") == 12500050
    assert parse_major("(1,200.00)") == -120000
    with pytest.raises(TypeError):
        parse_major(1.5)  # type: ignore[arg-type]

def test_format_indian_grouping():
    assert format_major(12500050) == "1,25,000.50"
    assert format_major(-120000) == "-1,200.00"

def test_largest_remainder_sums_exact():
    parts = largest_remainder_allocate(100, [1, 1, 1])
    assert sum(parts) == 100 and max(parts) - min(parts) <= 1

def test_variance_zero_budget():
    var, pct = variance(5000, 0)
    assert var == 5000 and pct is None
