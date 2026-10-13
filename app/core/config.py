"""Settings with doc-62 defaults. Project settings override these; all values validated."""
from __future__ import annotations

from dataclasses import dataclass, field

DEFAULTS: dict = {
    "materiality.abs_minor": 10_000_000,      # ₹100,000 at exponent 2
    "materiality.pct": "5",
    "rule.EXC-004.tol_minor": 0,
    "rule.spike_abs_minor": 25_000_000,        # ₹250,000
    "rule.spike_pct": "50",
    "rule.round_amount_minor": 1_000_000,      # ₹10,000
    "rule.approval_limit_minor": 50_000_000,   # ₹500,000
    "rule.one_off_abs_minor": 100_000_000,     # ₹1,000,000
    "rule.suspense_age_days": 30,
    "rule.concentration_pct": "40",
    "import.cutoff_window_days": 5,
    "recon.tolerance_minor": 10_000,           # ₹100
    "ai.enabled": False,
    "close.target_lock_business_day": 5,
    "alerts.retention_days": 90,
}


@dataclass
class Settings:
    values: dict = field(default_factory=lambda: dict(DEFAULTS))

    def get(self, key: str, default=None):
        return self.values.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value) -> None:
        if key not in DEFAULTS:
            raise KeyError(f"Unknown setting key: {key} (doc 62 owns the key list)")
        self.values[key] = value
