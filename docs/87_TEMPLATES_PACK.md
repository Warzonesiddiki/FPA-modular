# 87 — TEMPLATES PACK (uniform artefacts for the owner, the builder and support)

Copy the block, fill every field (write `n/a — reason` where truly n/a; blank = incomplete).

**ADR/DEC:** `ID · Date · Decider · Context (facts, links) · Options considered (with the rejected ones + why) · Decision · Consequences (work items/docs affected) · Revisit trigger.`
**RFC:** `Title · Problem (evidence) · Proposal · Alternatives · Spec docs touched · Work items created/re-opened · Risks · Owner decision needed by.`
**Defect:** `ID · Severity S1–S4 · Version · Environment · Dataset (synthetic id/hash — never real data) · Steps · Expected · Actual · Screen/FR · Evidence (logs id, screenshots on sample data) · Verification evidence.`
**Work-item handover:** `AGENT_PROMPT.md` §8 block (WI/STATUS/CONTRACT/TESTS RUN/MUTATIONS/EDGES/SPEC CHECKS/FILES TOUCHED/DEVIATIONS/OWNER QUESTIONS).
**Milestone audit report:** `evidence/audits/M<n>_audit.md` — `Milestone · Commit audited · Gate commands + outputs · Ten re-verified items (ids by the doc 34 §2 rule) · Streams run + cases · Defects (WI, severity) · Verdict`.
**Audit report (AUD):** `Stream · Scope · Method · Cases tried (list) · Findings (severity, evidence) · No-findings justification (mandatory) · Artefact hashes.`
**UAT sign-off:** `Version · UAT script ids run (71) · Tester (name/role) · Pass/fail per script · Defects raised · Sign-off statement + date.`
**Release sign-off:** doc 16 §4 checklist with an evidence link per line + owner signature line.
**Pilot report:** doc 83 metrics table + questionnaire deltas (58) + go/no-go recommendation.
**Post-go-live review:** doc 84 metrics (close cycle days trend, adoption, defects by theme) + backlog dispositions.
**Support ticket:** doc 35 §2 fields.
File naming per doc 77 index.
