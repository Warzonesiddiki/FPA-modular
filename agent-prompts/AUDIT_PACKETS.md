# AUDIT PACKETS (AUD-001…AUD-132) — for auditor agents
Master instruction for every auditor: `agent-prompts/00_MASTER_AGENT_PROMPT.md` + `docs/34_AUDIT_PLAYBOOK.md`. Each AUD below is one agent assignment. Report to `evidence/audits/` per doc 34 §3 (empty-report rule applies).

| Range | Stream (doc 34 §2) | Assignments |
|---|---|---|
| AUD-001…010 | A Recompute (10 periods/datasets, hand-rebuilt statements) | 10 |
| AUD-011…034 | B Rule hunting — one per rule EXC-001…024 (boundary ±1 minor unit, ±0.01%, false-positive attempts) | 24 |
| AUD-035…044 | C Contract parity (API, schema, tokens, keys, errors, screens, manifest, OpenAPI, packs, i18n) | 10 |
| AUD-045…058 | D Adversarial (injection ×4, hostile files ×4, tamper ×3, API abuse ×3) | 14 |
| AUD-059…066 | E UX tabletop (8 fresh-agent month-end runs incl. accessibility personas) | 8 |
| AUD-067…076 | F Truth audit (README, docs, UI copy, exports, AI claims, marketing wording) | 10 |
| AUD-077…086 | G Performance & 12-month soak | 10 |
| AUD-087…094 | H Accessibility deep-dive (per screen group) | 8 |
| AUD-095…104 | I Export fidelity on auditor-generated data (2nd golden dataset) | 10 |
| AUD-105…114 | J Docs completeness & traceability closure | 10 |
| AUD-115…124 | K Security review of code (auth/token, crypto, SQL, paths, secrets, deps) | 10 |
| AUD-125…132 | L Release readiness (install/upgrade/backup/restore/drill on clean VMs) | 8 |
**Total audit assignments: 132. Army total: 270 creators + 270 testers + 132 auditors = 672 prompt-addressable assignments** (integrators draw from AUD pool leads).
