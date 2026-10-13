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
