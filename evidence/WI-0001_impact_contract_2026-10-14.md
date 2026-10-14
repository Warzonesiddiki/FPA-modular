# WI-0001 impact transport checkpoint — 2026-10-14

**in_progress · M0 OPEN (0/8 done) · requested WI-0001…0030: 0/30 complete.**
Seven endpoint sections are not seven work items. This checkpoint is documentation,
JSON Schema and synthetic policy verification, not an HTTP, financial, database,
filesystem recovery, Windows-security or acceptance-harness pass.

## 1. Verified start and bounded scope

- Clean assigned branch `arena/5165fe46-fpa-modular`, HEAD `4257b5a`, the supplied
  PR #3 merge. No prior local changes were discarded, no branch switched/reset.
- Read AGENT_PROMPT in full, doc 00 source matrix/§10, TASKBOARD position and latest
  handovers, WORK_PLAN header/WI-0001, preceding close evidence including §4,
  owning 30/41 and relevant 02/03/05/22/24/45/63/64/90 contracts.
- First command accidentally used `/home/user` rather than the checkout and
  failed to find Git/AGENT_PROMPT; corrected cwd before reading/editing anything.
- Missing environment: created ignored `.venv`, installed pinned
  `tests/docs/requirements.txt`. Python **3.11.2**; this is the doc-verification
  environment, not verification of the declared product Python >=3.12 platform.
- Before edits: `.venv/bin/python -m pytest -q` → **394 passed in 11.94s**.
  Both `scripts/check.py` and `scripts/docs_check.py` absent; neither was run.

DEC-021, docs-first commits **e811c38** and **6d2bcef**:
- GET period restatement context; POST impact generation; GET immutable impact;
  GET paged changes; POST explicit approval; GET historical approval; GET retained
  baseline (including older cycles).
- 15 closed definitions added to the existing attachment, not another schema
  registry. **254 total definitions, 18 job kinds, 76 error codes**; all 239 prior
  definitions byte-equivalent as parsed JSON.
- Baseline from last locked pack, exact before/after snapshot + manifest binding,
  immutable comparison/approval, project/period ownership, expected period version,
  durable idempotency, audit events and atomic publication prescribed.
- Generation compares retained views synchronously; it does not run financial
  engines, refresh/stale the after forecast, generate packs or add a job kind.
  No performance claim: revisit the sync transport only with measured M3 evidence
  and an explicit contract decision if needed.
- Currentness uses cycle/revision/snapshot/manifest/checked-pack guards, permanent
  invalidation after financial mutation, and **durable audit append order**, not
  timestamps or random ids. Approval/sign-off audit events do not stale financial
  inputs. Lock/sign-off retain their independent audit-head concurrency fence.
- Null/absent amounts are not zero; deltas in presented units; paged, bounded
  statement/BvA money/finding/forecast/report changes with historical drill refs.
  The change stream is not a substitute for the full retained BvA viewer (ratios,
  favourability and materiality remain in its retained view).

This does **not** close the remaining snapshot/persistence/coordination omissions
in §4 below. DTO references do not establish that those snapshots exist.

## 2. Test-first and exact executed results

New paired test: `tests/docs/test_api_impact_contract.py`, registered by editing
`tools/generate_work_plan.py` and regenerating both plan files. Independent
synthetic fixtures and literal monetary expectations were authored before the
schema. Cookbook examples were authored from those literals, not generated from
schemas. Document test code is not installed into the product.

Initial pre-schema run:
```text
.venv/bin/python -m pytest tests/docs/test_api_impact_contract.py -q --tb=short
11 passed, 103 errors in 1.01s
AssertionError: DEC-021 impact definitions missing
```
The 11 standalone binding/hash checks passed; schema-dependent tests failed at
the deliberate contract-presence assertion, not imports/collection.

