# 04 — TECHNICAL ARCHITECTURE

> Owner of: stack, module map, data flow, ADRs. Coding rules: doc 15. Security: doc 12.

## 1. Shape: modular monolith, local desktop
```
ui/ React+TS (Vite) ──HTTP 127.0.0.1:<ephemeral port>──▶ app/api FastAPI (thin routes)
   └─ served as static build by the desktop shell; no internet at runtime except two user-initiated, allow-listed edges: AI (doc 11) and the Dynamics 365 connector (doc 26 §8)
app/services/month_end.py — orchestrates the pipeline (the spine)
app/connectors (D365 pull → snapshot file) → app/imports → app/store (SQLite/WAL, one file per project folder) → app/calc → app/rules → app/forecast → app/exports
app/ai — optional edge module; imported lazily; absence/keylessness changes nothing else
app/desktop/shell.py — pywebview host: starts API, opens window, single-instance lock
```
Why Python (ADR-001): attempt #4 proved the data ecosystem (openpyxl/python-pptx/Decimal); attempt #2 proved the cost of a native core nobody could compile/verify in-sandbox. Deterministic integer money makes Python speed sufficient at 250k rows (doc 14 NFRs; if a hotspot fails, optimise that function — do not re-platform).
Why SQLite only (ADR-002): one storage engine, one file = backup/restore/upgrade simplicity; attempt #4's DuckDB+SQLite duality is rejected. Analytics queries at this scale are index-served (doc 02 §3).
Why local FastAPI, not direct file access from UI (ADR-003): one contract (doc 05) shared by UI, CLI, and tests; UI never touches the DB or computes money.

## 2. Module map & ownership (one owner per concern)
| Module | Owns | Must never |
|---|---|---|
| `app/core/money.py` | All money parse/format/round/allocate | Be bypassed (AST/static check in scripts/check) |
| `app/core/*` | errors, calendar, ids, hashing, audit, config, logging | Import from engine modules (core depends on nothing app-level) |
| `app/store/*` | Persistence only (parameterised SQL, dataclasses out) | Contain business rules |
| `app/imports/*` | Parse→profile→map→validate→commit pipeline | Write GL rows except via commit.py |
| `app/connectors/*` | Dynamics 365 pull: Entra ID auth (msal), allow-listed HTTPS transport (httpx), OData/BC API paging, profile entity check, deterministic snapshot workbook (doc 26 §8) | Touch the store except `connector_pulls`/`connector_profiles` via the service; write `gl_rows` or staging tables (it produces a *file* that `app/imports` ingests); hold a token anywhere but the OS keyring; call any host outside the allow-list |
| `app/calc/*` | Statements, KPI, BvA, bridge, drilldown (pure over store reads) | Write anything |
| `app/rules/*` | 28 pure rule functions + runner/workflow (doc 07) | Read files or network; receive anything but rows+params |
| `app/forecast/*` | Methods, engine, scenarios, rolling | Mutate locked runs |
| `app/exports/*` | Render from calc objects/snapshots | Re-compute a number |
| `app/ai/*` | Draft text under guardrails | Compute numbers; run when disabled |
| `app/api/*`, `app/cli/*` | Transport: validate → call service → serialise | SQL or money math |
Dependency rule: arrows point one way (transport → services → engine → store/core). Circular import = build failure (import-linter or equivalent check in scripts/check).

## 3. Data flow (month-end)
Files (dropped by the analyst **or** written by the Dynamics 365 connector as a snapshot workbook — the pipeline cannot tell the difference) → staging tables (raw preserved) → validated staging → atomic commit → gl_rows → calc snapshots → rules (findings persisted) → forecast run → export snapshot (report registry stores the exact run/version ids) → files on disk. Every stage writes audit + status; the month-end checklist (S01/S03) is a view over real stage records, resumable after crash at stage granularity.

## 4. Concurrency & performance posture
Single user; background jobs for import/rules/forecast/exports behind a job registry with progress + cancel; UI never blocks >100ms on request thread. Budgets in doc 14 §4 (250k rows). No caching layer in v1 except statement snapshot memoisation keyed by (period, batch watermark) — cache invalidation by watermark change only.

## 5. Configuration & project layout
Project folder: `project.db`, `imports/` (original files, hash-named), `exports/`, `backups/`, `logs/`, `settings.json` (non-secret). App install dir holds no user data (upgrade-safe, doc 16). Settings precedence: project settings > user settings > defaults in config.py; every value validated with plain-language errors.

## 6. Technology budget (≤12 runtime deps, pinned, licence-checked)
Python: fastapi, uvicorn, pydantic, openpyxl, python-pptx, reportlab (PDF), pywebview, keyring (secrets: AI key, connector tokens), httpx (connector transport, ADR-010), msal (Entra ID auth, ADR-010) — 10 of the ≤12 budget — + stdlib (sqlite3, decimal, hashlib). UI: react, react-dom, react-router, zustand, echarts, decimal.js (display-only). Any addition requires an ADR line here + doc 12 licence entry.

## 7. ADR log
ADR-001 Python engine (above) · ADR-002 SQLite only · ADR-003 Local API contract · ADR-004 Money as integer minor units + Decimal boundary · ADR-005 AI edge-only, off-default (doc 11) · ADR-006 Windows-first packaging, macOS deferred Phase 3 · ADR-007 Findings keyed by canonical finding_key (doc 07) · ADR-008 Sample corpus generated from one coherent plan (MASTER_PLAN §6) · ADR-009 Connector-as-file-producer (DEC-013): every connector writes a deterministic snapshot workbook in a shipped preset shape and hands it to the unchanged import pipeline — one code path for files and APIs, idempotency and drill-to-source for free, no second validation/commit surface to secure; alternatives rejected: direct staging-table writes (bypasses file hashing/idempotency, duplicates validation), direct `gl_rows` writes (bypasses everything) · ADR-010 `msal` + `httpx` for the connector (DEC-013): msal because Entra ID auth-code+PKCE, token cache serialisation and refresh semantics are Microsoft-maintained and audited, hand-rolling OAuth is a security liability; httpx because it is small, synchronous-capable, has first-class timeouts, TLS verification on by default and a transport hook where the egress allow-list is enforced; alternatives rejected: `requests` (no per-request transport hook as clean, larger), `aiohttp` (async-only, the engine is synchronous), stdlib `urllib` (no connection pooling, clumsy retries). New ADRs append here; superseded ADRs are marked, never deleted.
