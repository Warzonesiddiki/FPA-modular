# 60 — DEVELOPER SETUP & CONTRIBUTING (humans)

## Toolchain (exact)
Windows 11 dev machine (app targets Windows; engine is OS-portable), Python 3.12.x, Node 22 LTS, Git. Optional: Inno Setup 6 (packaging only), LibreOffice (export-fidelity checks).
## Setup (15 min, must work verbatim)
```
git clone <repo> && cd FPA-modular
python -m venv .venv && .venv\Scripts\activate && pip install -e ".[dev]"
cd ui && npm ci && cd ..
python scripts/check.py        # baseline must be green before you change anything
python -m app.cli run-month-end --sample   # golden run on sample project
python -m app.cli pull --sample --period 2025-P07 --mock   # Dynamics 365 connector against the local mock (starts tools/mock_d365.py, no tenant, no internet)
```
To exercise the connector by hand: `python tools/mock_d365.py --port 8765` then point the sample project at `http://127.0.0.1:8765` via *Connect to the demo ledger (local)* in S13. No developer ever needs a real tenant to run every connector test; a real-tenant smoke is a pilot activity (doc 83) with the owner's own identity, never with shared credentials in the repo or CI.
## Daily flow
Commit `WI-####: <path>` (the builder) / branch `feat-<slug>` (humans) → spec-first if behaviour changes (doc 17 §6) → tests → `scripts/check.py` → PR with template (87): WI/FR ids, spec sections, tests+output, evidence. Reviews: the self-verification block (doc 34 §1) for the builder; one human reviewer for humans. Main protected: check + acceptance green, no direct pushes.
## Repo hygiene
No real financial data in repo, ever (78). No binaries except installer artefacts in releases. Generated files (`docs/WORK_PLAN.*`, OpenAPI snapshot) changed only via their generators. Scratch work in `scratch/` (gitignored).

## M0 documentation tests (DEC-016; before the product toolchain exists)
Use Python 3.11+ and `python -m pip install -r tests/docs/requirements.txt`, then `python -m pytest tests/docs -q`. The pinned file includes the JSON Schema validator and its transitive dependencies; these are verification-only, not product runtime dependencies. The schema uses local references only; validation must never fetch a URL. M1 still owns the product pyproject pin/lock correction. Do not run missing M6 gates or treat their absence as a pass.
