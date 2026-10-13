# 45 — STATEMENT PRESENTATION & ACCOUNT MAPPING SPECIFICATION

## 1. Statement line registry (fixed keys; labels analyst-renamable, keys never)
PL: `rev` Revenue · `cogs` Cost of Goods/Services · `gp` Gross Profit (calc) · `opex_pers` Personnel · `opex_rent` Rent & Facilities · `opex_it` IT & SaaS · `opex_mkt` Marketing · `opex_prof` Professional Services · `opex_other` Other Operating · `ebitda` (calc) · `depr` Depreciation & Amortisation · `ebit` (calc) · `int` Interest (net) · `pbt` (calc) · `tax` Tax · `net` Net Income (calc).
BS: `ast_cash` Cash & Equivalents · `ast_ar` Receivables · `ast_inv` Inventory · `ast_oca` Other Current Assets · `ast_fa` Fixed Assets (NBV) · `ast_onca` Other Non-Current · `lia_ap` Payables · `lia_debt_st` Short-term Debt · `lia_acc` Accruals & Provisions · `lia_ocl` Other Current Liab. · `lia_debt_lt` Long-term Debt · `eq_cap` Share Capital · `eq_re` Retained Earnings · `eq_oci` Other Equity.
CF (indirect): starts `net`, ± non-cash (`depr`, provisions Δ), ΔWC lines (AR/Inv/AP/OCA/OCL), = Operating CF; Capex; = Investing CF; Debt Δ, Equity Δ, Interest paid (policy setting) = Financing CF; Net Δ; tie to `ast_cash` movement.

## 2. Mapping rules
Every account maps to exactly one line via `accounts.statement_line`; calc-line accounts are never mapping targets. Unmapped account with activity → statements still render, line `unmapped` appears at the end of its statement with the amounts (never dropped), S06 banner + DQ deduction + S12 deep link (P13). Mapping change = new master version with effective_from (doc 41 reclass rules). Sign: each line has presentation_sign from normal_side majority mapping defined in the registry table in code (`calc/statements.py` single table) — changes need doc change here + changelog (P2).

## 3. Presentation rules
Subtotals only from registry calc lines; ordering fixed as listed; zero lines hidden except in Excel (shown, zero) — UI hides with "show zero lines" toggle; ₹'000 view via largest-remainder (doc 03 §3); comparative columns (PY, budget, forecast) use identical line structure; BS without opening → movement presentation (doc 03 §3) driven by the same registry.

## 4. Tests
Registry completeness (every template account in doc 28 maps), unmapped-line behaviour, calc-line rejection as target, FY template → first-import statements render (golden).
