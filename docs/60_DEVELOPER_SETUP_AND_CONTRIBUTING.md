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
```
## Daily flow
Commit `WI-####: <path>` (the builder) / branch `feat-<slug>` (humans) → spec-first if behaviour changes (doc 17 §6) → tests → `scripts/check.py` → PR with template (87): WI/FR ids, spec sections, tests+output, evidence. Reviews: the self-verification block (doc 34 §1) for the builder; one human reviewer for humans. Main protected: check + acceptance green, no direct pushes.
## Repo hygiene
No real financial data in repo, ever (78). No binaries except installer artefacts in releases. Generated files (`docs/WORK_PLAN.*`, OpenAPI snapshot) changed only via their generators. Scratch work in `scratch/` (gitignored).
