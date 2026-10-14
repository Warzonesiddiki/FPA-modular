# WI-0001 — project/period contract checkpoint, 2026-10-14

**in_progress; 0/30 requested WIs complete; M0 open (0/8 done).** Seven more endpoint contracts are expanded, not seven completed work items. No HTTP server, project repository, financial engine or milestone gate is claimed implemented.

## Session recovery and baseline

- Fetched origin. The sandbox had HEAD `6cc5776` with the saved worktree, while the pushed session branch was `fc736ff`. Stayed on `arena/f906a206-fpa-modular`; `git reset --mixed origin/arena/f906a206-fpa-modular` reconciled metadata without replacing any working file. Status then clean. No hard reset or clean.
- Read AGENT_PROMPT, index §10, TASKBOARD, WI-0001 contract and relevant owning docs. First unfinished item remains WI-0001; no later item started.
- System `python -m pytest -q` failed because pytest was absent. System pip correctly refused an externally managed environment. Created ignored `.venv`; installed exact `tests/docs/requirements.txt` pins from PyPI, without overriding system protection.
- `.venv/bin/python -m pytest -q` baseline: **129 passed in 8.83s**.

## Contract and scope

Docs-first commit `221fc3d`, DEC-017 in doc 17 §4; creation-response clarification `e6ae4bf` preceded its schema definition. Doc 05 §6 now owns:

1. GET /health
2. GET /projects
3. POST /projects
4. GET /projects/{id}
5. GET /projects/{id}/periods
6. POST /projects/{id}/periods
7. GET /projects/{id}/periods/{period_id}

Each has auth/scope, request, response, status/errors, pagination, idempotency and examples. Doc 05 §6.0 merges field definitions previously abbreviated in doc 90; doc 90 is an index for this sub-scope. Project is bounded metadata, not an unbounded embedded period/close list. Initial FY is explicit; a full-year ensure creates exactly twelve periods or returns existing state without resetting locks. Reads never materialise data. Project creation receipts are installation-scoped and durable, with deleted-target handling rather than resurrection.

Doc 27's seven previously enumerated currencies are now an explicit v1 code/exponent registry (INR/USD/EUR/GBP/AED=2, JPY=0, KWD=3); unlisted codes are rejected, never assumed two-decimal. Extensions need a reviewed registry entry/test. No rate, financial formula or amount rounding changed.

The attachment adds **16 definitions**, now **223 total**, plus a seven-endpoint metadata catalogue. The **18 jobs and 76 errors** remain unchanged. General Project reads allow samples/later revisions; CreatedProject restricts create results to non-sample/version 1. Cross-property equality, NFC, ownership, FY/calendar consistency and transactional behaviour remain explicit adapter/repository obligations, not capabilities falsely attributed to JSON Schema.

Doc 02 §1 already required revision metadata but explicit project/period columns omitted it. Delta 14 records the M1 migration obligation; **frozen SQL was not edited**. M1 gate wording was extended consistently to include that delta, with no existing requirement removed. Doc 19's 4-4-5 wording is aligned to doc 27's existing monthly-only v1 policy. Docs 18/63 now show an explicit FY start year. Legacy lock/backup/restore input summaries remain visibly incomplete, not silently removed or represented as finished.

## Test-first execution trail

Paired test: `tests/docs/test_api_project_contract.py`, authorised in DEC-017 and the generated WI-0001 test field. Fixtures are independent literal field/calendar oracles, not generated from the schema or product code. The cookbook uses those independently specified values.

1. Before the schema extension: `.venv/bin/python -m pytest tests/docs/test_api_project_contract.py -q --tb=short` → **68 errors in 0.81s**, all explicit fixture assertions `DEC-017 project contract definitions missing`, not import errors.
2. First schema run → **1 failed, 67 passed in 1.21s**. The error-map extractor included a sentence saying ERR-012 must *not* be used in a 503 list. Moved that negative distinction to its own labelled bullet; no status or test expectation weakened. Then **68 passed in 1.23s**, full **197 passed in 9.63s**.
3. Creation-specific response regression → **1 failed, 73 passed in 1.35s** (`Creation-specific response contract missing`). Spec/definition now distinguish CreatedProject from the general read model.
4. Review caught a legacy locked-pull HTTP example missing the mandatory project header: **1 failed, 76 passed in 1.32s**. Fixed the example to include matching X-FPA-Project and the required Idempotency-Key; regression asserts both. It previously could not honestly illustrate the documented request.

Latest executed commands:

```text
.venv/bin/python -m pytest tests/docs/test_api_project_contract.py -q --tb=short
77 passed in 1.31s
.venv/bin/python -m pytest tests/docs -q --tb=short
197 passed in 9.46s
.venv/bin/python -m pytest -q --tb=short
206 passed in 9.78s
git diff --check
[exit 0, no output]
```

