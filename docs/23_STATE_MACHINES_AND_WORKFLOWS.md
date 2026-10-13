# 23 — STATE MACHINES & WORKFLOWS

> Every lifecycle in one place; code (workflow modules) implements exactly these transitions; illegal transition = ERR-040/080. All transitions write audit + history.

## 1. Period: `open → closing → locked → (unlock→) closing`
Enter `closing` when analyst starts close checklist (S16); `locked` via lock action (FR-PRJ-003 guards). Imports into `locked` rejected; into `closing` allowed with banner.

## 2. Import batch: `staged → validated → committed | rejected | superseded`
`staged` on upload; `validated` after validation run (quarantine may be non-empty); `committed` only via atomic commit passing control totals; `rejected` = analyst discard (staging removed, audit kept); `superseded` when same (file-hash, period, kind) recommitted. Crash in commit → stays `validated` (never half-committed).

## 3. Finding: `new → acknowledged → explained → corrected → verified → closed`; `waived` from any non-closed state
Guards: corrected needs reference note (re-import batch/journal); verified needs a re-run where the finding no longer fires OR evidence-accept note; waived needs reason + expiry ≤90d → auto-returns to `new` on expiry (job on app open + on rule run). Re-firing of a closed finding (same key, later run) reopens as `new` with history preserved.

## 4. Forecast run & scenario: run `draft → locked` (immutable); scenario `draft → applied-view → saved`; sandbox what-if has no persistence state (session only).
## 5. Budget version: `draft → approved → locked`; BvA default compares latest locked, analyst may select approved (labelled in exports).
## 6. Commentary: `draft → approved` (exports read approved only); AI drafts enter as draft w/ provenance; editing an approved commentary creates a new draft version.
## 7. Close task: `not_started → in_progress → done | blocked | waived(reason)`; period sign-off requires all tasks done/waived + zero blockers (TB, high findings, stale forecast, exports) or override note.
## 8. Recon: `open → in_review → signed_off`; sign-off guard ERR-081 (tolerance).
## 9. Alert: `active → acknowledged → dismissed(auto after period lock)`; deduped by key.
## 10. Report: `generating → ready | failed(checks)`; ready reports immutable, regeneration = new report row.

## Month-end happy-path workflow (the spine, services/month_end.py)
Import commit → TB gate → statements snapshot → rules run → findings triage → forecast run+lock → commentary approve → checks → board pack → close sign-off → period lock. Each step's completion is derived from the state machines above (never a manually-ticked checkbox pretending completion — S01/S16 read real states; manual tasks in S16 are the only human-attested items, and they say so).
