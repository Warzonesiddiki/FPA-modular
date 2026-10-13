# BRUTAL AUDIT — FPA-modular doc & prompt system (2026-10-14)

> Auditor stance: trust nothing, verify everything. Method: full-repo automated cross-checks (doc refs, EXC/ERR/screen IDs, manifest↔prompt parity, oracle arithmetic re-computation, contradiction greps) + manual contract tracing. **Verdict: NOT READY FOR WAVE 1. Score: 5/10 as a plan, 3/10 as buildable spec.** The skeleton is genuinely good; the flesh is thinner than the page count claims, and several contracts that agents must build against do not exist yet. Dispatching 500 agents today would reproduce attempt #4's failure at 10× the scale.

## What actually passed (credit where due)
Manifest↔prompts parity is perfect (270 = 270 = 270 testers, no duplicate paths, no case-clashes). No dangling doc references. EXC-001…024, S01…S19, ERR catalogue cross-refs all resolve. Every hand-worked oracle recomputed correctly (PL chain, bridge 1000+600=1600, allocation, HW fixture, doc-29 integrated 480,000, DSO). No duplicate doc numbers. Canonical finding-key rule and coherent-corpus principle are the right calls.

## P0 — BLOCKERS (agents will invent contracts; that's the firing offence we defined)

**A1. Every one of the 270 creator prompts cites a section that does not exist.** Prompts order agents to read `docs/00_INDEX.md §2 and §10`; 00_INDEX has no numbered sections at all (headings are unnumbered, and there is no §10 content). The constitution's first instruction is a dead reference — in all 270 packets.

**A2. The new flagship features have NO code packets and NO API routes.** Docs 38 (year-end), 39 (adjustments), 40 (allocations), 48 (assumptions) define features, but the manifest contains no creator packet for them (verified: no packet path contains adjustments/allocations/assumptions/year-end) and doc 05/29 define no endpoints (`adjustments`/`allocations` absent from API docs). Close/reconcile/alerts/planning exist in docs 29's one-paragraph "API addendum" with no route files (only 9 route packets exist, none for them). Traceability doc 20 was never updated for docs 38–87 — its own rule ("empty cell blocks release") fails on arrival.

**A3. Data dictionary is missing the tables the new docs require.** Doc 39 defines `adjustments(...)`, doc 48 defines `assumptions(...)`, doc 40 needs allocation definitions/runs — none appear in doc 02 §5's expansion table list. The schema agent (PKT for schema.sql) will faithfully build a database that cannot store management adjustments. This is exactly attempt-#4's K3 divergence, pre-installed.

**A4. The acceptance corpus — the project's "ground truth" — is not actually specified.** Doc 42 never enumerates P01–P32 (only P01/P30/P32 are even named; one plant function mentioned). "Every rule ≥1 plant, high-severity ≥2" does not mathematically guarantee the "high-severity recall 18/18" bar in doc 14 — nobody can verify 18 high-severity plants exist. The answer key that killed attempt #4 is still a promise, not a spec.

**A5. Direct contradictions between owning docs.**
- EXC-004 tolerance: doc 07 says "beyond ₹0.01 tolerance (setting, default exact)" *and* its own worked example fires at exactly ₹0.01 with "0 tolerance"; doc 44 sets `tol` default 0 minor units. Three versions of one number.
- Holt-Winters minimum history: doc 08 table says 12; doc 46 says n ≥ 14 else Holt. `seasonal` says 24 in 46, "12 for seasonal" in 08's table row for exponential_smoothing conflates two methods.
- Settings key naming: doc 03 uses `material_abs_minor`/`material_pct`; doc 62 uses `materiality.abs_minor`/`pct`. Two names for one setting = two implementations.

**A6. "87 docs written" is page-count inflation.** 92 md files total 2,191 lines (avg ~24/doc). Docs 57, 74, 76, 79, 81, 83, 84 are 3 lines each (single-paragraph executive summaries, 91–160 words). Glossary (31) is 3 lines. These are *stubs with good posture*, not specifications — an agent asked to implement WCAG conformance, model risk, or licensing from them must invent ~90% of the content. By the project's own banned-pattern list ("stub presented as done"), roughly 25 of the 50 new docs fail review.

**A7. Tester prompts are theatre about theatre.** Each TST prompt is 5 lines. Doc 34 demands mutation testing, edge checklists, and evidence — the actual per-packet tester prompt contains none of the packet-specific acceptance detail beyond echoing one line. "220 individual tester prompts" is technically true and substantively false.

**A8. Creator prompts are generic where it matters most.** The same universal edge checklist orders a `.gitignore` agent and a docs-verification agent to handle "expired waivers" and "float money via app/core/money.py" (meaningless for UI TypeScript and docs); dependencies are cited as bare words (`api/client`, `calc/bva`) that are not file paths; inputs for most packets are one-line fragments ("actions", "state"). An agent following PKT-0150 literally cannot find its dependency. The prompts prevent *some* failure modes and guarantee BLOCKED-or-invent on contact with reality.

## P1 — SERIOUS (will cause rework/defects mid-build)

