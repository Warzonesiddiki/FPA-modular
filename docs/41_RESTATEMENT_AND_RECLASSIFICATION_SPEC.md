# 41 — RESTATEMENT, CORRECTION & RECLASSIFICATION SPECIFICATION

## 1. Three distinct events (never conflated)
- **Source correction:** ERP data was wrong → fix in ERP, re-export, re-import (batch supersedes, doc 06). In-app history shows both batches; findings re-run; exports regenerated get new snapshot ids.
- **Reclassification:** presentation mapping changes (account moved to another statement line / cost centre restructure) → mapping/master change with `effective_from` period. Comparatives: reports offer `as originally reported | as reclassified` toggle; default for board pack = reclassified, stamped.
- **Restatement:** locked-period source data must change → unlock workflow (below).

## 2. Locked-period restatement workflow
1. Analyst requests unlock (period screen): POST unlock (doc 05 §7.4), expected_version and reason mandatory → period `locked → closing`, version +1, audit `RESTATE_OPEN`. The transaction first retains immutable pre-unlock snapshot references and old lock metadata; any failure rolls back and leaves the period locked. The prior sign-off remains historical, not current. 2. Correct via re-import (superseding batch) — old batch retained. 3. System produces a **Restatement Impact Report** (auto, before re-lock can complete): statements Δ per line (old snapshot vs new), BvA Δ, findings added/removed/changed, forecast runs invalidated (marked `stale` — never silently reused; rolling re-run required), reports superseded list. 4. Re-lock requires reviewing the impact report (checkbox attestation + note). 5. Prior exports remain on disk with their snapshot stamps — the new pack cross-references "supersedes report <id> dated …" on Cover.

## 3. Invariants
No silent history rewrite: every number ever exported remains reproducible from its snapshot (batches + mappings + layers are versioned, doc 24 §4). Findings closed on superseded data move to `explained` with system note linking the superseding batch (not deleted). Forecast-vs-actual history keeps the run's original base data hash.

## 4. Tests
Restate a locked golden period: impact report Δ matches hand-computed change; stale forecast flagged; re-lock blocked until attestation; as-reported vs as-reclassified toggle reproduces both statement versions; audit chain contains full sequence.

## 5. Current approval is not a reusable checkbox (DEC-020)
Sign-off and re-lock both require a nonblank approval note attached to a reviewed impact report for the exact immutable pre-unlock baseline and current after-input snapshot. The approval must identify that report and both snapshots in its retained history. Later source/mapping/layer/budget/forecast/commentary/finding changes that alter the report's inputs invalidate it; a different report or an earlier unlock cycle cannot satisfy it. A note on lock or generic close override is **not** this approval. Missing/stale approval remains ERR-083, reason=approval_note_required (no new code); refresh/regenerate impact and review it. Doc 05 §8 guards are specified, but impact generation/approval routes and field schemas still require WI-0001 work and must not be invented in a route implementation.

The acyclic re-lock sequence is: corrected inputs → current forecast/approved commentary → checked pack → impact report for the original baseline and that current after-input snapshot → impact approval → sign-off → lock. Impact generation/reading does not itself alter financial inputs. Only forecasts based on superseded inputs are stale; a newly regenerated run matching current inputs must not be invalidated merely because impact is generated, or this would create another cycle. Later financial changes require refreshed impact and approval before the next sign-off.