The full total is **77 new project-document tests + 120 prior job-document tests + 9 unchanged product tests**. Repeated runs passed throughout the green checkpoints; fixed IDs/timestamps and hand-written FY2027 dates require no clock/random/network. Neither docs checker nor scripts/check.py exists yet; no checker/cold-audit pass is claimed.

## Self-verification

### Three caught schema mutations
`test_three_project_schema_mutations_are_caught` runs the same `assert_project_oracles` helper on isolated deep copies:
- Allow unknown ProjectCreate fields → server-controlled is_sample escapes; rejection assertion fails.
- Remove Project currency/exponent conditional → JPY with exponent 2 escapes; rejection assertion fails.
- Increase full-year creation maximum 9998→9999 → upper-bound rejection assertion fails.

Only the expected assertion failures are caught; no repository file is temporarily mutated. Existing three job-schema mutation probes also remain green.

### Three high-risk checks
- **Docs 05 §6.3, 02 §2, 27 §1:** requests cannot set sample flag/id/exponent/path/revision/timestamps; all seven currencies and incorrect exponent combinations exercised; owner currency table equals schema set; created response restrictions do not reject legitimate general sample/later-version reads.
- **Docs 05 §6.5–§6.7 / 02 period identity:** zero-padded FY0001; FY9998 ending March9999; January/December FY starts; handwritten leap-February2028; twelve ordered periods; wrong project/FY/identity, partial/duplicate/reordered periods, invalid calendar dates and invalid lock metadata detected by schema and independent relational oracles. Actual non-reset/atomicity behaviour awaits M1/M3.
- **Docs 05 §1/§6 and 22 §2:** exactly seven explicit methods/paths match schema metadata; response/query/request names and idempotency/scope flags match independent expectations; every listed error agrees with the global HTTP mapping and validates its typed error body. Token requirement checked as contract metadata, **not runtime auth enforcement**.

### Edge checklist
- Zero/negative money/credit-normal accounts: N/A to new metadata DTOs; original money-string tests still pass. Currency exponents 0/2/3: PASS, no financial arithmetic.
- Empty/single/duplicate inputs: PASS for pages, missing fields and duplicate/partial FY payloads. Duplicate JSON/query members are forbidden in the owning contract; real raw-request parsing and name uniqueness need M3 tests.
- 250k rows: no transaction data exposed; pages capped at 1000 and FY action at 12. Schema cap probes pass; no throughput/performance claim.
- Optional data: explicit null cursors/lock metadata, optional query filters and defaults tested.
- Locked periods/versions: legal read shapes and illegal lock-field combinations tested; preventing changes/reset/stale writes remains runtime work.
- Superseded batches, expired waivers: N/A to metadata reads; later period-lock/restatement/import contracts remain unfinished.
- Hostile text: Unicode/script/formula text preserved as literal data; controls, blank/oversized/non-trimmed names rejected; NFC checked by a relational oracle. UI escaping, filesystem safety and SQL parameterisation are not implemented here.
- Ambiguous dates: malformed/impossible Gregorian dates and out-of-range FY rejected. Amount parsing N/A.
- Month-2/year rollover: FY2027 spans 2027–2028; independent year-boundary/least/greatest creation-year cases pass; no server-clock-derived year.
- Determinism: generator repeat hashes identical; fixed document oracles. No artifact/financial-engine determinism claim.

### Scope, plan and money checks
Executed assertions: **267/267 WI id/path identities unchanged; new paired test declared; 7/7 gate texts equal; both generated plan files repeat-identical; frozen app/unit/integration diff against fc736ff empty; 223 definitions / 18 kinds / 76 errors; zero `float(` calls in changed schema/new tests**. Manual review: only calendar/count/metadata comparisons, no financial computation. Changes outside doc 05 are its authorised attachment/tests, owning/repeating docs, generator/gates, and handover evidence; no product code or original tests changed.

## Exact continuation — still WI-0001

1. Finish project sample/delete/backup/restore and period start-close/lock/unlock contracts. Preserve typed confirmation + 30-day trash, secret exclusion and restore verification. Resolve doc 30 sign-off/lock dependencies and doc 41 impact-review attestation without circular T-09/T-10 prerequisites or weakening guards.
2. Expand imports/mapping, connector foreground actions, and all remaining §2/§4 route families; every endpoint still needs explicit constraints/status/details/example, not CRUD/path alternatives.
3. Complete doc 90's remaining index conversion and per-endpoint example/schema coverage. Seven new + three prior job-transport sections do not close the full inventory.
4. Reconcile FR-PRJ's referenced project_repo ownership with the plan before final route coverage sign-off (there is no dedicated project_repo WI); do not invent a second persistence module in routes. M1 must also verify four-digit low-year formatting in frozen calendar.py (its current f-string does not pad FY0001).
5. Re-run the full coverage/mutation review before marking WI-0001 done. Do not start WI-0002 or WI-0008 yet.

DECISIONS TAKEN: DEC-017 (auto). OWNER-ONLY ITEMS: none for this work; the existing Entra registration requirement applies only before a real tenant pilot.
