from app.store.db import init_db, verify_integrity

EXPECTED = {"projects","periods","gl_rows","findings","adjustments","allocation_definitions","assumptions","year_end_runs","budget_lines","audit_log","close_tasks","recon_runs","alerts"}

def test_schema_tables_and_integrity(tmp_path):
    conn = init_db(tmp_path / "p.db")
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert EXPECTED <= tables
    assert verify_integrity(conn)
    # budget grain uniqueness incl. NULL cost centre (doc 02 fix)
    conn.execute("INSERT INTO budget_lines VALUES ('l1','v1','2026-P01','IN01','6100',NULL,100)")
    try:
        conn.execute("INSERT INTO budget_lines VALUES ('l2','v1','2026-P01','IN01','6100',NULL,200)")
        assert False, "duplicate grain must fail"
    except Exception:
        pass