**B1. Missing files the build cannot proceed without** (no packets): all package `__init__.py` except `app/` (1 of ~12), UI build config (`vite.config.ts`, `tsconfig*.json`, `index.html`, eslint/prettier configs), DB migration files (doc 61 mandates `app/store/migrations/m0001…`, zero packets), industry pack JSONs (doc 28 promises 4 packs as data files, zero packets), oracle/fixture files (fixtures are referenced as test inputs in dozens of packets but are nobody's deliverable), TASKBOARD.md, docs/CHANGELOG maintenance, evidence templates. The manifest claims "every file" — it is missing at least 4 whole categories.

**B2. One-file rule is violated by design.** Every creator packet says "ONE FILE" and simultaneously assigns a paired test file (170 paired tests). Two files, one owner, and the tester is told to scope-diff "only the packet's file (+ paired test)". Minor — but a constitution that contradicts itself in §1 teaches agents to improvise around rules.

**B3. 88 packets order agents to "verify, don't rewrite" files that already exist** (the docs) while the master prompt says "You create exactly this file". A creator agent receiving PKT for docs/42 will either overwrite the lead-authored doc or return confused. These are review assignments mislabelled as creation packets, inflating the "270 creators" headline.

**B4. Unbuildable design system.** Doc 53 names colour tokens but contains **zero hex values**, zero actual spacing/type assignments beyond a scale list. 19 screens will be built by 19 agents inventing 19 palettes — precisely the attempt-#2 undefined-token disaster, one layer up.

**B5. AI prompts do not exist.** Doc 11/75 name PROMPT-01…06 and demand versioned prompt texts + golden eval sets; no prompt text, no golden payload set is written anywhere. The AI agents must invent the core artefact they were supposed to implement under guardrails.

**B6. No dependency graph.** Doc 86's WBS lists dependencies as layer names ("2b + frozen doc 44"); the generator stores `deps` as prose. Nobody — human or script — can compute dispatch order or detect a packet started before its contract froze. For a 500-agent plan, the coordination artefact is a paragraph.

**B7. Copy catalog is 7 lines.** Doc 55 promises "every string"; it contains ~10 strings. Screens will invent microcopy per-agent (the exact drift doc 55 exists to prevent).

**B8. Performance budgets are asserted, not reasoned.** 250k-row DrillData sheet via openpyxl in ≤60s *while also* generating 11 other sheets, plus a ≤1.5GB memory ceiling (doc 36 NFR-09), on the stated reference profile — nobody has benchmarked openpyxl at this scale in this project, and doc 67's plan would only discover infeasibility in Wave 5. Attempt-#4's DEF-030 (236 rows/s surprise) is the precedent for exactly this.

**B9. Fiscal-period identity is ambiguous.** Doc 02 uses `2026-P01` with FY starting April — is 2026 the calendar year of April or the FY label? Every PY/YoY/rollforward computation depends on this; it is defined nowhere.

**B10. Stale status everywhere.** 00_INDEX still says "docs 00–18 complete, awaiting approval" (it's 00–87 now); doc 01 still scopes "screens S01–S15" and lists budget authoring as Phase-2 while docs 19/29 spec it in v1 — scope is simultaneously in and out. A new agent reading PRD first (as instructed) gets the wrong product.

## P2 — REAL BUT FIXABLE LATER
C1. Doc 03's TB statement "Σ debit = −Σ credit" is sign-confused under its own storage convention (with credit stored negative, balance means Σ all rows = 0). C2. Doc 43's cash-conversion fixture (1,480k OCF) appears from nowhere — no CF oracle fixture defines it. C3. Budget_lines composite PK includes nullable cost_centre_id (SQLite allows NULLs in PK columns — uniqueness silently unenforced for the common case). C4. `driver_values`/`quantity REAL` reintroduces float through the side door (drivers feed money computations). C5. API token mechanics for pywebview (doc 12) never specified — how does the UI learn the per-launch token? C6. Licensing (doc 79) has no screen/packet despite S13/settings scope. C7. Doc 14's "every extra justified" bar is subjective prose, not a measurable gate. C8. Glossary defines ~30 terms for a domain needing ~120. C9. `evidence/` folder, TASKBOARD, and audit artefact locations referenced but not scaffolded.

## Root cause (one sentence)
The doc set was optimised for *coverage of topics* under time pressure, not for *implementability per contract* — it reads like the index of the perfect doc set more than the doc set itself, which is precisely how attempts #1–4 felt at this stage.

## Remediation order (before any Wave-1 code)
1. Fix A1 (number 00_INDEX sections or fix all prompts via generator) + regenerate. 2. Write the missing contracts: adjustments/allocations/assumptions/year-end data+API+packets (A2/A3), enumerate P01–P32+C01–C08 with rule/amount/key each (A4). 3. Resolve A5 contradictions in owning docs. 4. Deepen the ~25 stub docs to implementable depth or honestly reclassify them "summary — detail deferred to <wave>" in doc 37 (A6). 5. Rewrite tester prompts with packet-specific checks; inject real file-path deps + inputs into creator prompts via the generator (A7/A8). 6. Add missing file categories to the manifest (B1), resolve the one-file/test pairing wording (B2), convert doc packets to REVIEW-type packets (B3). 7. Tokens with values (B4), AI prompt texts + golden set (B5), machine-readable dependency graph (B6). 8. Re-audit (AUD-J) against this report; only then ask the owner for DEC-006 approval.
