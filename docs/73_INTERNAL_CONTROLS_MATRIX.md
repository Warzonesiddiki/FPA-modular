# 73 — INTERNAL CONTROLS MATRIX

> For CFO/auditor conversations. Control types: P=preventive, D=detective. Single-user limitation stated in §2 — never oversold.

| Process | Risk | Control | Type | Evidence |
|---|---|---|---|---|
| Import | Rows silently lost/altered | Count reconciliation in=valid+quarantined; file hash retained; control totals gate | P+D | Import report, Sources sheet |
| Import | Duplicate posting | Re-import supersede (idempotent) + EXC-001/002 | P+D | Batch history |
| Numbers | Transcription/formula error | Single calc engine; exports generated, cross-artifact tie-out; Checks sheet | P+D | Checks, AUD-A/I |
| Numbers | Rounding drift | Integer minor units; largest-remainder presentation | P | Money tests (03) |
| Exceptions | Finding ignored forever | Owner+due workflow, waiver expiry resurfacing, lock guard | D+P | Finding history |
| Period integrity | Locked month changed silently | Lock + audited unlock/restatement impact report | P+D | Audit chain, doc 41 report |
| Adjustments | GL rewritten to hide variance | Immutable GL; separate adjustment layer with reasons | P | Layer drill (39) |
| Access/integrity | DB/audit tampering | Hash-chained audit, verify on demand + before pack | D | S14 verify (ERR-090) |
| Confidentiality | Data leaves machine | Offline design, AI opt-in aggregate-only, redacted logs/diagnostics | P | Socket test (12) |
| Change | Threshold/spec quietly changed | Audit before/after + spec-first change control (72) | D+P | Audit, DEC log |

§2 Limitation: one local user can perform and approve their own actions (no segregation of duties inside the app). Mitigations: named attestations (close sign-off, commentary approval), exportable audit trail for external review, advisory disclaimer. Organisations needing SoD should pair the tool with their review process — stated in the pilot plan (83), not discovered later.
