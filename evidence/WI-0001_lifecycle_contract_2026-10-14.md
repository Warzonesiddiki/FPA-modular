# WI-0001 lifecycle checkpoint — 2026-10-14

**STATUS: in_progress. M0 open, 0/8 done. Requested batch WI-0001…0030: 0/30 done.** Four endpoint sections are not four completed work items. No API, sample loader, deletion implementation, filesystem transaction, keyring operation or financial engine is claimed built.

## Baseline and contract

Fetch/log/status confirmed clean `8b00506` on the session branch. Read AGENT_PROMPT, index §10, TASKBOARD and the WI/owning contracts. `.venv/bin/python -m pytest -q` → **206 passed in 10.44s**. Environment already available; no system-package changes or branch changes.

DEC-018 / docs-first commit **e5bb560** specifies doc 05 §7:
- POST /projects/sample: server-owned sample defaults and FY2024–2026, no precomputed ledger/false completed workflow. Financial data still enters through ordinary import/validation/commit.
- DELETE /projects/{id}: exact confirmation, expected version, required durable key, exclusive lifecycle admission, local credential clearing, private same-volume trash and ≥30-day retention. Minimal receipt survives move/purge; normal reads cannot see trash.
- POST /projects/{id}/periods/{period_id}/start-close: only open→closing; one revision increment/template/audit; GET never starts close.
- POST /projects/{id}/periods/{period_id}/unlock: only locked→closing; mandatory note; immutable before-state retained atomically before correction; current lock fields cleared but history retained; no automatic impact approval or re-lock.

Seven added DTO definitions bring the authored attachment to **230 definitions**; **18 job kinds and 76 errors unchanged**. Four additional endpoint metadata entries and lifecycle policy annotations are document contracts, not implementations. Doc 90 indexes these fields, doc 63 §9 has complete examples.

DEC-019 / docs-first commit **438e13d** resolves a security-spec contradiction: doc 12 placed the CLI launch token inside a project while doc 70 promised no credential files and backup guidance copied the project. The descriptor is now specified outside projects/install payload, with owner-only ACLs, atomic publication/cleanup, single-active-instance discovery and a live-session check. **No real credential was found, relocated or handled by this task; no runtime code changed.** This is a corrected specification, not proof of implemented Windows ACL/backup protection.

Review also adds ERR-090 to new period mutations for audit-broken read-only mode; deletion's credential removal is explicitly local, not an outbound Microsoft revocation call. Recovery timestamps cannot shorten trash retention.

## Executed red → green trail

Paired test: `tests/docs/test_api_lifecycle_contract.py`. Initial collection failed because pytest reserves the parametrisation name `request` (**1 collection error in 0.19s**). Renamed it to `payload`; this tooling mistake is **not counted as a contract red**.

Actual pre-schema red:
```text
.venv/bin/python -m pytest tests/docs/test_api_lifecycle_contract.py -q --tb=short
67 errors in 0.89s
AssertionError: DEC-018 lifecycle DTOs missing
```
All were intentional fixture assertions, not missing imports. Independent literal DTOs and UTC/calendar examples were written before schema implementation; the schema did not generate the oracle values.

After schema extension: **67 passed in 0.56s**, full **273 passed in 10.59s**.

Adversarial review tests then produced **2 failed, 67 passed in 0.63s**:
- Period endpoint metadata lacked the ERR-090 read-only guard.
- The launch-token location still named the project folder.

Spec corrections preceded schema adjustment. Then **69 passed in 0.58s**, full **275 passed in 10.34s**. Additional source-state, retention, sample policy and minimal-receipt checks were added without changing a runtime gate.

Final executed checks:
```text
.venv/bin/python -m pytest tests/docs/test_api_lifecycle_contract.py -q --tb=short
80 passed in 0.62s
.venv/bin/python -m pytest tests/docs -q --tb=short
277 passed in 10.67s
.venv/bin/python -m pytest -q --tb=short
286 passed in 11.48s
```
Fresh repeat:
```text
.venv/bin/python -m pytest tests/docs/test_api_lifecycle_contract.py -q --tb=short
80 passed in 0.61s
.venv/bin/python -m pytest -q --tb=short
286 passed in 10.56s
git diff --check
[exit 0, no output]
```
Total: **80 lifecycle + 77 project + 120 job document tests + 9 unchanged product tests**. Neither docs checker nor scripts/check.py exists yet; no checker/milestone/cold-audit pass is claimed.

## Self-verification

### Three additional caught mutations
`test_three_lifecycle_schema_mutations_are_caught` executes the same independent `assert_lifecycle_oracles` helper against deep-copied, valid schemas:
1. Return a non-sample flag for CreatedSampleProject → the positive sample oracle fails validation.
2. Drop ClosingPeriod's status constraint → an open Period escapes the expected rejection.
3. Allow a 501-character note instead of 500 → the boundary probe escapes the expected rejection.

Only expected ValidationError/pytest assertion failures are caught. No product/repository file is mutated during probes. The six earlier job/project schema mutations remain tested in the full run.

