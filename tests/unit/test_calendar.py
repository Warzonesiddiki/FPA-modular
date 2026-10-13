from datetime import date
from app.core.calendar import make_period, period_of_date, prior_year, shift_period

def test_period_identity():
    p = make_period(2026, 1, 4)
    assert p.period_id == "2026-P01" and p.start == date(2026, 4, 1) and p.end == date(2026, 4, 30)
    assert make_period(2026, 12, 4).start == date(2027, 3, 1)

def test_of_date_and_py():
    assert period_of_date(date(2026, 4, 15)) == "2026-P01"
    assert period_of_date(date(2027, 3, 15)) == "2026-P12"
    assert period_of_date(date(2026, 1, 15)) == "2025-P10"
    assert prior_year("2026-P01") == "2025-P01"
    assert shift_period("2026-P12", 1) == "2027-P01"
