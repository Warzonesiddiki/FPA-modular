# 77 — EVIDENCE & AUDIT ARTIFACT INDEX

All gate evidence lives in `evidence/` with naming `<YYYY-MM-DD>_<gate>_<wave-or-version>.<md|json>`:
| Artefact | Produced by | Gate |
|---|---|---|
| acceptance_report.{json,md} (+ corpus hash) | scripts/acceptance.py | 14 §3 release |
| check_report.txt (scripts/check full output) | CI/local | every merge |
| perf/<scenario>.json (machine profile incl.) | tests/perf | 36/67 |
| audits/AUD-###.md (method + cases + verdict) | auditor agents | 34 |
| cross_artifact_<period>.json | integration test | 14 §3 |
| migration_fixture_results.md | CI | 61 |
| ai_eval_<prompt-version>.md | doc 11 §7 runner | prompt changes |
| uat_signoff_<version>.pdf/md | owner UAT (71) | release |
| release_checklist_<version>.md (evidence links) | integrator | 16 §4 |
| sbom_<version>.json + payload_audit | scripts/build.py | 12 §6 |
Retention: evidence for shipped versions kept for the life of the product line; wave evidence for 2 subsequent releases. An artefact not in this index does not count as evidence (34 empty-report rule).
