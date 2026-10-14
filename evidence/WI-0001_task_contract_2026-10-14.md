# WI-0001 task/calendar/history checkpoint — 2026-10-14

**WI-0001 in_progress · M0 OPEN (0/8) · requested batch WI-0001…0030: 0/30 complete.**
Eight endpoint sections are not eight work items. This is document/schema/model
verification, not implementation of HTTP, calendars, SQL, financial close,
filesystem recovery or Windows security.

## 1. Baseline, contract and decisions

Read AGENT_PROMPT in full, doc 00 source matrix/§10, TASKBOARD position/latest
handovers, WORK_PLAN header/WI-0001, impact evidence §4, docs 30/23/02/05/22/62/90
and relevant 19/24/48/63 sections. The doc-48 annual planning category shares
calendar concepts but is **not** a set of mandatory month-end prerequisites;
its transport/persistence remains a separate unfinished WI-0001 family.

Local Git metadata had reverted to `4257b5a`, with the prior checkpoint visible
as modified/untracked files. Fetched **only the assigned branch**, compared
**every** file in remote `d7ddb98` byte-for-byte, including both locally untracked
checkpoint files; all matched. `git reset --mixed origin/arena/5165fe46-fpa-modular`
reconciled branch/index metadata only; repeated byte comparisons confirmed no
working file changed. No branch switch, hard reset or discarded edits.

Ignored environment absent again: created `.venv`, installed pinned
`tests/docs/requirements.txt`. Python **3.11.2** (document-verification environment,
not the declared product Python >=3.12 certification).
Before edits: `.venv/bin/python -m pytest -q` → **539 passed in 15.10s**.
Neither `scripts/check.py` nor `scripts/docs_check.py` exists; neither run.

**DEC-022 (auto)**, docs-first **58759fc**, refinement **e17e96c**, cursor correction
**44bef75**:
- Eight explicit routes: close overview; paged tasks; individual task; guarded
  task PUT; template GET/PUT; per-period calendar; paged close outcome history.
- Future-only bounded whole-template replacement, exactly T-01…T-10 plus custom
  manual tasks; scalar acyclic dependency relation retained from doc 02.
  No dependencies on T-09/T-10, no manual transition of system/outcome tasks.
- Task + period version and exact task-review digest guard live writes. Expose
  CloseTaskReview so clients can match the statements actually displayed before
  T-04 attestation. Only the statement-input fingerprint is retained in that
  attestation, avoiding downstream forecast/commentary/pack cycles.
- Calendar copied once at start-close; template/holiday changes never rewrite
  live or locked periods. Explicit weekend/holiday/zero/negative/overflow rules;
  UTC civil evaluated_on is exposed for overdue display, not silently replaced
  by browser timezone. No holiday network service.
- Lock/sign-off/unlock history is immutable, paged in audit append order, and
  never current permission. Missing legacy evidence is labelled, not fabricated.
- Live task cursor expiry is bounded by the next relevant effective waiver
  expiry; ERR-002 on expiry, not a fictional row revision. Genuine audit-head
  conflicts use audit_id+1 positive revision details in ERR-003.
- Doc 02 **delta 15** explicitly records missing template/period-copy/task
  storage fields and constraints. Existing period_repo/close_service/core/calendar
  WIs own persistence/orchestration/date arithmetic. The M1 gate adds delta 15;
  all prior requirements remain. **SQL and product files remain frozen.**

22 definitions added: **276 definitions, 18 job kinds, 76 errors**; all 254 prior
schema definitions unchanged. No new WI, error, job kind or weaker acceptance bar.

## 2. Test-first execution and results

New paired test `tests/docs/test_api_task_contract.py` registered through the
plan generator (never hand-edited WORK_PLAN). Independent literal template/date/
state fixtures precede the schema; document-model graph/date/guard checks do not
call product code or a database. Cookbook DTOs use those fixtures, not schemas.

Pre-schema:
```text
.venv/bin/python -m pytest tests/docs/test_api_task_contract.py -q --tb=short
6 passed, 120 errors in 1.57s
AssertionError: DEC-022 close task definitions missing
```
Six standalone token/overdue checks passed; the schema-dependent tests failed at
an explicit missing-contract assertion, not collection/import errors.

