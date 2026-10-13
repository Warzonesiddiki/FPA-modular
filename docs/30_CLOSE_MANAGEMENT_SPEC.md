# 30 — MONTH-END CLOSE MANAGEMENT SPECIFICATION

## 1. Close calendar
Per project: close start = period end + offset business days (setting, default T+1), target lock day (default T+5 business days, holiday list per project — manual list v1). Calendar view S16 shows tasks on business days, overdue in words + colour (never colour-only).

## 2. Default task template (instantiated per period; owners pre-filled from master data)
T-01 Import GL & subledgers (system-verified: batch committed) · T-02 Trial balance balanced (system) · T-03 Bank/AR/AP/payroll reconciliations signed (FR-REC) · T-04 Statements reviewed (attest) · T-05 Material variances explained (system: material BvA rows all have approved commentary) · T-06 Exceptions triaged (system: no `new` high findings) · T-07 Forecast refreshed & locked (system) · T-08 Board pack generated, checks green (system) · T-09 Close sign-off (attest) · T-10 Period locked (system). System-verified tasks complete themselves from real states (doc 23 §10); attested tasks need a named human click + optional note. Custom tasks addable (title, owner, due offset, dependency) — template edits apply to future periods only.

## 3. Blockers & escalation
Blocker = unmet system condition for sign-off/lock; shown on S01/S16 with deep links. Overdue tasks → alerts (FR-ALR) at due+1. Close cycle days (period end → lock) recorded per period → KPI + trend on S01 ("close is getting faster/slower" — the product's core promise, measured).

## 4. Sign-off record
Attestation text ("I confirm the pack for <period> is complete and reviewed"), signer label, timestamp, snapshot ids — stored, shown on Excel Cover and S16 history. Sign-off ≠ statutory certification (advisory wording applies).
