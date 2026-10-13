# 64 — JOB & BACKGROUND PROCESS SPECIFICATION

1. **Registry:** jobs run in-process workers (`app/jobs/`): import-validate, import-commit, rule-run, forecast-run, export-generate, backup/restore, audit-verify. One heavy job at a time per project (queue FIFO, UI shows position); light reads never queue.
2. **Contract (doc 05):** states queued|running|done|failed|cancelled; progress = stage label (copy keys, doc 55) + pct where measurable (rows processed/total) else indeterminate with elapsed time; cancellation is cooperative at stage boundaries (commit stage cancellable only before the transaction begins — after that it completes or rolls back, UI says which).
3. **Crash behaviour:** app restart marks running jobs `failed` with reason `interrupted` and offers resume where the stage design supports it (import staging persists; exports simply re-run). No job may leave partial artefacts: exports write to temp then atomic-rename; DB writes are transactional (61).
4. **Limits & logging:** per-job log slice (job_id in every line), retained with project logs (65); job history (type, started, duration, result counts) viewable in S13 diagnostics.

