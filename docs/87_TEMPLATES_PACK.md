# 87 — TEMPLATES PACK (uniform artefacts for humans + 500 agents)

Copy the block, fill every field (write `n/a — reason` where truly n/a; blank = incomplete).

**ADR/DEC:** `ID · Date · Decider · Context (facts, links) · Options considered (with the rejected ones + why) · Decision · Consequences (packets/docs affected) · Revisit trigger.`
**RFC:** `Title · Problem (evidence) · Proposal · Alternatives · Spec docs touched · Packets created/re-issued · Risks · Owner decision needed by.`
**Defect:** `ID · Severity S1–S4 · Version · Environment · Dataset (synthetic id/hash — never real data) · Steps · Expected · Actual · Screen/FR · Evidence (logs id, screenshots on sample data) · Tester verification.`
**Packet handover:** as in agent-prompts master prompt (PACKET/FILE/STATUS/TESTS/EVIDENCE/CONTRACTS/DEVIATIONS/BLOCKED ON).
**Tester verdict:** `TST-id · Packet · Commands run + outputs · Mutations tried + results · Edge cases checked · VERDICT SIGN/REJECT · Defects (file:line).`
**Audit report (AUD):** `Stream · Scope · Method · Cases tried (list) · Findings (severity, evidence) · No-findings justification (mandatory) · Artefact hashes.`
**UAT sign-off:** `Version · UAT script ids run (71) · Tester (name/role) · Pass/fail per script · Defects raised · Sign-off statement + date.`
**Release sign-off:** doc 16 §4 checklist with an evidence link per line + owner signature line.
**Pilot report:** doc 83 metrics table + questionnaire deltas (58) + go/no-go recommendation.
**Post-go-live review:** doc 84 metrics (close cycle days trend, adoption, defects by theme) + backlog dispositions.
**Support ticket:** doc 35 §2 fields.
File naming per doc 77 index.
