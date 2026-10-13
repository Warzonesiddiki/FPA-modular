# 07 — EXCEPTION RULES CATALOG (EXC-001…EXC-028)

> Owner of: what each rule flags, at what grain, with what key, **and what fix it proposes** (§7). Rule code (`app/rules/exc_###.py`) implements this and nothing else; `app/rules/suggestions.py` implements §7. Wording: findings are **potential exceptions** for human review (P8) — never "errors" or "fraud" in any UI/export text; a proposed fix is a **suggested fix**, never an instruction.
>
> Why this catalogue exists (DEC-011): the analyst's job includes *finding the wrong or abnormal entries that were posted and proposing how to put them right*. Rules 001–024 cover control, cut-off, budget and pattern anomalies; rules 025–028 are the **entry-hygiene** rules that catch the everyday mispostings a human spots by reading the ledger (wrong account for the narration, a decimal slip, a stray cost centre, a double-billed invoice). Every finding of every rule carries a rectification suggestion (§7) so the inbox is a work list, not a watch list.

## 1. Common contract (all rules)
- Pure function `(gl_rows, budget_lines?, params, context) -> Finding[]`. Deterministic; Decimal/integer only; no I/O, no clock (run date injected).
- Params from settings `rule.EXC-###.*` with the defaults below; every param change is versioned + audited, and the run records the param snapshot in evidence.
- Severity: `high|medium|low` per rule default; **amount escalation (all rules): a finding whose amount ≥ 3× the rule's *escalation base* is High; for AND-test rules (EXC-013, EXC-018) escalation requires ≥ 3× on *both* legs** (this is what makes doc 42's P12/P14/P17/P20/P21 High and keeps P30 Medium). The escalation base is the rule's absolute threshold **except** for the entry-hygiene rules EXC-025…028, whose own `min_abs` (₹25,000) is deliberately low; their escalation base is `material_abs` (₹100,000 → High at ≥ ₹300,000). EXC-026 additionally escalates on the magnitude of the shift (§3).
- Finding evidence_json always contains: triggering row ids, computed values, thresholds used, and the grain key parts — enough for a stranger to re-derive the finding by hand (audit standard).
- A rule that cannot run (missing budget, missing PY, no vendor column mapped) returns `not_run: reason`, shown on S08 — silent skips are defects.
- Every emitted finding carries a `suggestion` (§7) built by `rules/suggestions.py` from the finding's evidence. The suggestion is advisory: nothing is posted anywhere by the app; the analyst applies it as a management adjustment (doc 39) or exports it as a rectification journal for the ERP (doc 26 §7).

## 2. Canonical finding key (the attempt-#4 fix — this format is law)
`finding_key = EXC-###|<entity_id>|<account_id or ->|<period_id>|<grain_key>` where grain_key is defined per rule below. `finding_id = SHA256(finding_key)[:32]`. Catalog, answer key, engine, and acceptance harness all use exactly this. Changing it requires: this doc + CHANGELOG + answer-key regeneration in one commit (MASTER_PLAN §5).

