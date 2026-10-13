# 49 — INTERCOMPANY & CONSOLIDATION DESIGN (Phase-3 build; v1 data reservations NOW)

> Purpose: guarantee v1 decisions never block consolidation later (01 §4). Nothing here is built in v1; the reservations in §2 are mandatory in Wave-1 schema review.

## 1. Phase-3 scope (when built)
Group reporting over entities: IC transaction tagging, IC matching/elimination (sales/purchases, loans/interest, dividends), NCI, goodwill placeholder, consolidated PL/BS/CF with elimination column, group currency (doc 50).
## 2. v1 reservations (checklist for schema packet PKT for schema.sql)
- gl_rows carries entity_id on every row (already) — never aggregate away entity in storage.
- Accounts can be tagged `intercompany` + counterparty entity field reserved: `accounts.ic_counterparty_entity_id NULL` column EXISTS in v1 schema (unused in UI).
- Vendors/customers masters can link to entities (`vendors.linked_entity_id NULL` reserved).
- Adjustment layer (39) supports kind=`elimination` reserved enum value (rejected in v1 UI, allowed in schema).
- Reports snapshot format versions its schema (`snapshot_json.v=1`) so consolidated snapshots can extend compatibly.
## 3. Design sketch (for the Phase-3 PRD amendment)
Elimination via adjustment layer groups generated from IC-tagged pairs with matching workflow (mirror doc 19I recon); consolidated statements = statements engine run over entity set + elimination layer — reusing calc, not a second engine (doc 04 one-owner rule).