Initial schema: **126 passed in 4.15s**. After the docs-first exposed review
context, tests rejected the unimplemented `review` field: **13 failed, 113 passed
in 3.15s**. Added the declared field, then contextual negative controls: **150
passed in 4.59s**, full **689 passed in 20.83s**.

Adversarial checks then caught **4 failed, 150 passed in 4.84s**:
1. T-04 status=done with no current statement fingerprint was admitted.
2. A waived task could omit its retained reason.
3. A non-statement task could claim a statement-review fingerprint.
4. The synthetic policy interpreter incorrectly required current statements for
   custom tasks (the spec requires this only for T-04).

Tightened schema branches and corrected the interpreter to the already-written
spec; also explicitly reject every system/outcome key in that model. No test
removed or acceptance bar weakened. **154 passed in 4.76s**. One final cursor
expiry-boundary oracle added after the owning-doc correction.

Final fresh results:
```text
.venv/bin/python -m pytest tests/docs/test_api_task_contract.py -q --tb=short
155 passed in 4.63s
.venv/bin/python -m pytest tests/docs -q --tb=short
685 passed in 20.70s
.venv/bin/python -m pytest -q --tb=short
694 passed in 20.85s
.venv/bin/python -m pytest -q --tb=short
694 passed in 20.99s
git diff --check
[exit 0, no output]
```
Total = **155 task + 145 impact + 108 close + 80 lifecycle + 77 project + 120 job
= 685 document tests; plus 9 unchanged product tests = 694.** No checker/cold audit,
HTTP adapter, SQL migration, legacy repair or finance acceptance gate passed.

## 3. Self-verification

### Three caught mutations
Same independent `assert_oracles`, isolated schema/policy copies only:
1. Replace T-10 kind=system with constant manual → default-template positive
   oracle fails validation. Outcome identity is not a caller choice.
2. Drop same_period_version from terminal transition conjunction → deliberately
   stale-period case is accepted and oracle assertion fails.
3. Count the anchor date for nonzero business offsets → Friday Jan30 +1 incorrectly
   stays Jan30 instead of Tue Feb03 (Monday holiday); hand-worked date oracle fails.
All restored by discarding copies. Previous fifteen probes still pass. The graph,
calendar and policy interpreters are **document models**, not an alternate app
implementation or proof that a future service discovers true input facts.

### Three high-risk spec checks
- **30 §8 / 23 §7 / 05 §10:** required built-ins, immutable kinds/titles, custom
  graph cycles/self/missing/outcome/duplicate edges, task/period/review guards,
  all system/outcome transition rejection, retained waiver reason and stale
  T-04 evidence. Exposed review hash binds eight components with negative controls;
  custom tasks do not inherit a statement-only prerequisite. Actual database
  reference ownership, race arbitration and persistent revocation remain future.
- **30 §9 / 62 / 05 §10:** literal weekday/holiday/zero/negative/leap/month-2/year-
  boundary oracles, unclipped overflow, overdue strictly after due date, immutable
  period-copy contract, and task cursor before/at expiry. This tests a document
  date model and schema, not frozen core/calendar implementation or alert jobs.
- **05 §10 / 02 §5 / 22 / 90:** eight route method/request/query/response/status/
  idempotency sets equal declared metadata; errors belong to their global HTTP
  rows; history shape discriminates sign-off/lock/unlock and legacy-null evidence.
  Scope/time/version/order/duplicate history negative controls exercised. No raw
  audit JSON/current-permission flag is admitted. No auth/HTTP/storage test claimed.

### Universal edge checklist
- Zero amounts/denominators/negative money/credit-normal accounts/currency 0/2/3:
  **N/A** to these metadata DTOs; no money computation introduced; earlier monetary
  document tests retained. Zero date offsets and zero counts are separately tested.
- Empty input: empty task page; not-instantiated overview cannot be ready or have
  fake counts/template version. Single row/duplicate keys/graph cycles tested.
- Large-input posture: 1000-entry bounded template including a 990-custom chain,
  1001 rows rejected; page cap 1000. Not a 250k-ledger-row performance measurement.
