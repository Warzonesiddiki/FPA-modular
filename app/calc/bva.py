"""Budget-vs-Actual at entity x account grain (doc 03 SS5) with AND-materiality (doc 62 keys)."""
from __future__ import annotations
from app.core import money
from app.core.config import DEFAULTS

def bva(conn, project_id: str, period_id: str, budget_version: str,
        abs_minor: int | None = None, pct: str | None = None) -> list[dict]:
    abs_minor = int(DEFAULTS["materiality.abs_minor"] if abs_minor is None else abs_minor)
    pct_threshold = float(DEFAULTS["materiality.pct"] if pct is None else pct)
    actual = {(r[0], r[1]): int(r[2]) for r in conn.execute(
        "SELECT entity_id, account_id, SUM(amount_minor) FROM gl_rows WHERE project_id=? AND period_id=? GROUP BY 1,2",
        (project_id, period_id))}
    budget = {(r[0], r[1]): int(r[2]) for r in conn.execute(
        "SELECT entity_id, account_id, SUM(amount_minor) FROM budget_lines WHERE version_id=? AND period_id=? GROUP BY 1,2",
        (budget_version, period_id))}
    rows = []
    for key in sorted(set(actual) | set(budget)):
        a, b = actual.get(key, 0), budget.get(key, 0)
        var, p = money.variance(a, b)
        material = abs(var) >= abs_minor and p is not None and abs(float(p)) >= pct_threshold
        rows.append({"entity_id": key[0], "account_id": key[1], "actual_minor": a, "budget_minor": b,
                     "var_minor": var, "var_pct": (str(p) if p is not None else None),
                     "favourable": var <= 0, "material": material})  # expense-grain default; statement layer refines by account_type
    return rows

def refine_favourability(conn, rows: list[dict]) -> list[dict]:
    """Revenue-favourable = positive variance; cost-favourable = negative. Uses accounts.account_type."""
    types = {r[0]: r[1] for r in conn.execute("SELECT account_id, account_type FROM accounts")}
    for row in rows:
        row["favourable"] = row["var_minor"] >= 0 if types.get(row["account_id"]) == "revenue" else row["var_minor"] <= 0
    return rows
