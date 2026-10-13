# 07 — EXCEPTION RULES CATALOG (EXC-001…EXC-024)

> Owner of: what each rule flags, at what grain, with what key. Rule code (`app/rules/exc_###.py`) implements this and nothing else. Wording: findings are **potential exceptions** for human review (P8) — never "errors" or "fraud" in any UI/export text.

## 1. Common contract (all rules)
- Pure function `(gl_rows, budget_lines?, params, context) -> Finding[]`. Deterministic; Decimal/integer only; no I/O, no clock (run date injected).
- Params from settings `rule.EXC-###.*` with the defaults below; every param change is versioned + audited, and the run records the param snapshot in evidence.
- Severity: `high|medium|low` per rule default; **amount escalation (all rules): a finding whose amount ≥ 3× the rule's absolute threshold is High** (this is what makes doc 42's P14/P20/P21 high-severity).
- Finding evidence_json always contains: triggering row ids, computed values, thresholds used, and the grain key parts — enough for a stranger to re-derive the finding by hand (audit standard).
- A rule that cannot run (missing budget, missing PY) returns `not_run: reason`, shown on S08 — silent skips are defects.

## 2. Canonical finding key (the attempt-#4 fix — this format is law)
`finding_key = EXC-###|<entity_id>|<account_id or ->|<period_id>|<grain_key>` where grain_key is defined per rule below. `finding_id = SHA256(finding_key)[:32]`. Catalog, answer key, engine, and acceptance harness all use exactly this. Changing it requires: this doc + CHANGELOG + answer-key regeneration in one commit (MASTER_PLAN §5).

## 3. The rules
Defaults: material_abs ₹100,000 (`10000000` minor), material_pct 5%, spike_pct 50%, spike_abs ₹250,000, round_amount ₹10,000 multiples, approval_limit ₹500,000. All configurable per project.

