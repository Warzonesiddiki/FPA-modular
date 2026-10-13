# 73 — INTERNAL CONTROLS MATRIX

> For CFO/auditor conversations. Control types: P=preventive, D=detective. Single-user limitation stated in §2 — never oversold.

| Process | Risk | Control | Type | Evidence |
|---|---|---|---|---|
| Import | Rows silently lost/altered | Count reconciliation in=valid+quarantined; file hash retained; control totals gate | P+D | Import report, Sources sheet |
| Import | Duplicate posting | Re-import supersede (idempotent) + EXC-001/002 | P+D | Batch history |
| Import (Dynamics 365 pull) | Partial or stale month read from the ERP | `$count` vs rows-received check with one re-pull then hard stop (ERR-118); snapshot file + content hash = same idempotency as a file; pull row (host, company, filter, count, sha256, actor) and audit event per pull | P+D | `connector_pulls`, audit log, Meta sheet of the snapshot |
| Import (Dynamics 365 pull) | ERP data changed by the tool | Read-only scopes; no write endpoint exists in the code (static scan); rectification journal leaves as a file for human posting | P | Static scan evidence, doc 26 §8 |
| Numbers | Transcription/formula error | Single calc engine; exports generated, cross-artifact tie-out; Checks sheet | P+D | Checks, AUD-A/I |
| Numbers | Rounding drift | Integer minor units; largest-remainder presentation | P | Money tests (03) |
| Exceptions | Finding ignored forever | Owner+due workflow, waiver expiry resurfacing, lock guard | D+P | Finding history |
| Exceptions | Wrong or abnormal entry posted and never corrected | Entry-hygiene rules EXC-025…028 + suggested fix on every finding; corrections tracked `corrected → verified` by matching the correcting lines in a later import; unseen corrections surface in the close checklist (T-06) | D+C | Finding history, suggestion status, verification evidence |
| Exceptions | App posts to the ERP by mistake | No ERP write-back by API; corrections leave only as a reviewed journal *file* with a disclaimer footer; adjustments live in the app's own layer | P | Doc 26 §7 formats, doc 39 layer |
| Import | Vendor mis-attributed by enrichment | 1:1 match only on (voucher, date); ambiguous matches reported, never assigned; column-sourced vendors never overwritten; `vendor_source` kept per row | P+D | Enrichment report, audit row |
| Import | ERP export filtered/incomplete (silent row loss) | Per-account trial-balance tie-out (`tb_check`) before commit and as close item T-02 | D | TB tie-out report |
| Period integrity | Locked month changed silently | Lock + audited unlock/restatement impact report | P+D | Audit chain, doc 41 report |
| Adjustments | GL rewritten to hide variance | Immutable GL; separate adjustment layer with reasons | P | Layer drill (39) |
| Access/integrity | DB/audit tampering | Hash-chained audit, verify on demand + before pack | D | S14 verify (ERR-090) |
| Confidentiality | Data leaves machine | Offline design, AI opt-in aggregate-only, Dynamics 365 egress only to the allow-list on user click, redacted logs/diagnostics | P | Socket test, allow-list test (12 §8) |
| Confidentiality | ERP credentials leak | Tokens/secret only in the OS keyring; never in DB, settings, logs, exports, diagnostics, backups; Disconnect wipes them (audited) | P+D | Keyring-only + redaction tests (12 §8) |
| Change | Threshold/spec quietly changed | Audit before/after + spec-first change control (72) | D+P | Audit, DEC log |

§2 Limitation: one local user can perform and approve their own actions (no segregation of duties inside the app). Mitigations: named attestations (close sign-off, commentary approval), exportable audit trail for external review, advisory disclaimer. Organisations needing SoD should pair the tool with their review process — stated in the pilot plan (83), not discovered later.
