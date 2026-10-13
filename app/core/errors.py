"""Typed error catalogue (doc 22). Every error: code + plain message + hint + retryable."""
from __future__ import annotations


class AppError(Exception):
    def __init__(self, code: str, message: str, hint: str, retryable: bool = False, details: dict | None = None):
        super().__init__(message)
        self.code, self.message, self.hint, self.retryable = code, message, hint, retryable
        self.details = details or {}

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "hint": self.hint,
                "retryable": self.retryable, "details": self.details}


# Canonical constructors (doc 22 codes)
def not_found(what: str = "that") -> AppError:
    return AppError("FP&A-ERR-001", f"We couldn't find {what}.", "Go back and pick it from the list.")


def duplicate_name(kind: str) -> AppError:
    return AppError("FP&A-ERR-010", f"A {kind} with this name already exists.", "Choose a different name.")


def unsupported_file() -> AppError:
    return AppError("FP&A-ERR-020", "This file type isn't supported.", "Use CSV or Excel (.xlsx) exported from your ERP.")


def file_too_large(limit_mb: int = 200) -> AppError:
    return AppError("FP&A-ERR-021", f"This file is larger than the {limit_mb} MB limit.",
                    "Split it by period or company and import in parts.")


def mapping_conflict(detail: str) -> AppError:
    return AppError("FP&A-ERR-022", detail, "Fix the highlighted mapping.")


def control_total_mismatch(details: dict) -> AppError:
    return AppError("FP&A-ERR-023", "The file's totals don't match the totals you declared.",
                    "Check you picked the right file and period, then correct the totals.", details=details)


def trial_balance_imbalance(details: dict) -> AppError:
    return AppError("FP&A-ERR-024", "Debits and credits don't balance yet.",
                    "Open Trial Balance to see the vouchers causing it.", details=details)


def illegal_transition() -> AppError:
    return AppError("FP&A-ERR-040", "That action isn't available for an item in this state.",
                    "Refresh — its state may have changed.", retryable=True)


def waive_needs_reason() -> AppError:
    return AppError("FP&A-ERR-041", "A waiver needs a reason and an expiry date.", "Add both (maximum 90 days).")


def adjustment_unbalanced(delta_minor: int) -> AppError:
    return AppError("FP&A-ERR-042", "These adjustment lines don't net to zero.",
                    "Balance the group, or change the kind to provision with a contra account.",
                    details={"delta_minor": delta_minor})


def duplicate_code(kind: str) -> AppError:
    return AppError("FP&A-ERR-050", f"That {kind} code is already used.", "Use a unique code.")


def export_blocked(checks: list) -> AppError:
    return AppError("FP&A-ERR-060", "Some numbers don't tie yet, so the deck is blocked.",
                    "Open the Checks list, fix the source, and generate again.", details={"checks": checks})


def ai_disabled() -> AppError:
    return AppError("FP&A-ERR-070", "AI drafting is off.",
                    "Add a provider key in Settings — everything else works without it.")


def ai_guardrail_rejected(tokens: list) -> AppError:
    return AppError("FP&A-ERR-071", "The draft mentioned a number that isn't in your data, so it wasn't used.",
                    "Try again, or write the commentary manually.", retryable=True, details={"tokens": tokens})
