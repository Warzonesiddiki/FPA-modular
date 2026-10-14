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
POST start-close (doc 05 §7.3) creates the period template exactly once in the open→closing transaction; GET close/S16 navigation never mutates state. It completes no attest/system task merely by creating rows. Unlock (§7.4) retains task history and the old sign-off, invalidates current readiness, and does not recreate the template. Sign-off/lock dependency and impact-review contracts still need WI-0001 expansion; this section does not resolve their T-09/T-10 dependency cycle or declare them implemented.
