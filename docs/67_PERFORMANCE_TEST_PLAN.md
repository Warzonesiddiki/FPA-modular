# 67 — PERFORMANCE TEST PLAN (companion to doc 36 budgets)

1. **Datasets:** PERF-250K = corpus generator flag `--scale 250k` (doc 42), PERF-1M rows import cap test, PERF-UI-10K table fixture. Datasets generated, hash-stamped, never hand-tuned to pass.
2. **Protocol:** reference profile (36) recorded in evidence (CPU/RAM/disk/OS); warm-up run discarded; 3 measured runs, median reported; budgets assert on median, and any single run > 1.5× budget is investigated. Cold vs warm cache labelled.
3. **Scenarios:** parse+stage, commit, TB, full rule run, statements+BvA, Excel pack, PPT, dashboard API, drill on largest account, UI filter/sort, 12-period soak (memory growth < 10% period-over-period after P03).
4. **Regression triage:** >10% median regression = CI fail (14 §4): bisect by packet, profile the hotspot (py-spy/cProfile artefacts in evidence), fix or owner-accepted DEC with new budget — budgets never edited silently in the same PR as a regression.

## 5. Feasibility spike (Wave-1, before budgets are believed — brutal-audit B8)
Before Wave 5 opens, a spike packet benchmarks: openpyxl writing a 250k-row sheet (time/RSS), python-pptx deck with 8 native charts, SQLite rule-run over 250k rows with the doc-02 indexes. Results filed in evidence/perf/; if any budget in doc 36 is infeasible, the budget changes via DEC with the spike data attached — budgets are hypotheses until this spike lands, and saying so is the point of this section.
