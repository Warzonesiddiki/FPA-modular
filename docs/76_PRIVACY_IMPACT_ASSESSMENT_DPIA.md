# 76 — PRIVACY IMPACT ASSESSMENT (DPIA)

Data processed: financial transactions; names that appear inside them (vendors, customers, employees in payroll extracts, finding owners' names/emails-optional). Purpose: internal FP&A only. Lawful basis: the customer's own legitimate business use — the vendor (us) receives **no data by design** (offline, no telemetry, 12); support data flows are user-initiated files only (diagnostics value-free, anonymised extracts per 78). Minimisation: AI payloads aggregate-only (11 §4); logs/diagnostics redacted (65); descriptions never sent anywhere by default. Retention: user's project folder, user-controlled deletion (12 §7); waivers/audit retained while project exists (integrity purpose, disclosed). Risks & mitigations: local device compromise → OS encryption guidance (18); over-sharing exports → advisory stamps + share-guidance (70); AI enablement → explicit consent copy naming what leaves the machine (aggregates + labels) in S13. Data-subject requests are the customer-employer's process; the app supports them via drill/export of the person's rows (a support runbook note in 35). Review trigger: any feature adding network, accounts, or new personal-data categories reopens this DPIA before build (DEC required).


## Data inventory
| Data | Source | Stored | Sent anywhere? |
|---|---|---|---|
| Employee names in payroll descriptions | ERP export | gl_rows.description (local) | No — AI payloads exclude descriptions (doc 11 §4) |
| Vendor/customer names | GL + masters | local DB | AI commentary may include vendor names for material variances (disclosed in S13 consent) |
| Owner names/emails | Analyst-entered | owners table | Never (no email sending v1) |
| Analyst label | Local setting | audit_log | Never |
The client is data controller; the vendor receives no data by design (support = user-sent diagnostics/anonymised extracts, docs 65/78). This controller/processor fact must be stated precisely in doc 80's legal pack.
