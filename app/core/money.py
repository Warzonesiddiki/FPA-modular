"""THE only money module (doc 03). Integer minor units internally, Decimal at boundaries.

Rules: floats are rejected for money; rounding is ROUND_HALF_UP and happens only here;
storage exponent comes from the project currency (doc 27: INR/USD=2, JPY=0, KWD=3).
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .errors import AppError


def _reject_float(value: object) -> None:
    if isinstance(value, float):
        raise TypeError("Float is banned for money — use Decimal or integer minor units (doc 03).")


def parse_major(value: str | int | Decimal, exponent: int = 2) -> int:
    """Parse a major-unit amount ('125000.50', '(1,200.00)', '₹1,200') into integer minor units."""
    _reject_float(value)  # type: ignore[arg-type]
    if isinstance(value, int):
        return value * (10 ** exponent)
    text = str(value).strip().replace(",", "").replace("₹", "").replace("$", "").strip()
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1]
    if text.startswith("+"):
        text = text[1:]
    try:
        dec = Decimal(text)
    except InvalidOperation:
        raise AppError("FP&A-ERR-021", f"We couldn't read the amount '{value}'.",
                       "Check the amount column in your file — it should contain numbers only.")
    if negative:
        dec = -dec
    return to_minor(dec, exponent)


def to_minor(dec: Decimal, exponent: int = 2) -> int:
    _reject_float(dec)
    q = Decimal(1).scaleb(-exponent)
    return int((dec.quantize(q, rounding=ROUND_HALF_UP)).scaleb(exponent))


def to_major(minor: int, exponent: int = 2) -> Decimal:
    return Decimal(minor).scaleb(-exponent)


def format_major(minor: int, exponent: int = 2, grouping: str = "en-IN") -> str:
    """Format minor units as a grouped decimal string (display only; canonical value stays minor)."""
    dec = to_major(minor, exponent)
    sign = "-" if dec < 0 else ""
    dec = abs(dec)
    whole = int(dec)
    frac = dec - whole
    frac_str = f"{frac:.{exponent}f}"[1:] if exponent else ""  # '.50' or ''
    digits = str(whole)
    if grouping == "en-IN" and len(digits) > 3:  # lakh/crore grouping
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head:
            parts.insert(0, head)
        grouped = ",".join(parts + [tail])
    else:
        grouped = f"{whole:,}"
    return f"{sign}{grouped}{frac_str}"


def pct_change(actual_minor: int, base_minor: int) -> Decimal | None:
    """Percentage change; None when base is zero (never divide by zero — doc 03 §5)."""
    if base_minor == 0:
        return None
    return (Decimal(actual_minor - base_minor) / Decimal(abs(base_minor)) * Decimal(100))


def variance(actual_minor: int, budget_minor: int) -> tuple[int, Decimal | None]:
    return actual_minor - budget_minor, pct_change(actual_minor, budget_minor)


def largest_remainder_allocate(total_minor: int, weights: list[int]) -> list[int]:
    """Split total by weights so the parts sum EXACTLY to total (doc 03 §3)."""
    if not weights:
        return []
    wsum = sum(abs(w) for w in weights)
    if wsum == 0:
        out = [0] * len(weights)
        out[0] = total_minor
        return out
    sign = -1 if total_minor < 0 else 1
    total = abs(total_minor)
    raw = [Decimal(total * abs(w)) / Decimal(wsum) for w in weights]
    floors = [int(r) for r in raw]
    remainder = total - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: raw[i] - floors[i], reverse=True)
    for i in order[:remainder]:
        floors[i] += 1
    return [sign * v for v in floors]