## 3. The rules
Defaults: material_abs ₹100,000 (`10000000` minor), material_pct 5%, spike_pct 50%, spike_abs ₹250,000, round_amount ₹10,000 multiples, approval_limit ₹500,000, one_off_abs ₹1,000,000, suspense_age 30 d, concentration 40%; entry-hygiene rules (025–028): `min_abs` ₹25,000 each, EXC-025 `dominance_pct` 90% / `min_signal_tokens` 2 / `min_token_count` 12, EXC-026 `outlier_factor` 5 / `shift_tolerance_pct` 2 / `min_history_count` 6, EXC-027 `dominant_share_pct` 90 / `min_history_rows` 10, EXC-028 `window_days` 30. All configurable per project (keys in doc 62; algorithms in doc 44).

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
| EXC-012 | Contra-normal postings (`account`) | Postings against an account's normal side — credits (negative) into expense accounts, debits (positive) into revenue accounts — excluding accounts tagged `contra`, totalling ≥ material_abs in the period after removing exact reversal pairs | Medium |
| EXC-013 | Account spike (`account`) | Period total vs trailing-3-period average: |Δ| ≥ spike_abs AND ≥ spike_pct (AND-test) | Medium |
| EXC-014 | Vendor→new account (`vendor|account`) | Vendor posts to an account it has never used in prior 6 periods, amount ≥ material_abs | Low |
| EXC-015 | Missing recurring charge (`vendor|account`) | Vendor+account active in ≥5 of prior 6 periods (median amount ±30%) absent this period | Medium |
| EXC-016 | Accrual pattern break (`account`) | Monthly accrual in ≥5 of prior 6 periods absent or < 50% of median this period | Medium |
| EXC-017 | Material unbudgeted spend (`account`) | Actual ≥ material_abs where budget = 0/absent for the grain | Medium |
| EXC-018 | Material BvA variance (`account`) | AND-test: |Var| ≥ material_abs AND |Var%| ≥ material_pct (doc 03 §5) | Medium→High if ≥ 3× both thresholds |
| EXC-019 | Cumulative overrun trend (`account`) | YTD actual > YTD budget by ≥ material_abs and overrun grew in each of last 3 periods | Medium |
| EXC-020 | Round-amount clustering (`account`) | ≥ 5 vouchers in period with amounts exact multiples of round_amount totalling ≥ spike_abs, share of account vouchers ≥ 30% | Low |
| EXC-021 | Threshold splitting (`vendor`) | ≥ 3 vouchers, same vendor+entity within 7 days, each < approval_limit, Σ ≥ approval_limit × 1.5 | High |
| EXC-022 | Round-tripping (`account|amount`) | Debit and credit of same |amount| (±0) on same account within 5 days, distinct vouchers, net ≈ 0 | Medium |
| EXC-023 | Single-line voucher risk (`voucher_no`) | Voucher with exactly 1 line and |amount| ≥ material_abs (excludes system balancing legs tagged at import) | Low |
| EXC-024 | Dormant/new account activity (`account`) | Account inactive ≥ 6 periods (or created this period) with period total ≥ material_abs | Low |
| EXC-025 | Account–narration mismatch (`voucher_no`) | A P&L line of |amount| ≥ min_abs whose description tokens are, in the entity's prior-12-period history, ≥ dominance_pct associated with **one other** account and ≤ 2% with the posted account; needs ≥ min_signal_tokens such tokens agreeing on the same account (doc 44) | Medium |
| EXC-026 | Amount outlier / decimal-shift suspect (`voucher_no`) | A vendor line whose |amount| is ≥ outlier_factor × (or ≤ 1/outlier_factor of) the median of the vendor's prior lines on the same account (≥ min_history_count lines, prior 12 periods) and differs from it by ≥ min_abs; ratio within ±shift_tolerance_pct of 10/100/1000 marks `decimal_shift_suspect` | Medium; **High** when ratio ≥ 100 or |amount| ≥ 3× material_abs |
| EXC-027 | Unusual cost centre for the account/vendor (`voucher_no`) | A line of |amount| ≥ min_abs whose cost centre never appears in the prior-6-period history of its (entity, account, vendor-if-present) group, when that history has ≥ min_history_rows rows and ≥ dominant_share_pct of them sit in ≤ 2 cost centres | Low |
| EXC-028 | Near-duplicate vendor charge (`voucher_no`) | Same entity + vendor + account + |amount| (≥ min_abs) + sign on a **different** voucher within window_days of an earlier anchor line; fires on the later line; a flagged line never becomes an anchor (so a double-billed month does not taint the next legitimate bill); exact same-voucher duplicates belong to EXC-001 | Medium |

Grain note for the row-level rules 025–028: the grain is the voucher number; when a second row of the **same** voucher also fires the same rule, that finding's grain is `voucher_no|row_no` (source row number) so keys stay unique and deterministic (doc 44).

