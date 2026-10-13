# 85 — RACI & PROJECT GOVERNANCE (single-builder model, DEC-007)

Roles: **Owner** (product owner — approves docs, DECs, gate changes, releases, cuts; spot-checks any item), **Builder** (the one agent: plans nothing new, executes `docs/WORK_PLAN.md` under `AGENT_PROMPT.md`, verifies its own work procedurally, runs the milestone audit sessions, keeps `TASKBOARD.md`), **Support** (post-release, doc 35). There is no integrator, creator pool, tester pool or auditor pool; their duties are folded into the Builder's protocol (docs 33, 34) and the Owner's spot-checks.

| Decision / artefact | Owner | Builder |
|---|---|---|
| Doc set approval, scope change, phase gate (DEC) | A by delegation — since DEC-010 the builder decides and records `DEC-nnn (auto)`; the owner may reverse | **R/A** (drafts the DEC with rationale, alternatives costed, reversal cost) |
| Class-A open question (design choice with a labelled default) | I (reads the DEC log; may reverse) | **R/A** (decides, records DEC (auto), proceeds — AGENT_PROMPT §4) |
| Class-B spec fix (omission/contradiction) | I (reads CHANGELOG/DEC) | **R/A** (doc first, then code) |
| Class-C block (impossible/unsafe as specified) | A only when the way out needs the owner (money, legal, hardware); otherwise the builder decides a DEC (auto) with the evidence | R (evidence in TASKBOARD, moves on) |
| Work item implementation + paired test + handover | I | **R/A** |
| Self-verification (mutations, scope diff, spec checks) | I (spot-checks) | **R/A** |
| Milestone audit session + gate closure | **A** (may reopen) | R |
| Acceptance bar / gate / threshold change (docs 14, 36, 42) | **A** (DEC required) | R (proposes with recomputation) |
| Release go/no-go (doc 16 §4) | **A** | R (evidence pack) |
| P0 defect stop-line | I (informed same session) | **R/A** (stops the item, fixes or blocks) |

**Escalation:** Builder → TASKBOARD *Owner attention* (batched) → Owner reply in the next session's instructions or by editing doc 17. Immediate interruption only for class-C on the critical path, security holes, data-loss risk, or any temptation to weaken a gate (`AGENT_PROMPT.md` §9).

**Cadence:** gate review at each milestone (doc 86 §1) using `evidence/audits/M<n>_audit.md`; the DEC log (doc 17 §4) is the only decision record that counts — "we agreed in chat" is not a decision until it is a DEC.
