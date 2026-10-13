# 26 — INTEGRATIONS & ERP EXPORT FIELD GUIDES

> v1 integration = **files, done perfectly** (no live connectors — PRD 01 §4). This doc makes "any ERP" concrete so import is never a guessing game.

## 1. Canonical import templates (ship as downloadable .xlsx/.csv from S03)
GL template: Entity, Account, CostCentre, Vendor, VoucherNo, DocDate, PostingDate, Description, Debit, Credit (or signed Amount). Budget: Period, Entity, Account, CostCentre, Amount. Drivers: Period, Entity, Driver, Account(optional), Value. Opening: Account, Entity, Amount(signed). Subledger (bank/AR/AP/payroll): Date, Reference, Party, Amount(signed), Account(optional). Each template has an instruction row + 3 example rows + a "do not rename headers in your saved mapping" note.

## 2. Per-ERP export recipes (step lists in S15/doc 18 appendix; mapping profile presets shipped)
- **Microsoft Dynamics 365 F&O / Business Central** — General journal / Chart of accounts exports; debit/credit columns; preset profile `D365-GL v1`.
- **Tally (India)** — Day Book / Ledger exports via XML→CSV guidance + Tally ODBC note; parentheses negatives; preset `Tally-GL v1`.
- **SAP (ECC/S4)** — FBL3N/FAGLL03 layouts; leading-zero account handling (text, never numeric-strip); preset `SAP-GL v1`.
- **QuickBooks / Xero / Zoho Books** — Journal/General Ledger reports; date-format presets (MM/DD vs DD/MM declared, never guessed — doc 06 ambiguous-date quarantine); presets per product.
- **Generic/legacy** — profiler + suggestions carry the load; analyst saves as a named profile (month-2 free).
Presets are *mapping profiles as data* — adding one needs no code release.

## 3. Future connectors (Phase 2, contract-first)
When built, connectors must land data through the identical staging→validation→commit pipeline (a connector is just another file producer writing import_batches) — no connector may write gl_rows directly. API credentials, if ever, live in OS keyring only. This constraint is architectural (doc 04) so Phase 2 cannot bypass quarantine/TB/audit.

## 4. Export integrations
Excel/PPT/PDF (docs 09/10); owner action list (Excel per owner, S08); diagnostics bundle (12 §5); CSV re-export of any table grid (same formula-injection guard). No email sending in v1 (no stored SMTP credentials) — files are shared by the analyst's normal tools.
