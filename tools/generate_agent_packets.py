#!/usr/bin/env python3
"""
Generate the complete file manifest + one extreme-detailed agent prompt per file.

Run:  python tools/generate_agent_packets.py
Outputs:
  docs/FILE_MANIFEST.csv
  docs/FILE_MANIFEST.md
  agent-prompts/PKT-####-<slug>.md   (one per work packet)
  agent-prompts/INDEX.md

Design rule: ONE packet = ONE file = ONE agent. No agent touches two files.
Shared contracts live in docs/ (00..15) and in packets' "READ FIRST" section.
"""
import csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKETS = []  # (path, layer, purpose, deps, inputs, outputs, acceptance, tests, notes)

def add(path, layer, purpose, deps="", inputs="", outputs="", acceptance="", tests="", notes=""):
    PACKETS.append(dict(path=path, layer=layer, purpose=purpose, deps=deps,
                        inputs=inputs, outputs=outputs, acceptance=acceptance,
                        tests=tests, notes=notes))

# ---------------------------------------------------------------- foundation
add("pyproject.toml","config","Project metadata, pinned deps (fastapi, pydantic, openpyxl, python-pptx), pytest/ruff/mypy config.","docs/04_TECHNICAL_ARCHITECTURE.md","-","Importable package `app`; `pip install -e .` works","`pip install -e .` exit 0; `python -c 'import app'` exit 0","-","Pin exact versions. No unpinned dep.")
add("README.md","config","Human entry point: what it is, install, run, verify commands, disclaimer.","docs/00_INDEX.md","-","New user runs app in <10 min following only this file","Commands copy-paste verbatim on clean Windows","-","No marketing claims not backed by a gate.")
add(".gitignore","config","Ignore data, venv, build, secrets, generated outputs.","docs/12_SECURITY_PRIVACY.md","-","`git status` clean after full run","Run app+tests; git status shows no data files","-")
add("app/__init__.py","core","Package marker + __version__ single source.","pyproject.toml","-","app.__version__","Import test","tests/unit/test_smoke.py")
add("app/core/errors.py","core","Typed error catalogue: every error = code, user_message, retryable, hint. FP&A-ERR-001..099.","docs/04 §Errors","error code","AppError instances; JSON-serialisable","Every code unique; no raw exception reaches API/UI","tests/unit/test_errors.py","Plain-language messages (analyst, not developer).")
add("app/core/money.py","core","THE ONLY money module: Decimal minor-unit math, parse/format, rounding (ROUND_HALF_UP), largest-remainder allocation, currency-safe add/sub/mul/div.","docs/03_CALCULATION_SPEC.md","str/int/Decimal","Decimal; formatted str","Float input raises TypeError; 0.1+0.2==0.3 exactly; allocation sums to total","tests/unit/test_money.py","AI and UI NEVER compute money; they call this.")
add("app/core/calendar.py","core","Fiscal calendar: periods, FY, quarters, 4-4-5 optional, period arithmetic, YoY/PY lookups.","docs/02_DATA_DICTIONARY.md","fy_start_month, calendar type","Period objects","Period round-trip; PY mapping correct for leap years","tests/unit/test_calendar.py")
add("app/core/ids.py","core","Deterministic IDs: batch_id, row_id (hash of source file+row), finding_id, uuid helpers.","docs/02","source hash + row no","stable id str","Same input -> same id (idempotent re-import)","tests/unit/test_ids.py")
add("app/core/hashing.py","core","SHA-256 file/row hashing, checksum manifest for reproducibility.","docs/12","bytes/path","hex digest","Known-vector test passes","tests/unit/test_hashing.py")
add("app/core/audit.py","core","Append-only audit log writer: who/when/what/before/after/hash-chain.","docs/12; docs/05 §Audit","event dict","audit row; chain verifies","Tampered row -> verify() fails","tests/unit/test_audit.py")
add("app/core/config.py","core","Settings: paths, tolerances defaults, AI off-by-default flag, feature flags. Env+file, validated.","docs/04","env/file","Settings object","Invalid config -> FP&A-ERR with hint","tests/unit/test_config.py")
add("app/core/logging.py","core","Structured local logging, no telemetry, PII/financial redaction.","docs/12","-","log files in project dir","No network call; secrets redacted in test","tests/unit/test_logging.py")

# ---------------------------------------------------------------- store
add("app/store/schema.sql","store","SQLite schema: ALL tables (projects, periods, imports, gl_rows, mappings, budgets, forecasts, exceptions, owners, audit, settings). Money as INTEGER minor units.","docs/02_DATA_DICTIONARY.md (every table/column)","-","DDL applies cleanly","Apply to empty DB; FK on; no orphan tables vs data dictionary","tests/unit/test_schema.py","One storage engine only: SQLite (lesson from attempt #2: no dual engines).")
add("app/store/db.py","store","Connection factory: WAL, FK on, migrations runner, transaction context manager.","schema.sql, core/errors","db path","sqlite3 connection","Migration idempotent; crash mid-txn leaves no partial data","tests/unit/test_db.py")
for repo, tbl in [("import_repo","imports/batches/rows"),("gl_repo","gl_rows queries: by period/account/entity/cc/voucher"),
                  ("mapping_repo","account mappings + versions"),("master_repo","entities/accounts/cost centres/owners"),
                  ("budget_repo","budget lines + versions"),("forecast_repo","forecast runs + lines"),
                  ("exception_repo","findings, status, owner, comments"),("report_repo","generated reports registry"),
                  ("period_repo","period open/close/lock state")]:
    add(f"app/store/{repo}.py","store",f"Repository for {tbl}. Parameterised SQL only; returns dataclasses; money as int minor units.","store/db.py, core/money, docs/02",f"{tbl} filters","dataclass lists / ids","CRUD round-trip; SQL-injection test; money round-trip exact","tests/unit/test_"+repo+".py","No business logic here - persistence only.")