- Missing optional data: null owner/dependency/completion, legacy-null evidence,
  required/unknown fields and optional bounded query fields covered.
- Locked period/version: retained outcome shape is not edit permission; stale
  task and period conjuncts, version bounds and force-note lock-history shape
  covered. Real locking/replay/rollback not executed.
- Superseded batches: statement fingerprint stale controls and unchanged-history
  checks only. Full canonical manifests/source invalidation still unfinished.
- Expired waiver: cursor expiry at exact instant tested; due-date equality not
  overdue; no scheduler/persistence or live waiver lookup claimed.
- Hostile text: formula/script/Unicode literal title/note values accepted as data;
  controls, overlong/blank text, actor/force/completion injection rejected. No UI
  escaping/Windows ACL proof. 10k-char strings necessarily exceed existing bounds.
- Ambiguous dates/amounts: invalid Gregorian holiday rejected, fixed injected
  clocks and year overflow tested; financial parsing N/A here.
- Month-2 reuse: April-end → May 1/7 oracles, cross-year/holiday/leap checks; no
  product month-2 E2E pass claimed.
- Determinism: repeated full runs same 694 results; canonical review token fixed
  at `72b90e097d6a3780b6775897effc3d71294c62648c7c98ba435f766ea876a21d`;
  plan regeneration byte-identical. Elapsed pytest timings naturally differ.

### Scope, money and plan
Executed assertions versus `d7ddb98`: 267 WI id/path/milestone identities unchanged.
Only dependency delta: **WI-0152** now explicitly depends on **WI-0001 WI-0050
WI-0031** (contract/period repository/calendar), all earlier in order. Seven gate
texts match doc 86; the **only** gate change is M1 schema delta range 1–14 → 1–15.
No previous clause dropped. Generator rerun produces byte-identical md/csv.
All 254 old definitions unchanged; 276/18/76 counts verified. `git diff d7ddb98 --
app tests/unit tests/integration` empty. No `float(` in new test/shared schema;
manual inspection finds date/count/hash/version operations only, no money math.
All new public fields, bounds and behaviors are documented in 05 §10 / 30 §§8–9
before schema changes; schema cross-field arithmetic/ownership/currentness still
requires real runtime validation. No invention silently placed into product code.

Files: docs 02/05/17/19/22/23/24/30/48/62/63/86/90/CHANGELOG; schema attachment;
new document test; generator + generated WORK_PLAN; TASKBOARD and this evidence.
Doc 48 only resolves shared-calendar/close-prerequisite scope; no planning engine
or later WI was started. Doc 86 only strengthens delta coverage.

## 4. Exact continuation — WI-0001 remains open

1. **Next bounded piece: retained financial snapshot/impact/statement bindings and
   persistence coordination.** Define full manifest/view storage, canonical
   finding-state hashing, statement-only fingerprint (including prior-period
   inputs), atomic input-change invalidation and legacy calendar/evidence repair.
   Specify baseline/impact/change/approval tables and durable replay ownership in
   doc 02; assign all repository/service coordination in the generator. Task
   persistence now has explicit owners, but project lifecycle/receipts and full
   impact/manifest storage do NOT become solved merely by referencing period_repo.
   Statement viewer API must expose the fingerprint T-04 requires.
2. **Backup/restore** remains unresolved: bounded safe transport/selection instead
   of arbitrary `{path}`; live SQLite/WAL snapshots; archive/hash/audit/path/size
   validation; credential/control-state exclusions; durable jobs/receipts;
   rollback epoch/stale-write fencing; target ownership; preserved pre-restore data.
3. Remaining import/mapping/connector/financial/planning/report/workflow families,
   annual planning calendar/category persistence and doc-90 index migration.
   No complete OpenAPI/route implementability claim yet.
4. Frozen doc-02 deltas **14 and 15**, low-year calendar defect and all runtime
   calendar/close behavior remain M1/M3 work, not permission to implement now.
   No WI-0002/checker/M1 started; no cold M0 audit exists.

DECISIONS TAKEN: DEC-022 (auto) · OWNER-ONLY ITEMS: none for this checkpoint;
Entra setup remains a future real-tenant pilot prerequisite · NEXT WI: **WI-0001**.
