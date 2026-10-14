# 30 — MONTH-END CLOSE MANAGEMENT SPECIFICATION

## 1. Close calendar
Per project: close start = period end + offset business days (setting, default T+1), target lock day (default T+5 business days, holiday list per project — manual list v1). Calendar view S16 shows tasks on business days, overdue in words + colour (never colour-only).

## 2. Default task template (instantiated per period; owners pre-filled from master data)
T-01 Import GL & subledgers (system-verified: batch committed) · T-02 Trial balance balanced (system; when an ERP trial-balance file was imported for the period, also zero per-account tie-out differences — doc 06 §1 `tb_check`) · T-03 Bank/AR/AP/payroll reconciliations signed (FR-REC) · T-04 Statements reviewed (attest) · T-05 Material variances explained (system: material BvA rows all have approved commentary) · T-06 Exceptions triaged (system: no `new` high findings, and no finding `corrected` more than 2 periods ago whose correction is still unseen in the ledger — doc 07 §7.4) · T-07 Forecast refreshed & locked (system) · T-08 Board pack generated, checks green (system) · T-09 Close sign-off (attest) · T-10 Period locked (system). System-verified tasks complete themselves from real states (doc 23 §10); attested tasks need a named human click + optional note. Custom tasks addable (title, owner, due offset, dependency) — template edits apply to future periods only.

## 3. Blockers & escalation
Blocker = unmet system condition for sign-off/lock; shown on S01/S16 with deep links. Overdue tasks → alerts (FR-ALR) at due+1. Close cycle days (period end → lock) recorded per period → KPI + trend on S01 ("close is getting faster/slower" — the product's core promise, measured).

## 4. Sign-off record
Attestation text ("I confirm the pack for <period> is complete and reviewed"), signer label, timestamp, snapshot ids — stored, shown on Excel Cover and S16 history. Sign-off ≠ statutory certification (advisory wording applies).

## 5. Starting and reopening close (DEC-018)
POST start-close (doc 05 §7.3) creates the period template exactly once in the open→closing transaction; GET close/S16 navigation never mutates state. It completes no attest/system task merely by creating rows. Unlock (§7.4) retains task history and the old sign-off, invalidates current readiness, and does not recreate the template. Sections 6–7 resolve the T-09/T-10 cycle and define non-bypassable sign-off/lock guards; impact generation/approval transport remains unfinished.

## 6. Acyclic readiness and permitted exceptions (DEC-020)
T-01…T-08 are prerequisites. T-09 is the **result of successful sign-off**, and T-10 is the **result of successful lock**; neither is a prerequisite to itself or to sign-off. Custom task dependencies must be acyclic and cannot point at T-09/T-10. An absent checklist is not an empty satisfied checklist: start-close must have instantiated it first. System tasks are derived from current evidence, never manually marked done or waived. T-04 remains a named human attestation; custom manual tasks can be waived with a recorded reason. Reading readiness neither instantiates tasks nor writes completion rows, runs rules, refreshes data or creates reports.

The closed blocker register below drives doc 05 §8. Count is the number of offending resources for high_findings, manual_tasks and busy; all other aggregate checks use count=1 when unsatisfied. Omit satisfied rows, sort by code, emit each code once. The fingerprint retains the sorted offending resource identities, not just counts, so replacing one finding with another is not the same review. System/attest/custom prerequisite failures map to their owning check; a missing/cyclic/invalid template maps to statements_review and cannot be bypassed.

| Code | Unsatisfied condition | Overridable |
|---|---|---|
| audit_integrity | Known broken audit chain / integrity read-only state | no |
| busy | Active/queued period-affecting job or incompatible write/lifecycle lease | no |
| period_state | Period is not closing | no |
| no_gl | No committed GL batch for the period (a validated committed zero-activity batch is distinct from no import) | no |
| trial_balance | Any entity's TB is not balanced; an earlier analysis waiver does not make it balanced | no |
| tb_tie_out | An imported ERP TB has unresolved per-account differences | no |
| reconciliations | Required bank/AR/AP/payroll reconciliation sign-offs missing or stale | no |
| statements_review | T-04 not attested for current statements, or template/dependency integrity failure | no |
| material_variances | Material BvA commentary absent, unapproved or stale | no |
| rules | No current completed rule run accounting for all 28 rules (executed or explicit not_run reason); no run is not zero findings | no |
| high_findings | High finding not closed and not effectively waived at the injected evaluation time | yes |
| aged_corrections | Corrected finding more than two periods old still unseen in the ledger (doc 07 §7.4) | no |
| forecast | Forecast missing, unlocked or stale against the current financial inputs | no |
| board_pack | Required Excel/PPT pack missing, failed checks, mismatched snapshots or stale financial inputs | no |
| manual_tasks | Custom manual prerequisite not done/validly waived, including its unresolved manual dependencies | yes |
| restatement_review | Reopened period lacks a current approved impact report with a nonblank approval note | no |

A sign-off override note can cover **only high_findings and manual_tasks**; record the exact overridden rows and review fingerprint. It never marks the task done or removes a finding. All other conditions are hard stops, irrespective of note, force flag or prior waiver. This narrows the earlier blanket 'or override note' wording rather than weakening a gate. Only the lock endpoint's force=true plus a nonblank note permits remaining High findings at lock, and only when the current sign-off already approved that exact review. Neither force nor sign-off overrides a missing/stale impact approval.

## 7. Review binding and sign-off durability (DEC-020)
Doc 05 §8 owns DTOs and token bytes. Evaluate readiness against one consistent project read snapshot and an injected clock. The review binds project/period/version, current project audit head, selected immutable financial snapshot and the full blocker fingerprint. Financial inputs must match the pack manifest (doc 24 §4), not merely the batch watermark. Effective waiver expiry and any state change are re-evaluated before signing/locking, even if no background expiry job has run.

Sign-off appends an immutable close_signoffs record and one CLOSE_SIGNOFF audit event (entity_type=close_signoff, entity_id=signoff_id) atomically. It creates a record; it does **not** change period.version or lock the period. T-09 is a projection of a current valid record. Its audit event hashes the stored fields, not its own resulting hash. To be current, the event must be the **latest project audit event**, the period/version/snapshot must still match, and the recomputed blocker fingerprint must equal the approved one. A new sign-off replaces only which record is current, never historical rows. The deliberately conservative v1 rule invalidates sign-off on any subsequent project mutation, including another period; GET polling is not a mutation. Re-sign after changes. Optimising to domain-specific revision tracking is deferred, not silently inferred.

Lock rechecks all guards and the same sign-off under an exclusive period-write boundary, then atomically changes closing→locked, increments period.version once, sets injected locked_at/updated_at and lock_note, writes PERIOD_LOCK with the signoff_id, and publishes its receipt. T-10 is a projection; do not write a second task-update audit after sign-off before checking its binding. Lock retains the snapshot and sign-off link for history and unlock baseline capture. Failures leave period/tasks/sign-off history untouched. A stale review produces ERR-080 with blocker review_changed; callers refresh readiness. Current-signoff absence/staleness produces ERR-080 with blocker signoff_required. Wrong period state is ERR-016; audit break ERR-090; busy ERR-092; remaining High without force ERR-011; absent/current-impact approval ERR-083. Force without a valid note is ERR-015.

The task editor/calendar/template APIs and impact generation/approval APIs still require WI-0001 expansion. These rules and three transport contracts are not their runtime implementation.
