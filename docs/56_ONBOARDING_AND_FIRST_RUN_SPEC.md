# 56 — ONBOARDING & FIRST-RUN SPECIFICATION

1. **First launch:** no login, no network prompt. S02 with two cards: "Explore the sample company" (default focus) and "Create your project". Version + data-location line in footer.
2. **Sample tour (S15 walkthrough):** 8 steps mirroring J1 (doc 52), each step deep-links and ticks from real state; skippable; resumable; completable in ≤10 min; ends with a generated sample board pack the analyst can open.
3. **New-project wizard:** name → currency + FY start → COA template/industry pack (28) → first period → (optional) import opening balances → done, landing on S03 with the import checklist. Defaults pre-filled from OQ defaults (17) so Enter-through works.
4. **Excel-migration path:** Help topic + checklist: export your current month from ERP using doc 26 recipes → save mapping → compare first in-app pack vs your spreadsheet pack side-by-side (Sources/Checks sheets designed for this) → trust checklist before retiring the spreadsheet.
5. **Abandonment recovery:** any wizard/walkthrough exit resumes where left (state persisted per project); nothing is half-created (project creation is atomic).
Tests: fresh-install E2E (J1), wizard defaults path, resume-after-kill at each step.
