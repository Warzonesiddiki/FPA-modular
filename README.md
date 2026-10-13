# FPA-modular — FP&A Month-End Copilot (Attempt #5, planned as the final one)

One analyst. One tool. The whole month-end: import messy ERP exports → validated, balanced books → explained budget-vs-actual → owner-assigned exception inbox → rolling forecast → board-ready Excel + PowerPoint. Offline, local-only, every number traceable to its source row. AI (optional, off by default) drafts commentary around verified numbers — it never computes one.

## Start here
1. **`docs/MASTER_PLAN.md`** — the complete plan: lessons from attempts 1–4, product definition, architecture, 500-agent execution model, waves, gates, audit plan.
2. **`docs/00_INDEX.md`** — document map and source-of-truth matrix.
3. **`docs/FILE_MANIFEST.md`** — every file to be generated (184 packets), also `FILE_MANIFEST.csv`.
4. **`agent-prompts/`** — hand any agent `00_MASTER_AGENT_PROMPT.md` + one `PKT-####-*.md` file. Nothing else is needed.
5. **`docs/RESEARCH_AND_LESSONS.md`** — evidence from the four previous repos + market check.

## Status
Planning complete; **no product code yet — by design.** Next step: owner approves `MASTER_PLAN.md` §12, then Wave 0 (spec docs 01–18) is dispatched. Regenerate the manifest/prompts with `python tools/generate_agent_packets.py` (edit the generator, never the outputs).