Initial schema run: **1 failed, 113 passed in 2.81s**. The route parity parser
mistook the prose “not unlock's ERR-015” for a declared failure. Changed the
parser to compare the explicit **Failures** row (all codes/statuses still
checked against doc 05's global table); no error route or assertion dropped.
Then **114 passed in 3.30s**, full **508 passed in 15.24s**.

Refinement red after docs-first durable ordering/historical baseline changes:
**2 failed, 142 passed in 2.51s**, missing seventh route and declared audit-order
policy. An earlier run accessed the missing policy field with KeyError; replaced
that with an explicit missing-contract assertion and reran the red before adding
metadata. Then **144 passed in 3.41s**. Added a labelled-unavailable/month-2/numeric-
delta test; final fresh runs:
```text
.venv/bin/python -m pytest tests/docs/test_api_impact_contract.py -q --tb=short
145 passed in 3.13s
.venv/bin/python -m pytest tests/docs -q --tb=short
530 passed in 14.53s
.venv/bin/python -m pytest -q --tb=short
539 passed in 14.78s
.venv/bin/python -m pytest -q --tb=short
539 passed in 14.75s
git diff --check
[exit 0, no output]
```
**145 impact + 108 close + 80 lifecycle + 77 project + 120 job document tests,
plus the 9 unchanged product tests = 539.** Equal deterministic outcomes, not
identical pytest elapsed times.

## 3. Self-verification

### Three caught mutations
`test_three_mutations_caught` runs the same independent `assert_oracles` against
isolated schema/policy copies; no product files modified:
1. Replace forecast-change result `stale` with constant `fresh` → the positive
   retained stale-run oracle fails JSON Schema validation.
2. Remove `same_cycle` from the conjunctive current-report guards → an old-cycle
   synthetic case is incorrectly accepted and the oracle assertion fails.
3. Increase ImpactCreate expected_version minimum **2→3** → the migrated locked
   version-1 → unlocked version-2 fixture is rejected (actual version boundary).

The previous twelve probes remain in the full suite. This tests declarative
policy, not whether a real service discovers correct cycle/manifest facts.

### Three highest-risk spec checks
- **41 §5–§6 / 05 §9.0 / 30 §6–§7:** all eleven current-report conjuncts have
  independent false-case tests; ten approval binding fields have negative controls;
  locked/open/history shapes cannot advertise current ids. Generation/approval
  are declared non-financial and do not bump period revision. Audit ordering and
  persistent invalidation are policy assertions, NOT a storage/race proof.
- **03 §1/§5 / 41 §6 / 05 §9.0:** independently literal revenue 100.00→125.00,
  actual +25.00, var_abs 20.00→45.00; absent is not zero. Schema rejects numeric
  values/deltas and unavailable-with-drill inconsistencies. The complete cookbook
  identities, sorted rows, counts, bindings and canonical hash are checked;
  negative controls replace an identity without changing counts, duplicate/reorder
  a row, and corrupt counts/hash. No finance arithmetic is implemented here.
- **05 §1/§9.1–§9.7 / 22 / 90:** exact seven methods/paths/request/response/query/
  status/idempotency records match doc sections; every listed error belongs to
  its global HTTP status. Closed-field injections/attest/note bounds are tested.
  No raw HTTP duplicate-query/JSON/auth/ownership execution is claimed.

### Universal edge checklist
- **Zero amounts/denominators:** zero and absent/not_available distinguished by
  schemas/fixtures; division N/A, impact transport does not compute percentages.
- **Negative/credit-normal:** negative decimal-string values accepted, revenue
  oracle is presented-unit positive delta (not ledger-credit subtraction).
  Actual sign conversion/calculation remains the money/calc owner's work.
- **Empty/single/duplicate:** empty report/page, one change, required/unknown
  fields, duplicate/order semantic controls. A zero-change report is not approval.
- **250k-row posture:** counts=250000 and page limit 1000 validated. No throughput,
  memory, streaming DB or synchronous latency measurement claimed.
- **Missing optional data:** null/absent/not_available side labels and drill
  coherence; unbounded/missing schema fields rejected; query fields optional.
- **Locked period/version:** locked/open context cannot expose current ids;
  expected versions reject 0/1/negative/bool/non-integers, version 2 accepted;
  wrong-cycle/revision flags reject. Real transactions/replay/rollback unbuilt.
- **Superseded batch:** changed input manifest/never_invalidated flags reject;
  retained stale-forecast/superseded-report shapes. No live supersession test.
- **Expired waiver:** N/A to impact transport; the 108 prior close tests remain
  green. Effective waiver evaluation is still a runtime readiness obligation.
- **Hostile text:** script/formula/Unicode remain literal bounded text; 500-char
  note accepted, 501 rejected, 10k necessarily outside same bound; controls,
  blank note, actor/snapshot/force/impact_approved injections rejected. Not proof
  of rendered escaping/ACL protection.
- **Ambiguous dates/amounts:** inherited ISO types, explicit injected example
  clocks; locale/exponent/NaN/Infinity/numeric monetary values rejected. No new
  date parser or calendar engine added.
- **Currency 0/2/3:** syntactic decimal variants tested; actual per-project exponent
  conversion/formatting belongs to core/money and runtime adapters, not schema.
- **Month 2:** P02 baseline/report/approval shapes tested; no month-2 E2E claim.
- **Determinism:** two fresh full runs same 539 result, fixed canonical cookbook
  hash `ea4dcc1c58bfceee6c0cce5852eadef0feea058032782c46d8f0050f86a8ecaa`,
  generated WORK_PLAN files byte-identical on repeat.

### Scope, money, no-invention and plan
Executed assertions: 267 WI id/path/milestone/dependency tuples unchanged from
`4257b5a`; seven gate texts unchanged and equal to doc 86; plan regeneration
byte-identical; 254/18/76 schema/job/error counts; all old definitions unchanged;
`git diff 4257b5a -- app tests/unit tests/integration` empty. No `float(` in the
new test/shared schema; manual inspection found only counts/hashes/version
operations and literal monetary expectations, no financial calculation.
Every added DTO/field/identity/error/paging bound is declared in docs 05 §9 and
41 §6 before schema additions. No new errors or stages, no acceptance bar change.

Files: docs 05/17/22/24/30/41/63/90/CHANGELOG; shared schema; new document test;
generator and generated WORK_PLAN md/csv; TASKBOARD and this evidence. Repeating
spec corrections are part of WI-0001, not starts/completions of later WIs.

## 4. Exact continuation — still WI-0001

1. **Next bounded API piece:** task/calendar/template and sign-off/lock history.
   Read doc 30 §§1–7, doc 23 §7 and doc 02 close-task/sign-off storage first;
   finish GET close / PUT task shorthands, permitted edits/dependencies, pagination,
   guards and historical outcome reads. Reject dependency cycles and manual
   completion/dependencies on T-09/T-10. No later WI starts.
2. **Impact depth still owed before WI-0001 sign-off:** specify full retained
   snapshot/view/manifest storage and canonical finding business-state
   serialization; explicit baseline/impact/change/approval/invalidation tables
   and schema-equality obligations in doc 02; assign persistence, input-affecting
   invalidation and lifecycle coordination ownership in the plan generator.
   The current DTOs prescribe this but do not implement or verify it. Historical
   drill endpoint expansion must resolve frozen inputs, not current rows. The
   old project persistence/lifecycle ownership gap also remains open.
3. **Backup/restore:** safe bounded selection/transport (not arbitrary `{path}`),
   live SQLite/WAL snapshots, archive/hash/audit/path/size validation,
   credential/control-state exclusions, durable job/receipt behaviour, fencing
   after rollback, target ownership, preserving pre-restore data. Permanent
   impact invalidation is not proof of a restore epoch/stale-write fence.
4. Remaining import/mapping/connector/financial/planning/report/workflow families
   and doc-90 index migration. No complete endpoint/OpenAPI parity claim.
5. Frozen doc-02 delta 14 and calendar low-year concerns remain M1 work. Neither
   checker nor cold M0 audit exists. **M0 0/8; WI-0001 in_progress; batch 0/30.**

DECISIONS TAKEN: DEC-021 (auto). OWNER-ONLY ITEMS: none for this checkpoint;
real-tenant Entra registration remains a future pilot requirement. NEXT WI:
WI-0001 (continue, do not advance).