# ---------------------------------------------------------------- imports
add("app/imports/models.py","imports","Dataclasses: RawFile, RawRow, StagedRow, ImportBatch, ValidationIssue, ControlTotals.","docs/02, docs/06_IMPORT_SPEC","-","typed models","Type-check mypy strict","tests/unit/test_import_models.py")
add("app/imports/parser_csv.py","imports","CSV/TSV parser: encoding sniff, delimiter sniff, header detection, row numbers preserved.","imports/models","file path","RawRow[]","Malformed rows quarantined, never silently dropped (P13)","tests/unit/test_parser_csv.py")
add("app/imports/parser_xlsx.py","imports","XLSX parser (openpyxl read-only): sheet selection, header row, merged-cell handling, formula cells -> cached values flagged.","imports/models","file path","RawRow[]","113-xlsx-corpus lesson: every sheet accounted in report","tests/unit/test_parser_xlsx.py")
add("app/imports/profiler.py","imports","Column profiler: dtype guess, null %, distinct, sample values -> mapping suggestions input.","imports/models","RawRow[]","ColumnProfile[]","Deterministic output for fixture","tests/unit/test_profiler.py")
add("app/imports/mapping.py","imports","Mapping engine: apply saved mapping profile (source col -> canonical field), versioned, reusable next month (P11/P14).","imports/models, store/mapping_repo","profile + RawRow","StagedRow[]","Same profile next month = zero re-mapping","tests/unit/test_mapping.py")
add("app/imports/mapping_suggest.py","imports","Deterministic header-similarity suggestions (no AI required); AI suggestion optional hook.","profiler output","headers","ranked suggestions","Known headers -> correct top-1 in fixtures","tests/unit/test_mapping_suggest.py")
add("app/imports/validation.py","imports","Row validation: required fields, date/amount parse, debit=credit per voucher, duplicate detection, quarantine with reasons.","imports/models, core/money","StagedRow[]","valid[] + quarantine[] + issues[]","Nothing silently discarded; counts reconcile: in = valid+quarantined","tests/unit/test_validation.py")
add("app/imports/control_totals.py","imports","Control totals: row count, debit sum, credit sum, hash total vs user/ERP-declared totals.","core/money, imports/models","batch + declared totals","pass/fail + deltas","Mismatch blocks commit with plain-language error","tests/unit/test_control_totals.py")
add("app/imports/commit.py","imports","Atomic commit: staging -> GL store in ONE transaction; re-import = replace batch, never duplicate (idempotent by batch hash).","store/*, validation, control_totals","validated batch","batch_id + counts","Kill mid-commit -> DB unchanged (test); re-import same file -> same row count","tests/unit/test_commit.py","All-or-nothing (P12). Bulk insert batched (DEF-030 lesson: no row-by-row executemany).")
add("app/imports/trial_balance.py","imports","Trial balance check post-commit: total debit == total credit per entity/period; imbalance report to account level.","store/gl_repo, core/money","period","TB report","Planted imbalance fixture detected to the rupee","tests/unit/test_trial_balance.py")

# ---------------------------------------------------------------- calc
add("app/calc/statements.py","calc","P&L, Balance Sheet, Cash Flow (indirect) from GL + mappings. Every line drills to gl_rows.","store/gl_repo, core/money, docs/03","period, entity","Statement{lines[]}","BS balances (A=L+E); CF net == BS cash delta; oracle fixtures match to minor unit","tests/unit/test_statements.py","Oracle fixtures FIRST (attempt #2 lesson: fixtures before engine).")
add("app/calc/kpis.py","calc","KPI library: GM%, EBITDA, Opex ratio, WC days, DSO/DPO/DIO, cash conversion. Defined once, used by UI/Excel/PPT.","calc/statements, docs/03","statement + GL","KPI values + formula text","Each KPI hand-verified fixture","tests/unit/test_kpis.py")
add("app/calc/bva.py","calc","Budget-vs-Actual / Forecast-vs-Actual / PY: variance abs, %, contribution, materiality flags at lowest shared grain.","store/gl_repo,budget_repo, docs/03","period, version pair","VarianceRow[]","Hand-computed fixture matches; % variance zero-base handled (no div0 crash)","tests/unit/test_bva.py")
add("app/calc/attribution.py","calc","Variance bridge: volume / price / mix / FX / other decomposition where driver data exists; else explicit 'insufficient data'.","calc/bva","variance + drivers","bridge components summing to total variance","Components sum == total (minor unit)","tests/unit/test_attribution.py","Never fabricate a bridge without drivers.")
add("app/calc/drilldown.py","calc","Any aggregate -> voucher -> source row -> file+row number (P5 traceability chain).","store/gl_repo","aggregate key","row list + source refs","Every statement/BvA cell in fixtures drills to >=1 row","tests/unit/test_drilldown.py")

