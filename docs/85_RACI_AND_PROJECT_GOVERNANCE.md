# 85 — RACI & PROJECT GOVERNANCE

Roles: **Owner** (product owner — approves docs, DEC, releases, cuts), **Integrator** (waves, taskboard, gates, merges), **Creator agents**, **Tester agents**, **Auditor agents**, **Support** (post-release, doc 35).
| Decision/artefact | Owner | Integrator | Creator | Tester | Auditor |
|---|---|---|---|---|---|
| Doc set approval / scope change (DEC) | **A** | R | C | C | I |
| Packet issue/re-issue, wave open/close | A(cut only) | **R/A** | I | C | I |
| Code file (own packet) | I | C | **R** | A(sign) | I |
| Test verdict | I | C | I | **R/A** | C |
| Gate bar change (14/36) | **A** | R | — | C | C |
| Release go/no-go (16 §4) | **A** | R | — | C | C |
| Defect severity S1 stop-line | I | **R/A** | C | C | C |
Escalation: creator→integrator (BLOCKED, same day) → owner (scope/contract decisions, batched weekly except S1). Governance cadence: wave reviews at each gate; DEC log (17 §4) is the only decision record that counts ("we agreed in chat" is not a decision until it's a DEC).
