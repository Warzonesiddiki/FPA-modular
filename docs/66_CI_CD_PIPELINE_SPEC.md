# 66 — CI/CD PIPELINE SPECIFICATION

1. **CI (`.github/workflows/ci.yml`, windows-latest):** checkout → Python 3.12 + Node 22 setup (cache by lockfiles) → `pip install -e .[dev]` + `npm ci` → `python scripts/check.py` (ruff, mypy, pytest, coverage gates, money-AST, token/schema/docs parity, secret+telemetry scans) → acceptance double-run (doc 14 §3) → UI build → migration-fixture tests (61) → artefact: test + acceptance reports (retention 90d). Any red stage blocks merge (branch protection: required checks, no admin bypass — the attempt-#2 "fixes sat unpushed while CI red" failure is a process defect, treated as P1).
2. **CD (tag `vX.Y.Z`):** CI must be green on the tagged commit → `scripts/build.py` (installer + SBOM + payload audit) → checksum file → draft GitHub release with changelog section; publishing is a human click (owner) after doc 16 §4 checklist evidence is attached.
3. **Secrets:** none needed beyond GITHUB_TOKEN; code-signing secret (when OQ-07 decided) as repo secret, referenced by name only.