# ---------------------------------------------------------------- exceptions (24 rules, one file each)
RULES = [
 ("001","Duplicate voucher / duplicate posting"),("002","Same voucher, overlapping re-import (duplicate batch)"),
 ("003","Control-total mismatch on import"),("004","Unbalanced voucher (debit != credit)"),
 ("005","Posting to closed/locked period"),("006","Spend concentration / single-vendor spike by entity-account"),
 ("007","Suspense / clearing account ageing (1999-type)"),("008","Large one-off journal above threshold"),
 ("009","Manual journal by unusual user / outside hours"),("010","Cut-off: posting date vs document date across period end"),
 ("011","Stale recurring accrual not reversed"),("012","Negative expense / credit in expense account"),
 ("013","Account spike vs trailing average (material %)"),("014","Vendor-to-account mapping anomaly (new account for vendor)"),
 ("015","Recurring charge missing (expected SaaS/rent absent)"),("016","Accrual pattern break (accrued then never expensed)"),
 ("017","Material unbudgeted spend"),("018","Material BvA variance (abs AND % AND-test)"),
 ("019","Cumulative budget overrun trend"),("020","Round-amount journal clustering"),
 ("021","Threshold-splitting (multiple just-below-approval-limit)"),("022","Round-tripping / same-amount in-out"),
 ("023","Voucher with single-line imbalance risk"),("024","Dormant account sudden activity / new account first use"),
]
for num, name in RULES:
    add(f"app/rules/exc_{num}.py","rules",f"EXC-{num}: {name}. Pure function: (gl_rows, params) -> Finding[]. Deterministic, Decimal only, catalog key format `rule|entity|account|period|grain-key` exactly as docs/07.","docs/07_EXCEPTION_RULES_CATALOG.md EXC-"+num+", core/money, imports/models","GL rows + threshold params","Finding[] with evidence row_ids, amount, severity","Planted case fires exactly once; control case does NOT fire; key format snapshot test","tests/unit/test_exc_"+num+".py",
        "Cause of death in attempt #4: keys/thresholds diverged from answer key. The catalog doc is law - quote its sample case in your test.")
add("app/rules/engine.py","rules","Rule runner: runs enabled rules, dedupes by finding key, persists, assigns severity, links owners.","rules/exc_*, store/exception_repo","period, rule config","run report: per-rule counts","Two identical runs -> identical findings (stability bar)","tests/unit/test_rule_engine.py")
add("app/rules/owner_resolver.py","rules","Finding -> accountable owner (account->owner map, vendor owner, fallback FP&A lead) + due date by severity.","store/master_repo","finding","owner assignment","Unmapped -> explicit 'Unassigned' queue, never dropped","tests/unit/test_owner_resolver.py")
add("app/rules/workflow.py","rules","Finding lifecycle: New -> Acknowledged -> Explained -> Corrected -> Verified/Closed; waive with reason+expiry; full audit.","store/exception_repo, core/audit","finding id, action","new state","Illegal transition rejected; waive requires reason","tests/unit/test_finding_workflow.py")

# ---------------------------------------------------------------- forecast
METHODS=[("naive","Last-period / seasonal-naive baseline"),("moving_average","Moving average (n configurable)"),
 ("exponential_smoothing","Holt-Winters exponential smoothing"),("linear_trend","Linear trend / CAGR"),
 ("driver_based","Driver-based: revenue=volume*price etc. from driver table"),("seasonal","Seasonal index decomposition"),
 ("budget_phasing","Phasing: annual budget spread by seasonal/profile curve"),("manual","Manual analyst override layer (versioned, never overwrites system forecast)")]
for slug,name in METHODS:
    add(f"app/forecast/{slug}.py","forecast",f"Forecast method: {name}. Pure, deterministic, Decimal; returns series + method metadata.","docs/08_FORECAST_SPEC.md, core/money, core/calendar","history series + params","forecast series","Fixture series -> hand-verified values; no negative revenue unless allowed flag","tests/unit/test_fc_"+slug+".py")
add("app/forecast/engine.py","forecast","Forecast orchestration: pick method per account group, backtest (MAPE/bias), choose best, lock forecast version.","forecast/*, store/forecast_repo","period, scope","ForecastRun + accuracy report","Backtest reproducible; locked version immutable","tests/unit/test_forecast_engine.py")
add("app/forecast/scenarios.py","forecast","Scenarios: Base/Upside/Downside = versioned assumption deltas on drivers; compare scenarios side by side.","forecast/engine","assumption deltas","scenario series","Delta application exact; base untouched","tests/unit/test_scenarios.py")
add("app/forecast/rolling.py","forecast","Rolling forecast: actuals replace elapsed periods, forecast re-runs forward, version history kept (P11 monthly rhythm).","forecast/engine, core/calendar","new actuals period","new rolling version","Month+1 run does not mutate prior version","tests/unit/test_rolling.py")

# ---------------------------------------------------------------- exports
add("app/exports/excel_pack.py","exports","Board Excel pack orchestrator: builds workbook sheet-by-sheet, stamps version/source/date, tie-out sheet.","exports/sheets_*, docs/09_EXCEL_SPEC","period, project",".xlsx path","Workbook opens; all sheets tie to statements (cell==DB value)","tests/unit/test_excel_pack.py","Real Excel formulas for subtotals where spec requires, values elsewhere; never float.")
for sheet in ["cover","contents","pl","bs","cf","bva","exceptions","forecast","kpis","drilldata","checks","sources"]:
    add(f"app/exports/sheet_{sheet}.py","exports",f"Excel sheet '{sheet}': exact layout, headers, formats, print setup per docs/09 §{sheet}.","docs/09_EXCEL_SPEC.md, calc/*, core/money","statement/BvA data","openpyxl worksheet","Golden-file cell assertions (values + number formats)","tests/unit/test_sheet_"+sheet+".py","Colour never sole signal: +/- signs and labels too (P19).")
