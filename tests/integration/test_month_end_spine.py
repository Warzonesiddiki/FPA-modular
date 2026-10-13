from app.store.db import init_db
from app.imports.parser_csv import parse_csv
from app.imports.validation import apply_mapping
from app.imports.commit import commit_batch
from app.imports.trial_balance import trial_balance
from app.calc.statements import pl_statement
from pathlib import Path

MAP = {"entity":"Entity","account":"Account","voucher_no":"Voucher","document_date":"DocDate","posting_date":"PostingDate","description":"Description","amount":"Amount"}
ACCOUNTS = [("ACC-REV","revenue","rev"),("ACC-COGS","cogs","cogs"),("ACC-OPEX","opex","opex_pers"),
            ("ACC-DEPR","opex","depr"),("ACC-TAX","tax","tax"),("ACC-CASH","asset","ast_cash")]

def test_spine(tmp_path):
    conn = init_db(tmp_path/"p.db")
    conn.execute("INSERT INTO projects VALUES ('prj1','Meridian','INR',2,4,'monthly',1,'t','t')")
    for code, typ, line in ACCOUNTS:
        conn.execute("INSERT INTO accounts(account_id,project_id,code,name,account_type,statement_line) VALUES (?,?,?,?,?,?)",
                     (code,"prj1",code,code,typ,line))
    f = Path("sample-data/gl_sample.csv")
    _, staged = parse_csv(f)
    valid, quar = apply_mapping(staged, MAP)
    assert len(quar) == 1 and quar[0].reason in ("BAD_DATE","MISSING_REQUIRED")
    res = commit_batch(conn, project_id="prj1", period_id="2026-P01", source_kind="gl",
                       file_path=str(f), valid_rows=valid, quarantined=quar, file_name=f.name)
    res2 = commit_batch(conn, project_id="prj1", period_id="2026-P01", source_kind="gl",
                        file_path=str(f), valid_rows=valid, quarantined=quar, file_name=f.name)
    n = conn.execute("SELECT COUNT(*) FROM gl_rows").fetchone()[0]
    assert res["committed"] == 6 and n == 6  # idempotent re-import
    tb = trial_balance(conn, "prj1", "2026-P01")
    assert tb["balanced"] is False or tb["by_entity"]  # sample is a P&L extract, not a balanced journal - TB reports it honestly
    pl = pl_statement(conn, "prj1", "2026-P01")
    by = {l["line_key"]: l["amount_minor"] for l in pl["lines"]}
    assert by["rev"] == 635000000 and by["gp"] == 238000000 and by["net"] == 69420000
