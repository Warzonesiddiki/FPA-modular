# WI-0001 close-contract checkpoint — 2026-10-14

**in_progress · M0 open (0/8 done) · requested WI-0001…0030 batch: 0/30 done.** Three transport specifications are not three completed work items. This is document/schema/model verification, not an implemented close service, HTTP adapter or financial readiness evaluation.

## 1. Baseline and contract

Fetched origin; clean baseline `7b9a34f`, session branch unchanged. Read AGENT_PROMPT, doc 00 §10, current/last TASKBOARD handovers, WI-0001 acceptance and owning sections in 02/05/22/23/24/30/41/64/90. `.venv/bin/python -m pytest -q` → **286 passed in 10.66s**. No checker script exists yet; none is claimed run.

DEC-020 / docs-first **2b8162a** specifies:
- GET `/projects/{id}/periods/{period_id}/close-readiness`: bounded 16-code aggregate, current review/snapshot digest and readiness, no task creation or hidden work on reads.
- POST `/close/sign-off`: explicit human attestation, version and exact review binding, immutable record + one audit event + durable idempotency, no implicit lock or period-version bump.
- POST `/projects/{id}/periods/{period_id}/lock`: explicit current signoff_id, refreshed review token, version, force/note; separate atomic transition and revision increment, no generic integrity/restatement bypass.

Doc 30 §6–§7 resolves the T-09/T-10 dependency cycle: they are **outcomes**, not sign-off prerequisites. Only High findings and custom manual prerequisites admit a recorded exception. TB, rule coverage, forecast, checked pack, integrity and current impact approval remain hard guards. Old blanket override wording is reconciled in repeating specs. Missing template is not an empty satisfied checklist.

Sign-off validity is deliberately conservative: its event must be the latest project audit event and its period revision, financial snapshot and blocker fingerprint must still match. Any intervening project mutation requires a fresh sign-off, including another period's mutation. GET does not mutate. This avoids inventing an incomplete dependency-revision graph. Effective expiry is re-evaluated even without a background expiry run. Snapshot checks cannot rely on batch watermark alone.

Review **6e5ad92** clarifies locked history vs permission for another lock and excludes the caller's own lease from the busy guard. Locked T-09/T-10 history remains true; current_signoff in readiness is null outside closing. Impact generation must not itself stale a freshly regenerated forecast and create another cycle.

Nine new definitions → **239 definitions**, with **18 job kinds / 76 errors unchanged**. Existing ERR-011 is tightened to n≥1 and 1..100 detail IDs; exact count/first-min(n,100) ordering is contextual. Its previous zero-count example was contradictory and corrected. ERR-080/083 hints now distinguish stale/current review and limited overrides. No new error or job kind.

## 2. Executed red → green

Paired test: `tests/docs/test_api_close_contract.py` (registered in generator/WI-0001; no new WI).

Before schema implementation:
```text
.venv/bin/python -m pytest tests/docs/test_api_close_contract.py -q --tb=short
7 passed, 81 errors in 1.08s
AssertionError: DEC-020 close definitions missing
```
Seven standalone canonical-token tests already passed; 81 schema-dependent tests failed at the deliberate missing-contract assertion, not an import/collection problem. Fixtures and policy cases were authored independently, not generated from the schema.

After nine definitions, before correcting the old error shape:
```text
1 failed, 87 passed in 0.76s
Failed: DID NOT RAISE ValidationError
(test_high_error_cannot_claim_zero_findings)
```
The old schema admitted n=0/empty finding_ids and the example actually claimed “0 high-severity items are still open.” The doc-22/doc-05 positive-count/bounded-detail specification preceded its schema correction. Then **88 passed in 0.79s**, full **374 passed in 11.06s**.

Additional adversarial static-shape checks found **6 failed, 102 passed in 1.07s**: false ready flags, repeated blocker codes with different counts, and historical sign-off incorrectly exposed as current while locked. Added the corresponding schema constraints from the already documented invariants. Then **108 passed in 0.93s**, full **394 passed in 11.46s**.

Final fresh commands:
```text
.venv/bin/python -m pytest tests/docs/test_api_close_contract.py -q --tb=short
108 passed in 0.99s
.venv/bin/python -m pytest tests/docs -q --tb=short
385 passed in 11.73s
.venv/bin/python -m pytest -q --tb=short
394 passed in 11.51s
git diff --check
[exit 0, no output]
```
Total: **108 close + 80 lifecycle + 77 project + 120 job document tests + 9 unchanged product tests**. This is not a docs-checker, M0 cold audit, HTTP, database, Windows or acceptance-harness pass.

## 3. Self-verification

### Three caught mutations (same oracle, isolated schema copies)
`test_three_mutations_caught` calls the same `assert_oracles`:
1. LockedPeriod returns status=open → positive locked-response oracle fails.
2. Drop same_snapshot from the conjunctive current-signoff policy → the deliberately stale-snapshot case becomes permitted and the expected rejection fails.
3. LockedPeriod minimum response revision 2→3 → the migrated closing/version-1 → locked/version-2 positive fixture fails. This catches an actual off-by-one, not just the usual version-3 example.

No on-disk product file is mutated. Nine prior schema mutation probes remain in the full run. The policy interpreter is **a document model over synthetic facts**, not an engine computing whether a live trial balance/report is valid.

