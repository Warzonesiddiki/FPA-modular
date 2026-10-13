"""Trial balance gate (doc 03 SS2): per entity, sum(amount_minor) must be exactly 0."""
from __future__ import annotations

def trial_balance(conn, project_id: str, period_id: str) -> dict:
    rows = conn.execute(
        "SELECT entity_id, SUM(amount_minor) s FROM gl_rows WHERE project_id=? AND period_id=? GROUP BY entity_id ORDER BY entity_id",
        (project_id, period_id)).fetchall()
    entities = {r[0]: int(r[1]) for r in rows}
    return {"balanced": all(v == 0 for v in entities.values()), "by_entity": entities,
            "imbalance_minor": sum(entities.values())}
