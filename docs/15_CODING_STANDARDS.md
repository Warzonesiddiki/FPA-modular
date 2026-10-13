# 15 — CODING STANDARDS

> Owner of: how code is written. Reviewers (tester agents) reject on these by number.

## 1. Python (engine)
Python 3.12, type-annotated everywhere (mypy strict in core/calc/rules/forecast), dataclasses/pydantic at boundaries, `pathlib`, no `print` (logging via core/logging). Functions: single purpose; engine functions pure where doc'd pure (rules/forecast methods/calc) — I/O only in store/api/services. Errors: raise `AppError` with catalogue code from `app/core/errors.py` (`FP&A-ERR-001…` grouped: 0xx general, 1x projects/periods, 2x import, 3x calc, 4x findings, 5x master, 6x export, 7x AI); raw exceptions never cross the API boundary. Money: integer minor units in storage, `Decimal` in computation, conversions only in money.py; **banned:** `float` on money, `/` on ints producing float money, rounding anywhere except money.py presentation functions (AST-checked, doc 14 §5). Dates: `datetime.date` for business dates; UTC aware datetimes for timestamps; no naive `now()` in calculations (inject clock).
Naming: modules snake_case; rule files `exc_###.py`; IDs and keys exactly as docs 02/07. Docstrings: one line + contract reference (`"""Implements doc 07 EXC-018 (AND-test)."""`) on public engine functions.

## 2. SQL & store
Parameterised queries only (no f-string SQL — linted); transactions via db.py context manager; migrations append-only numbered SQL in db.py registry with a fixture upgrade test (doc 16); repositories return dataclasses, never sqlite rows, never dicts past the store boundary.

## 3. TypeScript / React
TS strict; no `any` without a justifying comment + issue note; API types mirror doc 05 (client generated/checked against OpenAPI); state via zustand stores listed in the manifest — no new store libraries; components: function components, props typed, no money arithmetic (formatting helpers in `ui/src/lib/format.ts` operate on decimal strings); every component handles loading/empty/error where it fetches; `data-testid` on interactive elements used by E2E; no inline hard-coded user strings (copy via i18n-ready constants file per screen — v1 ships en only, structure ready).

## 4. Tests
Named `test_<unit>_<behaviour>`; arrange-act-assert visible; fixtures in `tests/fixtures` or `sample-data` (never inline 200-line literals); every bug fix lands with the failing-test-first evidence in the PR description; deterministic (seeded, clock-injected) — flaky test = P1 defect, quarantining a test requires doc-17 entry.

## 5. Git & change discipline
Spec → changelog (docs/CHANGELOG.md entry) → tests → code → traceability (packet handover) order (P2). Commits: `feat|fix|docs|test|build(scope): summary` with packet id (`PKT-####`). One packet per PR where practical; PR template requires: packet id, spec sections, tests run + output, evidence links. Main is protected: scripts/check + acceptance green required (doc 16).

## 6. Banned patterns (auto-reject in review)
Stub/`pass`/TODO returns presented as done · mock-only feature paths · silent `except: pass` · float money · colour-only status · user text containing "error/fraud" for findings · invented API/field/key not in docs · second implementation of an owned concern (doc 04 §2) · telemetry/network outside AI client · hand-editing generated files (manifest, OpenAPI snapshot) instead of regenerating.
