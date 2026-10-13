# 64 — JOB & BACKGROUND PROCESS SPECIFICATION

1. **Registry:** jobs run in-process workers (`app/jobs/`): import-validate, import-commit, rule-run, forecast-run, export-generate, backup/restore, audit-verify. One heavy job at a time per project (queue FIFO, UI shows position); light reads never queue.
2. **Contract (doc 05):** states queued|running|done|failed|cancelled; progress = stage label (copy keys, doc 55) + pct where measurable (rows processed/total) else indeterminate with elapsed time; cancellation is cooperative at stage boundaries (commit stage cancellable only before the transaction begins — after that it completes or rolls back, UI says which).
3. **Crash behaviour:** app restart marks running jobs `failed` with reason `interrupted` and offers resume where the stage design supports it (import staging persists; exports simply re-run). No job may leave partial artefacts: exports write to temp then atomic-rename; DB writes are transactional (61).
4. **Limits & logging:** per-job log slice (job_id in every line), retained with project logs (65); job history (type, started, duration, result counts) viewable in S13 diagnostics.


## Job catalogue (normative)
| Job | Stages (doc 55 copy keys) | Cancellable | Resume |
|---|---|---|---|
| import-validate | reading → profiling → validating → summarising | yes, any stage | restart (staging persists) |
| import-commit | checking totals → writing rows → trial balance | before "writing rows" only | no (re-run; idempotent, doc 06) |
| rule-run | loading → EXC-001…028 (progress per rule) → suggestions → verification matching → assigning owners | between rules | no |
| forecast-run | backtesting → fitting per group → writing lines | between groups | no |
| export-generate | snapshot → checks → rendering → stamping | before rendering only | no |
| backup/restore | copying → verifying hashes → (restore) integrity+audit verify | no | no |
| audit-verify | walking chain | yes | restart |
Progress pct: rows-based where the total is known (import/rule/export), stage-based otherwise (equal stage weights, labelled "stage x of y" in UI rather than a fake %). A job exceeding 2× its doc-36 budget on the reference profile logs a perf warning with its dataset hash (feeds doc 67 evidence).
