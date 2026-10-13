# 44 — RULE ALGORITHMS, DETAILED (appendix to doc 07)

> Doc 07 owns *what* each rule flags + the canonical key format. This doc owns the exact algorithm, so an implementation written from this text alone produces identical findings to the answer key (doc 42). Thresholds come from settings keys `rule.EXC-###.<param>` with the defaults in doc 07 §1.

## 0. Common definitions (apply to every rule)
- **Input rows:** committed `gl_rows` of the project for the run's layer (`gl` default; `gl_adj` adds applied `adjustments`, doc 39 §3) for the target period plus the rule's lookback window. Amounts are integer minor units.
- **Spend** of an (entity, account[, vendor]) in a period = Σ `amount_minor` of its rows in that period, **debit-positive** (credits reduce it); for revenue-type accounts the sign is flipped so spend is a positive magnitude. Where a rule says "amount" of a voucher it means |Σ debit legs| of that voucher.
- **Manual journal** = a row whose batch has `import_batches.is_manual = 1` (doc 02; set from the mapping profile's `is_manual_journal` flag or the import wizard checkbox) **or** whose `voucher_no` matches the project setting `rule.manual_prefixes` (default `JV,MJ`). Both conditions are evaluated; evidence names which one matched.
- **Tags** are read from `accounts.tags` (doc 02 §2 closed list): `suspense`, `accrual`, `contra`, `accrual_balancing` (system balancing legs, EXC-023). Untagged projects → the rule runs on the empty set and reports `not_run: no accounts tagged <tag>` (counted, doc 07 §5).
- **Lock evidence (EXC-005):** `periods.locked_at` + `finding` evidence lists rows whose `posting_date` falls in a period whose status is `locked` **and** whose batch `committed_at > periods.locked_at` of that period. Rows committed before the lock are legitimate.
- **Short history:** each rule states its minimum lookback (periods with committed GL for the entity). Below the minimum the rule returns `not_run` with reason `insufficient_history:<have>/<need>`; it never runs on a partial window silently. Minimums: EXC-006 3 · 008 3 · 009 6 · 013 3 · 014 6 · 015 6 · 016 6 · 019 3 · 020 0 · 024 6; rules not listed need only the current period (and the budget version for 017/018/019).
- **Boundary semantics:** `≥` means fires at the threshold exactly; `>` means strictly above (EXC-004 tolerance, EXC-007 age). Tests encode both sides (§ boundary matrix).

## Per-rule algorithm (pseudocode pattern: SCOPE → GROUP → TEST → EMIT)
- **EXC-001** GROUP (entity, voucher_no): collect batches; if same |amount| multiset appears in ≥2 batches OR duplicate rows in-batch without an equal opposite-sign row within the group → EMIT per voucher, grain=`voucher_no`, evidence: batch ids + row ids both sides.
- **EXC-002** JOIN current batch rows to prior committed rows on (entity, voucher_no, account, amount, posting_date): any hit → EMIT grain=`voucher_no|account`.
- **EXC-003** Recompute batch totals from gl_rows; compare stored control totals; Δ≠0 → EMIT grain=`batch_id` (also blocks at commit per doc 06; this catches post-hoc tampering).
- **EXC-004** GROUP (entity, voucher_no): Σamount; |Σ| > tol → EMIT with all row ids.
- **EXC-005** Rows in a `locked` period whose batch was committed after `periods.locked_at` (§0 lock evidence): EMIT per voucher, grain=`voucher_no`, evidence: locked_at, committed_at, batch id.
- **EXC-006** GROUP (entity, account, vendor) period spend share; prior-3 avg share; TEST share ≥40% AND spend ≥ spike_abs AND prior avg <25% → EMIT grain=`vendor`.
- **EXC-007** Accounts tagged suspense: net balance at period end; oldest unmatched voucher age via FIFO offsetting (debits vs credits chronological); TEST age >30d OR |balance| ≥ material_abs → EMIT grain=`account`, evidence: oldest voucher + ageing buckets 0-30/31-60/61-90/90+.
- **EXC-008** Manual vouchers (§0) to P&L accounts with amount ≥ one_off_abs (₹1,000,000): lookback 3 periods for a voucher on the same account with amount within ±5%; none → EMIT grain=`voucher_no`.
- **EXC-009** Requires poster/time columns (else not_run): poster ∉ usual set (posters covering ≥80% of account's vouchers in 6 periods) OR hour 0–5 OR Sat/Sun → EMIT Low grain=`voucher_no`.
- **EXC-010** |doc_date − posting_date| spans period boundary AND |amount| ≥ material_abs → EMIT grain=`voucher_no`.
- **EXC-011** Accrual-tagged vouchers (or description match list): search next period for offsetting row (same account, opposite sign, |amount| within 1%): none → EMIT grain=`voucher_no` (original).
- **EXC-012** Expense accounts (type opex/cogs, not contra-tagged): sum credit-side (negative) rows excluding pairs that exactly reverse a debit in same/prior period (same |amount|, same account, ≤45d): net ≥ material_abs → EMIT grain=`account`.
- **EXC-013** Account period spend vs average of prior 3 periods' spend: Δ = spend − avg; AND-test Δ ≥ spike_abs AND Δ/avg ≥ spike_pct → EMIT grain=`account`, evidence: the three prior values. Zero prior avg: fires only if spend ≥ 2× spike_abs (pct leg n/a, recorded). Severity High when Δ ≥ 3× spike_abs AND Δ/avg ≥ 3× spike_pct.
- **EXC-014** Vendor's account set over prior 6 periods; new account this period with amount ≥ material_abs → EMIT grain=`vendor|account`.
- **EXC-015** Vendor+account active ≥5 of prior 6 periods (median amount m): absent this period → EMIT Medium grain=`vendor|account`, evidence m. (If project history <6 periods → not_run with reason until enough history.)
- **EXC-016** Accrual-tagged accounts monthly in ≥5/6 prior periods: this period missing or <50% of median → EMIT grain=`account`.
- **EXC-017** BvA grain actual ≥ material_abs AND budget line absent/0 → EMIT grain=`account`.
- **EXC-018** Doc 03 §5 AND-test exactly; severity escalates at ≥3× both legs → EMIT grain=`account`.
- **EXC-019** YTD var ≥ material_abs AND monthly overrun strictly increased 3 consecutive periods → EMIT grain=`account`.
- **EXC-020** Vouchers with amount mod round_amount == 0: count ≥5 AND Σ ≥ spike_abs AND share of account voucher count ≥30% → EMIT Low grain=`account`.
- **EXC-021** GROUP (entity, vendor) sliding 7-day windows: ≥3 vouchers each < approval_limit, Σ ≥ 1.5×limit → EMIT High grain=`vendor`, evidence window + vouchers. Windows evaluated on posting_date sorted; overlapping windows merged into one finding (max Σ window).
- **EXC-022** Same account, debit row and credit row |amount| equal, dates ≤5d apart, different vouchers, and pair nets the account's period movement by ≥90% → EMIT grain=`account|amount_minor`.
- **EXC-023** Voucher line-count == 1 AND |amount| ≥ material_abs AND the row's account is not tagged `accrual_balancing` (§0) → EMIT Low grain=`voucher_no`.
- **EXC-024** Account's last activity ≥6 periods ago (or created_at in period) AND period |total| ≥ material_abs → EMIT Low grain=`account`.

## Boundary test matrix (mandatory per rule in tests)
Threshold −1 minor unit (silent), threshold exact (fires unless spec says >), threshold +1; pct boundary ±0.01%; zero-budget/zero-prior variants; lookback-insufficient → not_run. The acceptance plants (doc 42 §7) sit ≥10% inside thresholds so boundary noise cannot flip recall; the controls (doc 42 §8) each target one specific wrong implementation and must stay silent.
