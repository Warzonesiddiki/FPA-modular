from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class StagedRow:
    row_no: int
    sheet: str
    raw: dict
    values: dict = field(default_factory=dict)  # canonical fields; amount_minor in values['amount_minor']

@dataclass
class Quarantine:
    row_no: int
    sheet: str
    reason: str  # doc 06 closed list
    raw: dict
