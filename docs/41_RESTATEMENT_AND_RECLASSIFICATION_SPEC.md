# 41 — RESTATEMENT, CORRECTION & RECLASSIFICATION SPECIFICATION

## 1. Three distinct events (never conflated)
- **Source correction:** ERP data was wrong → fix in ERP, re-export, re-import (batch supersedes, doc 06). In-app history shows both batches; findings re-run; exports regenerated get new snapshot ids.
- **Reclassification:** presentation mapping changes (account moved to another statement line / cost centre restructure) → mapping/master change with `effective_from` period. Comparatives: reports offer `as originally reported | as reclassified` toggle; default for board pack = reclassified, stamped.
- **Restatement:** locked-period source data must change → unlock workflow (below).

## 2. Locked-period restatement workflow
1. Analyst requests unlock (period screen): reason mandatory → period `locked → closing`, audit `RESTATE_OPEN`. 2. Correct via re-import (superseding batch) — old batch retained. 3. System produces a **Restatement Impact Report** (auto, before re-lock can complete): statements Δ per line (old snapshot vs new), BvA Δ, findings added/removed/changed, forecast runs invalidated (marked `stale` — never silently reused; rolling re-run required), reports superseded list. 4. Re-lock requires reviewing the impact report (checkbox attestation + note). 5. Prior exports remain on disk with their snapshot stamps — the new pack cross-references "supersedes report <id> dated …" on Cover.

## 3. Invariants
No silent history rewrite: every number ever exported remains reproducible from its snapshot (batches + mappings + layers are versioned, doc 24 §4). Findings closed on superseded data move to `explained` with system note linking the superseding batch (not deleted). Forecast-vs-actual history keeps the run's original base data hash.

## 4. Tests
Restate a locked golden period: impact report Δ matches hand-computed change; stale forecast flagged; re-lock blocked until attestation; as-reported vs as-reclassified toggle reproduces both statement versions; audit chain contains full sequence.
