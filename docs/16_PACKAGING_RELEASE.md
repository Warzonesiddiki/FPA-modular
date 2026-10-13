# 16 — PACKAGING, RELEASE & VERSIONING RUNBOOK

> Owner of: build → installer → upgrade → release evidence.

## 1. Build (`scripts/build.py`, one command, clean checkout → installer)
1. UI: `npm ci && npm run build` → `ui/dist`. 2. Checks: `scripts/check.py` must pass first (build refuses on red). 3. PyInstaller `packaging/fpa.spec`: one-folder bundle (API + desktop shell + UI dist + sample-data), pinned PyInstaller version, reproducible-path flags. 4. Payload audit: bundle scanned — no `.db` user projects, no keys/env, no tests/scratch; SBOM-lite written (doc 12 §6). 5. Inno Setup `packaging/installer.iss` → `FPAMonthEndCopilot-Setup-<version>.exe` with version from `pyproject.toml` (single source; `app.__version__` mirrors it, equality-tested).

## 2. Install / upgrade / uninstall contract (P15)
Installs per-user (no admin) to `%LocalAppData%\Programs\FPA Month-End Copilot`; user project folders live wherever the user puts them (default `Documents\FPA Projects`) and are **never** touched by install/upgrade/uninstall (uninstall asks, default keep). Upgrade: new version opens old projects via append-only DB migrations (fixture: project created by previous release's sample opens, migrates, acceptance smoke passes — tested before release). Downgrade: opens read-only with a clear message if DB schema is newer.

## 3. Versioning
SemVer. `MAJOR` = data/API contract break (migration notes mandatory), `MINOR` = features per roadmap phase, `PATCH` = fixes. Every release: docs/CHANGELOG.md entry (user-visible changes in plain language + technical notes), git tag `vX.Y.Z`, release notes generated from changelog — not handwritten separately.

## 4. Release checklist (all with evidence links; any unchecked = no release)
☐ scripts/check green on clean clone ☐ acceptance verdict PASS (evidence/acceptance_report.*) + cross-artifact green ☐ perf budgets met ☐ security suite (doc 12 §8) green ☐ fresh-Windows-VM install → sample month-end → Excel+PPT generated and spot-tied ☐ upgrade fixture from previous release passes ☐ payload audit + SBOM attached ☐ doc 18 matches shipped UI (screenshot pass) ☐ changelog + tags ☐ owner sign-off recorded (doc 17 DEC).

## 5. Code signing & distribution
Installer unsigned during pilot (Windows SmartScreen guidance in doc 18 with screenshots); signing certificate decision at go-live (owner decision, doc 17 OQ) — Authenticode signing step is scripted but certificate-optional in build config. Distribution: direct file share; no auto-update in v1 (doc 12) — new version announced in-app only via release-notes file the user chooses to check.

## 6. Support & diagnostics
S15 diagnostics bundle: app/OS versions, redacted logs, project DB integrity + audit-verify result, file hashes — explicitly no financial values (doc 12 §5). Support flow: bundle → reproduce on sample/malformed corpus → defect or OQ. Backup guidance (doc 18): copy project folder; restore verified by hash + audit chain before open.
