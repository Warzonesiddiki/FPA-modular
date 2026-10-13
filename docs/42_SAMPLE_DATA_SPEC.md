# 42 — SAMPLE DATA SPECIFICATION (the coherent corpus)

> Implements MASTER_PLAN §6. This corpus is the project's ground truth: acceptance (14 §3), oracles (03/29), E2E, demos and the S02 sample project all derive from it. Owner packet: `sample-data/generate_sample_data.py` + `answer_key.json`.

## 1. The fictional company
"Meridian Trading & Services Pvt Ltd" — 2 entities (IN01 Mumbai HQ, IN02 Bengaluru), 14 cost centres, COA = doc 28 template (≈85 accounts), 30 vendors, 8 customers-as-text, FY Apr–Mar, INR. 24 months of history (FY25, FY26) + FY27 budget, so backtests, YoY, seasonality (doc 08) and rolling forecasts have real depth.

## 2. Generation model (one plan, controlled noise — the anti-attempt-#4 design)
1. **Plan first:** monthly revenue by entity (growth + seasonal indices: festive Q3 spike, Mar year-end push), GM% band, opex lines as %/fixed, headcount plan, capex calendar, debt schedule. Written as `plan.json` (human-readable, reviewed like a spec).
2. **Budget** = plan exactly (FY27 + FY26 budgets).
3. **Actuals** = plan × (1 + ε), ε ~ seeded RNG, per-line σ ≤ 1.5%, rounded to minor units; then **trial-balance construction**: every voucher generated in balanced debit/credit pairs from transaction templates (sales, purchases, payroll, rent, SaaS, capex, debt, tax), so TB balances by construction; balancing is verified, never force-plugged.
4. **Plants:** only the deviations in §4 are injected, as explicit generator functions `plant_P##()` each emitting an entry in answer_key.json.
5. Determinism: single seed (default 42) in generator header; regeneration → identical SHA-256 manifest (`hashes.json`) — CI-tested.

## 3. Volume & shapes
GL ≈ 9,500 rows/month (~230k over 24 months — doubles as the perf corpus seed, doc 67), budget 24×2 versions, drivers (volume/price/headcount), opening BS for FY25, bank/AR/AP subledgers for last 6 months (recon fixtures), malformed set (§5).