add("app/exports/ppt_pack.py","exports","PowerPoint deck orchestrator (python-pptx): title, exec summary, P&L, BvA bridge, exceptions, forecast, appendix.","docs/10_PPT_SPEC","period data",".pptx path","Deck opens; every number == Excel pack number (cross-artifact test)","tests/unit/test_ppt_pack.py")
for slide in ["title","summary","pl","bridge","exceptions","forecast","risks","appendix"]:
    add(f"app/exports/slide_{slide}.py","exports",f"PPT slide '{slide}' per docs/10 layout: native charts/tables, speaker notes = data source + drill reference.","docs/10_PPT_SPEC.md","calc data","pptx slide","Slide numbers match Excel golden values","tests/unit/test_slide_"+slide+".py")
add("app/exports/pdf_report.py","exports","Printable PDF summary (same numbers, generated from same data objects - never re-computed).","exports data objects","period",".pdf","PDF values == statement values in test extraction","tests/unit/test_pdf_report.py")

# ---------------------------------------------------------------- AI (never computes money)
add("app/ai/client.py","ai","LLM client abstraction: OFF by default; provider config; timeout; every call logged with prompt hash. No key -> app fully works.","docs/11_AI_SPEC, core/config","prompt","text + usage","AI disabled -> zero network calls (test with socket blocked)","tests/unit/test_ai_client.py")
add("app/ai/guardrails.py","ai","Guardrails: input = aggregated/anonymised figures only; output validated (no new numbers: every number in AI text must exist in input payload); prompt-injection screening of imported text (P18).","docs/11, core/money","payload + draft","approved/rejected + reasons","Draft containing invented number is rejected (fixture)","tests/unit/test_ai_guardrails.py","AI NEVER computes, approves, posts or decides (P3). It drafts words around verified numbers.")
add("app/ai/commentary.py","ai","Variance commentary drafter: verified variance table in -> narrative draft out -> analyst edits -> saved as versioned commentary.","ai/client, ai/guardrails, calc/bva","VarianceRow[]","commentary draft","Guardrail test; commentary stored with source variance ids","tests/unit/test_ai_commentary.py")
add("app/ai/prompts.py","ai","Versioned prompt templates PROMPT-01..06 (commentary, exec summary, exception explanation, forecast narrative, Q&A, board highlights).","docs/11","template id + payload","rendered prompt","Snapshot tests per template","tests/unit/test_ai_prompts.py")

# ---------------------------------------------------------------- API + CLI + desktop
add("app/api/main.py","api","FastAPI app factory: local-only bind 127.0.0.1, CORS locked to local UI, error handlers mapping AppError->JSON.","docs/05_API_CONTRACT","config","ASGI app","OpenAPI matches docs/05 endpoint-for-endpoint","tests/api/test_main.py")
for route in ["projects","imports","statements","bva","exceptions","forecast","exports","settings","health"]:
    add(f"app/api/routes_{route}.py","api",f"REST routes for {route} per docs/05_API_CONTRACT.md: request/response pydantic models, status codes, error codes.","api/main, docs/05 §"+route,"HTTP requests","JSON responses","Contract tests per endpoint incl. error paths","tests/api/test_routes_"+route+".py","Thin: validate -> call service -> return. No SQL, no money math in routes.")
add("app/services/month_end.py","services","THE month-end orchestrator (the 'army replacement' workflow): import->validate->TB->statements->BvA->rules->forecast->packs, resumable checklist with per-step status.","all engine modules","project, period","run state + artefacts","Golden month-end run on sample corpus completes; re-run resumes, not restarts","tests/integration/test_month_end.py","This is the product's spine. One click, one analyst, board pack out.")
add("app/services/dashboard.py","services","Dashboard aggregates: period KPIs, top variances, open findings by owner/severity, forecast accuracy.","calc/*, store/*","project, period","dashboard DTO","Values tie to calc fixtures","tests/unit/test_dashboard_service.py")
add("app/cli/main.py","cli","CLI: `fpa run-month-end`, `fpa import`, `fpa acceptance`, `fpa check` - scriptable, exit codes meaningful.","services/month_end","argv","exit code + reports","CLI golden run exit 0 on sample corpus","tests/integration/test_cli.py")
add("app/desktop/shell.py","desktop","Desktop shell: starts API on free local port, opens UI window (pywebview), single-instance lock, clean shutdown.","api/main, ui build","-","running app","Launch test (headless-safe smoke)","tests/unit/test_desktop_shell.py")

