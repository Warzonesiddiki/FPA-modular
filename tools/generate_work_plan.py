#!/usr/bin/env python3
"""
Generate the single-agent WORK PLAN for FPA-modular.

Run:  python tools/generate_work_plan.py
Outputs (generated — never hand-edit; edit this file and re-run):
  docs/WORK_PLAN.md     one sequenced plan: milestones -> work items (WI-####), each with
                        mission, dependencies, inputs/outputs, acceptance criteria, paired test, notes
  docs/WORK_PLAN.csv    machine-readable mirror (id, path, layer, milestone, depends_on WI ids, read_first, tests)
  TASKBOARD.md          created ONLY if missing (it is the agent's live ledger afterwards)

Execution model (DEC-007, docs/17 §4): ONE agent builds everything, in WORK_PLAN order, following
AGENT_PROMPT.md at the repo root. A work item (WI) = one deliverable file + its paired test.
The per-agent prompt packets of the earlier 500-agent model were deleted; their content lives here.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS: list[dict] = []  # path, layer, purpose, deps, inputs, outputs, acceptance, tests, notes


def add(path, layer, purpose, deps="", inputs="", outputs="", acceptance="", tests="", notes=""):
    ITEMS.append(dict(path=path, layer=layer, purpose=purpose, deps=deps, inputs=inputs, outputs=outputs,
                      acceptance=acceptance, tests=tests, notes=notes))


# =====================================================================================
# M0 — SPEC HARDENING (docs + docs-only verification tooling; the P0/P1 gaps of audit/BRUTAL_AUDIT_PASS3_2026-10-14.md)
# =====================================================================================
add("docs/05_API_CONTRACT.md", "docs0",
    "Rewrite to OpenAPI-grade: every endpoint with method, path, auth, request schema, response schema, status codes (200/201/202/204/400/404/409/422), error codes, pagination, idempotency, example. Merge doc 90 field tables into per-endpoint sections (doc 90 stays as the schema index).",
    "docs/05 (current), docs/90, docs/63, docs/22, docs/02", "current tables", "complete endpoint catalogue",
    "Every route file in M3 can be written without inventing a field; a parity script (M6) diffs OpenAPI against the catalogue with zero gaps; `/jobs/{id}` result schema defined per job kind (import, rules, forecast, export, allocation, reconcile, year-end).",
    "tests/docs/test_api_job_contract.py; tests/docs/test_api_project_contract.py; tests/docs/test_api_lifecycle_contract.py; tests/docs/test_api_close_contract.py", "Audit pass-3 finding P0-8. Keep the 'money is a decimal string' rule in every schema. DEC-016: docs/api_job_schemas.json is the normative job-schema attachment, with document-only tests (test_api_job_contract.py, DEC-017 test_api_project_contract.py DEC-018 test_api_lifecycle_contract.py and DEC-020 test_api_close_contract.py) and tests/docs/requirements.txt (pinned verification dependencies, docs 60/81); product code stays frozen. Full endpoint rewrite still required.")
add("docs/21_SCREEN_SPEC_DETAILED.md", "docs0",
    "Expand from one table row per screen to one section per screen S01–S19: route, layout zones (doc 54), every field with source DTO path (doc 05/90), every action with API call + success/failure copy key (doc 55), validations, the five states, keyboard map (doc 57), drill paths, acceptance tests.",
    "docs/21, docs/13, docs/53, docs/54, docs/57, docs/05, docs/90", "current table", "19 implementable screen specs",
    "A UI work item in M4 can be built from its section alone; every DTO field shown is named; every string has a doc-55 key; no 'etc.'.",
    "-", "Audit pass-3 finding P0-11. Copy keys are *declared* here and *defined* in doc 55 (which depends on this item). Doc 13 §1 navigation rail already fixed in pass 3.")
add("docs/44_RULE_ALGORITHMS_DETAILED.md", "docs0",
    "Per rule EXC-001…028: parameter table (setting key, type, default, range), full pseudocode (SCOPE/GROUP/TEST/EMIT), lookback + insufficient-history behaviour (fires / not_run), 'spend', 'manual journal', 'vendor' and 'narration token' definitions used, evidence_json schema, grain_key derivation, boundary matrix values, false-positive design notes; suggestion derivations (doc 07 §7.3 data-dependent parts) per rule.",
    "docs/44, docs/07, docs/42 §7, docs/62", "current one-liners", "28 implementable rule algorithms + suggestion derivations",
    "Two independent readers produce identical findings on the doc-42 plant register from the text alone; every parameter has a doc-62 key; every rule states its not_run conditions.",
    "-", "Audit pass-3 finding P1-7.")
add("docs/03_CALCULATION_SPEC.md", "docs0",
    "Deepen: BS opening-balance and retained-earnings roll (link doc 38), CF classification table (statement_line → operating/investing/financing + sign), KPI balance basis (closing vs average) and annualisation, YTD/PY phasing rules with oracles, display-rounding algorithm statement matching money.py.",
    "docs/03, docs/45, docs/38, docs/43, docs/89", "current spec", "complete calc contract",
    "Every statement/KPI oracle in doc 89 is derivable from this doc by hand; no formula lives only in code.",
    "-", "Audit pass-3 findings P1-1..P1-4 (partially closed in pass 3; this item finishes it).")
add("docs/55_COPY_AND_MICROCOPY_CATALOG.md", "docs0",
    "Complete string catalogue: every button, title, empty/error/partial state, tooltip, confirm dialog, toast and export label for S01–S19 + Excel/PPT/PDF labels, keyed (`screen.element.state`), with the doc-22 error mapping.",
    "docs/55, docs/21, docs/22, docs/13", "current partial list", "complete keyed catalogue",
    "Mechanical check possible: every key referenced by a doc-21 screen section exists here; no inline strings allowed in UI code (M4 lint).",
    "-", "Audit pass-3 finding P1-12.")
add("docs/31_GLOSSARY.md", "docs0",
    "Expand to the ~120 domain + product terms actually used across docs (finance: accrual, cut-off, suspense, reclass, NBV, DSO…; product: batch, layer, finding key, plant, control, oracle, milestone, WI). One definition each, cross-referenced to the owning doc.",
    "docs/31, all docs", "current ~30 terms", "complete glossary", "Every capitalised product term in docs 01–91 appears here (script-checked in M6 docs gate).", "-", "")
add("docs/20_TRACEABILITY_MATRIX.md", "docs0",
    "Convert from family-level to FR-level: one row per FR in doc 19 (statement → spec § → screen → endpoint → WI → test → acceptance evidence).",
    "docs/19, docs/20, docs/05, docs/21, docs/WORK_PLAN.md", "doc 19 FR register", "FR-level matrix", "Zero empty cells for v1 FRs; script in M6 regenerates and diffs.", "-", "Audit pass-3 finding P0-4 (FR register rebuilt in pass 3; matrix follows).")

# DEC-014: the M0 exit check must be buildable before the M0 gate; no product imports.
add("scripts/docs_check.py", "docs0",
    "Bootstrap documentation gate using only the Python standard library; section/ID/doc-section-reference/link checks plus ERR/FR/settings-key reference parity against docs 22/19/62. Validate doc 20 FR-to-WI-to-planned-test coverage, period notation, retired operational terminology and milestone gate text parity (doc 86 section 1.1).",
    "docs/05, docs/21, docs/44, docs/03, docs/55, docs/31, docs/20, docs/86 §1.1, docs/91, docs/22, docs/19, docs/62",
    "normative docs + WORK_PLAN.csv (future files are planned, not required to exist)",
    "deterministically ordered file:line diagnostics; exit 0 only with zero defects",
    "Runs clean on the hardened set; every check has a planted-defect test; unknown IDs/keys and unresolved section references fail; checks are not skipped because product code does not exist; no app imports or runtime dependencies; two runs identical. ERR/FR/settings parity is doc-to-doc in M0, not equality to the frozen nucleus; M6 release checker adds code parity.",
    "tests/unit/test_docs_check.py", "DEC-014; build only after WI-0007. No product code authorised in M0.")

# =====================================================================================
# M1 — CORE & TRUTH
# =====================================================================================
add("pyproject.toml", "config", "Project metadata, EXACT-pinned deps (fastapi, uvicorn, pydantic, openpyxl, python-pptx, reportlab, pywebview, keyring, httpx, msal — the 10 of doc 04 §6; ADR-010), pytest/ruff/mypy config, requires-python 3.11+ (OQ-11).", "docs/04_TECHNICAL_ARCHITECTURE.md, docs/60", "-", "Importable package `app`; `pip install -e .` works", "`pip install -e .` exit 0; `python -c 'import app'` exit 0; no version range operators remain (`==` only) — the current file uses ranges and violates doc 04 §6; dependency set equals doc 04 §6 exactly (httpx + msal present, nothing beyond the 10); every dep has a licence row in doc 81.", "-", "Pin exact versions + add a lock/constraints file per doc 60.")
add("README.md", "config", "Human entry point: what it is, install, run, verify commands, disclaimer, live status.", "docs/00_INDEX.md", "-", "New user runs app in <10 min following only this file", "Commands copy-paste verbatim on clean Windows; every status claim traces to a gate (doc 34 truth audit).", "-", "No marketing claims not backed by a gate.")
add(".gitignore", "config", "Ignore data, venv, build, secrets, generated outputs, evidence project folders.", "docs/12_SECURITY_PRIVACY.md, docs/70", "-", "`git status` clean after full run", "Run app+tests+exports; git status shows no data files, DBs, exports or logs.", "-", "")
for pkg in ["core", "store", "imports", "connectors", "calc", "rules", "forecast", "planning", "adjustments", "exports", "ai", "api", "services", "jobs", "desktop", "cli"]:
    add(f"app/{pkg}/__init__.py", "core", f"Package marker for app/{pkg} (no logic, no imports with side effects).", "docs/04 §2", "-", "package", f"python -c 'import app.{pkg}' exit 0", "tests/unit/test_smoke.py")
add("app/__init__.py", "core", "Package marker + __version__ single source.", "pyproject.toml", "-", "app.__version__", "Import test; version equals pyproject.", "tests/unit/test_smoke.py")
add("app/core/errors.py", "core", "Typed error catalogue: every doc-22 code = constructor with code, user_message, hint, retryable, details. Complete set (doc 22 is the list).", "docs/22_ERROR_CATALOG.md", "error code", "AppError instances; JSON-serialisable", "Every doc-22 code has a constructor; a test iterates doc 22's table and asserts message+hint non-empty and retryable flag; no code reused for two meanings (money.py's misuse of ERR-021 fixed → ERR-025).", "tests/unit/test_errors.py", "Plain-language messages (analyst, not developer).")
add("app/core/money.py", "core", "THE ONLY money module: integer minor units, Decimal boundary, parse/format, ROUND_HALF_UP, largest-remainder allocation, pct helpers, currency exponent (doc 27).", "docs/03_CALCULATION_SPEC.md, docs/27", "str/int/Decimal", "int minor / Decimal / formatted str", "Float input raises TypeError; parse of '(1,200.50)', '₹1,200', '1.200,50' (de-DE profile) exact; allocation sums to total incl. negatives/zero weights; format en-IN lakh grouping; bad amount → ERR-025 (not ERR-021).", "tests/unit/test_money.py", "AI and UI NEVER compute money; they call this.")
add("app/core/calendar.py", "core", "Fiscal calendar: period ids, FY, quarters, period arithmetic, PY/YoY lookups, business days (doc 30), 4-4-5 reserved.", "docs/02_DATA_DICTIONARY.md (period identity), docs/30", "fy_start_month, calendar type", "Period objects", "Period round-trip; PY mapping; leap years; fy_start_month 1 and 4; shift across FY boundary negative; business-day count with weekend-only calendar.", "tests/unit/test_calendar.py")
add("app/core/ids.py", "core", "Deterministic IDs: batch_id, gl_row_id (doc 06 §3), finding_id (doc 07 §2), prefixed random ids for user-created rows.", "docs/02, docs/06 §3, docs/07 §2", "source hash + row no", "stable id str", "Same input -> same id; vectors from docs 06/07 reproduced exactly.", "tests/unit/test_ids.py")
add("app/core/hashing.py", "core", "SHA-256 file/row hashing (streaming), checksum manifest for reproducibility.", "docs/12", "bytes/path", "hex digest", "Known-vector test; 200MB streaming without loading whole file.", "tests/unit/test_hashing.py")
add("app/core/audit.py", "core", "Append-only audit log writer: who/when/what/before/after/hash-chain + verify.", "docs/12 §3, docs/02 audit_log", "event dict", "audit row; chain verifies", "Tampered row -> verify() fails and names the first broken row; clock injected.", "tests/unit/test_audit.py")
add("app/core/config.py", "core", "Settings: doc-62 keys with types/defaults/ranges, precedence project > user > defaults, validation with plain-language errors, AI off by default.", "docs/62, docs/04 §5", "env/file/db settings", "Settings object", "Every doc-62 key present with its default; out-of-range value -> AppError with hint; unknown key rejected.", "tests/unit/test_config.py")
add("app/core/logging.py", "core", "Structured local logging per doc 65: levels, rotation, redaction of amounts/names at INFO and of secrets/tokens everywhere (Bearer, JWT `eyJ…`, client_secret=, code=/state= query values, Authorization headers), connector.log request lines without query values or bodies, diagnostics bundle manifest, zero network.", "docs/65, docs/12 §5", "-", "log files in project dir", "No network call; redaction test for amounts/names; token-redaction test with a synthetic JWT + fake secret in message, ctx and exception text; rotation test with injected clock.", "tests/unit/test_logging.py")
add("app/core/license.py", "core", "Offline licence verification per doc 79: Ed25519-signed licence file, trial expiry, perpetual core never expires.", "docs/79, docs/12", "licence file", "licence state", "Forged/expired licence fixtures; core access never blocked for perpetual; clock injected.", "tests/unit/test_license.py")
add("app/store/schema.sql", "store", "SQLite schema: EVERY doc-02 table/column 1:1 (sections 2, 5, 6, 7 — incl. the §7 deltas: gl_rows.posting_layer/source_account_ref/vendor_source, findings.suggestion_json/suggestion_status/suggestion_ref, import_batches tb_check kind + enrichment_json + source/pull_id, tables connector_profiles + connector_pulls and project/period revision metadata — deltas 13/14), FKs, CHECK constraints on enums, indexes, created_by/updated_at where doc 02 §1 requires. Money INTEGER minor units.", "docs/02_DATA_DICTIONARY.md (every table/column)", "-", "DDL applies cleanly", "Schema-equality test parses doc 02 tables+columns and diffs against PRAGMA table_info for every table: zero missing, zero extra; FK on; duplicate budget grain with NULL cc rejected.", "tests/unit/test_schema.py", "Closes audit pass-3 P0-5 (doc 02 ≠ schema). One storage engine only.")
add("app/store/db.py", "store", "Connection factory: WAL, FK on, migration runner (doc 61), transaction context manager, integrity check.", "schema.sql, core/errors, docs/61", "db path", "sqlite3 connection", "Fresh DB == migrated DB (schema dump equality); crash mid-txn leaves no partial data; backup-before-migrate file exists and hash-verified.", "tests/unit/test_db.py")
add("app/store/migrations/__init__.py", "store", "Migration registry per doc 61: ordered m0001.. steps with up(conn), description, app version.", "docs/61", "-", "registry", "Migration list ordered + unique + contiguous test.", "tests/unit/test_migrations.py")
add("app/store/migrations/m0001_initial.py", "store", "Initial schema migration: applies schema.sql as migration 1.", "docs/61, docs/02", "schema.sql", "tables", "Fresh vs migrated schema equality test.", "tests/unit/test_migrations.py")
for repo, tbl in [("import_repo", "import batches + raw rows"), ("gl_repo", "gl_rows queries: by period/account/entity/cc/voucher/layer"),
                  ("mapping_repo", "mapping profiles + rules + versions"), ("master_repo", "entities/accounts/cost centres/vendors/owners/account_owners"),
                  ("budget_repo", "budget versions + lines"), ("forecast_repo", "forecast runs + lines + scenarios"),
                  ("exception_repo", "findings, history, comments"), ("report_repo", "reports registry + report_definitions"),
                  ("period_repo", "period open/closing/lock state + lock log"),
                  ("connector_repo", "connector_profiles (versioned, one active) + connector_pulls (status, counts, sha, error code; never a token) + last-successful-pull lookup per period")]:
    add(f"app/store/{repo}.py", "store", f"Repository for {tbl}. Parameterised SQL only; returns dataclasses; money as int minor units; every mutation writes audit.", "store/db.py, core/money, core/audit, docs/02", f"{tbl} filters", "dataclass lists / ids", "CRUD round-trip; SQL-injection test (hostile names); money round-trip exact; audit row written per mutation.", f"tests/unit/test_{repo}.py", "No business logic here - persistence only.")
add("sample-data/generate_sample_data.py", "data", "COHERENT corpus generator per doc 42: one plan -> budget and actuals = plan × (1 + controlled noise); balanced vouchers by construction; plants P01–P36 + controls C01–C13 ONLY from the doc-42 §7/§8 registers (vendor roles V05/V08/V21/V26 and cost centres CC-SAL/CC-FIN per doc 42 §1); seed-fixed; writes answer_key.json (incl. expected_suggestion per plant) + hashes.json; also emits the golden period in the ERP shapes of doc 42 §4 (`erp_shapes/`: D365 F&O voucher transactions + vendor transactions + trial balance + budget register, D365 BC G/L entries + budget) and the API shapes `erp_shapes/api/{fo,bc}/*.json` + `fo/$metadata.xml` served by tools/mock_d365.py (same rows, incl. the Tax-layer variant and one hostile-cells BC page).", "docs/42, docs/07, docs/44, docs/28, docs/26 §5", "seed", "CSV/XLSX files + erp_shapes/ + answer_key.json + hashes.json + plan.json", "Regenerate -> byte-identical (hash test); TB balances every entity×period; coherence: no unplanted |var| ≥ both materiality legs; answer key has 36 plants, 19 high, 13 controls (asserted); every plant hand-findable in raw files (spot list in tests); erp_shapes rows == CSV rows for 2025-P07 (parity); erp_shapes/api JSON row counts == file-shape row counts per source and the metadata names every default-profile field.", "tests/data/test_corpus.py", "Attempt #4 died here: independent random budget/actuals created 370 false exceptions. Coherence is the spec.")
add("sample-data/answer_key.json", "data", "Generated planted-exception answer key: 36 plants + 13 controls, each {id, rule, finding_key, entity, account, period, voucher(s), amount, severity, generator_function, expected_suggestion{kind, lines, confidence}}.", "docs/42 §7–§8, generate_sample_data", "-", "JSON", "Schema-valid; finding_key format per doc 07 §2; counts asserted; every key traceable to a plant function.", "tests/data/test_answer_key.py")
add("sample-data/malformed/", "data", "Malformed corpus per doc 42 §5: each file with expected.json {rows_in, valid, quarantined_by_reason}.", "docs/06 §4, docs/42 §5", "-", "fixtures + expected.json", "Import of each -> expected quarantine counts by reason; zero-byte and zip-bomb handled without crash.", "tests/data/test_malformed.py", "Directory item: ≥12 files + expected.json.")
add("tests/integration/test_erp_shape_parity.py", "test", "ERP shape parity per doc 14 §3 / doc 42 §4: import each sample-data/erp_shapes/ file of 2025-P07 through the real pipeline with its doc 26 §5 preset and compare committed gl_rows with the CSV shape; F&O Tax-layer rows quarantined OUT_OF_SCOPE_LAYER; vendor enrichment fills every vendor; TB tie-out zero differences; BC vendor only for Source Type = Vendor.", "imports/mapping, imports/validation, imports/commit, imports/enrichment, imports/tb_check, generate_sample_data, docs/26 §5, docs/42 §4", "erp_shapes files", "parity report", "Row multiset equality (ids excluded) for every shape; expected quarantine/enrichment/tie-out counts exactly; a preset header renamed in the fixture fails the test (guards silent drift).", "-", "This is what makes 'D365 first-class' a tested claim rather than a sentence.")
add("tests/fixtures/README.md", "test", "Fixture index per doc 89: every fixture, its oracle source (doc §) and hash. Fixtures ARE expectations (doc 78).", "docs/89, docs/78, docs/14 §2", "-", "index", "Every tests/fixtures file listed; CI fails on unlisted fixture; every doc-89 fixture exists.", "-")
for pack in ["general", "manufacturing", "saas", "retail"]:
    add(f"packs/{pack}.json", "data", f"Industry starter pack '{pack}' per doc 28 (COA + statement_line map + KPI set + drivers + threshold tweaks) as validated data.", "docs/28, docs/45", "-", "pack JSON", "Pack schema validation; loads into a new project; fixture GL produces statements with zero `unmapped` lines.", f"tests/data/test_pack_{pack}.py")
add("packs/pack.schema.json", "data", "JSON Schema for industry packs (doc 28): COA entries, statement lines (doc 45 keys only), tags, KPI keys, driver keys.", "docs/28, docs/45, docs/43", "-", "schema", "All packs/*.json validate; an unknown statement_line key fails validation.", "tests/data/test_pack_schema.py")
add("tests/acceptance/test_acceptance.py", "test", "THE acceptance harness (doc 14 §3): load corpus -> run all rules -> recall 36/36, high 19/19, controls 0/13, suggestion exactness (kind/lines/confidence per answer key), extras justified, two runs identical, 28/28 wired, ERP shape parity.", "generate_sample_data, answer_key, store/exception_repo, docs/14 §3, docs/42", "corpus", "evidence/acceptance_report.json + verdict", "Built in M1 and RED by design (0/36) until M2; never weaken bars.", "-", "This test IS the release gate.")

# =====================================================================================
# M2 — ENGINE
# =====================================================================================
add("app/imports/models.py", "imports", "Dataclasses: RawFile, RawRow, StagedRow, ImportBatch, ValidationIssue, ControlTotals, QuarantineReason enum (doc 06 §4 closed list).", "docs/02, docs/06", "-", "typed models", "mypy strict; QuarantineReason values == doc 06 §4 list exactly.", "tests/unit/test_import_models.py")
add("app/imports/parser_csv.py", "imports", "CSV/TSV parser: encoding sniff (UTF-8/BOM/UTF-16/Latin-1), delimiter sniff, header detection, 1-based row numbers preserved, streaming.", "imports/models, docs/06 §1", "file path", "RawRow iterator", "Malformed corpus files parse without crash; row numbers match the source editor; 1M-row streaming memory-bounded.", "tests/unit/test_parser_csv.py")
add("app/imports/parser_xlsx.py", "imports", "XLSX parser (openpyxl read-only): sheet listing, header row, merged cells, formula cells -> cached values flagged, missing cache -> quarantine.", "imports/models, docs/06 §1", "file path", "RawRow iterator + sheet report", "Every sheet accounted for in report; zip-bomb/size guard; formula-no-cache fixture quarantined with reason.", "tests/unit/test_parser_xlsx.py")
add("app/imports/profiler.py", "imports", "Column profiler: type guess, null %, distinct, 5 escaped samples -> mapping suggestion input.", "imports/models", "RawRow[]", "ColumnProfile[]", "Deterministic output for fixture; samples never contain raw markup.", "tests/unit/test_profiler.py")
add("app/imports/mapping.py", "imports", "Mapping engine: apply saved profile (source col -> canonical field, transforms from the doc 06 §2.4 closed list incl. split:<field>:<n> with source_account_ref retention, conditional:<col>=<value>, constant:), versioned, auto-apply on header match; ships the doc 26 §5 presets as data (D365FO-GL/AP/TB/Budget v1, D365BC-GL/Budget/TB v1, Tally, SAP, QuickBooks/Xero/Zoho; legacy alias D365-GL v1).", "imports/models, store/mapping_repo, docs/06 §2.3–2.4, docs/26 §5", "profile + RawRow", "StagedRow[]", "Month-2 reuse = zero re-mapping; debit/credit pair -> signed; sign_flip; date formats incl. ambiguous -> AMBIGUOUS_DATE; D365 F&O ledger-account split keeps the raw string; short segments -> BAD_SEGMENT; BC vendor only when Source Type = Vendor; every preset maps its doc-89 ERP-shape fixture with zero manual edits; unknown transform -> ERR-022.", "tests/unit/test_mapping.py")
add("app/imports/mapping_suggest.py", "imports", "Deterministic header-similarity suggestions (synonym table, normalised similarity, confidence 0..1); AI hook optional and never auto-applies.", "profiler output, docs/06 §2.3, docs/26", "headers", "ranked suggestions", "Doc-26 ERP header fixtures -> correct top-1; confidence monotone.", "tests/unit/test_mapping_suggest.py")
add("app/imports/validation.py", "imports", "Row validation: required fields, date/amount parse via money.py, master-code resolution, period window, posting-layer scope (import.posting_layers), duplicate-in-file detection; quarantine with closed-list reasons.", "imports/models, core/money, docs/06 §2.5, §4", "StagedRow[]", "valid[] + quarantine[] + issues[]", "in = valid + quarantined always; every reason from the closed list; hostile text preserved verbatim, never executed; a Tax-layer row -> OUT_OF_SCOPE_LAYER with the layer name kept.", "tests/unit/test_validation.py")
add("app/imports/control_totals.py", "imports", "Control totals: row count, debit sum, credit sum vs declared; per-account declared movements from an attached ERP trial-balance file (tb_check shape).", "core/money, imports/models, docs/06 §2.6, docs/26 §5", "batch + declared totals (+ TB file)", "pass/fail + deltas (batch and per account)", "Mismatch -> ERR-023 with declared vs actual deltas; per-account differences listed when a TB file is attached (doc-89 fixture: one account altered by ₹1,000 -> exactly one difference); absent declaration acknowledged path.", "tests/unit/test_control_totals.py")
add("app/imports/enrichment.py", "imports", "Vendor enrichment per doc 06 §2 step 9: GL rows without vendor matched 1:1 on (voucher_no, posting_date) to the period's AP sub-ledger batch -> vendor_id with vendor_source='ap_match'; column-sourced vendors never overwritten; ambiguous/unmatched counted; re-runnable; audited.", "store/gl_repo, store/import_repo, docs/06 §2.9, docs/26 §5", "gl batch + ap batch", "{matched, ambiguous, unmatched, already_had_vendor}", "Doc-89 ERP-shape fixture: matched == every vendor row of P07, ambiguous 0, unmatched 0; a many-to-one voucher stays unmatched and is reported; running twice changes nothing; column vendors untouched.", "tests/unit/test_enrichment.py", "Without this the D365 F&O voucher export has no vendors and seven rules go not_run (doc 44 §0).")
add("app/imports/tb_check.py", "imports", "Trial-balance tie-out per doc 06 §1 (`tb_check`) and doc 26 §5: committed TB-shape batch vs committed GL per account -> differences {account_id, erp_minor, app_minor, delta_minor}; zero differences flips the doc-30 close item.", "store/gl_repo, store/import_repo, core/money, docs/06, docs/30", "period, tb batch", "differences[]", "ERP-shape fixture ties out to zero; altered copy yields exactly one difference of ₹1,000; period without GL -> ERR-030.", "tests/unit/test_tb_check.py")
add("app/imports/commit.py", "imports", "Atomic commit: validated staging -> gl_rows in ONE transaction, 1,000-row multi-insert batches, supersede on same file hash + period + kind, audit.", "store/*, validation, control_totals, docs/06 §2.7, docs/23 §2", "validated batch", "batch_id + counts", "Kill mid-commit -> DB unchanged and batch stays `validated`; re-import same file -> old batch superseded, row count == new file.", "tests/unit/test_commit.py", "All-or-nothing (P12). No row-by-row executemany (attempt #4 DEF-030).")
add("app/imports/trial_balance.py", "imports", "Trial balance gate: Σ amount_minor == 0 per entity/period; imbalance drill to account → voucher; waiver support.", "store/gl_repo, core/money, docs/03 §2", "period", "TB report", "Doc 03 §2 oracles; planted ₹0.01 imbalance detected and located.", "tests/unit/test_trial_balance.py")
add("app/imports/reconcile.py", "imports", "Subledger-to-GL reconciliation per doc 19 §I: match scoring amount/date/reference, unmatched both sides, tolerance.", "docs/19 §I, docs/06", "subledger rows + gl_rows", "recon run + matches", "Fixture: matched/unmatched counts tie both sides; tolerance boundary ±1 minor unit.", "tests/unit/test_reconcile.py")
add("app/calc/statements.py", "calc", "P&L, BS, CF (indirect) from gl_rows (+ adjustment layer) via the doc-45 line registry; presentation signs; movement-BS labelling; every line drillable.", "store/gl_repo, core/money, docs/03, docs/45, docs/39", "period, entity, layer", "Statement{lines[]}", "Oracles pl_basic/bs_basic/cf_basic to the minor unit; A = L + E; CF net == BS cash Δ; unmapped line rendered, never dropped.", "tests/unit/test_statements.py", "Fixtures FIRST (doc 14 §2).")
add("app/calc/kpis.py", "calc", "KPI library per doc 43: formula, basis (closing balances, period days), n/a with reason on zero denominators, 2dp half-up.", "calc/statements, docs/43, docs/03 §4", "statement + GL", "KPI values + formula text", "Every doc-43 fixture reproduced; every n/a case tested.", "tests/unit/test_kpis.py")
add("app/calc/bva.py", "calc", "BvA / FvA / PY at lowest shared grain: Var₹, Var% (n/a on zero budget), favourable, contribution, AND-materiality.", "store/gl_repo, budget_repo, docs/03 §5", "period, version pair, layer", "VarianceRow[]", "Doc 03 §5 oracles incl. the four AND-discriminating controls; grain collapse disclosed.", "tests/unit/test_bva.py")
add("app/calc/attribution.py", "calc", "Variance bridge: volume / price / mix / other where drivers exist; else explicit unavailable.", "calc/bva, docs/03 §6", "variance + drivers", "bridge components summing to total", "Components sum == total exactly; no drivers -> {available:false, reason}.", "tests/unit/test_attribution.py", "Never fabricate a bridge without drivers.")
add("app/calc/drilldown.py", "calc", "Any aggregate -> vouchers -> rows -> file + row number (P5), paginated, layer-aware.", "store/gl_repo, docs/03 §8", "drill_key", "row list + source refs", "Every statement/BvA cell in fixtures drills to ≥1 row; adjustment lines shown in their own section.", "tests/unit/test_drilldown.py")
add("app/calc/quality_score.py", "calc", "Data-quality score per doc 29 §9: deductions table, never a bare number.", "docs/29 §9, calc/statements", "period data", "score + deductions[]", "Fixture deduction arithmetic exact; score without reasons impossible by type.", "tests/unit/test_quality_score.py")
RULES = [
    ("001", "Duplicate voucher / duplicate posting"), ("002", "Same voucher, overlapping re-import (duplicate batch)"),
    ("003", "Control-total mismatch on import"), ("004", "Unbalanced voucher (debit != credit)"),
    ("005", "Posting to closed/locked period"), ("006", "Spend concentration / single-vendor spike by entity-account"),
    ("007", "Suspense / clearing account ageing"), ("008", "Large one-off journal above threshold"),
    ("009", "Manual journal by unusual user / outside hours"), ("010", "Cut-off: posting date vs document date across period end"),
    ("011", "Stale recurring accrual not reversed"), ("012", "Contra-normal postings (credits to expense, debits to revenue)"),
    ("013", "Account spike vs trailing average (material %)"), ("014", "Vendor-to-account mapping anomaly (new account for vendor)"),
    ("015", "Recurring charge missing (expected SaaS/rent absent)"), ("016", "Accrual pattern break (accrued then never expensed)"),
    ("017", "Material unbudgeted spend"), ("018", "Material BvA variance (abs AND % AND-test)"),
    ("019", "Cumulative budget overrun trend"), ("020", "Round-amount journal clustering"),
    ("021", "Threshold-splitting (multiple just-below-approval-limit)"), ("022", "Round-tripping / same-amount in-out"),
    ("023", "Voucher with single-line imbalance risk"), ("024", "Dormant account sudden activity / new account first use"),
    ("025", "Account–narration mismatch (description tokens associated with another account)"), ("026", "Amount outlier / decimal-shift suspect vs the vendor's history on the account"),
    ("027", "Unusual cost centre for the account/vendor"), ("028", "Near-duplicate vendor charge (same vendor+account+amount, different voucher, within window)"),
]
for num, name in RULES:
    add(f"app/rules/exc_{num}.py", "rules", f"EXC-{num}: {name}. Pure function (gl_rows, budget_lines?, params, context) -> Finding[] | not_run. Deterministic, integer/Decimal only, canonical key per doc 07 §2.",
        f"docs/07 EXC-{num}, docs/44 EXC-{num}, docs/42 §7 plants for this rule, core/money, core/calendar", "GL rows + params + context (period, lookback rows, settings snapshot)", "Finding[] with evidence row_ids, values, thresholds, grain",
        "Doc-42 plant(s) for this rule fire exactly once with the exact finding_key; its control(s) are silent; boundary −1/exact/+1 matrix; insufficient lookback -> not_run with reason; evidence re-derivable by hand and sufficient for rules/suggestions.py to build the doc 07 §7.3 template without re-reading the ledger.", f"tests/unit/test_exc_{num}.py",
        "Attempt #4 died on key/threshold divergence. The catalogue + doc 44 are law — quote their cases in your test. Scope matters: P&L-only rules must not fire on balance-sheet accounts (doc 44 §0).")
add("app/rules/engine.py", "rules", "Rule runner: runs enabled rules on a layer, dedupes by finding key, persists, severity escalation (≥3× escalation base -> High; entry-hygiene rules use material_abs as base), reopen-on-refire, not_run registry, param snapshot in evidence, attaches the suggestion (rules/suggestions.py) to every finding, runs the verification loop for `corrected` findings.", "rules/exc_*, rules/suggestions, store/exception_repo, docs/07 §1, §5, §7", "period, rule config, layer", "run report: per-rule counts + not_run reasons + verification proposals", "Two identical runs -> identical findings; escalation rule incl. the EXC-025…028 base; closed finding re-firing reopens as new with history kept; no finding persisted without a suggestion object.", "tests/unit/test_rule_engine.py")
add("app/rules/suggestions.py", "rules", "Rectification suggestions per doc 07 §7 + doc 44 derivations: per-rule template -> {kind, lines (balanced), target_period_id, basis, confidence, erp_hint}; verification matcher (corrected -> verified proposals) per doc 44.", "rules/exc_*, store/gl_repo, store/master_repo, core/money, core/calendar, docs/07 §7, docs/44, docs/55", "finding + evidence + history rows", "Suggestion object / verification proposals", "One fixture per rule (doc 89 §2 suggestions): kind, lines, confidence exactly as doc 07 §7.3; every journal-kind suggestion nets to zero (type-level assertion); EXC-026 ₹4,800,000 -> ₹48,000 repost; EXC-027 dominant CC; locked original period -> lines dated in the open period with the prior-period narrative; verification fixture proposes verified only on a full match.", "tests/unit/test_suggestions.py", "Advisory only: nothing is posted anywhere. Copy from doc 55 `suggestion.*` keys; every correcting line ends with the `[FPA EXC-### <voucher>]` tag.")
add("app/rules/owner_resolver.py", "rules", "Finding -> accountable owner (account_owners -> vendor owner -> Unassigned) + due date by severity (settings).", "store/master_repo, docs/07 §5", "finding", "owner assignment", "Unmapped -> explicit 'Unassigned', never dropped; due-date table per severity.", "tests/unit/test_owner_resolver.py")
add("app/rules/workflow.py", "rules", "Finding lifecycle per doc 23 §3 with guards; waive needs reason+expiry ≤90d; expiry job returns to new; suggestion consumption (apply as adjustment / queue for journal / dismiss, doc 07 §7.4) with suggestion_status + suggestion_ref; every transition -> history + audit.", "store/exception_repo, adjustments/engine, core/audit, docs/23 §3, docs/22, docs/07 §7.4, docs/39 §4", "finding id, action", "new state", "Illegal transition -> ERR-040; waive without reason -> ERR-041; expiry with injected clock; apply creates a correction_view group and moves the finding to corrected; locked target period -> ERR-046; second apply -> ERR-005; dismiss without note -> ERR-002.", "tests/unit/test_finding_workflow.py")
METHODS = [("naive", "Last-period / seasonal-naive baseline"), ("moving_average", "Moving average (n configurable)"),
           ("exponential_smoothing", "Holt linear (n≥4) / Holt-Winters additive (n≥14) with deterministic grid search"), ("linear_trend", "Linear trend / CAGR"),
           ("driver_based", "Driver-based: revenue=volume*price etc. from driver registry"), ("seasonal", "Seasonal index decomposition (n≥24 else not_run)"),
           ("budget_phasing", "Phasing: annual budget spread by curve (largest remainder)"), ("manual", "Manual override layer (versioned, never overwrites system forecast)")]
for slug, name in METHODS:
    add(f"app/forecast/{slug}.py", "forecast", f"Forecast method: {name}. Pure, deterministic, Decimal; returns series + method metadata + not_run reason when history insufficient.", "docs/08 §2, docs/46, core/money, core/calendar", "history series + params", "forecast series", "Doc 46 numeric oracles reproduced exactly (Holt l4=122.035 b4=9.2485 ŷ5=131.2835; HW flat ŷ=100/110); floors per doc 08 §7; insufficient history -> not_run.", f"tests/unit/test_fc_{slug}.py")
add("app/forecast/engine.py", "forecast", "Forecast orchestration: per group backtest (MAPE/bias/hit-rate), recommend lowest MAPE with deterministic tie-break, analyst override, lock (immutable).", "forecast/moving_average, forecast/naive, forecast/exponential_smoothing, forecast/linear_trend, forecast/driver_based, forecast/seasonal, forecast/budget_phasing, forecast/manual, store/forecast_repo, docs/08 §3", "period, scope", "ForecastRun + accuracy report", "Doc 08 §3 oracle (APE 6.52%); backtest reproducible; locked run immutable (write -> error).", "tests/unit/test_forecast_engine.py")
add("app/forecast/scenarios.py", "forecast", "Scenarios: ordered deltas (driver -> % -> absolute) on a locked base; compare; base untouched.", "forecast/engine, docs/08 §4", "deltas", "scenario series", "Delta application exact; base hash unchanged; order of application tested.", "tests/unit/test_scenarios.py")
add("app/forecast/rolling.py", "forecast", "Rolling forecast: actuals replace elapsed periods, new draft run forward, prior runs untouched, FVA computed.", "forecast/engine, core/calendar, docs/08 §1, §6", "new actuals period", "new rolling run + FVA", "Month+1 run does not mutate prior run; FVA error/bias per doc 08 §6; bias advisory at ≥5% over 3 periods.", "tests/unit/test_rolling.py")
for slug2, nm in [("drivers", "Driver registry + formula evaluation (doc 29 §2)"), ("headcount", "Headcount plan -> personnel cost (29 §3)"), ("capex", "Capex + depreciation SLM/WDV pro-rata (29 §4)"), ("debt", "Debt schedule + interest on average balance (29 §5)"), ("working_capital", "WC from DSO/DPO/DIO targets (29 §6)"), ("cash13", "13-week cash forecast, calendar weeks Mon–Sun (29 §6)"), ("sensitivity", "One/two-variable sensitivity tables (19 §H)"), ("goal_seek", "Goal seek by bisection, 50 iterations, no-solution honest (19 §H)")]:
    add(f"app/planning/{slug2}.py", "planning", nm + ". Pure, Decimal, versioned inputs, every output traceable to inputs.", "docs/29, docs/08, core/money, docs/89 §5", "planning inputs + actuals/forecast", "computed series + provenance", "Doc 29 / doc 89 §5 oracle reproduced exactly; invalid input -> AppError with hint, never a silent clamp.", f"tests/unit/test_plan_{slug2}.py")
add("app/planning/integrate.py", "planning", "Integrated 3-statement forecast articulation check per doc 29 §7: imbalance named, never plugged.", "docs/29 §7, calc/statements", "PL/BS/CF forecast series", "balance verdict + broken link", "Doc 29 §7 oracle (Δcash 480,000) passes; planted imbalance detected and named.", "tests/unit/test_plan_integrate.py")
add("app/planning/allocations.py", "planning", "Cost allocations per doc 40 (pct/driver/step-down) producing balanced adjustment groups.", "docs/40, docs/39, app/adjustments/engine", "allocation def + drivers", "adjustment lines", "Doc 40 oracle (180,000/120,000) exact; pct sums 100.000 via largest remainder; zero-driver blocked; step-down order effect.", "tests/unit/test_allocations.py")
add("app/planning/assumptions.py", "planning", "Assumptions register per doc 48: versioned, approve, stale-marking of dependent runs.", "docs/48, docs/02 §6", "assumption drafts", "approved versions", "Change after lock lists impacted runs; versions immutable.", "tests/unit/test_assumptions.py")
add("app/adjustments/engine.py", "adjust", "Management-adjustment engine per doc 39: draft/apply/reverse, balanced pair-group invariant, layer-aware statement inputs.", "docs/39, docs/02 §6, core/money, store", "adjustment lines", "applied adjustment set", "Unbalanced group -> ERR-042 with Δ; reversal chain; layer selector changes totals by exactly the adjustment sum.", "tests/unit/test_adjustments.py")

# =====================================================================================
# M3 — SERVICES, API, CLI, AI
# =====================================================================================
# -------------------------------------------------------------------------------------
# M3 — DYNAMICS 365 CONNECTOR (DEC-013, doc 26 §8) — a file producer feeding app/imports
# -------------------------------------------------------------------------------------
add("app/connectors/models.py", "connectors", "Typed connector models: ConnectorSettings (non-secret, from connector.* settings), ConnectorProfile (sources -> entity, filter template, sort key, field->preset-header map, watermark), EntityCheckResult, PullRequest, PullResult, ConnectionState enum (doc 23 §11). Pydantic; no I/O.", "docs/26 §8.2–8.4, docs/62 connector.*, docs/23 §11, docs/02 connector_*", "dicts/settings", "validated models", "Profile JSON round-trips; a secret-shaped value in settings is rejected (ERR-105); base_url without https rejected (ERR-113); state derivation table of doc 23 §11 reproduced for every combination of settings/keyring/refresh outcome.", "tests/unit/test_connector_models.py")
add("app/connectors/profiles/d365fo.json", "connectors", "Default F&O connector profile per doc 26 §8.3 (gl GeneralJournalAccountEntries, ap VendorTransactions, budget BudgetRegisterEntryLines, masters LegalEntities/MainAccounts/VendorsV2/dimension values; field->D365FO-* preset headers; sort keys; filter templates).", "docs/26 §8.3, docs/26 §5", "-", "profile data", "Every target header exists in the D365FO-* presets of doc 26 §5 (cross-check test); every source names a sort key and a date filter; JSON schema valid.", "tests/unit/test_connector_profiles.py", "Defaults, not promises — the entity check is the contract.")
add("app/connectors/profiles/d365bc.json", "connectors", "Default Business Central connector profile per doc 26 §8.3 (gl generalLedgerEntries + dimensionSetLines flattening, ap purchaseInvoices, tb trialBalance, masters companies/accounts/vendors/dimensions; watermark lastModifiedDateTime; field->D365BC-* preset headers).", "docs/26 §8.3, docs/26 §5", "-", "profile data", "Headers exist in the D365BC-* presets; dimension flattening spec names dim1/dim2 codes; watermark declared; JSON schema valid.", "tests/unit/test_connector_profiles.py")
add("app/connectors/transport.py", "connectors", "The ONLY outbound HTTP path besides app/ai/client.py: httpx client with mandatory TLS verification, connect 10s / read connector.timeout_s, egress allow-list enforced per request incl. redirects (login.microsoftonline.com + configured host; 127.0.0.1 only when connector.allow_demo_host on the sample project), retry with Retry-After + exponential backoff (1-2-4-8-16s, max connector.retry_max_attempts) on 429/503/timeouts, request logging without query values/bodies, token-redacted exceptions.", "core/logging, core/errors, connectors/models, docs/12 §1(d), docs/26 §8.2/8.4, docs/62", "request spec + token provider", "parsed JSON/XML pages", "Non-allow-listed host -> ERR-113 before any socket (asserted with a socket-block fixture); redirect to another host refused; http:// refused; 429 with Retry-After honoured then success; 5 failures -> ERR-115 with attempts=5 logged; a synthetic JWT in a failing request never appears in the exception text or logs; no code path performs POST/PATCH/PUT/DELETE.", "tests/unit/test_connector_transport.py", "Security envelope lives here; everything else trusts it.")
add("app/connectors/auth.py", "connectors", "Entra ID auth via msal: delegated auth-code + PKCE (PublicClientApplication, system browser, loopback redirect served by the API's /connector/callback, state bound to the pending attempt, accepted once), silent refresh from a SerializableTokenCache persisted in the OS keyring (fpa/<project_id>/connector/*), application mode via ConfidentialClientApplication with secret/cert from the keyring; Disconnect wipes entries.", "connectors/models, core/config (keyring), docs/26 §8.2, docs/12 §5, docs/23 §11", "settings + keyring", "access tokens (never persisted outside keyring)", "Against the mock token endpoint: auth-code exchange stores cache in a fake keyring and nothing on disk/DB (grep test); wrong state rejected (ERR-111); expired refresh -> ERR-112 and state token_expired; application mode acquires by client credentials; disconnect leaves zero keyring entries + audit row; AADSTS code surfaced verbatim in ERR-111 details.", "tests/unit/test_connector_auth.py")
add("app/connectors/odata.py", "connectors", "Generic OData v4 / BC API reader: $count volume guard (import.max_rows -> ERR-116), $select/$orderby/$filter/$top building, cross-company scoping, @odata.nextLink paging with one page in memory, $expand flattening, page-total vs count consistency (one re-pull then ERR-118), $metadata parsing for the entity check (entity sets + properties) with candidate suggestions (ERR-114).", "connectors/transport, connectors/models, docs/26 §8.3/8.4", "profile source + period + company", "row iterator + counts", "Recorded fixtures (doc 89 §4b): 3 pages concatenated in order; count drift -> exactly one re-pull then ERR-118; truncated page -> ERR-118; metadata_missing_field -> ERR-114 listing Text with candidates Txt/Description; memory test: peak rows resident <= page size.", "tests/unit/test_connector_odata.py")
add("app/connectors/snapshot.py", "connectors", "Deterministic snapshot writer: one sheet per source with the exact doc 26 §5 preset headers, rows sorted by the stable key, every cell text (ISO dates, decimal strings via money.py, never float), Meta sheet; content sha256 over header+rows canonical text (not zip bytes); written to a temp name under imports/ and renamed only on success; returns path + content hash + per-sheet counts.", "connectors/models, core/money, core/hashing, imports/mapping (preset header names), docs/26 §8.4 step 6, docs/06 §1/§3", "row iterators", "imports/<sha256>.xlsx + content hash", "Same rows in different arrival order -> byte-identical data sheets and identical content hash (determinism oracle doc 89 §4b snapshot/expected_fo_2025-P07); no float cell anywhere (openpyxl type scan); failure mid-write leaves no file in imports/; header set equals the preset header set exactly.", "tests/unit/test_connector_snapshot.py", "Idempotency and 'no change' depend on this being exact.")
add("app/connectors/d365fo.py", "connectors", "Finance / F&O adapter: environment URL + scope, LegalEntities company listing, cross-company dataAreaId scoping, per-source entity queries from the profile, posting-layer passthrough (scope applied by validation), optional watermark field.", "connectors/odata, connectors/auth, connectors/profiles/d365fo.json, docs/26 §8.2/8.3", "profile + settings", "source row iterators + companies", "Against mock F&O: companies listed; gl/ap/budget/masters pulled with exact filters (recorded request assertions: cross-company=true, dataAreaId filter, AccountingDate range, $orderby RecId, $select = profile fields); unknown company -> ERR-117.", "tests/unit/test_connector_d365fo.py")
add("app/connectors/d365bc.py", "connectors", "Business Central adapter: tenant/environment URL, companies(<id>) scoping, generalLedgerEntries?$expand=dimensionSetLines flattening to Global Dimension 1/2, purchaseInvoices for vendor-by-document, trialBalance by dateFilter, accounts/vendors/dimensions masters, lastModifiedDateTime pre-check.", "connectors/odata, connectors/auth, connectors/profiles/d365bc.json, docs/26 §8.2/8.3/8.5", "profile + settings", "source row iterators + companies + changed-count", "Against mock BC: dimension flattening exact; trialBalance movements map to D365BC-TB headers; check-changes returns the mock's count; page size capped at 20,000; unknown company -> ERR-117.", "tests/unit/test_connector_d365bc.py")
add("tools/mock_d365.py", "connectors", "Local mock of BOTH products for tests and the offline demo ledger (doc 26 §8.8): token endpoint (client credentials + fake auth-code exchange), F&O $metadata + entity GET with $filter/$select/$orderby/$top/$skip/$count + @odata.nextLink + cross-company, BC companies/generalLedgerEntries($expand)/purchaseInvoices/trialBalance/accounts/vendors/dimensions; serves sample-data/erp_shapes/api/; fault injection via X-Mock-Fault: 429|503|truncate|count-drift|missing-entity; binds 127.0.0.1 on a free port; started by the sample project's 'Connect to the demo ledger (local)'.", "sample-data/generate_sample_data.py (erp_shapes/api), docs/26 §8.8, docs/42 §4", "corpus JSON", "HTTP server", "Contract test: every query option the connector emits is honoured (recorded requests replayed); nextLink chain terminates; each fault header produces the documented behaviour; binds only 127.0.0.1; starts in < 2 s; ships in the bundle (doc 16).", "tests/unit/test_mock_d365.py", "Keeps CI and the first-run walkthrough independent of any tenant.")
add("tests/fixtures/connectors/README.md", "connectors", "Recorded connector fixtures per doc 89 §4b: F&O pages 1–3 + metadata (+ missing-field variant), BC expand page + trial balance, fault payloads, synthetic token/secret strings, snapshot determinism oracle (expected_fo_2025-P07.xlsx + .sha256). README lists provenance (all synthetic from the corpus) and the regeneration command.", "docs/89 §4b, tools/mock_d365.py, sample-data/generate_sample_data.py", "corpus", "fixture files", "Every file named in doc 89 §4b exists; regeneration byte-identical; tokens/ directory excluded from the build payload (scripts/build audit).", "-")
add("app/services/connector_service.py", "services", "Pull orchestration per doc 26 §8.4 as job connector-pull: token -> entity check -> count guard -> paged pull per source -> consistency -> snapshot -> stage + validate via the import pipeline (source=connector, pull_id) -> optional auto-commit when clean -> enrichment / tb_check / masters; check-changes; test-connection; disconnect; connector_pulls rows + audit per pull; 'no change' when the content hash already has a batch for the period.", "connectors/d365fo, connectors/d365bc, connectors/snapshot, imports/parser_xlsx, imports/mapping, imports/validation, imports/commit, imports/enrichment, imports/tb_check, store/connector_repo, jobs/registry, docs/26 §8.4–8.6, docs/23 §11, docs/64", "pull request", "PullResult + staged batches", "Integration against the mock for both products: 2025-P07 pull ends staged with the preset auto-applied and counts == file import; second pull -> no_change and zero new batches; faults 429/503/truncate/count-drift/missing-entity -> ERR-115/115/118/118/114 with zero batches and no snapshot file; cancellation between pages leaves nothing; locked period -> ERR-030; concurrent pull refused; auto_commit_when_clean commits only when quarantine=0 and TB gate green.", "tests/integration/test_connector_pull.py", "Never writes staging or gl_rows itself — it calls the import pipeline with the snapshot file.")
add("app/jobs/registry.py", "services", "Job registry per doc 64: queued/running/done/failed/cancelled, progress, cancel, crash recovery on open, concurrency limit 1 heavy job.", "docs/64, docs/05 §1", "job fn", "job records", "Cancel mid-run honoured; crash -> job marked failed on next open; progress monotone.", "tests/unit/test_jobs.py")
add("app/services/month_end.py", "services", "THE month-end orchestrator: import->validate->TB->statements->BvA->rules->forecast->checks->packs, resumable at stage granularity; stage states derived from real records.", "all engine modules, docs/23 workflow, docs/04 §3", "project, period", "run state + artefacts", "Golden month-end on the corpus completes via CLI; re-run resumes, not restarts; stage states equal underlying record states (test flips each).", "tests/integration/test_month_end.py", "This is the product's spine.")
add("app/services/dashboard.py", "services", "Dashboard aggregates per doc 90 Dashboard DTO.", "calc/*, store/*, docs/90", "project, period", "dashboard DTO", "Values tie to calc fixtures; unassigned count; DQ deductions present.", "tests/unit/test_dashboard_service.py")
add("app/services/close_service.py", "services", "Close management per doc 30: task instantiation from template, system-verified completion, blockers, sign-off (ERR-080).", "docs/30, docs/23 §7", "project, period", "close state DTO", "System tasks derive from real states (test flips each source state); sign-off guard.", "tests/unit/test_close_service.py")
add("app/services/alerts.py", "services", "Alert engine per doc 19 §K: KPI/finding/bias alerts, dedupe by key+period, 90-day retention.", "docs/19 §K, docs/08 §6, docs/62", "snapshots", "alerts", "Duplicate run creates zero duplicate alerts; retention purge with injected clock.", "tests/unit/test_alerts.py")
add("app/services/year_end.py", "services", "Year-end close + rollforward per doc 38: checks, closing proposal, opening batch generation, Δ=0 verification.", "docs/38, app/adjustments/engine", "fiscal year", "year_end_run + opening batch", "Doc 38 oracle: RE roll, P&L opens 0, rollforward Δ 0; locked-FY regeneration rejected.", "tests/unit/test_year_end.py")
add("app/ai/client.py", "ai", "Provider-agnostic LLM client: OFF by default; timeout 30s; 1 retry; prompt/payload hashes logged; no key -> app fully works.", "docs/11 §5, core/config", "prompt", "text + usage", "AI disabled -> zero network calls (socket-blocked test); enabled -> only configured host.", "tests/unit/test_ai_client.py")
add("app/ai/guardrails.py", "ai", "Guardrails per doc 11 §3: number provenance, banned register, injection defence, human gate.", "docs/11 §3, docs/88", "payload + draft", "approved/rejected + reasons", "Invented number -> ERR-071 listing tokens; banned words rejected; injection fixture neutralised.", "tests/unit/test_ai_guardrails.py", "AI NEVER computes, approves, posts or decides.")
add("app/ai/commentary.py", "ai", "Commentary drafter: verified table in -> draft out -> stored as draft with provenance.", "ai/client, ai/guardrails, calc/bva, docs/11 §1", "VarianceRow[]", "commentary draft", "Guardrail applied; stored with source refs + prompt version; status draft.", "tests/unit/test_ai_commentary.py")
add("app/ai/prompts.py", "ai", "PROMPT-01..06 verbatim from doc 88, versioned; payload schemas per doc 11 §4.", "docs/88, docs/11 §4", "template id + payload", "rendered prompt", "Snapshot tests equal doc 88 texts; payload schema validation.", "tests/unit/test_ai_prompts.py")
add("app/api/main.py", "api", "FastAPI app factory: 127.0.0.1 only, per-launch token (doc 12), CORS locked, AppError -> JSON, OpenAPI export.", "docs/05 §1, docs/12", "config", "ASGI app", "OpenAPI endpoint set equals doc 05 catalogue; token-less call rejected.", "tests/api/test_main.py")
for route in ["health", "projects", "imports", "statements", "bva", "exceptions", "forecast", "exports", "settings", "adjustments", "allocations", "assumptions", "year_end", "close", "reconcile", "alerts", "planning", "reports_builder", "connector"]:
    add(f"app/api/routes_{route}.py", "api", f"REST routes for {route} per doc 05 (M0 rewrite) + doc 90 schemas: pydantic models, status codes, error codes, pagination, jobs.", f"api/main, docs/05 §{route}, docs/90, docs/63", "HTTP requests", "JSON responses", "Contract tests per endpoint: happy path, every listed error, money-as-string, pagination, unknown-field rejection" + ("; suggestion/apply all three modes + ERR-046/005/002; rectification-journal totals net to zero" if route == "exceptions" else "") + ("; kind=journal with the three formats + ERR-046 on an empty queue; included findings -> exported" if route == "exports" else "") + ("; enrich + control-file + tb-check endpoints" if route == "imports" else "") + ".", f"tests/api/test_routes_{route}.py", "Thin: validate -> call service -> return. No SQL, no money math in routes.")
add("app/cli/main.py", "cli", "CLI: `fpa run-month-end`, `fpa import`, `fpa pull --period --sources [--mock]` (Dynamics 365 pull via connector_service; `--mock` starts tools/mock_d365.py), `fpa acceptance`, `fpa check`, `fpa export` — scriptable, meaningful exit codes.", "services/month_end, services/connector_service, docs/60", "argv", "exit code + reports", "CLI golden run exit 0 on sample corpus; `fpa pull --mock` for 2025-P07 stages the parity batch and exits 0; failure exit codes documented and tested.", "tests/integration/test_cli.py")
add("app/desktop/shell.py", "desktop", "Desktop shell: free local port, per-launch token, pywebview window, single-instance lock, clean shutdown.", "api/main, ui build, docs/12, docs/16", "-", "running app", "Headless-safe smoke; second instance refused; shutdown closes DB cleanly.", "tests/unit/test_desktop_shell.py")

# =====================================================================================
# M4 — UI
# =====================================================================================
add("ui/package.json", "ui", "React+TS+Vite EXACT-pinned deps: react, react-dom, react-router, zustand, decimal.js (display only), echarts; vitest, eslint, axe.", "docs/04 §6, docs/15", "-", "installable UI", "npm ci && npm run build exit 0; no caret/tilde ranges.", "-", "UI never computes money: it formats API-provided decimal strings.")
for cfg in ["ui/vite.config.ts", "ui/tsconfig.json", "ui/tsconfig.node.json", "ui/index.html", "ui/eslint.config.js", "ui/src/main.tsx", "ui/src/App.tsx", "ui/src/lib/format.ts"]:
    add(cfg, "ui", f"UI project file {cfg} per docs 04/13/15 (format.ts = decimal-string display formatting ONLY, no money arithmetic; eslint rule bans inline user strings).", "docs/13, docs/15, docs/53, docs/27", "-", "working UI build", "npm run build includes it; format.ts unit tests for grouping (en-IN/en-US), negatives in parentheses, zero exponent.", "ui/src/lib/format.test.ts" if "format" in cfg else "-")
add("ui/src/api/client.ts", "ui", "Typed API client matching doc 05/90; decimal-as-string; error -> doc-55 message mapping; token header.", "docs/05, docs/90, docs/55", "endpoint calls", "typed DTOs", "Contract fixture tests against recorded API fixtures (doc 89 §6).", "ui/src/api/client.test.ts")
add("ui/src/theme/tokens.ts", "ui", "Design tokens single source per doc 53 §4 (light/dark hex values) + CSS bridge.", "docs/53 §4", "-", "token exports", "Token test computes contrast ratios ≥ doc 53 table; zero undefined tokens referenced anywhere (script).", "ui/src/theme/tokens.test.ts")
for comp in ["DataTable", "VarianceBadge", "DrillDrawer", "FileDrop", "WizardSteps", "FindingCard", "PeriodPicker", "ExportButton", "EmptyState", "ErrorBanner", "ConfirmDialog", "KpiCard", "LayerSelector", "JobToast", "ConnectionCard"]:
    add(f"ui/src/components/{comp}.tsx", "ui", f"Shared component {comp} per doc 53 §2: typed props, keyboard behaviour, aria, not colour-only.", "docs/53 §2, docs/57, theme/tokens", "props", "JSX", "Unit + axe tests; keyboard path test.", f"ui/src/components/{comp}.test.tsx")
for store in ["projectStore", "periodStore", "importStore", "findingStore", "forecastStore", "uiStore"]:
    add(f"ui/src/stores/{store}.ts", "ui", f"Zustand store {store}: server state via api/client only; job registry survives navigation (uiStore); no money logic.", "api/client, docs/13 §4", "actions", "state", "Store unit tests incl. error path and job persistence.", f"ui/src/stores/{store}.test.ts")
SCREENS = [("S01", "dashboard", "Period dashboard"), ("S02", "projects", "Projects"), ("S03", "import", "Import wizard"), ("S04", "mapping", "Mapping studio"),
           ("S05", "trial-balance", "Trial balance"), ("S06", "statements", "Statements viewer"), ("S07", "bva", "BvA explorer"), ("S08", "exceptions", "Exception inbox"),
           ("S09", "forecast", "Forecast studio"), ("S10", "scenarios", "Scenarios"), ("S11", "exports", "Export centre"), ("S12", "owners", "Master data"),
           ("S13", "settings", "Settings"), ("S14", "audit", "Audit trail"), ("S15", "help", "Help & walkthrough"), ("S16", "close", "Close management"),
           ("S17", "planning", "Planning studio"), ("S18", "reconcile", "Reconciliation"), ("S19", "alerts", "Alert centre")]
for sid, slug, desc in SCREENS:
    add(f"ui/src/pages/{sid}-{slug}/index.tsx", "ui", f"{sid} {desc} per doc 21 §{sid} (M0 rewrite): five states, doc-55 keys only, drill paths, keyboard map.", f"docs/21 §{sid}, docs/13, docs/55, docs/57, ui/src/api/client", "API DTOs", "rendered screen", "Component tests for all 5 states; axe pass; keyboard path; no number computed in component; every string from copy keys" + ("; suggested-fix panel renders for every finding (missing object = render error), apply/queue/dismiss flows incl. ERR-046 copy, verification banner, journal queue bar, all 28 rule names from the catalogue API" if sid == "S08" else "") + ("; rectification-journal card with format selector, disabled state + ERR-046 copy on empty queue" if sid == "S11" else "") + ("; connector chip + Refresh this month visible only for state signed_in/token_expired (token_expired renders Sign in again), Refresh -> job toast -> staged deep-links to S03 Validate, no_change toast copy" if sid == "S01" else "") + ("; step 0 Source cards Files / Dynamics 365 (ConnectionCard states not_configured/configured/signed_in/token_expired), period + sources checkboxes, pull progress per source, ERR-110…118 rendered with their actions, a staged pull lands at step 4 with the preset applied" if sid == "S03" else "") + ("; Connections tab: product/host/tenant/client/auth-mode form, write-only secret field with con.secret.safe, Sign in (waiting state + cancel), Test connection (companies + entity-check table with replacement picker), company picker, pull history, Disconnect confirm, what-we-read/never box, demo-ledger button only on the sample project; no token or secret ever rendered (DOM scan test)" if sid == "S13" else "") + ".", f"ui/src/pages/{sid}-{slug}/index.test.tsx")

# =====================================================================================
# M5 — EXPORTS
# =====================================================================================
add("app/exports/excel_pack.py", "exports", "Board Excel pack orchestrator per doc 09: 12 sheets, snapshot stamps, checks, ₹'000 variant as separate workbook.", "exports/sheet_*, docs/09", "period, project, layer", ".xlsx path", "Workbook opens; all sheets tie to calc objects (cell == value); Checks sheet lists every doc 09 §4 check.", "tests/unit/test_excel_pack.py", "Real Excel SUM formulas for subtotals; literals elsewhere; never float.")
for sheet in ["cover", "contents", "pl", "bs", "cf", "bva", "exceptions", "forecast", "kpis", "drilldata", "checks", "sources"]:
    add(f"app/exports/sheet_{sheet}.py", "exports", f"Excel sheet '{sheet}' per doc 09 §2 row + §3 formats + §5 safety.", "docs/09, calc/*, core/money", "calc objects", "openpyxl worksheet", "Golden-file cell assertions (values + number formats + formula presence); formula-injection guard on text cells.", f"tests/unit/test_sheet_{sheet}.py", "Colour never sole signal (P19).")
add("app/exports/ppt_pack.py", "exports", "PowerPoint deck orchestrator per doc 10: 8 slide types, blocked on failed checks (ERR-060).", "docs/10, exports/slide_*", "snapshot", ".pptx path", "Deck opens; every number == Excel pack number; blocked-generation case.", "tests/unit/test_ppt_pack.py")
for slide in ["title", "summary", "pl", "bridge", "exceptions", "forecast", "risks", "appendix"]:
    add(f"app/exports/slide_{slide}.py", "exports", f"PPT slide '{slide}' per doc 10 §2: native charts/tables, speaker notes with drill references, overflow policy.", "docs/10", "calc data", "pptx slide", "Slide numbers match Excel golden values; notes present; overflow splits, never truncates numbers.", f"tests/unit/test_slide_{slide}.py")
add("app/exports/journal_export.py", "exports", "Rectification journal writer per doc 26 §7: queued suggestion lines of a period -> d365fo_general_journal (.xlsx, entity field names + Readable sheet), d365bc_general_journal (.xlsx), generic_csv; ACCOUNTDISPLAYVALUE from source_account_ref or erp.d365fo.ledger_account_format; reports row + sha256; findings -> corrected/exported.", "store/exception_repo, store/report_repo, core/money, docs/26 §7, docs/07 §7.4, docs/55, docs/09 §5", "period + queued findings + format", "journal file + report row", "Golden files (doc 89 §6) cell-by-cell; nets to zero per finding and in total; decimal strings only; formula-injection guard; byte-identical re-export except the Readable timestamp; empty queue -> ERR-046, never an empty file; truncated TEXT at a word boundary with full text on Readable.", "tests/unit/test_journal_export.py", "The app never posts to an ERP; the file is a draft for the accountant (footer disclaimer from doc 55).")
add("app/exports/pdf_report.py", "exports", "Printable PDF summary from the same snapshot (reportlab); never re-computes.", "exports data objects, docs/09, docs/10", "snapshot", ".pdf", "PDF text extraction values == statement values.", "tests/unit/test_pdf_report.py")
add("app/exports/report_builder.py", "exports", "Saved report definitions -> Excel/PDF identical to fixed packs (doc 19 §J); KPI expression grammar evaluator per doc 69 (recursive descent, no eval).", "docs/19 §J, docs/69, docs/09", "report definition + snapshot", "workbook/pdf", "Definition round-trip; grammar rejection corpus (injection attempts) all rejected; precedence fixtures; numbers tie to calc fixtures.", "tests/unit/test_report_builder.py")
add("tests/integration/test_cross_artifact.py", "test", "Cross-artifact consistency: API value == Excel cell == PPT number == PDF text for the golden period, both layers.", "exports/*, api/*, docs/14 §3", "golden project", "assertions", "Any mismatch fails release.", "-")

# =====================================================================================
# M6 — SHIP
# =====================================================================================
add("scripts/check.py", "scripts", "One-command gate per doc 14 §5: ruff, mypy, pytest (not perf), coverage thresholds, UI lint/type/test, token check, money-AST check, full docs gate (scripts/docs_check_release.py, including bootstrap checks), schema↔doc-02 equality, secret/telemetry scan, outbound-host scan (only app/ai/client.py and app/connectors/transport.py may open sockets; literal hosts outside doc 12 §1 allow-lists fail), ERP-write scan (no POST/PATCH/DELETE/PUT to ERP hosts anywhere in app/connectors). Honest exit code.", "docs/14 §5, docs/15, docs/66, docs/12 §1", "-", "report", "Clean tree -> exit 0; each sub-check failure -> non-zero with the failing check named; no skip flags exist; a planted `requests.get('https://example.com')` in app/calc fails the host scan.", "-")
add("scripts/acceptance.py", "scripts", "Runs acceptance harness twice, diffs, writes evidence/acceptance_report.{json,md} + extras.json; verifies acceptance_justifications.json.", "test_acceptance, docs/14 §3", "-", "evidence pack", "Two runs byte-identical findings; report format per doc 14 §3.", "-")
add("scripts/docs_check_release.py", "scripts", "Full release docs gate: run every bootstrap check from scripts/docs_check.py, then numbered sections across docs 00–91, glossary coverage, WORK_PLAN-to-built-tree parity, FR-to-implemented-test/evidence parity, ERR/settings-to-code parity and OpenAPI-to-doc-05/90 parity. No skip flags; no bootstrap-only success advertised as a release pass.", "scripts/docs_check.py, docs/14 §5, docs/86 §1.1, docs/00_INDEX", "built repository + all docs", "release docs report", "Runs clean on the baselined doc set and built product; each check individually testable with a planted defect; a bootstrap failure propagates non-zero; missing product artefacts fail release checks.", "tests/unit/test_docs_check_release.py", "DEC-014 splits old M6 docs-check item without duplicating a deliverable path; bootstrap is WI-0008.")
add("scripts/build.py", "scripts", "Build: UI build -> PyInstaller -> Inno Setup installer; payload audit (no data/secrets, no tests/fixtures/connectors/tokens); bundles tools/mock_d365.py + erp_shapes/api + connector profiles + certifi CA bundle; SBOM + licence report (doc 81).", "packaging/*, docs/16, docs/81", "-", "installer .exe", "Fresh-VM install -> first month-end on sample project succeeds (doc 16 §4 checklist).", "-")
add("packaging/fpa.spec", "packaging", "PyInstaller spec: one-folder, pinned, reproducible paths.", "docs/16", "-", "app bundle", "Build on clean machine.", "-")
add("packaging/installer.iss", "packaging", "Inno Setup script: install/upgrade/uninstall, data preserved on upgrade (P15).", "docs/16 §2", "-", "installer", "Upgrade from prior version keeps projects (fixture test plan).", "-")
add(".github/workflows/ci.yml", "ci", "CI per doc 66: windows-latest, python+node, scripts/check.py, acceptance, docs_check_release, build smoke. No skipped gates.", "docs/66, docs/15", "-", "CI verdict", "Red CI blocks merge (branch protection documented in doc 66).", "-")
add("tests/perf/test_perf.py", "test", "Performance: 250k-row import + rules + exports within doc 14 §4 budgets on the reference profile, plus a 250k-row connector pull from the local mock (NFR-17: <= 300 s, <= 1 page resident); doc 67 §5 feasibility spike first.", "docs/14 §4, docs/67", "250k fixture (generated)", "timings", "Budgets asserted as numbers; regression > 10% fails CI.", "-")
add("docs/18_USER_GUIDE.md", "docs6", "Final user guide: first month-end walkthrough with real screenshots, month-2 rhythm, troubleshooting mapped to doc 22, tuning thresholds (doc 17 R2).", "docs/18, docs/52, docs/22, docs/55", "built product", "complete guide", "Tabletop (doc 14 §7): a stranger completes a month-end on the sample project using only this doc.", "-")
# Baseline verification of the remaining spec docs (cross-refs/IDs/depth) is one M6 docs-gate item, not 80 separate ones:
add("docs/00_INDEX.md", "docs6", "Final docs gate: run scripts/docs_check_release.py over docs 00–91; update §10 status; verify every doc's claims against gates (doc 34 truth audit).", "scripts/docs_check_release.py, docs/34", "all docs", "clean docs gate", "docs_check_release exit 0; README/00_INDEX status lines each trace to a gate artefact in evidence/.", "-")

# =====================================================================================
MILESTONE = {"docs0": "M0", "config": "M1", "core": "M1", "store": "M1", "data": "M1",
             "imports": "M2", "calc": "M2", "rules": "M2", "forecast": "M2", "planning": "M2", "adjust": "M2",
             "connectors": "M3", "services": "M3", "api": "M3", "cli": "M3", "desktop": "M3", "ai": "M3",
             "ui": "M4", "exports": "M5", "test": None, "scripts": "M6", "packaging": "M6", "ci": "M6", "docs6": "M6"}
MILESTONE_TITLES = {
    "M0": "Spec hardening + bootstrap docs checker — close the audit's P0/P1 contract gaps before product code",
    "M1": "Core & truth — foundations, schema = doc 02, coherent corpus + answer key, fixtures, acceptance harness (red by design)",
    "M2": "Engine — imports (incl. D365 transforms, enrichment, TB tie-out), calc, 28 rules + suggestions, forecast, planning, adjustments; acceptance gate turns green here",
    "M3": "Connector, services, API, CLI, AI — the Dynamics 365 pull lands through the pipeline and the spine runs end-to-end from the command line",
    "M4": "UI — 19 screens on the frozen API; five states, accessibility, tokens",
    "M5": "Exports — Excel pack, PPT deck, PDF, report builder; cross-artifact tie-out",
    "M6": "Ship — gates, packaging, CI, perf, user guide, final audits",
}
GATES = {
    "M0": "`scripts/docs_check.py` clean (sections, links, IDs, doc/§ references, ERR/FR/settings-key doc parity, FR↔WI↔planned-test matrix, period-id notation, no retired operational multi-agent terms, gate text parity); docs 05/21/44/03/55/31/20 at implementable depth per acceptance lines; every DEC recorded (DEC-007/008/009 accepted under DEC-010); cold M0 audit with no open defects.",
    "M1": "Schema-equality (doc 02 ↔ schema.sql, tables and columns incl. §7 deltas 1–14) green; corpus regenerates byte-identical; TB balanced per entity × period; answer key 36/19/13 asserted; ERP file and API shapes emitted; acceptance harness runs and reports 0/36 by design; all core tests green; coverage core ≥ 95%.",
    "M2": "Acceptance gate green (doc 14 §3): recall 36/36, High 19/19, controls 0/13, suggestion exactness, extras justified, two runs identical, 28/28 wired, ERP shape parity; statement/KPI/forecast/planning oracles green; malformed corpus `expected.json` exact.",
    "M3": "OpenAPI == doc 05 catalogue (incl. connector routes) and doc 90 fields; AI-off and connector-off socket test; connector parity bar (doc 14 §3) green against `tools/mock_d365.py` for both products incl. no-change and the five faults; connector security tests (doc 12 §8, incl. allow-list, redaction, keyring-only, state/PKCE, disconnect) green; CLI golden month-end exit 0 (file route and `fpa pull --mock`); job registry crash-recovery test; desktop shell launches the server and opens the UI placeholder.",
    "M4": "5-state + axe + keyboard tests on all 19 screens; token check zero-undefined; UI numbers == API fixtures; no inline strings; walkthrough (doc 18 §1) passes on the sample project.",
    "M5": "Cross-artifact tie-out 100% on golden period `2025-P07` (both layers); golden-file cell/slide tests incl. the three rectification-journal golden files; blocked-deck case; second-seed audit dataset generated and passed (doc 34 stream I).",
    "M6": "Fresh-machine install → sample month-end → pack out; perf budgets met or DEC; doc 16 §4 release checklist signed with evidence links; truth audit clean (doc 34 stream F); full `scripts/docs_check_release.py` gate green (includes all bootstrap checks).",
}

LAYER_RANK = {"docs0": 0, "config": 0, "core": 1, "store": 2, "data": 3, "test": 4,
              "imports": 0, "calc": 1, "rules": 2, "forecast": 3, "planning": 4, "adjust": 5,
              "connectors": 0, "services": 1, "api": 2, "cli": 3, "desktop": 4, "ai": 5,
              "ui": 0, "exports": 0, "scripts": 0, "packaging": 1, "ci": 2, "docs6": 3}


def milestone_of(item: dict) -> str:
    m = MILESTONE.get(item["layer"])
    if m:
        return m
    # tests with no fixed layer milestone: place by what they test
    p = item["path"]
    if "acceptance" in p or "fixtures" in p:
        return "M1"
    if "cross_artifact" in p:
        return "M5"
    if "erp_shape" in p:
        return "M2"
    return "M6"


UNIVERSAL = """## How to use this plan (the sole agent reads this once per session)
- Work items are listed in **build order**. Take the first item whose status in `TASKBOARD.md` is not DONE and whose dependencies are DONE. Do not skip ahead because an item looks more interesting.
- A work item = **one deliverable + its paired test**. Extra files are allowed only when the item's spec requires them (e.g. a fixture it names) — list every file touched in the handover.
- Before starting an item: read the cited spec sections in full, write the contract (inputs / outputs / errors / formulas / keys) into the TASKBOARD note, write the paired test from the spec's oracle FIRST, watch it fail for the right reason, then implement.
- After finishing: run the self-verification protocol (`AGENT_PROMPT.md` §6), paste evidence into TASKBOARD, commit as `WI-####: <path>`.
- If the spec is silent or contradictory: **fix the owning doc first** (`docs/00_INDEX.md` §5 decides who owns the fact), log it in `docs/CHANGELOG.md` (+ DEC in doc 17 §4 if contract-affecting), then build. Design decisions → decide them (the owner delegated decisions, DEC-010): record `DEC-nnn (auto)` in doc 17 §4 with alternatives and reversal cost, write the behaviour into the owning doc, proceed.