## 4. Plants & controls (32 + 8; IDs stable forever)
P01…P32 map 1:1 to answer_key entries {plant_id, rule EXC-###, entity, account, period, voucher, amount, severity, generator function}. Distribution: every rule ≥1 plant; high-severity rules (001/003/004/005/007/021) ≥2. P30 = the EXC-018 AND-test control (doc 07 §4). Controls C01…C08: near-miss cases per high-risk rule (just below threshold, balanced voucher, within-tolerance recon) that must NOT fire. Any plant change = this doc + answer key + doc 07 examples updated in one commit.

## 5. Malformed corpus (doc 06 §7; each with expected.json)
bad-encoding (Latin-1), missing-column, ambiguous-dates, unbalanced-file, duplicate-file, formula-no-cache.xlsx, zero-byte, wrong-delimiter, parentheses-negatives, mixed-debit-credit-and-signed, 1.2M-row stress (generated, not committed — script flag), zip-bomb.xlsx (build-time generated in tests only).

## 6. Verification (generator's own tests)
Regeneration hash equality · TB balanced per entity-period · actuals-vs-plan coherence (no unplanted |var| > 5% & ₹100k — the acceptance extras killer, asserted in CI) · every plant detectable in the raw files by hand (spot list) · answer-key schema valid · sample project loads via the real import pipeline (not a shortcut DB) in E2E.

## 7. Plant register (normative — answer_key.json is generated FROM this table; 18 high-severity plants make the 18/18 bar in doc 14 satisfiable and auditable)
Severity = the severity the finding must carry when the plant fires (rule default/escalation, doc 07). Plants sit ≥10% inside thresholds (doc 44).

| Plant | Rule | Sev | Entity/Account (indicative) | Period | Construction (one line) |
|---|---|---|---|---|---|
| P01 | EXC-001 | High | IN01/6100 | FY26-P07 | Same voucher+amount in two batches |
| P02 | EXC-001 | High | IN02/6200 | FY26-P08 | Duplicate rows in one batch, no reversal |
| P03 | EXC-003 | High | batch-level | FY26-P07 | Declared control total ≠ file total |
| P04 | EXC-004 | High | IN01/voucher | FY26-P07 | Voucher off by ₹0.01 (tol=0 fires) |
| P05 | EXC-004 | High | IN02/voucher | FY26-P09 | Voucher off by ₹50,000 |
| P06 | EXC-005 | High | IN01 | FY26-P06 (locked) | Posting dated into locked period via later batch |
| P07 | EXC-007 | High | IN01/1999 | FY26-P09 | Suspense balance 75 days old |
| P08 | EXC-007 | High | IN02/1999 | FY26-P10 | Suspense ≥ material_abs at period end |
| P09 | EXC-021 | High | IN01/vendor V14 | FY26-P08 | 4 vouchers just under ₹500k in 5 days, Σ ≥ ₹7.5L |
| P10 | EXC-021 | High | IN02/vendor V07 | FY26-P11 | 3 vouchers, Σ = 1.6× limit |
| P11 | EXC-002 | Medium | IN01 | FY26-P08 | Voucher tuple repeated from P07 batch |
| P12 | EXC-006 | Medium | IN01/6300 V22 | FY26-P09 | Vendor share 46%, prior avg 18% |
| P13 | EXC-008 | Medium | IN02/6400 | FY26-P09 | One-off manual ₹12L journal |
| P14 | EXC-010 | Medium | IN01/5100 | FY26-P09/P10 | Doc date Aug, posted Oct, ≥ material |
| P15 | EXC-011 | Medium | IN01/2300 | FY26-P08 | Accrual with no reversal next period |
| P16 | EXC-012 | Medium | IN01/6100 | FY26-P10 | Credits in expense ₹1.8L, no reversal pair |
| P17 | EXC-013 | Medium | IN02/6200 | FY26-P10 | Spike +₹4L and +68% vs trailing avg |
| P18 | EXC-015 | Medium | IN01/6300 V09 | FY26-P10 | Recurring SaaS charge absent |
| P19 | EXC-016 | Medium | IN02/2300 | FY26-P10 | Monthly accrual missing |
| P20 | EXC-017 | Medium | IN01/6600 | FY26-P09 | ₹2.2L spend, zero budget |
| P21 | EXC-018 | Medium | IN01/6100 | FY26-P09 | +₹2L / +20% (doc 07 sample) |
| P22 | EXC-018 | High | IN02/5100 | FY26-P10 | ≥3× both legs (escalated) |
| P23 | EXC-019 | Medium | IN01/6200 | FY26-P08–P10 | YTD overrun growing 3 months |
| P24 | EXC-022 | Medium | IN02/6150 | FY26-P11 | Same-amount in/out within 3 days |
| P25 | EXC-009 | Low | IN01 | FY26-P11 | Weekend 02:00 posting, unusual poster |
| P26 | EXC-014 | Low | IN01 V31/6800 | FY26-P11 | Vendor's first use of account, ₹1.5L |
| P27 | EXC-020 | Low | IN02/6400 | FY26-P11 | 6 round-amount vouchers, 35% share |
| P28 | EXC-023 | Low | IN01 | FY26-P12 | Single-line voucher ₹3L (not a balancing leg) |
| P29 | EXC-024 | Low | IN02/6900 | FY26-P12 | Dormant 8 periods, ₹2.5L activity |
| P30 | EXC-018 | — control | IN01/5200 | FY26-P09 | +₹20k/+2.27% — AND-test must NOT fire (doc 07 §4) |
| P31 | EXC-013 | High | IN01/6050 | FY26-P12 | Spike ≥3× spike_abs (escalated per rule severity policy in answer key) |
| P32 | EXC-005 | High | IN02 | FY26-P12 | Second locked-period posting (distinct entity) |

High-severity plants (exactly 18, asserted by the generator): P01–P10 (10) + P22, P31, P32 (3) + P12, P17, P21, P14, P20 authored at ≥3× thresholds so doc 07's amount-escalation makes them High (5) = **18**. Doc 14's recall denominator is the 31 non-control plants; P30 is counted only in the control bar (doc 14 §3).
Controls C01…C08: near-miss cases per high-risk rule (just below threshold, balanced voucher, within-tolerance recon) that must NOT fire. Any plant change = this doc + answer key + doc 07 examples updated in one commit.

## 5. Malformed corpus (doc 06 §7; each with expected.json)
bad-encoding (Latin-1), missing-column, ambiguous-dates, unbalanced-file, duplicate-file, formula-no-cache.xlsx, zero-byte, wrong-delimiter, parentheses-negatives, mixed-debit-credit-and-signed, 1.2M-row stress (generated, not committed — script flag), zip-bomb.xlsx (build-time generated in tests only).

## 6. Verification (generator's own tests)
Regeneration hash equality · TB balanced per entity-period · actuals-vs-plan coherence (no unplanted |var| > 5% & ₹100k — the acceptance extras killer, asserted in CI) · every plant detectable in the raw files by hand (spot list) · answer-key schema valid · sample project loads via the real import pipeline (not a shortcut DB) in E2E.

## 7. Plant register (normative — answer_key.json is generated FROM this table; 18 high-severity plants make the 18/18 bar in doc 14 satisfiable and auditable)
Severity = the severity the finding must carry when the plant fires (rule default/escalation, doc 07). Plants sit ≥10% inside thresholds (doc 44).

| Plant | Rule | Sev | Entity/Account (indicative) | Period | Construction (one line) |
|---|---|---|---|---|---|
| P01 | EXC-001 | High | IN01/6100 | FY26-P07 | Same voucher+amount in two batches |
| P02 | EXC-001 | High | IN02/6200 | FY26-P08 | Duplicate rows in one batch, no reversal |
| P03 | EXC-003 | High | batch-level | FY26-P07 | Declared control total ≠ file total |
| P04 | EXC-004 | High | IN01/voucher | FY26-P07 | Voucher off by ₹0.01 (tol=0 fires) |
| P05 | EXC-004 | High | IN02/voucher | FY26-P09 | Voucher off by ₹50,000 |
| P06 | EXC-005 | High | IN01 | FY26-P06 (locked) | Posting dated into locked period via later batch |
| P07 | EXC-007 | High | IN01/1999 | FY26-P09 | Suspense balance 75 days old |
| P08 | EXC-007 | High | IN02/1999 | FY26-P10 | Suspense ≥ material_abs at period end |
| P09 | EXC-021 | High | IN01/vendor V14 | FY26-P08 | 4 vouchers just under ₹500k in 5 days, Σ ≥ ₹7.5L |
| P10 | EXC-021 | High | IN02/vendor V07 | FY26-P11 | 3 vouchers, Σ = 1.6× limit |
| P11 | EXC-002 | Medium | IN01 | FY26-P08 | Voucher tuple repeated from P07 batch |
| P12 | EXC-006 | Medium | IN01/6300 V22 | FY26-P09 | Vendor share 46%, prior avg 18% |
| P13 | EXC-008 | Medium | IN02/6400 | FY26-P09 | One-off manual ₹12L journal |
| P14 | EXC-010 | Medium | IN01/5100 | FY26-P09/P10 | Doc date Aug, posted Oct, ≥ material |
| P15 | EXC-011 | Medium | IN01/2300 | FY26-P08 | Accrual with no reversal next period |
| P16 | EXC-012 | Medium | IN01/6100 | FY26-P10 | Credits in expense ₹1.8L, no reversal pair |
| P17 | EXC-013 | Medium | IN02/6200 | FY26-P10 | Spike +₹4L and +68% vs trailing avg |
| P18 | EXC-015 | Medium | IN01/6300 V09 | FY26-P10 | Recurring SaaS charge absent |
| P19 | EXC-016 | Medium | IN02/2300 | FY26-P10 | Monthly accrual missing |
| P20 | EXC-017 | Medium | IN01/6600 | FY26-P09 | ₹2.2L spend, zero budget |
| P21 | EXC-018 | Medium | IN01/6100 | FY26-P09 | +₹2L / +20% (doc 07 sample) |
| P22 | EXC-018 | High | IN02/5100 | FY26-P10 | ≥3× both legs (escalated) |
| P23 | EXC-019 | Medium | IN01/6200 | FY26-P08–P10 | YTD overrun growing 3 months |
| P24 | EXC-022 | Medium | IN02/6150 | FY26-P11 | Same-amount in/out within 3 days |
| P25 | EXC-009 | Low | IN01 | FY26-P11 | Weekend 02:00 posting, unusual poster |
| P26 | EXC-014 | Low | IN01 V31/6800 | FY26-P11 | Vendor's first use of account, ₹1.5L |
| P27 | EXC-020 | Low | IN02/6400 | FY26-P11 | 6 round-amount vouchers, 35% share |
| P28 | EXC-023 | Low | IN01 | FY26-P12 | Single-line voucher ₹3L (not a balancing leg) |
| P29 | EXC-024 | Low | IN02/6900 | FY26-P12 | Dormant 8 periods, ₹2.5L activity |
| P30 | EXC-018 | — control | IN01/5200 | FY26-P09 | +₹20k/+2.27% — AND-test must NOT fire (doc 07 §4) |
| P31 | EXC-013 | High | IN01/6050 | FY26-P12 | Spike ≥3× spike_abs (escalated per rule severity policy in answer key) |
| P32 | EXC-005 | High | IN02 | FY26-P12 | Second locked-period posting (distinct entity) |

High-severity plants: P01–P10, P22, P31, P32 = 13… plus P03/P06 counted — the register must total exactly 18 high: P01,P02,P03,P04,P05,P06,P07,P08,P09,P10,P22,P31,P32 = 13, therefore plants P12, P17, P21 are authored at escalated amounts (≥3× thresholds, doc 07 severity escalation) making them High: +3 = 16, and P14, P20 authored ≥3× material_abs with the answer key severity=high per doc 07's amount-escalation note added in this fix: +2 = **18 high**. The generator asserts `count(severity=high in answer_key) == 18` and `count(plants) == 32` (incl. P30 control; doc 14's "29/32 recall" counts P30 as a control, so recall denominator is 31 plants + separate control bar — doc 14 §3 amended accordingly in this fix).
Controls C01–C08: C01 EXC-004 balanced voucher ₹0.00 Δ · C02 EXC-018 P30 (above) · C03 EXC-021 two vouchers only under limit · C04 EXC-013 spike +₹3L but +30% (pct leg fails) · C05 EXC-012 credit exactly reversing a prior debit · C06 EXC-001 same voucher, second entry is a full reversal · C07 EXC-007 suspense cleared in 12 days · C08 EXC-015 vendor paused exactly at 4-of-6 history (insufficient history → not_run, not a finding).
