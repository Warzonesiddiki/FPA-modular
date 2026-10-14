# WI-0001 continuation — 2026-10-14

**Status: in_progress. Batch target: WI-0001…0030, 0/30 complete. M0: 0/8 complete; gate open.**

This is a tested **documentation-contract checkpoint**, not a running API, job registry, engine acceptance verdict, or milestone audit. No later WI was started. The prior 73-code checkpoint remains historical at commit `8e40345`.

## 1. Baseline and scope

Session-start fetch/log and baseline were completed before DEC-016; the recorded baseline in TASKBOARD is `python -m pytest -q` → **9 passed in 0.12s**, following `8e40345`. Read AGENT_PROMPT in full, index §10, TASKBOARD and the WI's contracts (05/90/63/22/02), then relevant owning docs (06/07/12/19/23/26/29/30/38–41/48/62/64) for the API omissions encountered. M1 product code remains frozen.

Spec-first commit: `674dfb8` (`docs: 05/12/64 — define scoped API protocol and typed job contracts (DEC-016)`). It records the decision, alternatives and reversal cost before adding the schema/test deliverables.

Completed sub-scope:
- Doc 05 §1.2–1.4: launch-token + explicit project scope; exact Host/Origin; paging/cursors; durable idempotency; version guards; decimal-string finance boundaries; job states and cancel protocol.
- Doc 12 §1.1: root-only OAuth callback exception, 300-second single-use state tied to project/tenant/client/redirect/S256 PKCE; no exchange on rejected/replayed state; fixed HTML and redaction rules. No runtime security behaviour is claimed tested.
- Doc 22: ERR-006/007/008 (local token/origin/interruption); **76 codes**, preserving remote Microsoft error meanings. Repeated suggestion consumption uses ERR-046, not payload-collision ERR-005; queueing does not mark corrected until application/export (docs 07/19/23).
- Doc 64: **18 explicit job kinds**, safe cancellation stages, typed terminal results, child auto-commit semantics, failure envelopes, separate general Commentary versus AI-only draft result.
- `docs/api_job_schemas.json`: **207 named definitions**, closed state/kind result union, all **76 error shapes/flags**, money/decimal-string types, local-only references, examples for every done kind, receipt/page/cancel schemas. This is an authored normative schema attachment, not a generated runtime OpenAPI snapshot.
- Doc 05 §5: explicit job poll/list/cancel endpoint contracts, including request/auth/response/status/errors/pagination/idempotency/examples. Other endpoint groups are **not** yet complete.
- Docs 63/90: full commit/pull examples, consistent job-schema references, no obsolete independent result definitions; typed board-pack wrapper and paged drill direction. All input/remaining response constraints still need WI completion work.

No app, original unit tests, original integration tests, money formula, corpus bar or gate threshold changed. Extra files are explicitly authorised in the existing WI by DEC-016; no WI was added or reordered. Pinned verifier dependencies live under `tests/docs/requirements.txt`, documented in docs 60/81; they are not product runtime dependencies.

## 2. Red → green trail

### Initial oracle run (before schema existed)
Command: `python -m pytest tests/docs/test_api_job_contract.py -q`.

```text
AssertionError: WI-0001 typed job schema missing (contract not implemented)
61 errors in 0.48s
```

All were fixture assertions against the missing contract, **not import errors**. Independent result fixtures were authored from doc 64 before the schema; schema examples were then populated from those oracles, never used to generate the test expectations.

First schema run: **3 failed, 58 passed in 3.50s**. Two positive fixtures incorrectly marked running backup/restore cancellable; fixed to the owning doc's non-cancellable rule (did not relax the schema). Third was a malformed mutation (`allOf:[]` violates the metaschema); changed the mutation to remove the discriminator entirely, creating a valid-but-wrong schema and proving the same oracle catches the escaped cross-kind result. Restricted mutation exception expectations instead of catching arbitrary BaseException.

Further adversarial checks found and fixed:
- Money/ID/date/hash/path newline acceptance through regex `$`; reject CR/LF explicitly on wire primitives.
- Optional date-time format checker absent in the validator's minimal install; installed no hidden extra. Registered a standard-library datetime checker and added impossible-date/hour cases.
- Cancel-response boolean/state contradictions: test-first run **7 failed, 101 passed in 5.63s**; restricted to the six legal response variants. A cancelled backup/restore must never have started.
- Gregorian year 0000: test-first run **1 failed, 117 passed in 5.50s**; tightened PeriodId without changing accepted 0001/9999 and P01/P12 boundaries.
- A shared Commentary DTO accidentally restricted general reads to AI drafts: test-first run **1 failed, 119 passed in 5.78s**; separated general Commentary from AICommentaryDraft while retaining strict draft-only job results.

### Latest executed commands

```text
python -m pytest tests/docs/test_api_job_contract.py -q --tb=short
120 passed in 5.71s
python -m pytest -q --tb=short
129 passed in 6.06s
git diff --check
[exit 0, no output]
```

Clean dependency reproduction also executed:

```text
python -m venv .venv/doc-contract
.venv/doc-contract/bin/python -m pip install --index-url https://pypi.org/simple -r tests/docs/requirements.txt
[all pinned dependencies installed; Windows-only colorama correctly skipped on Linux]
.venv/doc-contract/bin/python -m pytest tests/docs/test_api_job_contract.py -q --tb=short
120 passed in 6.09s
```

This clean run was Linux/Python 3.11, not Windows certification or proof of the future Python 3.12 product package. The ignored environment is not committed. A direct text scan of the schema/test files found **zero `float(` calls**; manual review found only count/partition arithmetic, no financial computation.

The 129 tests comprise **120 document-contract tests + 9 unchanged nucleus tests**. They are not 129 product features. No `scripts/check.py` or bootstrap docs checker exists yet; neither was run or claimed green.

Plan repeat verification ran `python tools/generate_work_plan.py`, hashing WORK_PLAN.md/.csv before and after: **267 items, identical repeat output**. `git diff 8e40345 --name-only -- app tests/unit tests/integration`: **empty**. Schema-oracle repeats use fixed IDs/timestamps; no clocks, randomness or ERP calls.

## 3. Self-verification

### Mutations (isolated copies, always restored by construction)
The test `test_three_schema_mutations_are_caught` executes the same oracle helper against:
1. Money schema replaced by JSON number → expected decimal-string example rejected / numeric-money rejection assertion violated.
2. Progress maximum 100 → 101 → invalid 101 probe unexpectedly validates; test catches the missed rejection.
3. Remove done-job kind/result discriminator → forecast result on an import-commit job escapes; test catches the missed rejection.

No product/source file is temporarily mutated; negative controls operate on deep copies of the schema. Cross-kind matrix checks every independently authored result against the other 17 kinds.

### Highest-risk spec checks
- **Doc 22 §2 / doc 05 §1.1:** exactly 76 unique catalogue codes, exact transport mapping, actual ErrorBody variants and examples agree; retry flags match the catalogue and their inversions fail.
- **Docs 12 §1.1, 26 §8.4, 64 §3:** no credential fields in job shapes, validator refuses external schema references before resolver/socket use; no_change cannot carry batches/auto-commit jobs; skipped sources require a reason; incomplete counts and auto-commit-with-quarantine fail the semantic oracle. This does **not** prove future HTTP allow-list/redaction/runtime ownership code.
- **Docs 05 §1.3/§5, 64 §1–§3:** all 18 done results plus queued/running/failed/cancelled variants; every required envelope field; closed nested results; stage/cancellation guards; date/period boundaries; false audit/restore/diagnostics success and nonzero year-end delta rejected; board-pack shared snapshot/period and rule partition verified by independent semantic oracles.

### Edge checklist (document-contract scope only)
- Zero / negative money: string fixtures pass; numeric money rejected. Currency exponents 0/2/3 syntactically covered; fixed per-project precision remains API-adapter runtime validation (not claimed implemented).
- Zero denominators: nullable forecast metrics require an explicit reason via the oracle; no formula executed.
- Empty/single/250k input: validation **count** fixtures cover 0/1/250000 conservation; this is not a 250k-row performance test.
- Duplicates: unknown/duplicate reason/rule semantics and cross-kind payload probes; idempotency behaviour specified, not implemented.
- Missing optional data: explicit nulls/reasons; skipped sources and missing watermark differ from zero changes.
- Locked periods/versions, superseded imports, expired waivers, month-2 reuse: protocol and existing owner contracts cited; **runtime tests pending M1–M3**, no claim of behavioural coverage here.
- Hostile text: quoted/Unicode/script/formula text remains data; unknown fields rejected; path traversal/control-newline probes reject. UI/export escaping and log redaction remain runtime tests.
- Ambiguous dates/amounts: wire numeric/date syntax rejected; import locale inference/quarantine belongs to M2 and is not tested here.
- Determinism: fixed examples; repeated checks same verdict; generated work plan byte-identical. Schema validation never computes financial results.

## 4. Exact next work — still WI-0001
1. Expand every remaining compound route in doc 05 §2/§4 into explicit method/path sections (not just `CRUD`, method lists or path alternations). Inventory against doc 19 and M3 route WIs, including sample/delete/unlock, master suggestions, budget phasing, comments, planning/report/KPI builders and workflow endpoints currently only implied by FRs.
2. Define every request/response field, required/optional/null constraints, selector defaults, scope, version precondition, status/error-detail mapping and complete example for those endpoints. General protocol and job schemas are now reusable; they do not substitute for endpoint-specific contracts.
3. Finish doc 90 as an index, remove remaining shorthand/untyped fields and reconcile per-endpoint schemas. In particular drill/layer/source-row detail, settings values, report-builder expressions and entity/profile fields need full contracts; never implement by guessing from generic objects.
4. Complete doc 63 examples for every endpoint; create-project currently illustrates the request only. Preserve callback/foreground-vs-job and board-pack-result decisions already recorded.
5. Execute endpoint/schema/example coverage and relevant mutations. Only then mark WI-0001 done and make its completion commit. Do not advance to WI-0002 or bootstrap WI-0008 prematurely.

The requested 30-item batch remains queued behind this first item's evidence bar. No owner decision is pending. Existing Entra app registration is required before a real tenant pull, not for any of this work.