# ---------------------------------------------------------------- UI
add("ui/package.json","ui","React+TS+Vite pinned deps: react, react-router, zustand, decimal.js (display only), echarts, ag-grid.","docs/04","-","installable UI","npm ci && npm run build exit 0","-","UI never computes money: it formats API-provided decimal strings.")
add("ui/src/api/client.ts","ui","Typed API client generated to match docs/05; decimal-as-string handling; error -> user message mapping.","docs/05","endpoint calls","typed DTOs","Contract fixture tests","ui/src/api/client.test.ts")
add("ui/src/theme/tokens.ts","ui","Design tokens single source (colours, spacing, type) + CSS bridge. Every token referenced must be defined.","docs/13_UI_UX_SPEC","-","token exports","Token-check script: zero undefined tokens (attempt #2 defect class)","ui/src/theme/tokens.test.ts")
SCREENS=[("S01","dashboard","Period dashboard: KPIs, top variances, findings, close progress"),
("S02","projects","Project list/create/open, sample project"),
("S03","import","Import wizard: drop files, profile, map, validate, commit"),
("S04","mapping","Mapping studio: save/reuse profiles, unmapped queue"),
("S05","trial-balance","Trial balance & import quality report"),
("S06","statements","P&L/BS/CF viewer with drilldown to voucher/row"),
("S07","bva","BvA explorer: filters, variance table, bridge chart, commentary editor"),
("S08","exceptions","Exception inbox: findings by owner/severity, workflow actions"),
("S09","forecast","Forecast studio: method per group, backtest, scenarios"),
("S10","scenarios","Scenario compare"),
("S11","exports","Export centre: Excel/PPT/PDF generation + history + checks"),
("S12","owners","Master data: entities, accounts, owners, thresholds"),
("S13","settings","Settings: tolerances, thresholds, AI toggle, backup/restore"),
("S14","audit","Audit trail viewer + verification"),
("S15","help","In-app help + guided first month-end walkthrough")]
for sid, slug, desc in SCREENS:
    add(f"ui/src/pages/{sid}-{slug}/index.tsx","ui",f"{sid} {desc}. Five states mandatory: loading/empty/error/success/partial. Plain-language copy per docs/13.","docs/13_UI_UX_SPEC "+sid+", ui/src/api/client","API DTOs","rendered screen","Component tests for all 5 states; axe a11y pass; no number computed in component","ui/src/pages/"+sid+"-"+slug+"/index.test.tsx")
for comp in ["DataTable","VarianceBadge","DrillDrawer","FileDrop","WizardSteps","FindingCard","PeriodPicker","ExportButton","EmptyState","ErrorBanner","ConfirmDialog","KpiCard"]:
    add(f"ui/src/components/{comp}.tsx","ui",f"Shared component {comp} per docs/13 component library; props typed; accessible (keyboard, aria, not colour-only).","docs/13, theme/tokens","props","JSX","Unit + a11y tests; storybook-less fixture render","ui/src/components/"+comp+".test.tsx")
for store in ["projectStore","periodStore","importStore","findingStore","forecastStore","uiStore"]:
    add(f"ui/src/stores/{store}.ts","ui",f"Zustand store {store}: server state via api/client only; no duplicated money logic.","api/client","actions","state","Store unit tests incl. error path","ui/src/stores/"+store+".test.ts")

# ---------------------------------------------------------------- sample data (coherent corpus - attempt #4 killer fix)
add("sample-data/generate_sample_data.py","data","COHERENT corpus generator: one plan -> budget and actuals = budget*(1+controlled noise); planted exceptions from answer key only; balancing legs computed, never hardcoded; deterministic seed.","docs/14_ACCEPTANCE, docs/07","seed","CSVs + answer_key.json","Regenerate -> byte-identical (hash test); TB balances; budget/actual coherence check","tests/data/test_corpus.py",
    "Attempt #4 died here: independent random budget/actuals created 370 false exceptions. Coherence is the spec.")
add("sample-data/answer_key.json","data","Planted-exception answer key: 32 plants + 8 controls, each {rule, key, entity, account, period, amount, severity}.","docs/07, generate_sample_data","-","JSON","Schema-valid; every plant traceable to a generator plant function","tests/data/test_answer_key.py")
add("sample-data/malformed/","data","Malformed corpus: bad encodings, missing columns, unbalanced vouchers, duplicate files - each with expected quarantine result.","docs/06","-","fixtures + expected.json","Import of each -> expected quarantine counts","tests/data/test_malformed.py","Directory packet: agent creates folder + >=10 fixture files + expected.json.")

# ---------------------------------------------------------------- tests / scripts / packaging / docs-as-code
add("tests/acceptance/test_acceptance.py","test","THE acceptance harness: load corpus -> run all rules -> recall >=29/32, controls 0/8 fire, high-severity 18/18, extras all justified, run twice identical.","app/rules/engine, sample-data","corpus","acceptance_report.json + verdict","This test IS the release gate (docs/14)","-","Red until green; never weaken bars to pass (attempt #4 honesty rule).")
add("tests/integration/test_cross_artifact.py","test","Cross-artifact consistency: UI API value == Excel cell == PPT slide == PDF for golden period.","exports/*, api/*","golden project","assertions","Any mismatch fails release","-")
add("tests/perf/test_perf.py","test","Performance: 250k-row import+rule run within docs/14 NFR budgets on reference hardware profile.","docs/14 NFRs","250k fixture","timings","Budgets as numbers in docs/14; regression >10% fails","-")
add("scripts/check.py","scripts","One-command gate: ruff, mypy, pytest (not perf), UI lint/type/test, token check, docs link check. Exit code honest.","docs/15_CODING_STANDARDS","-","report","Clean tree -> exit 0","-")
add("scripts/acceptance.py","scripts","Runs acceptance harness twice, diffs, writes evidence/acceptance_report.{json,md}.","tests/acceptance","-","evidence pack","Two runs byte-identical findings","-")
add("scripts/build.py","scripts","Build: UI build -> PyInstaller -> Inno Setup installer; payload audit (no data/secrets in installer).","packaging/*","-","installer .exe","Fresh-VM install -> first month-end on sample project succeeds","-")
add("packaging/fpa.spec","packaging","PyInstaller spec: one-folder, pinned, reproducible paths.","docs/16_PACKAGING","-","app bundle","Build on clean machine","-")
add("packaging/installer.iss","packaging","Inno Setup script: install/upgrade/uninstall, data preserved on upgrade (P15).","docs/16","-","installer","Upgrade from prior version keeps projects (fixture test plan)","-")
add(".github/workflows/ci.yml","ci","CI: windows-latest, python+node, scripts/check.py, acceptance, build smoke. No skipped gates.","docs/15","-","CI verdict","Red CI blocks merge (branch protection documented)","-")

