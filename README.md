# FPA-modular — FP&A Month-End Copilot (Attempt #5, planned as the final one)

One analyst. One tool. The whole month-end: import messy ERP exports → validated, balanced books → explained budget-vs-actual → owner-assigned exception inbox → rolling forecast → board-ready Excel + PowerPoint. Offline, local-only, every number traceable to its source row. AI (optional, off by default) drafts commentary around verified numbers — it never computes one.

## Start here
1. **`docs/MASTER_PLAN.md`** — the complete plan: lessons from attempts 1–4, product definition, architecture, 500-agent execution model, waves, gates, audit plan.
2. **`docs/00_INDEX.md`** — document map and source-of-truth matrix.
3. **`docs/FILE_MANIFEST.md`** — every file to be generated (317 creator packets + 317 tester prompts + 132 audit packets = 766 assignments), also `FILE_MANIFEST.csv`.
4. **`agent-prompts/`** — hand any agent `00_MASTER_AGENT_PROMPT.md` + one `PKT-####-*.md` file. Nothing else is needed.
5. **`docs/RESEARCH_AND_LESSONS.md`** — evidence from the four previous repos + market check.

## Status
**Current phase: DOCUMENTATION ONLY (owner direction).** Docs 00–91 baselined (DEC-006); Wave 1a/1b code (core/store/imports/calc, 9 tests green) is frozen until the owner re-opens build waves. Start at `docs/00_INDEX.md` §10 for live status. Manifest/prompts regenerate via `python tools/generate_agent_packets.py` (edit the generator, never the outputs).
