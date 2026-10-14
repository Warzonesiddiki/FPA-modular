# WI-0001 — API contract hardening (historical checkpoint before DEC-016)

> The 73-code checks below describe commit 8e40345 and are retained as executed history. Current continuation, 76-code/job schemas, tests and remaining work: `evidence/WI-0001_job_contract_2026-10-14.md` and TASKBOARD. Do not run the historical inline verifier against a newer contract and treat that as a current gate.

This is a partial review and verification record, **not** a completion or M0 gate verdict. Baseline read: docs 05, 90, 63, 22, 02 in full; connector/security/state/job owners docs 26 §8, 12 §1/§5/§8, 23 and 64; doc 07 §7. Product code remains frozen.

## 1. Contract written down
- Input: existing endpoint/payload catalogue (docs 05/90), normative examples (63), all catalogue errors (22), storage types and identities (02).
- Deliverable: one explicit contract per method/path: auth, request and response fields/types/requiredness/defaults/constraints, success/failure status and error details, pagination, idempotency, complete example (WI-0001 acceptance).
- Money: JSON decimal strings in major units, converted only by money.py; `*_minor` storage fields must not leak as numeric monetary response fields (05 introduction, 02 §1, 90).
- Scope: project ownership applies to resource-id routes; foreign ids must fail without cross-project disclosure (05 §1). Connector is a read-only file producer, with keyring-only secrets and local lock preflight (26 §8, 12, DEC-015).
- Jobs: discriminated terminal results for **every** asynchronous operation, including `connector-pull` and `connector-check-changes`; cancellation, failures and retention must match 23/64, not just a generic object.

## 2. Completed sub-scope (DEC-015)
The previous HTTP line mapped 45 of doc 22's 73 codes. A first naive regex counted only 9 because it did not expand slash shorthand; that result was discarded. Recomputed by expanding `ERR-002/005/...`: **28 omissions**, not 64:

`ERR-004 ERR-012 ERR-013 ERR-014 ERR-015 ERR-029 ERR-030 ERR-031 ERR-032 ERR-044 ERR-046 ERR-052 ERR-061 ERR-062 ERR-071 ERR-073 ERR-085 ERR-090 ERR-091 ERR-110 ERR-111 ERR-112 ERR-113 ERR-114 ERR-115 ERR-116 ERR-117 ERR-118`.

Doc 05 §1.1 now maps all 73 once (72 synchronous + cancelled-job-only ERR-004), retaining the previous 45 statuses. Docs 05/23/26 now agree that a locked connector target is ERR-027/423, not ERR-030, and is rejected after ownership checks but before job/network/writes. Doc 90 references this transport mapping and monetary error-detail rule. No endpoint implementation exists or is claimed tested.

## 3. Reproducible partial checks
Run from repository root:

`python -c 'from pathlib import Path; exec(Path("evidence/WI-0001_api_contract_review.md").read_text().split("```python\n", 1)[1].split("\n```", 1)[0])'`

```python
from collections import Counter
from pathlib import Path
import json
import re
import subprocess

api = Path("docs/05_API_CONTRACT.md").read_text()
state = Path("docs/23_STATE_MACHINES_AND_WORKFLOWS.md").read_text()
connector = Path("docs/26_INTEGRATIONS_AND_ERP_FIELD_GUIDES.md").read_text()
catalogue = set(re.findall(r"^\| (ERR-\d{3}) \|", Path("docs/22_ERROR_CATALOG.md").read_text(), re.M))
assert len(catalogue) == 73
old = subprocess.check_output(["git", "show", "6cc5776:docs/05_API_CONTRACT.md"], text=True)
old_line = next(line for line in old.splitlines() if line.startswith("**HTTP status"))
old_map = {}
for status, codes in re.findall(r"`(\d{3})` (ERR-\d{3}(?:/\d{3})*)", old_line):
    for number in codes.removeprefix("ERR-").split("/"):
        old_map["ERR-" + number] = status
assert len(old_map) == 45

def verify(text, state_text):
    mapping = {}
    seen = Counter()
    for line in text.splitlines():
        match = re.match(r"\| (\d{3}|Job error only) \| ([^|]+) \|", line)
        if match:
            for code in re.findall(r"ERR-\d{3}", match[2]):
                seen[code] += 1
                mapping[code] = match[1]
    assert set(seen) == catalogue, "code-set mismatch"
    assert all(count == 1 for count in seen.values()), "duplicate mapping"
    assert all(mapping[code] == status for code, status in old_map.items()), "old status changed"
    assert mapping["ERR-004"] == "Job error only"
    assert mapping["ERR-027"] == "423" and mapping["ERR-030"] == "422"
    assert mapping["ERR-046"] == "422" and mapping["ERR-115"] == "503"
    assert "ERR-027 period locked" in text
    assert "period is locked (ERR-027;" in state_text, "connector lock code drift"
    assert "period is locked (ERR-030)" not in state_text
    return mapping

mapping = verify(api, state)
assert "reject a locked target period with ERR-027 before creating a job" in connector
example = json.loads(api.split("```json\n", 1)[1].split("```", 1)[0])
assert set(example) == {"code", "message", "hint", "retryable", "details"}
assert example["code"] == "FP&A-ERR-027" and example["retryable"] is False
assert example["details"] == {"period_id": "2025-P07"}
print("PASS: 73/73 codes exactly once; 45/45 previous statuses retained; 72 synchronous + 1 job-only.")
print("PASS: ERR-027 lock guard agrees across docs 05/23/26; ERR-046=422, ERR-115=503; example parses.")
mutations = [
    ("remove ERR-118", api.replace("ERR-118 |", "|", 1), state, "code-set mismatch"),
    ("duplicate ERR-030", api.replace("ERR-030,", "ERR-030, ERR-030,", 1), state, "duplicate mapping"),
    ("restore wrong connector lock code", api, state.replace("period is locked (ERR-027;", "period is locked (ERR-030;", 1), "connector lock code drift"),
]
for label, changed_api, changed_state, expected in mutations:
    assert changed_api != api or changed_state != state
    try:
        verify(changed_api, changed_state)
    except AssertionError as error:
        assert str(error) == expected, (label, str(error))
        print("CAUGHT: " + label + " -> " + expected)
    else:
        raise AssertionError("mutation escaped: " + label)
print("PASS: 3/3 isolated document mutations caught; repository documents were not mutated.")
```