# docs packets (agent writes doc, not code)
DOCS=[("00_INDEX","Master index, reading order by role, source-of-truth matrix"),
("01_PRD","Product requirements: personas, JTBD, scope in/out, success metrics"),
("02_DATA_DICTIONARY","Every table/field/type/example - schema.sql must match 1:1"),
("03_CALCULATION_SPEC","Every formula, rounding, variance, KPI - hand-worked examples"),
("04_TECHNICAL_ARCHITECTURE","Stack, module map, data flow, ADRs, tech budget <=12"),
("05_API_CONTRACT","Every endpoint, payload, error - routes must match 1:1"),
("06_IMPORT_SPEC","Formats, mapping, validation, quarantine, control totals"),
("07_EXCEPTION_RULES_CATALOG","EXC-001..024: logic, grain key, thresholds, sample+control case each"),
("08_FORECAST_SPEC","Methods, backtesting, scenarios, rolling rhythm"),
("09_EXCEL_SPEC","Sheet-by-sheet layout, formats, formulas, tie-out checks"),
("10_PPT_SPEC","Slide-by-slide layout, chart data, speaker notes"),
("11_AI_SPEC","AI boundary: never computes; payloads, guardrails, prompts, off-default"),
("12_SECURITY_PRIVACY","Local-only, encryption at rest option, injection, supply chain, SBOM"),
("13_UI_UX_SPEC","Screens S01..S15, 5 states, copy rules, accessibility WCAG 2.2 AA"),
("14_TESTING_ACCEPTANCE","NFR numbers, acceptance bars, evidence format, Definition of Done"),
("15_CODING_STANDARDS","Python/TS standards, money rules, review checklist, banned patterns"),
("16_PACKAGING_RELEASE","Build, installer, upgrade, versioning, release checklist"),
("17_ROADMAP_RISKS","Phases, cut lines, risk register, open questions OQ/DEC log"),
("18_USER_GUIDE","End-user guide: first month-end walkthrough, troubleshooting in plain language")]
for num, desc in DOCS:
    add(f"docs/{num}.md","docs",desc+". Zero TBD/placeholder: every claim is a number, a name, or an example.","docs/00_INDEX (after 00)","research + prior docs","complete doc","Docs-verify: all cross-refs/links resolve; every FR/rule/endpoint ID referenced exists","-","Write as if an agent who never met the user must build from this alone.")

# ---------------------------------------------------------------- expansion (docs 19/29/30, all-in-one completeness)
add("app/calc/quality_score.py","calc","Data-quality score per doc 29 S9: deductions table, never a bare number.","docs/29 S9, calc/statements","period data","score + deductions[]","Fixture deduction arithmetic exact; score without reasons impossible by type","tests/unit/test_quality_score.py")
add("app/imports/reconcile.py","imports","Subledger-to-GL reconciliation per doc 19I: match scoring amount/date/reference, unmatched both sides, tolerance.","docs/19I, docs/06","subledger rows + gl_rows","recon run + matches","Fixture: matched/unmatched counts tie both sides; tolerance boundary +-1 minor unit","tests/unit/test_reconcile.py")
for slug2, nm in [("drivers","Driver planning registry + computation (29 S2)"),("headcount","Headcount plan -> personnel cost (29 S3)"),("capex","Capex + depreciation schedule SLM/WDV (29 S4)"),("debt","Debt schedule + interest on avg balance (29 S5)"),("working_capital","WC from DSO/DPO/DIO targets (29 S6)"),("cash13","13-week cash forecast, calendar weeks (29 S6)"),("sensitivity","One/two-variable sensitivity tables (19H)"),("goal_seek","Goal seek by bisection on deterministic model, no-solution honest (19H)")]:
    add(f"app/planning/{slug2}.py","planning",nm+". Pure, Decimal, versioned inputs, every output traceable to inputs.","docs/29, docs/08, core/money","planning inputs + actuals/forecast","computed series + provenance","Doc 29 oracle for the module reproduced exactly; invalid input -> AppError with hint, never silent clamp","tests/unit/test_plan_"+slug2+".py")
