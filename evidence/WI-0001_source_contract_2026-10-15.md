# WI-0001 — retained source codec / PR checkpoint

**in_progress**: M0 0/8; requested batch 0/30. User interrupted continuation to request a pull request; no later WI or product implementation started.

## Contract and docs-first changes
DEC-024 (auto), docs 02 §5.2 / 24 §6 / 05 §11.1: closed retained GL/adjustment contents, authentic file/generated origin, immutable project-scoped content addressing, strict versioned canonical JSON. Connector batch content identity is distinct from workbook byte identity. Integer minor units stay internal; the public money-string attachment is unchanged.

Docs-first commits: `62e235b`, `38bc085`. The M1 gate explicitly retains deltas 1–16 and requires delta 17; no existing document test was edited. Existing core/hashing and report_repo receive future ownership obligations, not runtime implementations. There are 15 internal definitions (7 mirrored primitives, 2 scalar types, 6 row/origin/record shapes); public attachment remains 285 definitions, 18 jobs and 76 error codes.

## Executed verification
- Baseline at a082578: `.venv/bin/python -m pytest -q` → **867 passed in 20.91s**.
- New paired test before schema: `.venv/bin/python -m pytest tests/docs/test_api_source_contract.py -q --tb=short` → **35 passed, 108 errors in 0.91s**, assertion `DEC-024 retained source schema missing`, not import failure.
- Initial schema: paired → **143 passed in 0.45s**.
- Expanded edge checks: **1 failed, 165 passed in 0.55s**; the test's SQL-column extractor omitted digits in `content_sha256`. Corrected the extractor to `[a-z_][a-z_0-9]*`, without changing the expected columns or schema.
- Final paired → **166 passed in 0.50s**; fresh PR-preparation repeat → **166 passed in 0.52s**.
- `.venv/bin/python -m pytest tests/docs -q --tb=short` → **1024 passed in 21.32s**.
- `.venv/bin/python -m pytest -q --tb=short` → **1033 passed in 21.04s**; fresh repeat → **1033 passed in 20.51s**.
- One-off scope probe initially had a Python parenthesis typo, then was corrected and executed successfully: app/SQL/all prior tests/public schema byte-unchanged from a082578; 267 plan identities and dependencies unchanged; generator regeneration byte-identical; all seven gate strings equal doc 86.
- `git diff --check`: clean before commit.

### Mutations and high-risk checks
`test_three_mutations_caught` uses the same independent oracles on isolated schema copies: codec constant v1→v0 rejects valid images; dropping the non-null vendor's source conjunct accepts an invalid fixture and fails the oracle; source_row minimum 1→2 rejects the first-row fixture. All three caught; original schema remains green. Additional byte-vector probes cover wrong domain prefix, ASCII-escaped Unicode and row-number offset. No product/runtime mutation is claimed.

1. **02 §5.2:** every GL/adjustment field required; kind/codec pairing, int64 bounds, vendor attribution, nullable FX reference preservation, generated-opening restriction and author/reason/version checks.
2. **24 §6.1:** exact UTF-8/control escaping/Unicode scalar key order; duplicate and escaped-equivalent keys, float/exponent tokens, non-finite values, BOM, malformed Unicode and noncanonical bytes reject in a pure reference model. JSON Schema alone does not reject every lexical or cross-field defect. Complete-image vector fixed before schema: `31673f761383c6aae3af28c7dae684fe4a5ab16af3b7f22ae0a7f49647ecd937`.
3. **24 §§6.2–6.3:** synthetic historical lookup refuses missing/corrupt files, wrong scope/membership, byte-length/hash/id mismatch and missing generated-run provenance. Same source id supports multiple immutable images; identical hash replay compares every scalar and payload. These are map/byte models, not SQL, authenticated HTTP or filesystem recovery tests.

## Edge / scope / money checklist
- Zero/negative/min/max amounts: internal integer layout tested; zero denominators and credit-normal financial calculations N/A.
- Empty/single/duplicate: missing required fields reject; one-row image/vector; duplicate immutable map insertion tested. 250k-row throughput **not tested**; no giant ledger fixture or performance claim.
- Missing optional source fields: explicit nulls preserved, never fabricated FX/date values. Live rule not_run behavior outside this slice.
- Locked/superseded: historical images survive synthetic enrichment/status changes; actual locking and batch publication unbuilt. Waiver expiry N/A to row encoding; earlier tests retained.
- Hostile text: literal quotes/formulas/markup, controls, Unicode and 10k/10k+ descriptions preserved as data; display filename never selects a file in the lookup model. Not browser/SQL/security implementation evidence.
- Ambiguous dates/amounts: date schemas and decimal-string syntax tested; original posted_at remains source text. No import parser or timezone conversion implemented.
- Currency exponents 0/2/3: N/A to internal minor-unit retention; no monetary conversion added. Nullable reference currency/FX columns tested.
- Month-2/prior-period inputs: own period ids retained, no current-period substitution.
- Determinism: paired/full repeated; literal byte/digest vectors and byte-identical plan regeneration.
- Money grep (`float\(|Decimal\(|amount_minor[[:space:]]*[+*/=-]`) found only fixture/keyword assignments, no conversion or financial arithmetic. Fractional/non-finite values occur solely in rejection tests.
- All new fields/types derive from owning docs before schema; public attachment and all earlier tests unchanged. No new endpoint, error or job. Separate internal attachment preserves rather than relaxes the public `_minor` ban.

## Unfinished scope / exact continuation
Still WI-0001. Complete snapshot membership and immutable file catalogue/publication (including exact connector bytes), full manifests/master/mapping/AP-enrichment lineage, retained financial views and finding business-state codecs; exact statement/viewer/layer fingerprint and authentic legacy repair; lifecycle/receipt coordinator and control-plane schema; bounded backup/restore with WAL consistency, validation, external restore epochs and pre-restore preservation. Then remaining endpoint families, annual planning and doc-90 index migration. A row image is not a complete reproducible snapshot or authorization token. Product code/SQL remain frozen until M0 closes.

DECISIONS TAKEN: DEC-024 (auto) · OWNER-ONLY ITEMS: none for this scope · NEXT WI: WI-0001 (continue).