## 4. Worked sample + control case (every rule; four shown, pattern mandatory for all 28 in fixtures)
- **EXC-018 sample:** Budget ₹1,000,000, Actual ₹1,200,000 → Var +200,000 (+20%) → both legs pass → fires, key `EXC-018|IN01|5100|2025-P01|5100`. **Controls (both required, because a control where both legs fail cannot tell an AND from an OR — the attempt-#4 bug was an OR):** (a) Budget ₹10,000,000, Actual ₹10,150,000 → +150,000 passes abs, +1.5% fails pct → does **not** fire; (b) Budget ₹200,000, Actual ₹260,000 → +60,000 fails abs, +30% passes pct → does **not** fire. (Corpus controls C02/C09, doc 42 §8.) **Escalation boundary:** Budget ₹1,000,000, Actual ₹1,150,000 → +150,000 (1.5× abs) / +15% (3× pct) → fires **Medium**, because escalation to High requires ≥3× on *both* legs (plant P30).
- **EXC-004 sample:** Voucher V1 lines +100,000.00, −99,999.99 → imbalance ₹0.01 beyond 0 tolerance → fires with both row ids in evidence. **Control:** +100,000.00/−100,000.00 → silent (C01).
- **EXC-025 sample:** IN01 posts ₹92,500 to 6400 Marketing with description "Office rent Oct-25 Andheri premises"; over the prior 12 periods the tokens `rent` (124 of 126 occurrences), `premises` (36/36) and `andheri` (38/38) all sit in 6200 Rent and never in 6400 → 3 signal tokens agree on 6200 → fires Medium, key `EXC-025|IN01|6400|2025-P07|JV-25-0733`, suggestion *reclass* Dr 6200 / Cr 6400 ₹92,500 (confidence high). **Control (C11):** "Event stall rent Diwali campaign" to 6400 → only `rent` is a signal token (`event`, `stall`, `campaign` are 6400-dominant) → 1 < 2 → silent. An implementation that fires on a single token is wrong.
- **EXC-026 sample:** V05 has 8 prior capex invoices on 1400 between ₹45,000 and ₹52,000 (median ₹48,000); a new line is ₹4,800,000 → ratio 100.0 → within 2% of 100 → `decimal_shift_suspect`; |Δ| ₹4,752,000 ≥ min_abs → fires **High** (ratio ≥ 100; also ≥ 3× material_abs), key `EXC-026|IN02|1400|2025-P08|PV-25-0866`, suggestion *reverse_and_repost* at ₹48,000 (confidence medium — "confirm against the invoice"). **Control (C12):** ₹96,000 from the same vendor → ratio 2.0 < 5 → silent.

## 5. Lifecycle & ownership (implemented in rules/workflow.py)
new → acknowledged → explained → corrected (requires one of: an applied management adjustment created from the suggestion, a rectification-journal export containing the finding, or a journal reference typed in the note) → verified (by analyst, after re-run no longer fires or the correcting lines are seen in a later committed batch — §7.4 proposes this transition automatically, the analyst confirms) → closed. `waived` from any state: reason + expiry ≤ 90 days mandatory; expired waivers resurface. Owner resolution: account_owners → vendor owner fallback → "Unassigned" queue on S01/S08 (never ownerless-invisible). Due dates: high 3 days, medium 7, low next period-end (settings). Every transition → finding_history + audit_log.

## 6. Acceptance linkage
Planted corpus (doc 42 §7–§8): 36 plants (19 High) + 13 controls mapped to the rules above; bars in doc 14 §3 (recall 36/36, controls 0/13, High 19/19 — DEC-008 as amended by DEC-011). Each rule's work item test includes its §4-style sample (fires once, exact key) and control (silent) before any integration run is trusted; the suggestion fixtures (doc 89 §2) assert the §7 template output for every plant.

## 7. Rectification suggestions (every finding carries one — `app/rules/suggestions.py`)
### 7.1 Shape
`suggestion = {kind, lines[], target_period_id, basis, confidence, erp_hint}` stored in `findings.suggestion_json` (doc 02). `lines[] = {entity_id, account_id, cost_centre_id|null, amount_minor (debit +, credit −), description, source_account_ref|null}`; journal-kind suggestions **must net to zero** (Σ amount_minor = 0 — enforced by the builder, tested per template). `target_period_id` = the current open period (never a locked one; when the offending row sits in a locked period the lines are dated in the open period and the description says "prior-period correction of <voucher>"). `basis` = one plain sentence that quotes the evidence numbers ("8 earlier invoices from this vendor on this account average ₹48,000; this one is ₹4,800,000 — exactly 100×"). `confidence ∈ {high, medium, low}` per the template rule below. `erp_hint` = the ERP-side action in the user's words ("Reverse voucher PV-25-0866 and re-enter at ₹48,000"). Descriptions on correcting lines are composed from the catalogue (doc 55 `suggestion.*` keys) and always end with `[FPA EXC-### <voucher>]` so the correction can be recognised on the next import (§7.4).

### 7.2 Kinds (closed list)
`reverse` (undo the posting) · `repost` (post what should have been posted) · `reverse_and_repost` (both, for amount/period/account slips) · `reclass` (move between accounts) · `reclass_dimension` (same account, different cost centre) · `accrue` (book the missing accrual) · `release_accrual` (reverse a stale one) · `clear_suspense` (move out of 1999 to the proposed account) · `move_period` (reverse here, repost in the period the document belongs to, or the open period with narrative) · `investigate` (no journal yet — lists the questions to answer) · `commentary` (explanation required, no entry) · `none` (information only, e.g. control-total mismatch is fixed by re-import).

### 7.3 Template per rule (the builder quotes this table in `test_suggestions.py`)
| Rule | Kind | Lines (Dr +, Cr −) | Confidence rule |
|---|---|---|---|
| EXC-001 | reverse | mirror of the duplicate voucher's legs (the later batch) | high |
| EXC-002 | investigate | — ("same tuple in two batches: re-import or genuine re-posting?") | medium |
| EXC-003 | none | — (fix = correct the file / declared totals and re-import) | high |
| EXC-004 | repost | one balancing leg to 1999 Suspense for the imbalance, flagged for follow-up | low |
| EXC-005 | move_period | reverse in locked period's open successor; repost dated in the open period with narrative | medium |
| EXC-006 | investigate | — (vendor share jump; questions: new contract? one-off? split?) | low |
| EXC-007 | clear_suspense | Cr 1999 / Dr proposed account = the account most used by the same vendor/narration tokens (EXC-025 association table), else `investigate` | medium if an account is proposed, else low |
| EXC-008 | commentary | — (large one-off: explanation + supporting document) | medium |
| EXC-009 | investigate | — (who/when/why; segregation-of-duties check) | medium |
| EXC-010 | move_period | reverse in posting period, repost in document period when open, else open period with "prior-period" narrative + accrual proposal | medium |
| EXC-011 | release_accrual | reverse the un-reversed accrual voucher legs | high |
| EXC-012 | investigate | — unless a reversal is identifiable → `reverse` | low |
| EXC-013 | commentary | — (spike: explanation; if EXC-025/026 fired on the same account the inbox links them) | medium |
| EXC-014 | reclass | Dr vendor's dominant account / Cr posted account, the line amount | medium (high if dominant share ≥ 95%) |
| EXC-015 | accrue | Dr account / Cr 2300 Accruals at the median of the prior-6 charges | medium |
| EXC-016 | accrue | Dr account / Cr 2300 at the median prior accrual | medium |
| EXC-017 | commentary | — (unbudgeted: explanation, or an audited budget-version edit on S17 — doc 29 §1; the suggestion links there) | medium |
| EXC-018 | commentary | — (variance commentary draft; AI-assisted if enabled, doc 11) | medium |
| EXC-019 | commentary | — (trend: forecast update prompt, doc 08) | medium |
| EXC-020 | investigate | — (round-amount cluster: supporting invoices) | low |
| EXC-021 | investigate | — (split approvals: approval evidence for the window) | low |
| EXC-022 | investigate | — (in-and-out pair: business reason) | low |
| EXC-023 | repost | balancing leg proposal to the voucher's usual counter-account (same journal template history), else `investigate` | low |
| EXC-024 | commentary | — (dormant account used: confirm intent) | low |
| EXC-025 | reclass | Dr proposed account / Cr posted account (line amount, same cost centre, `source_account_ref` copied) | high if ≥ 3 signal tokens, else medium |
| EXC-026 | reverse_and_repost | reverse the line; repost at median × nearest power of ten when `decimal_shift_suspect`, else at the median with "confirm amount" | medium when decimal-shift, else low |
| EXC-027 | reclass_dimension | Cr posted cost centre / Dr dominant cost centre, same account and amount | high if dominant share = 100%, else medium |
| EXC-028 | reverse | mirror of the later (flagged) line's voucher legs | medium ("confirm invoice numbers first") |

### 7.4 Consumption and verification
1. **Apply as adjustment** (S08 action, `POST /exceptions/{id}/suggestion/apply {mode: adjustment}`): creates a doc-39 adjustment group of kind `correction_view` from the lines, reason prefilled with the finding key, finding → `corrected` with the group id in history; locked target period → ERR-046. The GL layer is untouched (doc 39 §1).
2. **Add to rectification journal** (`{mode: journal}`): queues the lines (`findings.suggestion_status = queued`); S11 exports the period's queue as a journal file in the project's ERP format (doc 26 §7: D365 F&O General journal, D365 BC General Journal, generic CSV). Export → finding `corrected` with the report id. The accountant imports/reviews/posts in the ERP — the app never posts.
3. **Not applicable** (`{mode: dismiss, note}`): `suggestion_status = dismissed`, note mandatory, audited; the finding lifecycle is unaffected.
4. **Verification loop:** on every rule run, for findings in `corrected`, `suggestions.py` searches the newly committed rows for the correcting lines (same entity/account/|amount|, description tag `[FPA EXC-### <voucher>]` **or** amount+account match with posting_date after the correction date); a match attaches the rows as evidence and proposes `corrected → verified` (one-click confirm on S08; auto-confirm is a setting, default off). No match after 2 further periods → the finding shows "correction not yet seen in the ledger" and appears in the S16 close checklist.
5. **Idempotence:** apply/queue twice for the same finding → ERR-005 (idempotency) — one suggestion, one consumption, visible in history.
