"""Audit hash-chain primitives (doc 12 §3). Storage lives in app/store (audit_log table)."""
from __future__ import annotations

import json

from .hashing import chain_hash

GENESIS = "GENESIS"


def canonical_event(project_id: str, at: str, actor: str, entity_type: str,
                    entity_id: str, action: str, before: dict | None, after: dict | None) -> str:
    payload = {"project_id": project_id, "at": at, "actor": actor, "entity_type": entity_type,
               "entity_id": entity_id, "action": action, "before": before, "after": after}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def next_hash(prev_hash: str, canonical: str) -> str:
    return chain_hash(prev_hash or GENESIS, canonical)


def verify_chain(rows: list[dict]) -> tuple[bool, int | None]:
    """rows: [{prev_hash, hash, canonical...}] in audit_id order. Returns (ok, first_bad_index)."""
    prev = GENESIS
    for i, row in enumerate(rows):
        if row["prev_hash"] != prev:
            return False, i
        if row["hash"] != next_hash(prev, row["canonical"]):
            return False, i
        prev = row["hash"]
    return True, None
