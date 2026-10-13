# 50 — FX & MULTI-CURRENCY DESIGN (Phase-3 build; v1 reservations NOW)

## 1. v1 stance (shipped, honest)
One reporting currency per project (27); foreign-currency source columns may be imported as reference text; amounts entering gl_rows are already in reporting currency (analyst converts in the ERP export; S03 copy says so).
## 2. v1 reservations (Wave-1 schema checklist)
- gl_rows reserved columns: `fx_currency TEXT NULL`, `fx_amount_minor BIGINT NULL`, `fx_rate TEXT NULL` (decimal string) — populated only if the mapping profile maps them; never used in v1 calcs.
- Money module API is currency-exponent aware (27) and must not hard-code a single currency symbol anywhere (grep gate).
- No float rates anywhere, ever: rates are decimal strings (future-proofing the one decision that's expensive to retrofit).
## 3. Phase-3 design sketch
Entity functional currencies → translation (closing rate BS, average P&L, CTA to equity), transaction FX gain/loss accounts, consolidation per doc 49. Reuses adjustment/snapshot machinery; translation is a layer, never a rewrite of stored rows.
