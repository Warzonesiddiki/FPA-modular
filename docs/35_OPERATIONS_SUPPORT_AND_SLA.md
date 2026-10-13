# 35 — OPERATIONS, SUPPORT & CONTINUITY

1. **Support tiers:** L1 user guide/Help (18) → L2 diagnostics bundle review (16 §6) → L3 defect fix via packet process (33). Response targets (owner's commercial promise — defaults: acknowledge 1 business day pilot, 2 days standard; P1 wrong-number reports acknowledged same day).
2. **Defect intake template:** app version, OS, project period, screen, diagnostics id, steps, expected/actual, sample/malformed file if shareable (never require real financials — reproduction on synthetic data is the default ask).
3. **Release cadence:** PATCH as needed (checklist doc 16 §4 applies in full — no "minor" releases skip acceptance), MINOR quarterly at most during pilot year; every release ships with doc-18 updates in the same PR.
4. **Data continuity for the analyst:** backup guidance (18 §2), restore drills recommended quarterly; app verifies backups on restore only — a "verify backup now" action exists in S13 (hash + audit chain, no modification).
5. **End-of-life/data exit:** projects are plain folders (SQLite + files); a documented CSV export of gl_rows/findings/settings (S11 "data export") guarantees the analyst is never locked in — exit is a feature, stated in the user guide.
6. **Feedback loop:** in-app "Send feedback" creates a local text file (user shares it by their own channel — no phone-home, doc 12); feedback reviewed monthly into doc 17 backlog with dispositions recorded.