Executed twice after correcting the extraction delimiter (first attempt split on triple backticks **inside** a Python string and raised a SyntaxError; no check passed on that attempt). Both corrected runs produced identical output:

```text
PASS: 73/73 codes exactly once; 45/45 previous statuses retained; 72 synchronous + 1 job-only.
PASS: ERR-027 lock guard agrees across docs 05/23/26; ERR-046=422, ERR-115=503; example parses.
CAUGHT: remove ERR-118 -> code-set mismatch
CAUGHT: duplicate ERR-030 -> duplicate mapping
CAUGHT: restore wrong connector lock code -> connector lock code drift
PASS: 3/3 isolated document mutations caught; repository documents were not mutated.
```

`python -m pytest -q` → **9 passed in 0.12s**. `git diff --check` → exit 0. No API server, OpenAPI or full docs checker exists yet, so none was reported tested.

## 4. Remaining acceptance work — resume here, not at WI-0002
1. **Endpoint inventory and expansion:** doc 05 §2/§4 still has compound `CRUD`, `GET/POST/PUT`, `approve|lock|copy`, grid-selector and master-selector entries. Expand into explicit method/path sections and compare to consuming FRs (doc 19) and route work items. Do not infer unspecified delete/update/detail paths in implementation.
2. **Auth/project scope:** doc 12 requires `X-FPA-Token` on every request, while the browser OAuth callback cannot supply it; doc 05 says all paths use `/api/v1`, but docs 26/63 specify root `/connector/callback`. Resolve the callback's narrow state/PKCE-bound exception in owning docs before routes. Header-less routes such as `/mapping-profiles`, `/driver-values`, `/exceptions/bulk-assign`, `/close/sign-off` also need an explicit project context. Local API-token/origin HTTP failures remain unspecified; ERR-111/117 are remote identity errors, not substitutes.
3. **Jobs:** doc 64's table has nine rows (one is `backup/restore`), but doc 05 also makes enrichment, allocation, reconciliation, planning integration, year-end, diagnostics and report render asynchronous or insufficiently explicit. Reconcile the catalogue, initiation statuses and per-kind result schemas across 05/90/64; define nullability and discriminators. Crash interruption has no fully typed error details yet.
4. **Money/payload drift:** doc 05 TB-check returns numeric `erp_minor/app_minor/delta_minor`; doc 90 has `amount_minor` internal-test fields and `CheckResult.delta_minor` / `rollforward_delta_minor` despite the public money-string invariant. Translate at the public boundary, preserving integer storage ownership. Doc 90 drill uses `vouchers` whereas doc 63 pagination uses `items`; statement fields differ (`presentation_sign` vs `is_calc`); schemas/complete examples must converge.
5. **Connector DTOs:** doc 63 entity-check failure is a `200` result but doc 05 lists ERR-114; candidate nesting differs in 05/90; progress metadata and optional-source `row_counts.note` in doc 63 are not typed in doc 90. `no_change`, staged/validated batches and auto-commit need explicit result variants; no tokens in responses/logs/jobs. Check all against 26 §8 and 12.
6. **Workflow coverage:** tie every mutable endpoint to doc 23 guards/audit/version/idempotency semantics; fill pagination ordering, cursor scope/invalid cursor behaviour, full field constraints and every per-endpoint error `details` schema. Suggestion repeat-consumption currently cites ERR-005 although its catalogue trigger is a different-payload idempotency-key reuse; resolve via owning docs, do not silently reuse it.
7. **Verification:** current checks only prove the completed error/lock sub-scope. Finish the full catalogue and schema index before a WI completion commit. Run document checks/mutations across endpoints, examples, jobs, money, ownership and selectors. Bootstrap `scripts/docs_check.py` remains queued at WI-0008; no full docs-gate pass exists yet.

No remaining issue above is declared resolved. They are documented stopping-state defects for the **same in-progress WI**, not permission to implement around the spec. M0 remains open and WI-0002 must not start.

## 5. Baseline negative control
After the partial rewrite, the same verifier was also invoked with doc 05 from `git show 6cc5776:docs/05_API_CONTRACT.md` (not with the current document). It failed the first code-set equality assertion as expected:

```text
BASELINE RED: 6cc5776 doc 05 fails code-set equality (expected).
```

This is a retrospective negative control for the document check, not a claim that runtime tests were written or run before implementation. No product implementation was made.
