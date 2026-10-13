# 42 — SAMPLE DATA SPECIFICATION (the coherent corpus)

> Implements MASTER_PLAN §6. This corpus is the project's ground truth: acceptance (doc 14 §3), oracles (03/29), E2E, demos and the S02 sample project all derive from it. Owner work items: `sample-data/generate_sample_data.py` + `sample-data/answer_key.json` (doc WORK_PLAN, M1). **Period ids in this doc follow doc 02 exactly: `<fiscal_year>-P<nn>` where fiscal_year is the calendar year the FY starts (FY Apr-2025…Mar-2026 = `2025-P01`…`2025-P12`).**

## 1. The fictional company
"Meridian Trading & Services Pvt Ltd" — 2 entities (IN01 Mumbai HQ, IN02 Bengaluru), 14 cost centres, COA = doc 28 template (≈85 accounts), 30 vendors (V01…V30 + V31 first used in a plant), 8 customers-as-text, FY Apr–Mar, INR (exponent 2). 24 months of history (FY `2024` = Apr-2024…Mar-2025, FY `2025` = Apr-2025…Mar-2026) + FY `2026` budget, so backtests, YoY, seasonality (doc 08) and rolling forecasts have real depth. The **golden period** used by exports/cross-artifact tests is `2025-P07` (October 2025).

## 2. Generation model (one plan, controlled noise — the anti-attempt-#4 design)
1. **Plan first:** monthly revenue by entity (growth + seasonal indices: festive Q3 spike, March year-end push), GM% band, opex lines as %/fixed, headcount plan, capex calendar, debt schedule. Written as `plan.json` (human-readable, reviewed like a spec, committed).
2. **Budget** = plan exactly (FY `2025` and FY `2026` budget versions).
3. **Actuals** = plan × (1 + ε), ε from a seeded RNG, per-line σ ≤ 1.5%, rounded to minor units; then **trial-balance construction**: every voucher is generated in balanced debit/credit legs from transaction templates (sales, purchases, payroll, rent, SaaS, capex, debt, tax), so the TB balances by construction; balance is verified by test, never force-plugged.
4. **Plants and controls:** only the deviations in §7 and §8 are injected, each by an explicit generator function `plant_P##()` / `control_C##()` that also emits its `answer_key.json` entry. Nothing else in the corpus may deviate from plan beyond ε.
5. **Determinism:** single seed (default 42) in the generator header; regeneration → identical SHA-256 manifest (`hashes.json`) — CI-tested.
6. **Coherence guarantee (the extras killer):** the generator's own test asserts that no *unplanted* entity×account×period variance exceeds **both** materiality legs (doc 03 §5: ≥ ₹100,000 **and** ≥ 5%), and no unplanted spike exceeds both EXC-013 legs. Noise can never create a material finding.

## 3. Volume & shapes
GL ≈ 9,500 rows/month (~230k over 24 months — doubles as the perf corpus seed, doc 67), budget 2 FYs × 2 versions, drivers (volume/price/headcount), opening BS for FY `2024` P01, bank/AR/AP sub-ledgers for the last 6 months (recon fixtures), poster/time columns present in the GL export (so EXC-009 can run), malformed set (§5).

## 4. Files produced (all under `sample-data/`)
`plan.json` · `gl_<fy>_P<nn>.csv` (24 files; D365-style columns incl. `PostedBy`, `PostedAt`) · `budget_<fy>_v<n>.xlsx` · `drivers.csv` · `opening_bs_2024.csv` · `subledger_bank|ar|ap_<period>.csv` (6 periods) · `masters/{entities,accounts,cost_centres,vendors,owners}.csv` · `answer_key.json` · `hashes.json` · `malformed/` (§5). File names, column headers and the mapping profile that imports them are fixed by this doc; the E2E test imports them through the real pipeline (no shortcut DB).

## 5. Malformed corpus (doc 06 §4; each file ships with `<name>.expected.json` = {rows_in, valid, quarantined_by_reason})
`bad-encoding-latin1.csv` · `missing-column.csv` (no amount) · `ambiguous-dates.csv` (dd/mm vs mm/dd both plausible) · `unbalanced-file.csv` (one voucher off by ₹0.01) · `duplicate-file.csv` (byte-identical to a committed file) · `formula-no-cache.xlsx` · `zero-byte.csv` · `wrong-delimiter.csv` (semicolon) · `parentheses-negatives.csv` · `mixed-debit-credit-and-signed.csv` · `unknown-account.csv` · `out-of-period.csv` · `1.2M-row-stress.csv` (generated on demand by a script flag, never committed) · `zip-bomb.xlsx` (built at test time only).

## 6. Verification (the generator's own tests, M1)
Regeneration hash equality · TB balanced per entity×period · coherence per §2.6 · answer key schema-valid with **32 plants, exactly 18 severity=high, 10 controls** (asserted) · every plant hand-findable in the raw files (the test opens the file and finds the planted rows by voucher) · sample project loads via the real import pipeline in E2E.

