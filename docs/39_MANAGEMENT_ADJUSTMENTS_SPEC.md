# 39 — MANAGEMENT ADJUSTMENTS (TOP-SIDE) SPECIFICATION

## 1. Principle
GL rows from imports are **source truth and immutable**. Analysts need management views (reclasses for reporting, provisions, closing entries) — these live in a separate **adjustment layer** that is added on top, always visible as a layer, never merged invisibly.

## 2. Model (doc 02 addition)
`adjustments(adj_id PK, project_id, period_id, entity_id, account_id, cost_centre_id NULL, amount_minor (signed, doc 02 convention), kind: reclass|provision|closing|correction_view|other, label, reason TEXT mandatory, pair_group_id (reclasses come in balanced groups), created_by/at, status: draft|applied|reversed, reverses_adj_id NULL, source: manual|system_closing)`. Invariant: sum of a `pair_group_id` = 0 for reclass/closing (enforced on apply); provisions may be single-sided but require a mapped contra account field. Applied adjustments are immutable; correction = reversal entry + new adjustment (audit shows the chain).

## 3. Where they apply
Statements/BvA/KPIs/exports take a **layer selector**: `GL only | GL + adjustments (default for board pack, stamped on Cover/Sources)`. Every adjusted total drills in two sections: GL rows, then adjustment lines (with reason + author). BvA budget comparison uses the same layer for actuals as the pack declares. Rules (doc 07) run on GL only by default; EXC-004/007/012 may be re-run "incl. adjustments" as a separate labelled run — findings from each layer never mix (rule run records layer).

## 4. Workflow
Draft → Applied (requires reason; reclass requires balanced group) → Reversed. Bulk entry via grid + CSV import (same quarantine discipline). Monthly recurring adjustments can be copied forward (new draft, amounts editable) — never auto-applied.

## 5. Oracle & tests
GL expense 6100 = 500,000. Reclass pair: −200,000 (6100) / +200,000 (6200) group sums 0 → applied. PL total unchanged, line split changes; drill on 6200 shows GL rows + 1 adjustment line with reason. Unbalanced group apply → rejected with Δ shown. Board pack Cover stamps "Includes management adjustments: 3 lines, net ₹0 (list in Sources)". Tests: invariant, layer selector consistency across API/Excel/PPT, reversal chain, rules-layer separation.
