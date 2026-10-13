# 72 — DEFECT & CHANGE MANAGEMENT

**Defect lifecycle:** New → Triaged (severity: S1 wrong number/data loss/security; S2 wrong behaviour; S3 cosmetic; S4 docs) → Fixed (with failing-test-first evidence, doc 15 §4) → Tester-verified → Closed. S1: stop-the-line (wave pauses, integrator owns), fix + audit-stream re-run (34). Defect record: template 87 (steps, dataset hash, expected/actual, screens, version).
**Change (RFC) flow:** idea → backlog (17 §5) → RFC (87 template: problem, options, spec impact, packet impact, risk) → owner DEC → spec PR first (P2) → packets regenerated/re-issued → build. Breaking data/API changes additionally require doc 61 migration plan and doc 05 version note.
**Baselines:** doc set baselined at Phase-0 approval (DEC-006) and at each release tag; packet prompts pin the baseline hash they were generated from; mid-wave baseline changes re-issue affected packets only (integrator lists them in the DEC).
**Waivers of process:** none for S1/gates; any other waiver is a DEC with expiry (like finding waivers — process debt must resurface too).
