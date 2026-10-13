# 70 — FILE & FOLDER STRUCTURE SPECIFICATION

**Install dir** (app-owned, replaced on upgrade): `app/ ui/ sample-data/ packs/ THIRD_PARTY_NOTICES`. **Project folder** (user-owned, never touched by installer): 
```
<Project>/ project.db (+ -wal/-shm at runtime) settings.json
  imports/<sha256>.<ext> (originals; 62 privacy toggle)  exports/<YYYY-P##>/…(packs, decks, PDFs, owner lists)
  backups/ (manual + pre-migration)  logs/ (65)  diagnostics/ (bundles, user-generated)
```
Rules: every file the app writes lands under these (no temp outside OS temp, cleaned on success); file names sanitised (doc 12) and timestamped in UTC; exports never overwrite (name suffix `(2)`), because a forwarded board pack must remain the file that was sent; "safe to delete": exports/backups/logs/diagnostics (app recreates), never project.db/imports while periods are locked (UI warns accordingly); sharing guidance: project folder = full data (sensitive), exports = shareable with advisory stamps, diagnostics = shareable (value-free by construction, 65).
Repo structure mirrors manifest layers (app/, ui/, tests/, sample-data/, packaging/, scripts/, docs/, agent-prompts/, evidence/ for gate artefacts — evidence is committed only as small reports, never project data).
