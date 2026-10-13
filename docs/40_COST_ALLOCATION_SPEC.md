# 40 — COST ALLOCATION SPECIFICATION

## 1. Purpose
Distribute shared costs (rent, IT, HO salaries) from source cost centres/accounts to receiving cost centres for true profitability views — as an **allocation layer** (doc 39 mechanics: balanced groups, GL untouched, layer selector applies).

## 2. Methods
- **Direct %:** fixed percentages per receiver (must sum 100.000% — largest-remainder on save).
- **Driver-based:** by headcount, revenue, area, ticket count (driver values from doc 29): share = receiver driver ÷ total driver (Decimal; zero total → blocked with hint).
- **Step-down:** ordered source centres allocate sequentially, a closed centre receives no later allocations (order analyst-defined).
Reciprocal allocations: not in v1 (documented limitation with step-down as the offered alternative).
## 3. Runs
Allocation definition (versioned) → run per period → produces adjustment lines (kind=`reclass`, pair_group per source line, label `ALLOC:<def name>`). Re-run replaces draft run; applied runs lock with period. BvA/reporting can view pre/post allocation (layer + allocation-run selector, stamped in exports).
## 4. Oracle
Rent ₹300,000 in CC-HO; driver headcount: CC-A 30, CC-B 20 (total 50) → A ₹180,000, B ₹120,000; source −₹300,000; group sums 0. Tests: % sum validation, zero-driver block, step-down order effect, layer drill shows ALLOC lines.