## 7. Plant register (normative — `answer_key.json` is generated FROM this table)
Severity = the severity the finding must carry when it fires (rule default or ≥3× amount escalation, doc 07 §1). Plants sit ≥10% inside their thresholds (doc 44) so boundary noise cannot flip recall. Amounts in ₹ (major units); the generator converts to minor units. `finding_key` follows doc 07 §2; the grain part per rule is given in doc 07 §3.

| Plant | Rule | Sev | Entity / account / party | Period | Construction (one line) | Why this severity |
|---|---|---|---|---|---|---|
| P01 | EXC-001 | High | IN01 / 6100 | 2025-P07 | Same voucher no + same amount posted in two committed batches | rule default High |
| P02 | EXC-001 | High | IN02 / 6200 | 2025-P08 | Two identical rows in one batch, no reversal leg | rule default High |
| P03 | EXC-003 | High | batch `gl_2025_P07` | 2025-P07 | Declared control total differs from file total by ₹1,000 | rule default High |
| P04 | EXC-004 | High | IN01 / voucher JV-25-0712 | 2025-P07 | Voucher legs net to ₹0.01 (tol = 0 fires) | rule default High |
| P05 | EXC-004 | High | IN02 / voucher JV-25-0931 | 2025-P09 | Voucher legs net to ₹50,000 | rule default High |
| P06 | EXC-005 | High | IN01 | 2025-P06 (locked) | Row dated into locked P06 arrives in the P07 batch | rule default High |
| P07 | EXC-007 | High | IN01 / 1999 | 2025-P09 | Suspense debit aged 75 days, unmatched | rule default High |
| P08 | EXC-007 | High | IN02 / 1999 | 2025-P10 | Suspense balance ₹140,000 at period end (≥ material_abs) | rule default High |
| P09 | EXC-021 | High | IN01 / vendor V14 | 2025-P08 | 4 vouchers of ₹190,000–₹198,000 within 5 days, Σ ₹776,000 ≥ 1.5 × ₹500,000 | rule default High |
| P10 | EXC-021 | High | IN02 / vendor V07 | 2025-P11 | 3 vouchers, Σ = ₹800,000 (1.6× limit) | rule default High |
| P11 | EXC-002 | Medium | IN01 | 2025-P08 | Voucher tuple from the committed P07 batch re-appears in P08 batch | rule default |
| P12 | EXC-006 | **High** | IN01 / 6300 / V22 | 2025-P09 | Vendor share 46 % of account spend, prior-3 avg 18 %; spend ₹760,000 ≥ 3 × spike_abs | ≥3× escalation |
| P13 | EXC-008 | Medium | IN02 / 6400 | 2025-P09 | One-off manual journal ₹1,200,000, no similar amount in prior 3 periods | rule default |
| P14 | EXC-010 | **High** | IN01 / 5100 | 2025-P10 (posted) · doc date 2025-P07 | Doc date Aug-2025, posted Oct-2025, amount ₹310,000 ≥ 3 × material_abs | ≥3× escalation |
| P15 | EXC-011 | Medium | IN01 / 2300 | 2025-P08 | Accrual voucher with no reversing entry in P09 | rule default |
| P16 | EXC-012 | Medium | IN01 / 6100 | 2025-P10 | Credits of ₹180,000 into an expense account, no reversal pair | rule default |
| P17 | EXC-013 | **High** | IN02 / 6200 | 2025-P10 | Period total +₹780,000 (+68 %) vs trailing-3 average; Δ ≥ 3 × spike_abs | ≥3× escalation |
| P18 | EXC-015 | Medium | IN01 / 6300 / V09 | 2025-P10 | Recurring SaaS charge (6 of prior 6 periods) absent | rule default |
| P19 | EXC-016 | Medium | IN02 / 2300 | 2025-P10 | Monthly accrual (6 of prior 6 periods) missing | rule default |
| P20 | EXC-017 | **High** | IN01 / 6600 | 2025-P09 | ₹320,000 spend, budget 0 for the grain; ≥ 3 × material_abs | ≥3× escalation |
| P21 | EXC-018 | **High** | IN01 / 6100 | 2025-P09 | Budget ₹1,000,000, actual ₹1,310,000: +₹310,000 (≥3× abs) and +31 % (≥3× pct) | ≥3× both legs |
| P22 | EXC-018 | High | IN02 / 5100 | 2025-P10 | Budget ₹2,000,000, actual ₹2,420,000: +₹420,000 / +21 % (≥3× both legs) | ≥3× both legs |
| P23 | EXC-019 | Medium | IN01 / 6200 | 2025-P08–P10 | YTD overrun ≥ ₹100,000 and growing in each of P08, P09, P10 | rule default |
| P24 | EXC-022 | Medium | IN02 / 6150 | 2025-P11 | Debit and credit of ₹245,000 within 3 days, distinct vouchers | rule default |
| P25 | EXC-009 | Low | IN01 | 2025-P11 | Sunday 02:10 posting by a poster outside the account's usual set | rule default |
| P26 | EXC-014 | Low | IN01 / V31 → 6800 | 2025-P11 | Vendor's first-ever use of account 6800, ₹150,000 | rule default |
| P27 | EXC-020 | Low | IN02 / 6400 | 2025-P11 | 6 vouchers at exact ₹10,000 multiples, Σ ₹310,000, 35 % of account vouchers | rule default |
| P28 | EXC-023 | Low | IN01 / voucher JV-25-1204 | 2025-P12 | Single-line voucher ₹300,000, not a system balancing leg | rule default |
| P29 | EXC-024 | Low | IN02 / 6900 | 2025-P12 | Account dormant 8 periods, ₹250,000 activity | rule default |
| P30 | EXC-018 | Medium | IN01 / 5200 | 2025-P09 | Budget ₹1,000,000, actual ₹1,150,000: +₹150,000 (1.5× abs) / +15 % (3× pct → **not** both legs 3×) | rule default (escalation needs both legs) |
| P31 | EXC-013 | High | IN01 / 6050 | 2025-P12 | Spike +₹800,000 / +120 % vs trailing-3; Δ ≥ 3 × spike_abs | ≥3× escalation |
| P32 | EXC-005 | High | IN02 | 2025-P12 (locked, re-opened batch) | Second locked-period posting, distinct entity | rule default High |