| ID | Rule (grain_key) | Logic | Sev |
|---|---|---|---|
| EXC-001 | Duplicate voucher (`voucher_no`) | Same entity+voucher_no+|amount| posted in ≥2 distinct batches, or twice in one batch with distinct rows and no reversal pair | High |
| EXC-002 | Re-import overlap (`voucher_no|account`) | Voucher/account/amount/date tuple present in an earlier committed batch and again in current | Medium |
| EXC-003 | Control-total mismatch (`batch_id`) | Declared vs actual totals differ at commit (also raised retrospectively if a committed batch's stored totals ≠ recomputed) | High |
| EXC-004 | Unbalanced voucher (`voucher_no`) | Σ amounts per entity+voucher ≠ 0 exactly (tolerance setting `rule.EXC-004.tol_minor`, default 0 minor units) | High |
| EXC-005 | Posting to locked period (`voucher_no`) | posting_date in a period whose status was `locked` at commit time (post-lock imports require unlock audit) | High |
| EXC-006 | Vendor concentration spike (`vendor`) | One vendor ≥ 40% of entity×account period spend AND spend ≥ spike_abs, where prior-3-period average share < 25% | Medium |
| EXC-007 | Suspense/clearing ageing (`account`) | Accounts flagged `suspense` (master-data tag; default code pattern `1999*`) with net balance older than 30 days (oldest open voucher) or balance ≥ material_abs at period end | High |
| EXC-008 | Large one-off journal (`voucher_no`) | Single manual-source voucher ≥ ₹1,000,000 (setting) to a P&L account, not part of a recurring pattern (no similar amount/account in prior 3 periods) | Medium |
| EXC-009 | Unusual poster/time (`voucher_no`) | Only if source carries user/time columns: poster not in account's usual-poster set (prior 6 periods) or posting 00:00–05:00/weekend. Missing columns → not_run | Low |
| EXC-010 | Cut-off risk (`voucher_no`) | |document_date − posting_date| crosses period boundary and |amount| ≥ material_abs | Medium |
| EXC-011 | Stale accrual not reversed (`voucher_no`) | Accrual-pattern voucher (account tag `accrual` or description match setting list) with no reversing/offsetting entry within next period | Medium |
| EXC-012 | Negative expense / credit anomaly (`account`) | Credit (negative) postings into expense accounts (excluding accounts tagged `contra`-allowed) totalling ≥ material_abs in period, excluding exact reversal pairs | Medium |
| EXC-013 | Account spike (`account`) | Period total vs trailing-3-period average: |Δ| ≥ spike_abs AND ≥ spike_pct (AND-test) | Medium |
| EXC-014 | Vendor→new account (`vendor|account`) | Vendor posts to an account it has never used in prior 6 periods, amount ≥ material_abs | Low |
| EXC-015 | Missing recurring charge (`vendor|account`) | Vendor+account active in ≥5 of prior 6 periods (median amount ±30%) absent this period | Medium |
| EXC-016 | Accrual pattern break (`account`) | Monthly accrual in ≥5 of prior 6 periods absent or < 50% of median this period | Medium |
| EXC-017 | Material unbudgeted spend (`account`) | Actual ≥ material_abs where budget = 0/absent for the grain | Medium |
| EXC-018 | Material BvA variance (`account`) | AND-test: |Var| ≥ material_abs AND |Var%| ≥ material_pct (doc 03 §5) | Medium→High if ≥ 3× thresholds |
| EXC-019 | Cumulative overrun trend (`account`) | YTD actual > YTD budget by ≥ material_abs and overrun grew in each of last 3 periods | Medium |
| EXC-020 | Round-amount clustering (`account`) | ≥ 5 vouchers in period with amounts exact multiples of round_amount totalling ≥ spike_abs, share of account vouchers ≥ 30% | Low |
| EXC-021 | Threshold splitting (`vendor`) | ≥ 3 vouchers, same vendor+entity within 7 days, each < approval_limit, Σ ≥ approval_limit × 1.5 | High |
| EXC-022 | Round-tripping (`account|amount`) | Debit and credit of same |amount| (±0) on same account within 5 days, distinct vouchers, net ≈ 0 | Medium |
| EXC-023 | Single-line voucher risk (`voucher_no`) | Voucher with exactly 1 line and |amount| ≥ material_abs (excludes system balancing legs tagged at import) | Low |
| EXC-024 | Dormant/new account activity (`account`) | Account inactive ≥ 6 periods (or created this period) with period total ≥ material_abs | Low |

## 4. Worked sample + control case (every rule; two shown, pattern mandatory for all 24 in fixtures)
- **EXC-018 sample:** Budget ₹1,000,000, Actual ₹1,200,000 → Var 200,000 (20%) → fires, key `EXC-018|IN01|5100|2026-P01|5100`. **Control:** Actual ₹900,000 vs Budget ₹880,000 → +2.27% → pct leg fails AND → does **not** fire (this exact control failed in attempt #4; it is acceptance plant P30).
- **EXC-004 sample:** Voucher V1 lines +100,000.00, −99,999.99 → imbalance ₹0.01 beyond 0 tolerance → fires with both row ids in evidence. **Control:** +100,000.00/−100,000.00 → silent.

## 5. Lifecycle & ownership (implemented in rules/workflow.py)
new → acknowledged → explained → corrected (requires linked re-import batch or journal reference in note) → verified (by analyst, after re-run no longer fires or evidence accepted) → closed. `waived` from any state: reason + expiry ≤ 90 days mandatory; expired waivers resurface. Owner resolution: account_owners → vendor owner fallback → "Unassigned" queue on S01/S08 (never ownerless-invisible). Due dates: high 3 days, medium 7, low next period-end (settings). Every transition → finding_history + audit_log.

## 6. Acceptance linkage
Planted corpus (sample-data): 32 plants + 8 controls mapped to rules above; bars in doc 14 §3. Each rule's packet test includes its §4-style sample (fires once, exact key) and control (silent) before any integration run is trusted.
