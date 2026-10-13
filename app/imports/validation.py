"""Row validation + mapping to canonical GL fields (doc 06 SS4-5). Nothing silently discarded."""
from __future__ import annotations
from datetime import datetime
from app.core import money
from .models import StagedRow, Quarantine

REQUIRED = ["entity", "account", "voucher_no", "posting_date"]

def _parse_date(text: str, fmt: str) -> str | None:
    try:
        return datetime.strptime(text.strip(), fmt).date().isoformat()
    except (ValueError, AttributeError):
        return None

def apply_mapping(rows: list[StagedRow], mapping: dict[str, str], date_format: str = "%Y-%m-%d",
                  debit_col: str | None = None, credit_col: str | None = None) -> tuple[list[StagedRow], list[Quarantine]]:
    """mapping: canonical field -> source column. Returns (valid, quarantined); counts reconcile."""
    valid, quar = [], []
    for row in rows:
        v = {}
        for canon, src in mapping.items():
            v[canon] = row.raw.get(src, "")
        # amount: signed 'amount' or debit/credit pair
        try:
            if debit_col and credit_col:
                d = money.parse_major(v.get("debit_raw", row.raw.get(debit_col, "0")) or "0")
                c = money.parse_major(v.get("credit_raw", row.raw.get(credit_col, "0")) or "0")
                v["amount_minor"] = d - c
            else:
                v["amount_minor"] = money.parse_major(v.get("amount", ""))
        except Exception:
            quar.append(Quarantine(row.row_no, row.sheet, "BAD_AMOUNT", row.raw)); continue
        missing = [f for f in REQUIRED if not str(v.get(f, "")).strip()]
        if missing:
            quar.append(Quarantine(row.row_no, row.sheet, "MISSING_REQUIRED", row.raw)); continue
        iso = _parse_date(str(v["posting_date"]), date_format)
        if iso is None:
            quar.append(Quarantine(row.row_no, row.sheet, "BAD_DATE", row.raw)); continue
        v["posting_date"] = iso
        if v.get("document_date"):
            d2 = _parse_date(str(v["document_date"]), date_format)
            v["document_date"] = d2 or iso
        row.values = v
        valid.append(row)
    return valid, quar
