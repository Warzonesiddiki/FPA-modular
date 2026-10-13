"""Deterministic ids (doc 06 §3): same input -> same id, so re-imports replace, never duplicate."""
from __future__ import annotations

import hashlib


def _h(text: str, n: int = 32) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def batch_id(file_sha256: str, period_id: str, source_kind: str) -> str:
    return "bat_" + _h(f"{file_sha256}|{period_id}|{source_kind}", 12)


def gl_row_id(batch: str, sheet: str, row_no: int) -> str:
    return _h(f"{batch}|{sheet}|{row_no}")


def finding_id(finding_key: str) -> str:
    return _h(finding_key)


def project_id(name: str, created_iso: str) -> str:
    return "prj_" + _h(f"{name}|{created_iso}", 12)
