# 22 — ERROR CATALOGUE (complete)

> Implemented in `app/core/errors.py`; API shape in doc 05 §1. Rule: code + plain message + hint + retryable. New errors append here first (P2). UI never shows a code to the analyst (codes appear in logs/diagnostics).

| Code | Trigger | Message (analyst wording) | Hint | Retry |
|---|---|---|---|---|
| ERR-001 | Project/period/resource not found | "We couldn't find that." | Go back / pick from the list | no |
| ERR-010 | Duplicate project name | "A project with this name already exists." | Choose a different name | no |
| ERR-011 | Lock blocked by high findings | "N high-severity items are still open." | Review them in Exceptions, or record an override note | no |
| ERR-012 | Backup/restore path not writable | "That folder can't be written to." | Pick another folder | yes |
| ERR-020 | Unsupported file type | "This file type isn't supported." | Use CSV or Excel (.xlsx) exported from your ERP | no |
| ERR-021 | File too large / row cap | "This file is larger than the 200 MB / 1M-row limit." | Split by period or company and import in parts | no |
| ERR-022 | Mapping conflict/incomplete | "Two columns are mapped to the same field." (or unmapped required field named) | Fix the highlighted mapping | no |
| ERR-023 | Control-total mismatch | "The file's totals don't match the totals you declared." (values shown) | Check file/period, correct totals | no |
| ERR-024 | Trial balance imbalance | "Debits and credits don't balance yet." (amount + accounts shown) | See Trial Balance for the vouchers | no |
| ERR-030 | Statements with no committed GL | "No data has been committed for this period yet." | Import and commit this month's GL first | no |
| ERR-040 | Illegal finding transition | "That action isn't available for an item in this state." | Refresh — its state may have changed | yes |
| ERR-041 | Waiver without reason/expiry | "A waiver needs a reason and an expiry date." | Add both (max 90 days) | no |
| ERR-050 | Duplicate master code | "That code is already used." | Use a unique code | no |
| ERR-060 | Export blocked by failed checks | "Some numbers don't tie yet, so the deck is blocked." (checks listed) | Open the Checks list; fix the source and regenerate | no |
| ERR-070 | AI unavailable/disabled | "AI drafting is off." | Add a provider key in Settings — everything else works without it | no |
| ERR-071 | AI draft rejected by guardrails | "The draft mentioned a number that isn't in your data, so it wasn't used." | Try again or write the commentary manually | yes |
| ERR-080 | Close sign-off blocked | "Close blockers are still open." (list) | Resolve or record an override note | no |
| ERR-081 | Recon out of tolerance | "Sub-ledger and GL differ by more than your tolerance." (amount) | Review unmatched items on both sides | no |
| ERR-090 | Audit chain verification failed | "The audit trail check failed for this project." | Stop, restore your latest backup, then run diagnostics | no |
| ERR-091 | DB migration failed | "This project couldn't be upgraded." (backup path shown) | Your original file is untouched — restore and contact support with diagnostics | no |
| ERR-099 | Unexpected internal error | "Something went wrong on our side." (diagnostics id) | Retry; if it repeats, download diagnostics from Help | yes |

Job failures surface as the same catalogue via `/jobs/{id}.error`. Every code has a test asserting message+hint non-empty and retryable flag.
