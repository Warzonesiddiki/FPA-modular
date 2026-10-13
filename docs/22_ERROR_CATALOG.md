# 22 — ERROR CATALOGUE (complete)

> Implemented in `app/core/errors.py` (one constructor per code; the module's test asserts the set of codes in this table equals the set in code — doc 14 §4 contract parity). API shape in doc 05 §1 (`FP&A-ERR-###`). Rule: code + plain message + hint + retryable. New errors are appended **here first** (P2), then in code, same commit. UI never shows a code to the analyst (codes appear in logs/diagnostics). Message text in code must equal this table (parametrised parts in `{}`).

## 1. Numbering
`00x` general · `01x` project/period · `02x` import · `03x` statements/analysis · `04x` findings & adjustments · `05x` master data · `06x` exports/reports/licence · `07x` AI · `08x` close/recon/year-end · `09x` system · `10x` planning/forecast. Codes are never reused; retired codes stay in the table marked *(retired, DEC-nnn)*.

## 2. Catalogue
| Code | Trigger | Message (analyst wording) | Hint | Retry |
|---|---|---|---|---|
| ERR-001 | Project/period/batch/finding/report/job not found | "We couldn't find that {what}." | Go back and pick it from the list | no |
| ERR-002 | Request field invalid (type, range, missing) | "Something in this request isn't valid: {field}." | Correct the highlighted field | no |
| ERR-003 | Version conflict (row changed since it was read) | "This item was changed by another action since you opened it." | Refresh and apply your change again | yes |
| ERR-004 | Job cancelled by the analyst | "This task was cancelled." | Start it again when you're ready | yes |
| ERR-005 | `Idempotency-Key` reused with a different payload | "This request was already made with different details." | Use a new request | no |
| ERR-010 | Duplicate project name | "A project with this name already exists." | Choose a different name | no |
| ERR-011 | Lock blocked by open High findings | "{n} high-severity items are still open." | Review them in Exceptions, or record an override note | no |
| ERR-012 | Backup/restore path not writable or not found | "That folder can't be written to." | Pick another folder | yes |
| ERR-013 | Delete confirmation text does not match the project name | "The name you typed doesn't match." | Type the project name exactly to confirm | no |
| ERR-014 | Restore integrity failed (hash or audit chain mismatch) | "This backup can't be verified, so it wasn't opened." | Use a different backup; run Diagnostics if it repeats | no |
| ERR-015 | Unlock/override without a note | "A note is required to {action} this period." | Add a short note explaining why | no |
| ERR-016 | Period not in the right state for the action | "This period is {state}, so that action isn't available." | See the period's status in Settings → Periods | no |
| ERR-020 | Unsupported file type | "This file type isn't supported." | Use CSV or Excel (.xlsx) exported from your ERP | no |
| ERR-021 | File too large / row cap | "This file is larger than the {limit_mb} MB / {row_cap}-row limit." | Split by period or company and import in parts | no |
| ERR-022 | Mapping conflict or required field unmapped | "Two columns are mapped to the same field." / "{field} isn't mapped yet." | Fix the highlighted mapping | no |
| ERR-023 | Control-total mismatch | "The file's totals don't match the totals you declared." (declared vs actual shown) | Check file and period, then correct the totals | no |
| ERR-024 | Trial balance imbalance | "Debits and credits don't balance yet." (amount + accounts shown) | See Trial Balance for the vouchers | no |
| ERR-025 | Amount can't be parsed (API/batch level: declared total, setting, manual entry) | "'{value}' isn't a number we can read." | Use digits with an optional decimal point, e.g. 125000.50 | no |
| ERR-026 | Date can't be parsed or is ambiguous | "'{value}' isn't a date we can read with the format {fmt}." | Check the date format in the mapping profile | no |
| ERR-027 | Import into a locked period | "Period {period} is locked, so nothing can be imported into it." | Unlock the period (with a note) or choose another period | no |
| ERR-028 | Batch not in the required state (e.g. commit before validate) | "This import isn't ready for that step yet ({state})." | Finish the previous step first | no |
| ERR-029 | Unsafe file (decompression ratio, path traversal in name, macros, external links) | "This file was blocked for safety." (reason) | Re-export it from your ERP as a plain CSV or .xlsx | no |
| ERR-030 | Statements with no committed GL | "No data has been committed for this period yet." | Import and commit this month's GL first | no |
| ERR-031 | Invalid drill key | "We couldn't open the detail for that number." | Refresh the page and try again | yes |
| ERR-032 | Invalid layer / version / run selector | "That {selector} isn't available for this period." | Pick one from the list | no |
| ERR-040 | Illegal finding transition | "That action isn't available for an item in this state." | Refresh — its state may have changed | yes |
| ERR-041 | Waiver without reason/expiry | "A waiver needs a reason and an expiry date." | Add both (maximum 90 days) | no |
| ERR-042 | Adjustment group unbalanced (docs 39/40) | "These adjustment lines don't net to zero." (Δ shown) | Balance the group, or change the kind to provision with a contra account | no |
| ERR-043 | Adjustment or reclass on a locked period outside the restatement workflow | "This period is locked. Use Restate to change it." | Open the restatement workflow (it keeps the audit trail) | no |
| ERR-044 | Assignment to an unknown or inactive owner | "{owner} can't be assigned items right now." | Pick an active owner, or reactivate them in Master data | no |
| ERR-045 | Allocation basis empty or sums to zero | "This allocation has nothing to allocate on ({basis})." | Check the driver or basis values for the period | no |
| ERR-046 | Suggested fix can't be applied or exported (doc 07 §7) — details.reason ∈ `no_journal_lines` (kind investigate/commentary/none), `target_period_locked`, `queue_empty` | "This suggestion can't be turned into an entry: {reason_text}." | Add a note or handle it in the ERP; for a locked period use Restate; for an empty queue add suggestions to the journal first | no |
| ERR-050 | Duplicate master code | "That {kind} code is already used." | Use a unique code | no |
| ERR-051 | Invalid account metadata (calc line as mapping target, unknown tag, bad normal side) | "That setting isn't valid for an account: {detail}." | Choose a value from the list | no |
| ERR-052 | Delete of a master record that is referenced | "{kind} {code} is used by {n} rows, so it can't be deleted." | Deactivate it instead | no |
| ERR-060 | Export blocked by failed checks | "Some numbers don't tie yet, so the deck is blocked." (checks listed) | Open the Checks list; fix the source and regenerate | no |
| ERR-061 | Report not ready / failed | "This report isn't ready ({status})." | Wait for it to finish, or regenerate | yes |
| ERR-062 | Report definition invalid (unknown block, period, grain) | "This report layout has a problem: {detail}." | Edit the report definition | no |
| ERR-063 | Licence expired beyond grace (exports only) | "Your licence has expired, so exports are paused. Your data is untouched." | Renew the licence in Settings — everything else keeps working | no |
| ERR-070 | AI unavailable/disabled | "AI drafting is off." | Add a provider key in Settings — everything else works without it | no |
| ERR-071 | AI draft rejected by guardrails | "The draft mentioned a number that isn't in your data, so it wasn't used." | Try again or write the commentary manually | yes |
| ERR-072 | AI provider unreachable / timed out | "The AI service didn't respond." | Check your connection and try again | yes |
| ERR-073 | AI payload exceeds provider limit | "There's too much data for one draft." | Narrow the scope (one statement or fewer lines) | no |
| ERR-080 | Close sign-off blocked | "Close blockers are still open." (list) | Resolve them or record an override note | no |
| ERR-081 | Recon out of tolerance | "Sub-ledger and GL differ by more than your tolerance." (amount) | Review unmatched items on both sides | no |
| ERR-082 | Year-end checks failed (open periods, TB, rollforward Δ ≠ 0) | "The year can't be closed yet: {reasons}." | Fix each item listed, then run the check again | no |
| ERR-083 | Restatement without an approval note | "Restating a locked period needs an approval note." | Add who approved it and why | no |
| ERR-084 | Close task dependency unmet | "'{task}' can't be completed until '{dependency}' is done." | Finish the earlier task first | no |
| ERR-085 | Recon kind not supported for this batch | "This file isn't a {kind} extract." | Import it with the matching sub-ledger kind | no |
| ERR-090 | Audit chain verification failed | "The audit trail check failed for this project." | Stop, restore your latest backup, then run Diagnostics | no |
| ERR-091 | DB migration failed | "This project couldn't be upgraded." (backup path shown) | Your original file is untouched — restore it and contact support with Diagnostics | no |
| ERR-092 | Database busy/locked | "The project file is busy right now." | Wait a moment and try again | yes |
| ERR-093 | Disk full / write failed | "There isn't enough space to save this." | Free up disk space, then retry | yes |
| ERR-099 | Unexpected internal error | "Something went wrong on our side." (diagnostics id) | Retry; if it repeats, download Diagnostics from Help | yes |
| ERR-100 | Budget version state illegal for action | "This budget version is {state}, so it can't be {action}." | Copy it to a new draft version | no |
| ERR-101 | Headcount plan goes negative | "Headcount for {cc} would fall below zero in {period}." | Reduce leavers or add joiners for that month | no |
| ERR-102 | Integrated forecast doesn't articulate | "The forecast statements don't tie: {link}." (e.g. ΔCash CF vs BS) | Open the planning check list for the broken link | no |
| ERR-103 | Edit of a locked forecast run | "This forecast run is locked." | Create a new run or scenario instead | no |
| ERR-104 | KPI expression invalid | "This formula can't be read: {detail}." | Use + − × ÷, brackets and names from the list | no |
| ERR-105 | Setting value invalid / out of range | "{setting} must be {constraint}." | Enter a value in range | no |
| ERR-106 | Forced forecast method lacks history | "{method} needs at least {n} periods of history for {group}." | Choose another method or let the app pick | no |
| ERR-107 | Scenario base run not locked | "Scenarios need a locked forecast run as their base." | Lock the run first | no |
| ERR-108 | Sensitivity / goal-seek parameters invalid | "The {param} range isn't valid." | Check the range, step and target | no |
| ERR-109 | Driver formula references an unknown driver | "The formula for {line} uses '{driver}', which doesn't exist." | Add the driver or fix the formula | no |

## 3. Rules
- Job failures surface the same catalogue via `/jobs/{id}.error`.
- Import **row-level** problems are *quarantine reasons* (doc 06 §4), not errors: a bad amount in row 412 quarantines the row; ERR-025/026 are for values the analyst typed or declared, or batch-level fields.
- Every code has a test asserting message + hint non-empty and the retryable flag; the parity test asserts code-set equality between this table and `errors.py`.
- Message tone: doc 13 §copy — plain, says what happened, never blames, no jargon, no code in the sentence.
