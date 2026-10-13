# 54 — WIREFRAMES & LAYOUT SPECIFICATION (extends docs 13/21)

Global shell: left rail 232px (collapsible to icons 56px) · header 56px (project ▸ period picker ▸ lock state ▸ alerts bell ▸ help) · content max-width none, padding 24 · data screens full-bleed tables.
Per-screen layout zones (wireframe in text; M4 screen items are built from this + doc 21):
- **S01:** row1 KPI tiles (4–6); row2 two columns: close checklist (60%) + findings summary (40%); row3 top-variances table full width.
- **S03 wizard:** stepper top; step body card centred 960px; sticky footer (Back/Continue + stage summary counts); quarantine step switches to full-width table layout.
- **S06:** tabs; toolbar (period mode, scale, zero-lines); table with sticky line column; right DrillDrawer 480px overlay.
- **S07:** filter bar; split: table 65% / right column (bridge chart + commentary editor tabs).
- **S08:** filter bar + saved views; card list (not table — evidence text needs width) with bulk-select checkboxes; right detail drawer on select.
- **S09:** matrix table top; chart below (actual/forecast continuity); FVA table collapsible.
- **S11:** snapshot card; checks list (pass/fail rows w/ Δ); generate buttons; history table.
- **S16:** calendar strip (business days) + task table + blockers rail right.
- **S17:** tabs per plan type; each tab = editable grid + provenance column + totals footer.
Prototype standard: M4 first delivers the shell + S01/S03/S07 as clickable prototypes for owner review before remaining screens (one review gate, recorded as DEC) — the only planned mid-build visual check.