### Three highest-risk spec checks
- **05 §7.1 / 42 §1/§6:** sample flag/currency/calendar/revision are server-owned; injected seed/path/id/credentials rejected; fixed FY policy and no-preloaded-financial-rows annotation verified. Actual corpus loading still requires M1/M3/E2E verification.
- **05 §7.2 / 12 §2.1:** exact, non-normalised confirmation distinguished from bad request shape; response is minimal `trashed`, not claimed permanent erasure; literal UTC examples verify 30 days over month/leap boundaries and ±1 second negative controls. Credential, filesystem, recovery and actual purge behaviour remain runtime obligations.
- **05 §7.3–§7.4 / 23 §1 / 41 §2 / 12 §3:** all three source states exercised for both transitions; no version reset/calendar change/current lock residue in response oracles; note error-code precedence and bounds; ERR-090 preserved; endpoint/code mappings agree with the 76-code catalogue. Atomic baseline/task/audit and write-lease enforcement are specified, not implemented/tested as storage behaviour here.

### Edge checklist
- Zero/negative money, credit-normal accounts, zero denominators: N/A to these metadata DTOs. Existing public-money tests still pass; no financial computation added.
- Empty/single/duplicate input: missing/unknown fields, empty/incorrect confirmation, optional-key semantics, exact version/shape checks. Duplicate raw JSON/query parsing and durable replay are runtime obligations.
- 250k-row posture: no ledger rows in these responses; sample workspace is not a 230k-row preload. No performance claim.
- Missing optional data: explicit null lock metadata; required-note error distinction; no invented note/actor/timestamp defaults.
- Locked periods/versions: valid locked→closing/open→closing and wrong-source/version negative controls; runtime concurrency/replay still pending.
- Superseded batches/expired waivers: not changed; baseline/history retention requirements preserved. Lock/re-lock/impact/waiver guards remain unfinished WI-0001 work.
- Hostile text: bounded Unicode/formula/script note values remain data; control-containing notes and server-field injection rejected. Actual UI/log escaping, path containment and Windows reparse/ACL behaviour require runtime tests.
- Ambiguous dates/amounts: inherited Timestamp rules; fixed UTC retention over Jan/Feb leap boundary; amount parsing N/A.
- Currency exponents: sample fixed INR exponent 2; prior 0/2/3 tests unchanged.
- Month-2 reuse/determinism: no system-clock inference; stored period identity retained, fixed injected example times. Repeated tests and generated-plan hashes agree; no financial artifact determinism claim.

### Scope / money / plan checks
Executed assertions: **267 stable WI id/path identities**, new paired test declared, **7/7 gate texts equal and unchanged**, WORK_PLAN.md/.csv repeat-byte-identical, **230 definitions / 18 job kinds / 76 errors / 4 lifecycle endpoint entries**. `git diff 8b00506 --name-only -- app tests/unit tests/integration` empty. Zero `float(` calls in the new test/schema; manual review found only revision/calendar/retention comparisons, no money arithmetic.

Touched files are authorised document contract/schema/tests, owning/repeating docs 02/04/05/12/17/18/19/23/30/41/42/63/70/90, CHANGELOG, generator/generated plan and handover evidence. No SQL, product module, prior test or acceptance threshold changed.

## Exact continuation — still WI-0001

1. **Backup/restore** needs a complete transport/archive/ownership contract, not `{path}`. Resolve allowed root/selection or upload/download semantics; live SQLite/WAL snapshot safety; archive manifest/hash/audit/zip traversal/size validation; credential/control-plane exclusions; durable job/receipt retention through restoration; stale-write/version safety after rollback; recover-to-new versus existing target and preservation of pre-restore data. Runtime launch credentials are now specified outside projects, but that alone does not implement safe backup.
2. **Lock/re-lock/sign-off/impact review**: finish doc-30 readiness without circular T-09/T-10 prerequisites; bind doc-41 impact attestation to the exact current before/after snapshot so later changes invalidate approval. No force flag may accidentally waive an integrity/restatement guard. Start-close/unlock are not completion of this workflow.
3. Expand remaining imports/mapping, connector, financial/planning/report/workflow endpoints; finish doc 90 as index and per-endpoint examples/schemas. Four new + seven prior metadata + three job transport sections are not the whole catalogue.
4. Resolve missing project persistence/lifecycle module ownership in the work plan before WI-0001 sign-off; do not put SQL or a second persistence implementation in routes. Current plan remains 267; no new module/task silently invented.
5. M1 still must implement doc-02 delta 14 and verify frozen calendar low-year padding. Real sample assets/pipeline, desktop ACL/instance handling and destructive-operation fault injection are unbuilt.

DECISIONS TAKEN: DEC-018, DEC-019 (auto). OWNER-ONLY ITEMS: none for this work. Existing Entra setup is needed only before a real tenant pilot. Continue WI-0001; do not start WI-0002 or WI-0008 or claim the 30-item batch done.
