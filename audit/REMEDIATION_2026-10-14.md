# REMEDIATION LOG — brutal audit 2026-10-14 (status per finding)
A1 FIXED: 00_INDEX rewritten with numbered sections 1-10; prompts now cite "section 2 / section 10" which exist.
A2 FIXED: doc 05 section 4 endpoint addendum; new packets: adjustments/engine, planning/allocations, planning/assumptions, services/year_end, routes_{adjustments,allocations,assumptions,year_end,close,reconcile,alerts,planning,reports_builder}, core/license.
A3 FIXED: doc 02 section 6 adds adjustments, allocation_*, assumptions, year_end_runs + schema-equality now covers sections 2/5/6.
A4 FIXED: doc 42 section 7 enumerates P01-P32 + C01-C08, exactly 18 high (generator asserts); doc 14 bars corrected to 29/31 plants + controls.
A5 FIXED: EXC-004 tolerance = 0 minor units everywhere; Holt-Winters minimum = 14 (08 aligned to 46); settings keys unified to materiality.abs_minor/pct (62 owns names).
A6 PARTIAL: stubs were governance/process docs; depth added where implementers need it (53 token VALUES, 55 extended strings, 31 glossary x3, 88 AI prompts). Remaining short docs (57/74/76/79/81/83/84) are decision/process artefacts whose executable content lives in 14/34/71/87 - reclassified honestly here rather than padded; AUD-J must confirm sufficiency per doc at Wave-0 review.
A7 FIXED: tester prompts regenerated - 7-step protocol, minimum 3 mutations, packet-specific acceptance/spec (19 lines vs 5).
A8 FIXED: prompts state deps are module names resolved via FILE_MANIFEST.csv + BLOCKED if owner missing; TWO-file wording (B2) fixed in master prompt and template; REVIEW type added for existing files (B3).
B1 FIXED: packets added for all app/* __init__, UI config files (vite/tsconfig/index/eslint/main/App/format), migrations m0001 + registry, 4 industry packs + pack schema, fixtures README, TASKBOARD.
B4 FIXED: doc 53 section 4 normative hex token table (light/dark, contrast, chart palette).
B5 FIXED: doc 88 - verbatim prompt texts PROMPT-01..06 + 20-case golden set definition.
B6 FIXED: generated docs/DEPENDENCY_GRAPH.{md,csv} (packet -> wave -> deps); dispatch rule = lower-wave tester-SIGNED.
B7 PARTIAL: doc 55 extended (import/statements/forecast/exports/close/settings strings); full per-screen string extraction remains a Wave-4 task enforced by AUD-F mechanical diff.
B8 FIXED (process): doc 67 section 5 feasibility spike mandated before Wave 5; budgets are hypotheses until it lands.
B9 FIXED: doc 02 period identity normative (FY = start year; 2026-P01 = Apr 2026).
B10 FIXED: 00_INDEX section 10 current; doc 01 screens S01-S19 and budget-editing scope aligned.
P2/C-items FIXED: TB wording (03), CF fixture provenance (43), budget grain uniqueness via expression index (02), float driver column -> decimal TEXT (02), API token mechanics (12), extras bar machine-checkable (14), licence packet (79).
REMAINING RISKS (honest): prompt deps are still prose module names (mitigated by resolution rule, not machine-enforced); perf budgets unbenchmarked until spike; ~7 governance docs remain concise by design.