**Severity count (asserted by the generator and by `tests/data/test_answer_key.py`):** High = P01–P10 (10) + P12, P14, P17, P20, P21, P22, P31, P32 (8) = **18**; Medium = P11, P13, P15, P16, P18, P19, P23, P24, P30 (9); Low = P25–P29 (5). Total 32. Every rule EXC-001…024 has ≥1 plant; rules 001/003/004/005/007/021 have ≥2 (001, 004, 005, 007, 021 do; 003 is batch-level and has one plant plus control C03's negative). P30 also doubles as the **escalation boundary test**: it exceeds one leg 3× but not both, so it must stay Medium.

## 8. Control register (must NOT fire; the acceptance "control precision" bar is 0/10)
Controls are designed so that a wrong implementation would fire. In particular the two AND-tests (EXC-013, EXC-018) each get **both** one-leg-passes cases, because a control where both legs fail cannot distinguish an AND from an OR implementation (the attempt-#4 bug was exactly an OR).

| Control | Rule | Entity / account | Period | Construction | Wrong implementation it catches |
|---|---|---|---|---|---|
| C01 | EXC-004 | IN01 / voucher JV-25-0719 | 2025-P07 | Legs net to exactly ₹0.00 across 5 lines | tolerance applied with `>=` instead of `>`; per-line instead of per-voucher sum |
| C02 | EXC-018 | IN02 / 6100 | 2025-P09 | Budget ₹10,000,000, actual ₹10,150,000: +₹150,000 (abs **passes**) / +1.5 % (pct **fails**) | OR instead of AND; pct leg dropped |
| C03 | EXC-021 | IN01 / vendor V14 | 2025-P10 | Only 2 vouchers under the limit in 7 days, Σ ₹780,000 | count leg (≥3) dropped |
| C04 | EXC-013 | IN01 / 6400 | 2025-P08 | Spike +₹300,000 (abs **passes**) but +30 % (pct **fails**) | OR instead of AND; pct leg dropped |
| C05 | EXC-012 | IN02 / 6100 | 2025-P11 | Credit of ₹120,000 exactly reversing a P10 debit of the same amount | reversal-pair exclusion missing |
| C06 | EXC-001 | IN02 / 6300 | 2025-P09 | Same voucher no posted twice, second posting is a full reversal (equal opposite legs) | reversal exclusion missing |
| C07 | EXC-007 | IN01 / 1999 | 2025-P11 | Suspense item cleared in 12 days, balance ₹0 at period end | age computed from first entry, not oldest *open* entry |
| C08 | EXC-015 | IN02 / 6300 / V19 | 2025-P10 | Vendor active in exactly 4 of the prior 6 periods | history test `≥4` instead of `≥5`; must produce **no finding** (and no `not_run`, history is sufficient) |
| C09 | EXC-018 | IN01 / 6700 | 2025-P10 | Budget ₹200,000, actual ₹260,000: +₹60,000 (abs **fails**) / +30 % (pct **passes**) | OR instead of AND; abs leg dropped |
| C10 | EXC-013 | IN02 / 6050 | 2025-P11 | Spike +₹90,000 (abs **fails**) but +55 % (pct **passes**) | OR instead of AND; abs leg dropped |

Any plant or control change = this doc + `answer_key.json` + the doc 07 §4 examples + doc 14 §3 bars updated **in one commit** (DEC if a bar changes).

## 9. Relationship to the unit-level rule fixtures (doc 89 §2)
Each rule's `exc_###_fires.json` / `exc_###_silent.json` fixtures are miniatures of the plant and control rows above (same amounts, same keys, 1–3 vouchers), so a rule that passes its unit fixtures and then misses its plant in the corpus points at integration (lookback assembly, layer, period mapping), not at the rule logic.
