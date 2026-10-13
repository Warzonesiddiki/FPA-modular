"""Fiscal calendar (doc 02 period identity: FY = calendar year the FY starts; 2026-P01 = Apr 2026 at fy_start_month=4)."""
from __future__ import annotations

import calendar as _cal
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Period:
    period_id: str
    fiscal_year: int
    period_no: int
    start: date
    end: date

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


def make_period(fiscal_year: int, period_no: int, fy_start_month: int = 4) -> Period:
    if not 1 <= period_no <= 12:
        raise ValueError("period_no must be 1..12")
    month_index = (fy_start_month - 1) + (period_no - 1)
    year = fiscal_year + month_index // 12
    month = month_index % 12 + 1
    start = date(year, month, 1)
    end = date(year, month, _cal.monthrange(year, month)[1])
    return Period(f"{fiscal_year}-P{period_no:02d}", fiscal_year, period_no, start, end)


def parse_period_id(period_id: str) -> tuple[int, int]:
    fy, p = period_id.split("-P")
    return int(fy), int(p)


def shift_period(period_id: str, months: int, fy_start_month: int = 4) -> str:
    fy, no = parse_period_id(period_id)
    idx = (no - 1) + months
    return make_period(fy + idx // 12, idx % 12 + 1, fy_start_month).period_id


def prior_year(period_id: str) -> str:
    fy, no = parse_period_id(period_id)
    return f"{fy - 1}-P{no:02d}"


def periods_of_fy(fiscal_year: int, fy_start_month: int = 4) -> list[Period]:
    return [make_period(fiscal_year, n, fy_start_month) for n in range(1, 13)]


def period_of_date(d: date, fy_start_month: int = 4) -> str:
    """Map a calendar date to its period_id under the FY-start convention."""
    month_index = (d.month - fy_start_month) % 12
    fy = d.year if d.month >= fy_start_month else d.year - 1
    if fy_start_month == 1:
        fy = d.year
    return f"{fy}-P{month_index + 1:02d}"
