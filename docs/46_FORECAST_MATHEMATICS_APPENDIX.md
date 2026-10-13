# 46 — FORECAST MATHEMATICS APPENDIX (exact math for doc 08)

Notation: history `y[1..n]` monthly Decimal; forecasts `ŷ`. All fitting on Decimal via normal equations / iterative updates in `forecast/*` (no float; where a method is classically float (grid search), compute in Decimal with 6dp internal scale).
- **Moving average(n):** ŷ = mean(y[n-k+1..n]). **Naive seasonal:** ŷ[t] = y[t−12] if exists else y[n].
- **Linear trend:** least squares on last ≤12 points, x=1..m: b = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)², a = ȳ − b·x̄; ŷ = a + b·(m+h). CAGR variant (revenue only): (y[n]/y[n−11])^(1/11) − 1 over 12 points, requires all >0 else not_run.
- **Holt (linear):** l_t = α·y_t + (1−α)(l_{t−1}+b_{t−1}); b_t = β(l_t − l_{t−1}) + (1−β)b_{t−1}; ŷ = l_n + h·b_n. Init l_1=y_1, b_1=y_2−y_1.
- **Holt-Winters (additive, m=12):** l_t = α(y_t − s_{t−m}) + (1−α)(l_{t−1}+b_{t−1}); b as Holt; s_t = γ(y_t − l_{t−1} − b_{t−1}) + (1−γ)s_{t−m}; ŷ = l_n + h·b_n + s_{n+h−m}. Init: l = mean(first 12), b = (mean(next 6 if avail) − l)/6 else 0, s_i = y_i − l. Requires n ≥ 14 (else Holt). Grid search α,β,γ ∈ {0.1,…,0.9} minimising backtest MAPE (doc 08 §3 window) — deterministic tie-break smallest (α,β,γ) lexicographic.
- **Seasonal index:** index[p] = mean(y at period-of-year p)/overall mean, requires n ≥ 24 (two full years so every period-of-year has ≥2 observations); below 24 the method returns `not_run` with reason `insufficient_history:<n>/24` (doc 08 §2 — no silent fallback; the selector simply does not consider it). ŷ = index[p] × trend level (Holt level at horizon).
- **Metrics:** MAPE = mean(|A−F|/|A|) over A≠0 (report excluded count), Bias = Σ(F−A)/Σ|A|, Hit = share |err|≤5%.
- **Floors/negatives:** doc 08 §7 applied after method output, recorded per line.
**Numerical oracles (must match in tests; all values computed exactly in Decimal from the equations above — fixture-first per doc 14 §2):**
- **`holt_basic.json`** — y = [100, 110, 105, 115], α = 0.3, β = 0.1, init l₁ = 100, b₁ = 10:
  l₂ = 0.3·110 + 0.7·(100+10) = 110, b₂ = 0.1·(110−100) + 0.9·10 = 10;
  l₃ = 0.3·105 + 0.7·(110+10) = 115.5, b₃ = 0.1·(115.5−110) + 0.9·10 = 9.55;
  l₄ = 0.3·115 + 0.7·(115.5+9.55) = 122.035, b₄ = 0.1·(122.035−115.5) + 0.9·9.55 = 9.2485;
  ŷ₅ = 131.2835, ŷ₆ = 140.5320.
- **`hw_flat.json`** — y = [100, 110] repeated 12 times (n = 24, m = 12), any α, β, γ: init l = 105, b = 0, s = [−5, +5, −5, …]. The series is an exact fixed point of the additive recursions (every update reproduces l = 105, b = 0, s = ∓5), so ŷ₂₅ = 100, ŷ₂₆ = 110, ŷ₂₇ = 100 for **every** grid point; the grid search must still terminate deterministically on (0.1, 0.1, 0.1) by the lexicographic tie-break. (This fixture needs n ≥ 14 for HW; 24 points are used so the same series also exercises the seasonal-index method: indices 0.9524 / 1.0476 at 4 dp, overall mean 105.)
- **`seasonal_short.json`** — the same series truncated to n = 23 → `seasonal` returns `not_run` (`insufficient_history:23/24`); HW still runs.
