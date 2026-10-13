# 74 — MODEL RISK & VALIDATION SPECIFICATION

Models in scope: forecast methods (08/46), goal-seek/sensitivity (29), allocation (40), KPI definitions (43), rule thresholds (07). Controls: (1) **Inventory:** this doc + doc 62 config = the model inventory; every model has an owner (module), purpose, and validation evidence link. (2) **Independent validation before release:** backtest evidence per method on corpus + a second auditor-generated dataset (AUD-I data), challenger comparison (naive baseline must be beaten or the method's recommendation logic must say so — a method that can't beat naive is never recommended silently). (3) **Ongoing monitoring:** FVA/bias per group each period (08 §6) is the production model-monitoring; bias advisories are model-risk events logged in evidence at pilot reviews (84). (4) **Change control:** method/threshold/formula changes = spec PR + oracle regeneration + backtest re-run (72); locked forecast runs preserve the model version used (`method_map` + assumption versions, doc 48). (5) **Limitations disclosed in-product:** forecast screens show method + accuracy + "history length" (a forecast on 4 points is labelled as such); goal-seek shows iterations/convergence; AI commentary is drafting, not a model output (11).


## Validation evidence required per model
| Model | Artefact | Challenger |
|---|---|---|
| Forecast methods (08/46) | Backtest on corpus 24m + auditor dataset; MAPE/bias tables | Beat naive or disclose |
| Goal seek | Convergence log incl. unsolvable fixture | Hand-verified bounds |
| Sensitivity | Spreadsheet recompute of one fixture | Cell-by-cell diff |
| Allocations | Doc 40 oracle + step-down case | Σ = source, always |
| KPI library | Doc 43 fixtures incl. n/a paths | AUD-A recompute |
| Rule thresholds | Doc 42 register + doc 44 boundary matrix | AUD-B false-positive hunt |
| Entry-hygiene rules EXC-025 (token association) / EXC-026 (median outlier) / EXC-027 (dimension dominance) / EXC-028 (window dedupe) | Deterministic, explainable statistics only (counts, shares, median — no fitted model); parameters in doc 62; doc 42 plants P33–P36 + controls C11–C13; doc 44 boundary cases incl. the mean-vs-median trap | AUD-B false-positive hunt on the full 24-month corpus: every extra finding of these rules must be classified genuine/defect with a reason; defect count 0 |
| Rectification suggestion templates (doc 07 §7.3) | Σ = 0 type-level assertion; one fixture per rule (doc 89 §2); confidence rules quoted from the table | AUD-B reviews a sample of 10 suggestions for accounting correctness (debit/credit direction, account choice) and records the review |
Accepted residual risks: short-history forecasts (UI-labelled), driver data quality, default thresholds may need client tuning (doc 58 → DEC).