add("app/planning/integrate.py","planning","Integrated 3-statement forecast articulation check per doc 29 S7: imbalance named, never plugged.","docs/29 S7, calc/statements","PL/BS/CF forecast series","balance verdict + broken link","Oracle 29 S7 passes; planted imbalance detected and named","tests/unit/test_plan_integrate.py")
add("app/services/close_service.py","services","Close management per doc 30: task instantiation, system-verified completion, blockers, sign-off.","docs/30, docs/23","project, period","close state DTO","System tasks derive from real states (test flips each source state); sign-off guard ERR-080","tests/unit/test_close_service.py")
add("app/services/alerts.py","services","Alert engine per doc 19K: KPI/finding/bias alerts, dedupe by key+period, 90-day retention.","docs/19K, docs/08 S6","snapshots","alerts","Duplicate run creates zero duplicate alerts; retention purge tested with injected clock","tests/unit/test_alerts.py")
add("app/exports/report_builder.py","exports","Saved report definitions -> Excel/PDF rendering identical to fixed packs (doc 19J). Safe KPI expression grammar evaluator lives here for custom KPIs.","docs/19J, docs/09","report definition + snapshot","workbook/pdf","Definition round-trip; expression grammar rejects code-like input; numbers tie to calc fixtures","tests/unit/test_report_builder.py")
for sid, slug3, desc in [("S16","close","Close management screen per doc 21/30"),("S17","planning","Planning studio: drivers/headcount/capex/debt/WC/13-week tabs per docs 21/29"),("S18","reconcile","Reconciliation screen per docs 19I/21"),("S19","alerts","Alert centre per docs 19K/21")]:
    add(f"ui/src/pages/{sid}-{slug3}/index.tsx","ui",f"{sid} {desc}. Five states, doc 21 acceptance, no money computed in UI.","docs/21 "+sid+", docs/13","API DTOs","rendered screen","Component tests all 5 states + axe","ui/src/pages/"+sid+"-"+slug3+"/index.test.tsx")
for num2 in ["19_DETAILED_FUNCTIONAL_SPEC","20_TRACEABILITY_MATRIX","21_SCREEN_SPEC_DETAILED","22_ERROR_CATALOG","23_STATE_MACHINES_AND_WORKFLOWS","24_DATA_FLOWS_ERD_AND_SEQUENCES","25_THREAT_MODEL","26_INTEGRATIONS_AND_ERP_FIELD_GUIDES","27_LOCALIZATION_CURRENCY_AND_UNITS","28_MASTER_DATA_COA_AND_TEMPLATES","29_BUDGETING_PLANNING_AND_KPI_SPEC","30_CLOSE_MANAGEMENT_SPEC","31_GLOSSARY","32_COMPETITIVE_PARITY_AND_POSITIONING","33_AGENT_EXECUTION_HANDBOOK","34_AUDIT_PLAYBOOK","35_OPERATIONS_SUPPORT_AND_SLA","36_NFR_CATALOG"]:
    add(f"docs/{num2}.md","docs",f"Expansion spec {num2}: complete, cross-referenced, zero placeholders; already authored by lead - agent REVISES only via integrator instruction, else verifies links/IDs.","docs/00_INDEX, docs/"+num2.split('_')[0],"existing doc","verified doc","Docs-verify: all IDs referenced exist; no TBD; consistent with docs 01-18","-","This doc exists; packet = verification/hardening pass, report gaps as BLOCKED-style findings, do not rewrite unilaterally.")

for num3 in range(38,88):
    _f = sorted((ROOT/"docs").glob(f"{num3}_*.md"))
    if _f:
        add(f"docs/{_f[0].name}","docs",f"Perfection-register doc {num3}: authored by lead; agent verifies cross-refs, IDs, consistency with docs 01-36 and reports gaps - does not rewrite unilaterally.","docs/37_MISSING_DOCS_AND_PERFECTION_REGISTER","existing doc","verified doc","Docs-verify passes; every referenced ID exists; zero placeholders","-","See doc 37 for why this doc exists and its priority.")
def slug(p): return re.sub(r'[^a-z0-9]+','-',p.lower()).strip('-')[:60]

