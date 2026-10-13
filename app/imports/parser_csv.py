"""CSV/TSV parser (doc 06): delimiter+encoding handling, row numbers preserved, nothing dropped."""
from __future__ import annotations
import csv, io
from pathlib import Path
from .models import StagedRow

def _decode(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return data.decode("latin-1", errors="replace")

def parse_csv(path: str | Path, sheet: str = "csv") -> tuple[list[str], list[StagedRow]]:
    text = _decode(Path(path).read_bytes())
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(text), dialect)
    rows = list(reader)
    if not rows:
        return [], []
    headers = [h.strip() for h in rows[0]]
    out = []
    for i, r in enumerate(rows[1:], start=2):  # 1-based incl header
        if not any(c.strip() for c in r):
            continue  # counted by caller via row_count_in - len(out)
        raw = {headers[j]: (r[j].strip() if j < len(r) else "") for j in range(len(headers))}
        out.append(StagedRow(row_no=i, sheet=sheet, raw=raw))
    return headers, out
