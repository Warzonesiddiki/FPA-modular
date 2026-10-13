# MASTER PLAN — FPA-modular (Attempt #5, the final one)

> **Goal in one sentence:** One FP&A analyst, with this tool, does the complete monthly FP&A job that today takes a team — import messy ERP exports → validated, balanced books → explained variances → reviewed exceptions → rolling forecast → board-ready Excel + PowerPoint — in one guided sitting, with every number provable to the source transaction.
>
> **Status of this document:** This is the plan of record. No product code is written until Wave 0 (the 19 spec docs, `docs/00–18`) passes the doc gate in §9. Generated agent prompts live in `agent-prompts/`; the file list of record is `docs/FILE_MANIFEST.md` (+ `.csv`).

---

## 1. What we learned from attempts 1–4 (research, 2026-10-13)

Repos reviewed in full: `finalFPA` (Python+React, 355 py files, 37k lines of docs), `fpa`/OneFP&A (Tauri+Rust+React, 76 docs, 42 screens, 56 tables), plus the two inaccessible repos (`java-fpa-tool-development-2-`, `v0-fpa-tool-development` — private/blocked to this session's GitHub integration; conclusions below rely on the two readable codebases, which contain the same failure DNA).

### What failed — the five killers

| # | Killer | Evidence | Fix in this attempt (§) |
|---|--------|----------|--------------------------|
| K1 | **Scope explosion before a working spine.** Attempt #2 specified 42 screens / 56 tables / 103 commands / 12 industry packs / 3-OS parity before one month-end ran end-to-end. Attempt #4 was still adding architecture upgrades (ADR-015) while its acceptance gate was red. | `fpa/docs/STRATEGIC-VISION.md`; `finalFPA` README §2 | **One spine first** (§3): month-end pipeline is the product; everything else is a later wave behind a cut line (§8). |
| K2 | **Incoherent sample data.** Budget and actuals generated as independent random draws → 370 of 422 "extra" exceptions were noise; planted-exception recall **11/32**, control precision failed, 14 rules with zero findings. The acceptance gate could never go green. | `finalFPA/evidence/acceptance_remediation_2026-10-04.md` | **Coherent corpus is a spec'd deliverable** (§6, PKT for `sample-data/generate_sample_data.py`): one plan, actuals = budget ± controlled noise, plants only from the answer key, balancing legs computed. Corpus is built in Wave 1, *before* rule code. |
| K3 | **Answer-key / catalog / engine key divergence.** Finding keys, grains and thresholds differed between catalog doc, answer key and rule code (EXC-006/008/021/024…). Rules "worked" but matches failed. | same evidence file §2.1 | **One canonical key format + one catalog doc is law** (§5.3); every rule packet quotes its catalog sample case as its test. Contract-freeze gate before rule wave (§9). |
| K4 | **Unverifiable native code.** Attempt #2's Rust core was written for months in an environment with no Rust toolchain: "PARTIAL/NATIVE-UNVERIFIED" features accumulated; CI was red while fixes sat unpushed. | `fpa/audits/HANDOVER.md`, `AUDIT-2026-09-07.md` | **Stack chosen for verifiability** (§4): Python engine — every agent can run its own tests in any sandbox. No compiled-native financial code in v1. |
| K5 | **Mock-only / claimed-done drift.** Screens documented as done while backends were mocks (WS-05/WS-07); a README claiming "Feature Complete v1.0.0-rc2" that was false. | `fpa` audit §3; `finalFPA` README §2 correction note | **Evidence-or-not-done** (§9): DONE requires test output in the handover; acceptance harness is a release-blocking test, and weakening a bar requires an owner DEC entry, never a quiet edit. |

Also kept from the attempts (they were right): docs-before-code, Decimal-only money, offline/local-only, "potential exception, never error confirmed" wording, atomic imports, nothing silently discarded, versioned mappings, cross-artifact tie-outs (UI == Excel == PPT), 5-state screens, typed error catalogue.

### Market check (Oct 2026)
Competitors (Anaplan, Pigment, Datarails, Cube, Vena, Planful) are cloud, per-seat ($1.5k–$30k+/yr), Excel-add-in or implementation-heavy ([1](https://getaleph.com/answers/ai-fpa-software-variance-detection), [2](https://financecopilothq.com/best-fpa-software/)). The 2026 differentiators are: AI variance commentary with drill-down to transaction, anomaly detection, agentic forecasting ([3](https://getaleph.com/answers/best-ai-fpa-tools)). **Our wedge:** the same AI-assisted month-end, but offline, local-only, one-time desktop tool for a single analyst at a mid-size company — no seats, no cloud data exposure, no 8–16-week implementation. AI drafts words around verified numbers; it never computes a number.

---

## 2. Product definition

### 2.1 The job (the monthly rhythm — this is the product)
1. Drop in the month's exports (GL, budget, sub-ledgers: CSV/XLSX from Dynamics 365 / Tally / SAP / QuickBooks / any ERP — file import is the guaranteed path; **no live ERP connectors in v1**).
2. Tool profiles, suggests mappings (saved profile auto-applies next month), validates, quarantines bad rows *with reasons*, checks control totals and trial balance.
3. Tool produces P&L / BS / CF, budget-vs-actual at the lowest shared grain, variance bridge, KPI set.
4. Tool runs 24 exception rules, assigns each finding an owner and due date; analyst works an inbox (explain / correct / waive-with-reason).
5. Tool refreshes the rolling forecast (method per account group, backtested), analyst adjusts drivers, compares Base/Upside/Downside.
6. Tool emits the board Excel pack + PowerPoint deck + PDF summary — cross-tied to the same numbers, every figure drillable to voucher → source file + row.
7. Optional (off by default): AI drafts variance commentary and exec summary from the *verified* tables; analyst edits before anything ships.

### 2.2 Personas
- **Primary:** the single FP&A analyst (non-technical; Excel-fluent). Success = month-end pack out in hours, not days.
- **Secondary:** accounting owners who receive findings; CFO/MD who reads the pack (never operates the tool).

### 2.3 Non-goals / anti-goals (v1)
No cloud, no login/multi-user, no ERP write-back, no live connectors, no consolidation/eliminations/FX translation (data model must not *block* it later), no statutory audit opinion (advisory disclaimer ships in-app), single reporting currency per project. **Anti-goal:** a tool that produces a number nobody can trace — worse than no tool.

### 2.4 Success metrics (numbers, not adjectives)
Month-end on the golden sample company: **≤ 30 min analyst time** (excluding owner responses); acceptance bars in §9 all green; 250k GL rows import+rules within the NFR budgets in doc 14; zero float-money defects; every exported figure ties across Excel/PPT/API in the cross-artifact test.

---

## 3. Architecture — modular monolith, one spine

```
ui/ (React+TS) ──HTTP 127.0.0.1──▶ app/api (FastAPI, thin)
                                      │
                               app/services/month_end.py   ← THE spine
                                      │
   imports ─▶ store (SQLite) ─▶ calc ─▶ rules (24) ─▶ forecast ─▶ exports (Excel/PPT/PDF)
                                      │
                               app/ai (optional, guarded, off by default)
```
- **One owner per concern** (attempt #2's B14, kept): `core/money.py` is the only money math; `store/schema.sql` the only schema; `calc/` the only statement logic; exports consume calc objects, never re-compute.
- **Deterministic core, AI at the edge:** AI receives only aggregated, verified figures; guardrails reject any AI text containing a number not in its input payload.
- **Offline-first:** binds 127.0.0.1 only; zero telemetry; works with network cable pulled (tested).

## 4. Stack (my call — stated plainly, override in doc 04 ADR if you disagree)
| Layer | Choice | Why |
|---|---|---|
| Engine | Python 3.12, FastAPI, pydantic | Every one of 500 agents can run/test it anywhere (K4 fix); attempt #4 proved the ecosystem (openpyxl, python-pptx). |
| Store | SQLite (WAL), money as INTEGER minor units | One engine, one file per project, backup = copy file. (Attempt #4's DuckDB+SQLite duality and attempt #2's Rust are dropped for v1.) |
| UI | React 19 + TypeScript + Vite, zustand, echarts, decimal.js *display-only* | Attempt-proven; UI formats decimal strings, never computes. |
| Packaging | PyInstaller + Inno Setup (Windows first) | Double-click installer, no dev tooling on analyst's machine. macOS is Phase 3, not v1 (K1 fix). |
Tech budget: **≤ 12 libraries**, pinned, licence-checked (doc 12).

## 5. The three contracts that must never diverge again (K3 fix)
1. **Data dictionary ↔ schema:** `docs/02` lists every table/column; `app/store/schema.sql` implements it 1:1; a schema-equality test enforces it.
2. **Calculation spec ↔ oracle fixtures:** every formula in `docs/03`/`07`/`08` carries a hand-worked numeric example; the example *is* a test fixture, written before the engine code that must satisfy it.
3. **Canonical finding key:** `EXC-nnn|entity|account|period|grain-key` — defined once in `docs/07`, used by catalog, answer key, engine and acceptance harness. Any change = spec change + changelog + answer-key regeneration in the same commit.

## 6. Sample-data strategy (K2 fix — build the truth first)
`sample-data/generate_sample_data.py` (one packet) generates from **one financial plan**: budget authored → actuals = budget × (1 + controlled noise, seed-fixed) → only the 32 planted exceptions + 8 controls from `answer_key.json` deviate materially → balancing legs computed per entity×month, never hard-coded → byte-identical regeneration (hash-tested). Malformed corpus (≥10 files) ships with expected quarantine outcomes. **No rule code is accepted before this corpus + acceptance harness exist and run red for the right reasons.**

## 7. The 500-agent execution model

You do not need 500 *files* — you need 500 *accountable work packets*. The manifest (`docs/FILE_MANIFEST.md`) defines **184 creator packets** (one file + its paired test each). The army is deployed in three roles:

| Role | Count | Job |
|---|---|---|
| **Creators** | 184 | One packet each from `agent-prompts/PKT-*.md`, waves in §8 order. |
| **Independent testers** | 184 | A *different* agent re-runs the packet's acceptance criteria, mutation-checks the test (stub the code → test must fail), and signs the evidence block. Never the creator. |
| **Auditors & integrators** | 132 | Cross-cutting packets (§10): contract-parity (API↔docs, schema↔dictionary, tokens, finding-keys), cross-artifact tie-out, security scan, perf, docs-link/verify, accessibility, packaging, acceptance double-run, plus wave-gate reviewers (19 docs × reviewers) and conflict-resolution/integration agents per module. |

**Coordination rules (how 500 agents don't produce attempt #5):**
1. **Waves, not a free-for-all.** A wave opens only when the previous wave's gate (§9) is green. Agents within a wave touch disjoint files (the manifest guarantees it), so merging is file-union, not conflict resolution.
2. **Contracts freeze before dependents start.** Docs (Wave 0) → core+schema+corpus+fixtures (Wave 1) → engine (Wave 2) → services/API (Wave 3) → UI (Wave 4) → exports (Wave 5) → hardening/packaging (Wave 6). A creator who finds a missing contract returns `BLOCKED` — inventing one is the one firing offence.
3. **Every prompt is self-contained:** `agent-prompts/00_MASTER_AGENT_PROMPT.md` (the constitution) + one `PKT-####` file (mission, read-first list, inputs, outputs, 8 non-negotiables, acceptance criteria, exact handover format). Hand an agent exactly those two files plus the spec sections its packet names.
4. **Bring-back protocol:** collect returned files into the repo tree at their manifest paths, run `scripts/check.py` + `scripts/acceptance.py`, and let the *tester* packets — not the creators' claims — mark packets DONE in the task board.
5. Regenerate/adjust packets only by editing `tools/generate_agent_packets.py` and re-running it — never hand-edit 184 prompts.

## 8. Waves & cut lines

| Wave | Content (packet layers) | Exit gate |
|---|---|---|
| **0 — Specs** | `docs/00–18` (19 packets) | Doc gate: no TBD; every ID cross-referenced; tabletop walkthrough of one month-end using only the docs (P20). **Owner approval recorded.** |
| **1 — Truth** | core/*, store/schema+db, sample-data generator + answer key + malformed corpus, oracle fixtures, acceptance harness (runs, red) | Corpus regenerates byte-identical; TB balances; harness reports recall 0/32 *by design* (no rules yet) |
| **2 — Engine** | imports/*, calc/*, rules/* (24+engine), forecast/* | Acceptance green: recall ≥29/32, controls 0/8, high-severity 18/18, extras justified, two runs identical; unit gates green |
| **3 — Services/API** | services/*, api/*, cli, ai/* | API contract parity test; AI-off = zero network calls; month-end golden run via CLI |
| **4 — UI** | ui pages/components/stores | 5-state + a11y tests; token check zero-undefined; UI number == API number fixtures |
| **5 — Exports** | exports/* (Excel/PPT/PDF) | Cross-artifact tie-out green on golden period |
| **6 — Ship** | scripts, packaging, CI, user guide | Fresh-machine install → sample month-end → pack out; perf budgets met; release checklist signed |
**Cut line:** if a wave slips, cut from the *bottom of the next wave* (first: PDF export, scenarios UI, AI commentary) — never cut corpus, acceptance, or audit features.

## 9. Quality gates (evidence-or-not-done)
- `scripts/check.py`: ruff + mypy (strict on `app/core`, `app/calc`, `app/rules`) + pytest + UI lint/type/tests + token/schema/docs parity checks. One command, honest exit code.
- `scripts/acceptance.py`: runs the harness twice, diffs findings, writes `evidence/acceptance_report.{json,md}`. **Release-blocking.** Bars (doc 14 owns the numbers): recall ≥ 29/32 · controls 0/8 fire · high-severity 18/18 · every extra finding justified in the report · run-to-run identical · all 24 rules wired.
- **Definition of Done (every packet):** file + paired tests + test output pasted in handover + no deviation from cited spec (or deviation logged as DEC). A DONE without evidence is returned as not done (K5 fix).

## 10. Audit plan (where the remaining agents go — after build, before ship)
1. **Recompute audit:** independent agents re-derive P&L/BS/CF/BvA from raw fixtures by hand (spreadsheet) and diff against engine output to the minor unit.
2. **Rule-by-rule audit:** 24 agents, one rule each: plant cases beyond the answer key (boundary thresholds ±1 minor unit, zero-base %, leap periods) and hunt false positives on the coherent corpus.
3. **Contract parity:** API↔doc 05, schema↔doc 02, UI tokens, finding keys, error codes — scripted checks + human-agent review of failures.
4. **Adversarial:** prompt-injection via GL descriptions, formula-injection in Excel exports, SQL injection via mapping names, hostile files (zip bombs, 1M-row sheets, bad encodings).
5. **UX tabletop:** a fresh agent (or human) with only doc 18 completes a month-end; every stumble becomes a defect, not a "user error".
6. **Truth audit:** every README/doc claim traced to a gate or deleted (the "v1.0.0-rc2" lesson).

## 11. Risks (top 5)
| Risk | Mitigation |
|---|---|
| Owner decisions stall spec wave (thresholds, currency, FY start) | Doc 17 keeps OQ register with *labelled defaults*; defaults ship, decisions can override pre-freeze only. |
| Real-client data differs from corpus (format drift) | Mapping profiles + malformed corpus + "first real pilot" is an explicit Phase-2 gate, not a v1 promise. |
| 500-agent output variance | Self-contained prompts, BLOCKED-not-invent rule, independent testers, file-disjoint waves. |
| Excel/PPT fidelity arguments consume the schedule | Golden-file cell/slide assertions; "numbers tie, cosmetics iterate" rule. |
| Scope creep ("just add consolidation/AI forecasting…") | §2.3 non-goals + cut line + backlog doc; new ideas land in doc 17, not in waves. |

## 12. What happens next (decision needed from you)
1. **Approve this plan + stack (§4)** — or override stack/FY/currency defaults now; after Wave 0 freeze, changes cost a DEC entry and packet regeneration.
2. I (or your Wave-0 agents) write `docs/00–18` from their packets; you approve the doc set at the Wave-0 gate.
3. Dispatch waves 1–6; I act as integrator/auditor here: run gates, run the acceptance harness, and report evidence — not claims.
