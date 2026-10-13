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

## 5. Preset mapping tables (normative — presets ship as data; analysts can override per project)
Columns: Canonical (doc 06) ← source headers (case-insensitive, trimmed). Confidence = deterministic suggester's expected top-1 basis.

### D365-GL v1 (Dynamics 365 F&O, General journal account entries)
entity ← Company · account ← MainAccount · cost_centre ← CostCenter (financial dimension) · voucher_no ← JournalBatchNumber + Voucher (concatenate with `-`) · posting_date ← AccountingDate (ISO in export) · document_date ← DocumentDate · description ← Description · debit ← DebitAmountMST · credit ← CreditAmountMST · vendor ← name in Description? NO — vendor only if VendorAccount column present; else empty (never parse names out of descriptions).
### Tally-GL v1 (TallyPrime Ledger/Day-Book CSV via export)
entity ← Company (export is per-company; constant transform) · account ← Ledger · cost_centre ← Cost Centre (if enabled) · voucher_no ← Voucher No. · posting_date ← Date (DD-MM-YYYY declared) · description ← Narration (hostile-data rules) · amount ← Amount signed; if Dr/Cr suffix present (`1,200 Dr`) the transform `tally_dr_cr` converts suffix to sign — suffix parsing is part of this preset's tests.
### SAP-GL v1 (FAGLL03/FBL3N)
entity ← Company Code · account ← Account (leading zeros preserved: transform `keep_text`) · cost_centre ← Cost Center · voucher_no ← Document Number · posting_date ← Posting Date (declared format) · document_date ← Document Date · description ← Text · debit ← Debit (local curr.) · credit ← Credit (local curr.) · vendor ← Vendor where present.
### QuickBooks-GL v1 / Xero-GL v1 / Zoho-GL v1
entity ← constant (single-company exports) · account ← Account · voucher_no ← Num / Journal # / Transaction ID resp. · dates declared per preset (QB: MM/DD/YYYY; Xero/Zoho: DD/MM/YYYY default but profile records the analyst's confirmation — doc 06 ambiguous-date quarantine still applies) · amount ← Amount signed (QB/Xero) or Debit/Credit pair (Zoho).
## 6. Preset governance
A preset change is a data PR with: sample file (synthetic), expected mapping result, changelog (docs/CHANGELOG). Wrong-preset reports are S2 defects (doc 72). New ERP presets are the cheapest "integration" we ship — support can author one from a client sample in under a day using this section's pattern.
