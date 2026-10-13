"""Atomic commit (doc 06 SS7): one transaction, idempotent by batch_id, batched inserts (no row-by-row)."""
from __future__ import annotations
import json
from app.core.ids import batch_id as make_batch_id, gl_row_id
from app.core.hashing import sha256_file
from app.store.db import transaction

def commit_batch(conn, *, project_id: str, period_id: str, source_kind: str, file_path: str,
                 valid_rows, quarantined, file_name: str = "") -> dict:
    fh = sha256_file(file_path)
    bid = make_batch_id(fh, period_id, source_kind)
    with transaction(conn):
        prev = conn.execute("SELECT batch_id FROM import_batches WHERE project_id=? AND period_id=? AND source_kind=? AND file_sha256=? AND status='committed'",
                            (project_id, period_id, source_kind, fh)).fetchone()
        if prev:  # idempotent re-import: same deterministic batch_id -> replace its rows atomically
            conn.execute("DELETE FROM gl_rows WHERE batch_id=?", (bid,))
            conn.execute("DELETE FROM import_rows_raw WHERE batch_id=?", (bid,))
        conn.execute(
            "INSERT OR REPLACE INTO import_batches(batch_id,project_id,period_id,source_kind,file_name,file_sha256,status,row_count_in,row_count_valid,row_count_quarantined,committed_at)"
            " VALUES (?,?,?,?,?,?, 'committed',?,?,?, datetime('now'))",
            (bid, project_id, period_id, source_kind, file_name, fh,
             len(valid_rows) + len(quarantined), len(valid_rows), len(quarantined)))
        conn.executemany(
            "INSERT INTO import_rows_raw(raw_id,batch_id,sheet_name,row_no,raw_json,parse_status,quarantine_reason) VALUES (?,?,?,?,?,?,?)",
            [(f"{bid}-{q.row_no}", bid, q.sheet, q.row_no, json.dumps(q.raw), "quarantined", q.reason) for q in quarantined])
        conn.executemany(
            "INSERT INTO gl_rows(gl_row_id,project_id,period_id,batch_id,entity_id,account_id,cost_centre_id,vendor_id,voucher_no,document_date,posting_date,description,amount_minor,source_file,source_row)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [(gl_row_id(bid, r.sheet, r.row_no), project_id, period_id, bid, r.values.get("entity"), r.values.get("account"),
              r.values.get("cost_centre") or None, r.values.get("vendor") or None, r.values.get("voucher_no"),
              r.values.get("document_date"), r.values.get("posting_date"), r.values.get("description", ""),
              int(r.values["amount_minor"]), file_name, r.row_no) for r in valid_rows])
    return {"batch_id": bid, "committed": len(valid_rows), "quarantined": len(quarantined)}