def main():
    (ROOT/"agent-prompts").mkdir(exist_ok=True); (ROOT/"docs").mkdir(exist_ok=True)
    rows=[]
    for i,p in enumerate(PACKETS,1):
        pid=f"PKT-{i:04d}"
        p["id"]=pid
        rows.append(p)
        prompt=f"""# {pid} — {p['path']}

> **ONE AGENT. ONE FILE. NOTHING ELSE.** You create exactly `{p['path']}` (plus its paired test if named below). You do not modify any other file. If a contract you need is missing, STOP and write `BLOCKED: <what>` — never invent a contract.

## 1. Mission
{p['purpose']}

## 2. Read first (in this order, nothing else)
1. `docs/00_INDEX.md` §2 (reading plan) and §10 (current phase)
2. {p['deps'] or 'docs/00_INDEX.md'}
3. This packet in full.

## 3. Inputs you may rely on
{p['inputs'] or 'See dependencies above. Treat dependency APIs as fixed contracts.'}

## 4. Output you must produce
- File: `{p['path']}`
- Provides: {p['outputs'] or p['purpose']}
- Layer: {p['layer']}

## 5. Non-negotiable rules (violation = packet rejected)
1. **Money**: `Decimal`/integer minor units only, via `app/core/money.py`. Float for money anywhere = reject. AI never computes money.
2. **Traceability**: every aggregate must be drillable to source rows (file + row number).
3. **Nothing silently discarded**: rejected/quarantined data is reported with counts and reasons.
4. **No placeholders**: no TODO/TBD/`pass`/mock-only/stub returns. If you cannot finish, return `BLOCKED`, not a fake.
5. **No scope invention**: implement only what §1 + the cited spec section say. New ideas -> write them in your handover note, not in code.
6. **Plain language**: user-facing text is written for a non-technical FP&A analyst; every error has a hint telling them what to do next.
7. **Deterministic**: same input -> same output, byte-for-byte where applicable. No wall-clock/randomness in calculations (inject clock/seed).
8. Follow `docs/15_CODING_STANDARDS.md` (naming, typing, docstrings, error codes from `app/core/errors.py`).

## 6. Acceptance criteria (all must pass; evidence required)
{p['acceptance'] or 'Spec-conformance review + paired tests green.'}

## 7. Paired test file
`{p['tests'] or 'None for this packet - state why in handover.'}` — if named, the test is part of this packet's definition of done. Tests must include: happy path, the spec's worked example, one failure/edge case, and (for money) a rounding case. Tests must FAIL if the implementation is stubbed (mutation honesty).

## 8. Build order (follow exactly)
1. Re-read the cited spec sections; write down (in your head/notes) the exact contract: inputs, outputs, error codes, formulas/keys.
2. Write the paired test FIRST from the spec's worked examples + the edge checklist in section 9; run it - it must fail for the right reason.
3. Implement the smallest complete version satisfying the contract (no extra features, no extra files).
4. Run: paired tests, then the module's neighbouring tests, then `python scripts/check.py` if it exists yet (Wave>=3) - record exact commands/outputs.
5. Self-review against section 5 rules and section 9 checklist; fix before returning.

## 9. Universal edge-case checklist (address every line in code or test, or state why N/A)
Zero amounts / zero denominator; negative amounts and credit-normal accounts; empty input; single row; duplicate input; very large input (250k rows posture); missing optional data (rule must report not_run, export must label, UI must show empty state); locked period/version; superseded batch; expired waiver; hostile text (quotes, `=formula`, `<script>`, unicode, 10k-char description); ambiguous dates/amounts; currency minor-unit exponent; month 2 reuse (no month-1 assumptions hard-coded); deterministic repeat run.

## 10. Forbidden in this packet
Editing any other file (incl. "helpful" fixes); adding dependencies; changing a spec, threshold, key format, or error code; committing secrets/test data with real financials; disabling a lint/type rule; `float` on money; TODO/TBD/stub/mock-only code.

## 11. Packet-specific notes
{p['notes'] or 'None.'}

## 12. Definition of done — return exactly this handover format
```
PACKET: {pid}
FILE: {p['path']}
STATUS: DONE | BLOCKED
TESTS RUN: <command> -> <pass/fail counts>
EVIDENCE: <output excerpt or artefact path>
CONTRACTS USED: <spec sections + dependency APIs>
DEVIATIONS: none | <list, each with reason>
BLOCKED ON: none | <exact missing contract>
```
A `DONE` claim without test evidence is treated as not done.
"""
        (ROOT/f"agent-prompts/{pid}-{slug(p['path'])}.md").write_text(prompt, encoding="utf-8")
        (ROOT/"agent-prompts"/"testers").mkdir(exist_ok=True)
        tester = f"""# TST-{pid[4:]} - TESTER for {pid}: {p['path']}
You are the INDEPENDENT TESTER for packet {pid}. You did not write this code and must trust nothing in its handover.
Follow docs/34_AUDIT_PLAYBOOK.md section 1 exactly: (1) scope-diff - only `{p['path']}` (+ paired test `{p['tests']}`) may have changed; (2) fresh-run the paired tests and paste output; (3) MUTATION CHECK - stub/weaken the implementation (constant return, drop one leg of any AND-test, off-by-one period) - at least one test must fail per mutation, else REJECT (tests are theatre); (4) edge checklist from the creator packet section 9; (5) money grep - float/division/rounding outside app/core/money.py; (6) spec conformance - cite the spec lines you verified.
Acceptance under test: {p['acceptance'] or 'spec conformance'}
Return exactly: `TST-{pid[4:]} VERDICT: SIGN | REJECT` + evidence (commands, outputs, mutations tried) + defects with file:line.
"""
        (ROOT/f"agent-prompts/testers/TST-{pid[4:]}-{slug(p['path'])}.md").write_text(tester, encoding="utf-8")

    with open(ROOT/"docs/FILE_MANIFEST.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["id","path","layer","purpose","deps","tests"])
        w.writeheader()
        for p in rows: w.writerow({k:p.get(k,"") for k in ["id","path","layer","purpose","deps","tests"]})

    lines=["# FILE MANIFEST — every file to be generated (one agent per file)\n",
           f"Total packets: **{len(rows)}**  ·  Generated by `tools/generate_agent_packets.py` — do not hand-edit; edit the generator and re-run.\n",
           "| Packet | File | Layer | Purpose | Paired test |","|---|---|---|---|---|"]
    for p in rows:
        lines.append(f"| {p['id']} | `{p['path']}` | {p['layer']} | {p['purpose'][:110]} | `{p['tests']}` |")
    (ROOT/"docs/FILE_MANIFEST.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

    idx=["# AGENT PROMPT INDEX\n","Master prompt for every agent: `00_MASTER_AGENT_PROMPT.md`. One packet = one file = one agent.\n"]
    for p in rows: idx.append(f"- [{p['id']} {p['path']}]({p['id']}-{slug(p['path'])}.md)")
    (ROOT/"agent-prompts/INDEX.md").write_text("\n".join(idx)+"\n", encoding="utf-8")
    print(f"packets: {len(rows)}")

if __name__=="__main__": main()
