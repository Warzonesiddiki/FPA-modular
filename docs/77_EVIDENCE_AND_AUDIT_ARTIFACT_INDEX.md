# 77 — EVIDENCE & AUDIT ARTIFACT INDEX

All gate evidence lives in `evidence/` with naming `<YYYY-MM-DD>_<gate>_<milestone-or-version>.<md|json>`:
| Artefact | Produced by | Gate |
|---|---|---|
| acceptance_report.{json,md} (+ corpus hash) | scripts/acceptance.py | 14 §3 release |
| check_report.txt (scripts/check full output) | CI/local | every merge |
| perf/<scenario>.json (machine profile incl.) | tests/perf | 36/67 |
| audits/M<n>_audit.md (gate commands, ten re-verified items, streams, defects, verdict) | builder (cold session), owner spot-check | 34 §2 |
| cross_artifact_<period>.json | integration test | 14 §3 |
| connector_parity_<product>_<period>.json (mock pull vs file import vs CSV, fault matrix, no-change path) + connector_security.json (allow-list, redaction, keyring-only, state/PKCE, disconnect) | tests/integration/test_connector_pull + doc 12 §8 suite | 14 §3 connector parity; M3 gate |
| pilot_tenant_entity_check.md (per pilot: product, entity-check result, profile edits made, zero code changes confirmation) | pilot UAT-14 | 83 / R10 |
| migration_fixture_results.md | CI | 61 |
| ai_eval_<prompt-version>.md | doc 11 §7 runner | prompt changes |
| uat_signoff_<version>.pdf/md | owner UAT (71) | release |
| release_checklist_<version>.md (evidence links) | builder, owner-signed | 16 §4 |
| sbom_<version>.json + payload_audit | scripts/build.py | 12 §6 |
Retention: evidence for shipped versions kept for the life of the product line; milestone evidence for 2 subsequent releases. An artefact not in this index does not count as evidence (34 empty-report rule).
