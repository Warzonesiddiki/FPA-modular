"""P&L from gl_rows via accounts.statement_line + doc 45 registry presentation signs."""
from __future__ import annotations
from app.core import money

CALC_LINES = {"gp", "ebitda", "ebit", "pbt", "net"}
PL_ORDER = ["rev","cogs","gp","opex_pers","opex_rent","opex_it","opex_mkt","opex_prof","opex_other","ebitda","depr","ebit","int","pbt","tax","net"]
LABELS = {"rev":"Revenue","cogs":"Cost of Goods/Services","gp":"Gross Profit","opex_pers":"Personnel","opex_rent":"Rent & Facilities","opex_it":"IT & SaaS","opex_mkt":"Marketing","opex_prof":"Professional Services","opex_other":"Other Operating Expenses","ebitda":"EBITDA","depr":"Depreciation & Amortisation","ebit":"EBIT","int":"Interest (net)","pbt":"Profit Before Tax","tax":"Tax","net":"Net Income"}

def pl_statement(conn, project_id: str, period_id: str, entity_id: str | None = None) -> dict:
    q = ("SELECT a.statement_line line, SUM(g.amount_minor) amt FROM gl_rows g "
         "JOIN accounts a ON a.account_id = g.account_id WHERE g.project_id=? AND g.period_id=?")
    params: list = [project_id, period_id]
    if entity_id:
        q += " AND g.entity_id=?"; params.append(entity_id)
    q += " GROUP BY a.statement_line"
    raw = {r[0]: int(r[1]) for r in conn.execute(q, params)}
    # storage: revenue credit-negative -> present revenue positive; costs debit-positive shown as expense amounts
    def amt(line): return int(raw.get(line, 0))
    lines: dict[str, int] = {}
    lines["rev"] = -amt("rev"); lines["cogs"] = amt("cogs")
    lines["gp"] = lines["rev"] - lines["cogs"]
    opex = ["opex_pers","opex_rent","opex_it","opex_mkt","opex_prof","opex_other"]
    for o in opex: lines[o] = amt(o)
    lines["ebitda"] = lines["gp"] - sum(lines[o] for o in opex)
    lines["depr"] = amt("depr"); lines["ebit"] = lines["ebitda"] - lines["depr"]
    lines["int"] = amt("int"); lines["pbt"] = lines["ebit"] - lines["int"]
    lines["tax"] = amt("tax"); lines["net"] = lines["pbt"] - lines["tax"]
    out = [{"line_key": k, "label": LABELS[k], "amount_minor": lines[k],
            "amount": str(money.to_major(lines[k]))} for k in PL_ORDER]
    unmapped = amt("unmapped") if "unmapped" in raw else int(raw.get(None, 0) or 0)
    return {"statement": "pl", "period_id": period_id, "lines": out, "unmapped_minor": unmapped}
