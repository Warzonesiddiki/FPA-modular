# 06 — IMPORT & SOURCE-MAPPING SPECIFICATION

> Owner of: file → trustworthy gl_rows. Principles P12 (all-or-nothing), P13 (nothing silently discarded), P18 (hostile content).

## 1. Supported inputs
CSV/TSV (encoding: UTF-8/BOM, UTF-16, Latin-1 detected; delimiter sniffed `, ; \t |`), XLSX (openpyxl read-only; every sheet listed in the import report — used or explicitly skipped by the analyst, never silently). Max 200 MB/file, 1M rows/file (ERR-021 beyond). Unsafe files (decompression ratio > 100:1, path traversal in member names, macros, external links) → ERR-029 before any parsing (doc 12 §4). Source kinds: `gl`, `budget`, `subledger` (bank/payroll/AP-AR extracts landing in the same GL shape), `drivers`, `opening` (opening BS balances). Formula cells: cached value used and flagged `formula_cells:N` in the report; missing cached value → quarantined row with reason.

## 2. Pipeline (each stage persisted; resumable; UI = S03 wizard)
1. **Stage:** file copied to `imports/<sha256>.<ext>`, batch created, raw rows stored verbatim (`import_rows_raw`) with sheet + 1-based row number.
2. **Profile:** per column — guessed type, null %, distinct count, 5 sample values (samples are data, rendered escaped).
3. **Map:** saved profile auto-applies on header match ≥ threshold; else deterministic suggestions (normalised header similarity against canonical names/synonyms, e.g. `Amt`, `Value`, `₹` → amount) ranked with confidence; analyst confirms. AI suggestion (doc 11) may reorder, never auto-apply. Mapping profiles are versioned; month-2 reuse is the default path (P11).
4. **Transform:** debit/credit column pairs → signed amount; `sign_flip` for credit-normal extracts; dates parsed against the profile's declared format(s) — ambiguous dates (both dd/mm and mm/dd plausible) quarantined, never guessed; amounts parsed via money.py (thousands separators, parentheses-negatives, currency symbols stripped and recorded).
5. **Validate (per row; batch → `validated` when the stage completes with zero blocking issues — quarantined rows do not block, missing required mappings and ERR-023 do):** required canonical fields present; account/entity codes resolve to master data (unknown → quarantine with "add to master data?" action that creates + remaps in one flow); posting_date inside the batch period ± cut-off window setting; voucher balance check queued for commit stage. Output: valid set + quarantine set, counts reconcile exactly: `in = valid + quarantined` — displayed everywhere the batch is shown.
6. **Control totals:** analyst may enter (or file may carry) declared row count / debit total / credit total; mismatch vs staged = ERR-023, commit blocked, staging kept.
7. **Commit (atomic):** one transaction — gl_rows inserted in batches of 1,000 (multi-row INSERT; attempt #4 DEF-030: no row-by-row), master-data additions, batch status, audit. Crash/kill mid-commit → transaction rolls back, batch stays `validated` — the state it entered commit from (doc 23 §2); an integration test kills the process mid-commit and asserts zero `gl_rows` for the batch and status `validated`. Re-import of the same file hash for the same period → previous batch `superseded`, replaced atomically; row count after must equal new file, never double (idempotency test).
8. **Trial-balance gate:** per entity debit = −credit (doc 03 §2). Failure = ERR-024 with account-level drill; statements/BvA screens show a blocking banner until balanced or owner-waived (audited note).

## 3. Deterministic identity
`gl_row_id = SHA256(batch_id + "|" + sheet + "|" + row_no)` truncated 32 hex. `batch_id = bat_ + SHA256(file_sha256 + period_id + source_kind)[:12]`. Same file + period → same batch → re-import replaces, never duplicates.

## 4. Quarantine reasons (closed list; UI groups by these)
`MISSING_REQUIRED`, `BAD_DATE`, `AMBIGUOUS_DATE`, `BAD_AMOUNT`, `UNKNOWN_ACCOUNT`, `UNKNOWN_ENTITY`, `UNKNOWN_COST_CENTRE`, `UNKNOWN_VENDOR` (only when the profile maps the column and the setting `import.require_known_vendor` is on; default off → vendor stored as text label), `OUT_OF_PERIOD`, `NO_CACHED_FORMULA_VALUE`, `DUPLICATE_ROW_IN_FILE` (exact-hash dupes flagged, kept once), `EMPTY_ROW` (counted, not stored). Row-level problems are quarantine reasons, never ERR codes (doc 22 §3). Each carries a plain-language explanation + the fix action (doc 13 copy).

## 5. Duplicate & overlap handling
Within-file exact duplicates: flagged, analyst chooses keep-one (default) / keep-all (audited). Cross-batch overlap (same voucher+account+amount+date in a committed batch): not blocked — surfaced to EXC-002 at rule stage, since legitimate corrections exist. The import report shows overlap counts before commit so the analyst decides informed.

## 6. Performance posture
Streaming parse (no whole-file DOM); 250k-row GL commit ≤ 60s on doc-14 reference profile; profiler samples first 5k rows for stats but validates all rows.

## 7. Fixtures owned here
Coherent corpus + malformed corpus (≥10 files: bad encoding, missing column, ambiguous dates, unbalanced voucher file, duplicate file, formula-without-cache XLSX, 0-byte, wrong-delimiter, parentheses-negatives, mixed sign conventions) each with `expected.json` (counts by quarantine reason). Generator spec: MASTER_PLAN §6 — one plan, controlled noise, plants only from answer key, computed balancing legs, fixed seed, byte-identical regeneration hash-tested.