### Three highest-risk contract checks
- **30 §6 / 23 §7 / 05 §8:** prerequisite T-01…T-08 excludes T-09/T-10; exact 16-code table/schema parity; every hard code resists force+note+soft override in the policy model; all four current-signoff conjunction terms independently exercised. Actual custom-task dependency traversal/financial evidence evaluation is future implementation work.
- **05 §8.0 / 24 §4 / 30 §7:** golden canonical bytes independently authored before schema; SHA256 of `[]` checked with sha256sum; literal before/after sign-off review tokens; each of six review components invalidates the digest. Equal finding counts with different IDs do not hash equally; ordering/duplicate canonicalisation deterministic. Signer is a label, never an actor field or authority; review digest is not authentication. Full financial manifest freshness, audit walking and race control are not proved by these examples.
- **05 §8.2–§8.3 / 41 §5 / 22:** example sign-off retains period revision; lock uses the **refreshed** token and the returned signoff_id; lock bumps revision once, retains calendar identity and uses injected time. Locked history cannot reauthorise another lock. Force-note error precedence and hard-impact guard are explicit. Route errors match the shared HTTP table and validate against the catalogue; actual error-handler/persistence execution remains M3 work.

### Edge checklist
- Zero/negative money, credit-normal accounts, denominators, currency exponents: N/A to these DTOs (no financial values/computation); prior money-contract tests remain green. Do not infer TB correctness from the synthetic `trial_balance` flag.
- Empty/single/duplicates: empty blockers, one blocker, repeated code with different counts, canonical duplicate identities, absent/unknown fields tested. Missing template is specified as hard failure; task instantiation is unbuilt.
- Large input posture: 16 public aggregate codes; ERR-011 sample count 250,000 with 100 IDs validated, not a throughput measurement. Full identity fingerprinting/streaming remains runtime work.
- Optional/missing data: explicit null fields, force-note missing/null/blank/type/control precedence, no-body/query rules and explicit attest=true tested/documented. Raw duplicate JSON/query rejection not executed here.
- Locked periods/optimistic versions: wrong/static states, positive integer types, preserved locked-history distinction and migrated version-1 case covered. Atomic rollback/replay/lease behaviour is specified, not tested against storage.
- Superseded inputs/expired waivers: policy hard stops and fingerprint negative controls exercised over synthetic facts; live supersession, waiver expiry and age>2 computation need engine tests. No threshold was weakened.
- Hostile input: note/script/formula/Unicode treated as bounded data; actor/snapshot/impact_approved/completed_tasks/server-time injections rejected. UI escaping/ACLs are not implied.
- Ambiguous dates/amounts: inherited UTC/date schemas; no amount/date-locale parser added. Before/after fixture clocks deterministic.
- Multi-period/multi-month: project/period/version/snapshot digest changes, including another project mutation's audit-head invalidation; no month-2 E2E claim.
- Determinism: fresh runs agree; fixed canonical hashes and plan regeneration byte-identical. Financial artifact determinism remains untested at this checkpoint.

### Scope, plan and money
Executed Python assertions: **267 id/path pairs stable** against `7b9a34f`, paired test declared, **7/7 gate texts present/equal and unchanged**, generated WORK_PLAN.md/.csv repeat byte-identical, **239/18/76** schema/job/error counts and three new endpoint records. `git diff 7b9a34f --name-only -- app tests/unit tests/integration` empty. No `float(` in new test/schema; manual review found counts/revisions/hash operations only, no money arithmetic.

Changes: doc 05 plus owning/repeating docs 02/17/19/21/22/23/24/30/41/63/90, CHANGELOG, shared schema, generator/generated plan, new paired test, TASKBOARD and this evidence. The doc-21 one-line consistency correction does not start WI-0002. No SQL, dependency, runtime module, original test, bar or gate changed.

## 4. Exact continuation — WI-0001 remains open

1. **Impact generation/approval transport and field schemas.** Preconditions are now explicit, but there is still no complete DTO/endpoint for the immutable baseline/current report/deltas/attestation. Finish this before runtime routes are written; do not let a lock note or boolean become impact approval. Preserve the acyclic pack→impact→approval→sign-off→lock order.
2. **Task/calendar/template and sign-off/lock history reads.** Existing GET close and PUT task shorthands still need complete fields, permitted transitions, pagination, ownership and version guards. They must expose locked historical outcomes without treating them as current mutation permission; reject dependency cycles and T-09/T-10 dependency/edits.
3. **Backup/restore** remains unresolved: bounded safe transport/selection, live SQLite/WAL snapshot, archive structure/hash/audit/path/size validation, secret/control-plane exclusions, durable receipts/jobs, stale-write fencing after rollback, ownership and retention of pre-restore data. Moving the specified launch descriptor outside projects did not implement safe backup.
4. Remaining imports/mapping/connector/financial/planning/report/workflow endpoint families and doc-90 index migration; no complete OpenAPI/runtime parity claim yet.
5. Resolve missing project persistence/lifecycle coordination ownership in the generator before WI-0001 sign-off. Close evidence uses the existing snapshot_json field (doc 02); legacy rows without review binding remain historical, not fabricated approvals. Snapshot/impact persistence still needs full ownership/schema verification before M1.
6. Frozen doc-02 delta 14/calendar low-year issues remain M1 work. No later WI or milestone is started; no `scripts/docs_check.py` / `scripts/check.py` / cold M0 audit pass exists.

DECISIONS TAKEN: DEC-020 (auto). OWNER-ONLY ITEMS: none for this scope; real-tenant Entra setup remains a future pilot requirement.
