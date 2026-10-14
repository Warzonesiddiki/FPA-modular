# 70 — FILE & FOLDER STRUCTURE SPECIFICATION

**Install dir** (app-owned, replaced on upgrade): `app/ ui/ sample-data/ packs/ THIRD_PARTY_NOTICES`. **Project folder** (user-owned, never touched by installer): 
```
<Project>/ project.db (+ -wal/-shm at runtime) settings.json
  imports/<sha256>.<ext> (originals; 62 privacy toggle)  exports/<YYYY-P##>/…(packs, decks, PDFs, owner lists)
  backups/ (manual + pre-migration)  logs/ (65)  diagnostics/ (bundles, user-generated)
```
Rules: every file the app writes lands under these (no temp outside OS temp, cleaned on success); file names sanitised (doc 12) and timestamped in UTC; exports never overwrite (name suffix `(2)`), because a forwarded board pack must remain the file that was sent; "safe to delete": exports/backups/logs/diagnostics (app recreates), never project.db/imports while periods are locked (UI warns accordingly); sharing guidance: project folder = full data (sensitive), exports = shareable with advisory stamps, diagnostics = shareable (value-free by construction, 65).
Repo structure mirrors WORK_PLAN layers (app/ incl. `app/connectors/` with `profiles/*.json`, ui/, tests/ incl. `tests/fixtures/connectors/` (its `tokens/` sub-folder is synthetic and build-excluded), sample-data/ incl. `erp_shapes/` and `erp_shapes/api/`, packaging/, scripts/, docs/, tools/ incl. `tools/mock_d365.py` (shipped — it is the offline demo ledger), evidence/ for gate artefacts; root: AGENT_PROMPT.md, TASKBOARD.md — evidence is committed only as small reports, never project data). Project folder additions (DEC-013): connector snapshots are ordinary `imports/<sha256>.xlsx` files; `logs/connector.log`; **no** credential file ever exists in the project folder (keyring only).

DEC-018: deletion intents, minimal tombstones and idempotency receipts are app-owned control metadata outside the target project folder, retained through its move/purge (doc 12 §2.1); they contain no financial rows or typed confirmation/name after purge. Trash is a private same-volume sibling of the registered project location, not an installer-owned folder or arbitrary client path. The future lifecycle coordinator/registry owns recovery; no filesystem deletion is performed by metadata reads.
