# 44 — RULE ALGORITHMS, DETAILED (appendix to doc 07)

> Doc 07 owns *what* each rule flags + the canonical key format. This doc owns the exact algorithm an implementer follows, so two agents implementing the same rule produce identical findings. Common pre-steps for all rules: input rows are committed gl_rows (layer=GL unless run says otherwise) for (project, period) + lookback windows stated per rule; amounts are integer minor units; "manual journal" = batch source_kind `gl` with `is_manual` flag from import profile (default: vouchers whose source file kind is `journal` template or description-prefix setting `JV`); tolerance `tol` default 0 minor units unless stated.

## Per-rule algorithm (pseudocode pattern: SCOPE → GROUP → TEST → EMIT)
- **EXC-001** GROUP (entity, voucher_no): collect batches; if same |amount| multiset appears in ≥2 batches OR duplicate rows in-batch without an equal opposite-sign row within the group → EMIT per voucher, grain=`voucher_no`, evidence: batch ids + row ids both sides.
- **EXC-002** JOIN current batch rows to prior committed rows on (entity, voucher_no, account, amount, posting_date): any hit → EMIT grain=`voucher_no|account`.
- **EXC-003** Recompute batch totals from gl_rows; compare stored control totals; Δ≠0 → EMIT grain=`batch_id` (also blocks at commit per doc 06; this catches post-hoc tampering).
- **EXC-004** GROUP (entity, voucher_no): Σamount; |Σ| > tol → EMIT with all row ids.
- **EXC-005** Rows whose posting_date ∈ period locked_at snapshot (period lock log): EMIT per voucher.
- **EXC-006** GROUP (entity, account, vendor) period spend share; prior-3 avg share; TEST share ≥40% AND spend ≥ spike_abs AND prior avg <25% → EMIT grain=`vendor`.
- **EXC-007** Accounts tagged suspense: net balance at period end; oldest unmatched voucher age via FIFO offsetting (debits vs credits chronological); TEST age >30d OR |balance| ≥ material_abs → EMIT grain=`account`, evidence: oldest voucher + ageing buckets 0-30/31-60/61-90/90+.
- **EXC-008** Manual vouchers to P&L accounts ≥ one_off_abs (₹1,000,000): lookback 3 periods for same (account, amount ±5%) recurrence; none → EMIT grain=`voucher_no`.
- **EXC-009** Requires poster/time columns (else not_run): poster ∉ usual set (posters covering ≥80% of account's vouchers in 6 periods) OR hour 0–5 OR Sat/Sun → EMIT Low grain=`voucher_no`.
- **EXC-010** |doc_date − posting_date| spans period boundary AND |amount| ≥ material_abs → EMIT grain=`voucher_no`.
- **EXC-011** Accrual-tagged vouchers (or description match list): search next period for offsetting row (same account, opposite sign, |amount| within 1%): none → EMIT grain=`voucher_no` (original).
- **EXC-012** Expense accounts (type opex/cogs, not contra-tagged): sum credit-side (negative) rows excluding pairs that exactly reverse a debit in same/prior period (same |amount|, same account, ≤45d): net ≥ material_abs → EMIT grain=`account`.
- **EXC-013** Account period total vs avg prior 3: AND-test spike_abs + spike_pct → EMIT grain=`account`. Zero prior avg: fires only if ≥ 2× spike_abs (pct leg n/a, recorded).
- **EXC-014** Vendor's account set over prior 6 periods; new account this period with amount ≥ material_abs → EMIT grain=`vendor|account`.
- **EXC-015** Vendor+account active ≥5 of prior 6 periods (median amount m): absent this period → EMIT Medium grain=`vendor|account`, evidence m. (If project history <6 periods → not_run with reason until enough history.)
- **EXC-016** Accrual-tagged accounts monthly in ≥5/6 prior periods: this period missing or <50% of median → EMIT grain=`account`.
- **EXC-017** BvA grain actual ≥ material_abs AND budget line absent/0 → EMIT grain=`account`.
- **EXC-018** Doc 03 §5 AND-test exactly; severity escalates at ≥3× both legs → EMIT grain=`account`.
- **EXC-019** YTD var ≥ material_abs AND monthly overrun strictly increased 3 consecutive periods → EMIT grain=`account`.
- **EXC-020** Vouchers with amount mod round_amount == 0: count ≥5 AND Σ ≥ spike_abs AND share of account voucher count ≥30% → EMIT Low grain=`account`.
- **EXC-021** GROUP (entity, vendor) sliding 7-day windows: ≥3 vouchers each < approval_limit, Σ ≥ 1.5×limit → EMIT High grain=`vendor`, evidence window + vouchers. Windows evaluated on posting_date sorted; overlapping windows merged into one finding (max Σ window).
- **EXC-022** Same account, debit row and credit row |amount| equal, dates ≤5d apart, different vouchers, and pair nets the account's period movement by ≥90% → EMIT grain=`account|amount_minor`.
- **EXC-023** Voucher line-count == 1 AND |amount| ≥ material_abs AND row not tagged system balancing leg (import tag) → EMIT Low grain=`voucher_no`.
- **EXC-024** Account's last activity ≥6 periods ago (or created_at in period) AND period |total| ≥ material_abs → EMIT Low grain=`account`.

## Boundary test matrix (mandatory per rule in tests)
Threshold −1 minor unit (silent), threshold exact (fires unless spec says >), threshold +1; pct boundary ±0.01%; zero-budget/zero-prior variants; lookback-insufficient → not_run. The acceptance plants (doc 42 §4) sit ≥10% inside thresholds so boundary noise cannot flip recall.