### Universal edge-case checklist (every item: handled + tested, or stated N/A with reason in the handover)
Zero amounts / zero denominators · negative amounts and credit-normal accounts · empty input · single row · duplicate input · 250k-row posture · missing optional data (rule → not_run, export → labelled, UI → empty state) · locked period / locked version · superseded batch · expired waiver · hostile text (quotes, `=formula`, `<script>`, unicode, 10k-char description) · ambiguous dates/amounts · currency minor-unit exponent 0/2/3 · month-2 reuse (no month-1 assumptions hard-coded) · deterministic repeat run.

### Forbidden in every item
Float on money · TODO/TBD/stub/mock-only paths · weakening a test, bar or threshold · inventing an API/field/key/threshold not in the docs · a second implementation of an owned concern (doc 04 §2) · user text with "error"/"fraud" for findings · telemetry or network outside `app/ai/client.py` and `app/connectors/transport.py` (allow-listed hosts only, user-initiated jobs only) · hand-editing generated files (regenerate them) · committing data with real financials.
"""


# -------------------------------------------------------------------------------------
# Dependency resolution (doc 91): prose dependency strings -> WI ids. Unresolvable code
# references are a generator defect (fail loudly); doc-section references are informational.
# -------------------------------------------------------------------------------------
import fnmatch

INFORMATIONAL = {"profiler output", "exports data objects", "ui build", "all engine modules", "all docs",
                 "docs/23 workflow", "store"}
DOC_ITEM_PREFIXES = {}  # "docs/05" -> item path, filled from M0 docs items


def _aliases(path: str) -> set[str]:
    out = {path}
    stem = re.sub(r"\.(py|ts|tsx|sql|md|toml|json|yml|yaml|css)$", "", path)
    out.add(stem)
    for pre in ("app/ui/src/", "ui/src/", "app/", "tests/", "sample-data/"):
        if path.startswith(pre):
            out.add(path[len(pre):]); out.add(stem[len(pre):])
    out.add(Path(stem).name)
    out.add(Path(path).name)
    return out


def resolve_deps(order: list[dict]) -> list[str]:
    alias_index: dict[str, list[dict]] = {}
    for it in order:
        for a in _aliases(it["path"]):
            alias_index.setdefault(a, []).append(it)
    for it in order:
        if it["layer"] == "docs0":
            m = re.match(r"docs/(\d\d)_", it["path"])
            if m:
                DOC_ITEM_PREFIXES["docs/" + m.group(1)] = it
    problems = []
    for it in order:
        ids: list[str] = []
        for raw in re.split(r",|;| \+ |\+", it["deps"]):
            tok = re.sub(r"\s*\(.*?\)\s*", "", raw).strip()
            if not tok or tok in INFORMATIONAL or tok.startswith("§"):
                continue
            if tok.startswith("docs/"):
                key = tok.split(" ")[0][:7]
                d = DOC_ITEM_PREFIXES.get(key)
                if d and d is not it and d["id"] not in ids:
                    ids.append(d["id"])
                continue  # other doc references are read-first material, not build deps
            hits: list[dict] = []
            if "*" in tok:
                pat = tok.rstrip("/")
                for a, items in alias_index.items():
                    if fnmatch.fnmatchcase(a, pat) or fnmatch.fnmatchcase(a, "app/" + pat):
                        hits.extend(items)
            else:
                t = re.sub(r"\.(py|ts|tsx|sql|md|toml)$", "", tok)
                hits = alias_index.get(t) or alias_index.get(tok) or []
            hits = [h for h in hits if h is not it and (h["layer"] != "test" or "*" not in tok)]
            if not hits:
                problems.append(f"{it['id']} {it['path']}: cannot resolve dependency {raw.strip()!r}")
                continue
            for h in hits:
                if h["id"] not in ids:
                    ids.append(h["id"])
        it["dep_ids"] = ids
    return problems


def check_graph(order: list[dict]) -> list[str]:
    by_id = {it["id"]: it for it in order}
    pos = {it["id"]: i for i, it in enumerate(order)}
    problems = []
    # acyclic
    state: dict[str, int] = {}

    def visit(i: str, stack: list[str]) -> None:
        st = state.get(i, 0)
        if st == 1:
            problems.append("cycle: " + " -> ".join(stack + [i])); return
        if st == 2:
            return
        state[i] = 1
        for d in by_id[i]["dep_ids"]:
            visit(d, stack + [i])
        state[i] = 2

    for it in order:
        visit(it["id"], [])
    for it in order:
        for d in it["dep_ids"]:
            dep = by_id[d]
            if dep["milestone"] > it["milestone"]:
                problems.append(f"{it['id']} ({it['milestone']}) depends on later-milestone {d} ({dep['milestone']}) {dep['path']}")
            elif pos[d] > pos[it["id"]]:
                problems.append(f"{it['id']} precedes its dependency {d} in build order")
    return problems


def topo_order(items: list[dict]) -> list[dict]:
    """Stable topological order within the given list: dependencies first, ties by (layer rank, idx)."""
    by_id = {it["id"]: it for it in items}
    done: set[str] = set()
    out: list[dict] = []
    remaining = sorted(items, key=lambda it: (LAYER_RANK.get(it["layer"], 9), it["_idx"]))
    while remaining:
        progressed = False
        for it in list(remaining):
            if all((d not in by_id) or (d in done) for d in it["dep_ids"]):
                out.append(it); done.add(it["id"]); remaining.remove(it); progressed = True
                break
        if not progressed:
            out.extend(remaining); break  # cycle — reported by check_graph
    return out


def main() -> None:
    for i, it in enumerate(ITEMS):
        it["milestone"] = milestone_of(it)
        it["_idx"] = i
    order = sorted(ITEMS, key=lambda it: (it["milestone"], LAYER_RANK.get(it["layer"], 9), it["_idx"]))
    for n, it in enumerate(order, 1):
        it["id"] = f"WI-{n:04d}"  # provisional ids for resolution
    by_path = {it["path"]: it["id"] for it in order}
    paths = set(by_path)
    assert len(paths) == len(order), "duplicate path in ITEMS"
    problems = resolve_deps(order)
    # dependencies first within each milestone (doc 91 §1 rule 4), then renumber
    final: list[dict] = []
    for m in sorted(MILESTONE_TITLES):
        final.extend(topo_order([it for it in order if it["milestone"] == m]))
    old_to_new = {}
    for n, it in enumerate(final, 1):
        old_to_new[it["id"]] = f"WI-{n:04d}"
    for it in final:
        it["id"] = old_to_new[it["id"]]
        it["dep_ids"] = [old_to_new[d] for d in it["dep_ids"]]
    order = final
    problems += check_graph(order)
    if problems:
        raise SystemExit("WORK PLAN GENERATOR DEFECTS (fix the generator, doc 91 §2):\n  " + "\n  ".join(problems))

    out = ["# WORK PLAN — the sole agent's sequenced build (generated by `tools/generate_work_plan.py`)\n",
           f"Total work items: **{len(order)}** across milestones M0–M6. Generated — do not hand-edit; change the generator and re-run. "
           "Status and evidence live in `TASKBOARD.md`; process in `AGENT_PROMPT.md`; gates in `docs/14` and `docs/86`.\n",
           UNIVERSAL]
    out.append("## Milestone summary\n\n| Milestone | Scope | Items | Exit gate |\n|---|---|---|---|")
    for m in sorted(MILESTONE_TITLES):
        cnt = sum(1 for it in order if it["milestone"] == m)
        out.append(f"| **{m}** | {MILESTONE_TITLES[m]} | {cnt} | {GATES[m]} |")
    out.append("")
    cur = None
    for it in order:
        if it["milestone"] != cur:
            cur = it["milestone"]
            out.append(f"\n---\n\n## {cur} — {MILESTONE_TITLES[cur]}\n\n**Exit gate:** {GATES[cur]}\n")
        exists = (ROOT / it["path"]).exists()
        flag = " · _file exists — re-verify against the acceptance line before marking DONE_" if exists else ""
        out.append(f"### {it['id']} · `{it['path']}` · {it['layer']}{flag}")
        out.append(f"- **Mission:** {it['purpose']}")
        dep_ids = ", ".join(it["dep_ids"]) if it["dep_ids"] else "—"
        out.append(f"- **Depends on (WI ids, must be DONE):** {dep_ids}  ·  **Read first:** {it['deps'] or 'docs/00_INDEX.md'}")
        out.append(f"- **Inputs:** {it['inputs'] or '—'}  ·  **Provides:** {it['outputs'] or it['purpose']}")
        out.append(f"- **Acceptance (evidence required):** {it['acceptance'] or 'Spec-conformance review + paired tests green.'}")
        out.append(f"- **Paired test:** `{it['tests']}`" if it["tests"] and it["tests"] != "-" else "- **Paired test:** none — state why in the handover (docs/config items are verified by the docs gate or the build).")
        if it["notes"]:
            out.append(f"- **Notes:** {it['notes']}")
        out.append("")
    (ROOT / "docs/WORK_PLAN.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    with open(ROOT / "docs/WORK_PLAN.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, lineterminator="\n", fieldnames=["id", "path", "layer", "milestone", "depends_on", "read_first", "tests"])
        w.writeheader()
        for it in order:
            w.writerow({"id": it["id"], "path": it["path"], "layer": it["layer"], "milestone": it["milestone"],
                        "depends_on": " ".join(it["dep_ids"]), "read_first": it["deps"], "tests": it["tests"]})

    tb = ROOT / "TASKBOARD.md"
    if not tb.exists():
        lines = ["# TASKBOARD — live ledger of the sole agent (hand-maintained; regenerate WORK_PLAN, never this file)\n",
                 "Statuses: `queued` · `in_progress` · `done` (evidence pasted) · `blocked` (class-C only: evidence + next step) · `exists-unverified` (file predates this plan; re-verify before `done`).\n",
                 "## Owner attention (informational — the owner delegated decisions, DEC-010; list what was decided and where, never a queue)\n- none\n",
                 "## Current position\n- Milestone: M0 · In progress: — · Last session: —\n",
                 "## Items\n", "| WI | Path | Milestone | Status | Evidence / note |", "|---|---|---|---|---|"]
        for it in order:
            st = "exists-unverified" if (ROOT / it["path"]).exists() else "queued"
            lines.append(f"| {it['id']} | `{it['path']}` | {it['milestone']} | {st} | |")
        tb.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"work items: {len(order)}; milestones: " + ", ".join(f"{m}={sum(1 for it in order if it['milestone']==m)}" for m in sorted(MILESTONE_TITLES)))


if __name__ == "__main__":
    main()
