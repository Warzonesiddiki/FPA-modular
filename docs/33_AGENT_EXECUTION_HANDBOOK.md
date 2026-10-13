# 33 — SINGLE-AGENT EXECUTION HANDBOOK (how one builder builds this without becoming attempt #5)

> Supersedes the 500-agent handbook (DEC-007). The operating prompt is `AGENT_PROMPT.md` at the repo root; this doc explains the *system* around it — files, ledgers, commit discipline, and why each rule exists — so the owner can audit the process and the builder can recover it after a long gap. Where this doc and `AGENT_PROMPT.md` disagree, `AGENT_PROMPT.md` wins and this doc is fixed.

## 1. The operating files
| File | Role | Who writes it |
|---|---|---|
| `AGENT_PROMPT.md` | The one prompt: session protocol, work-item loop, gap rules, non-negotiables, self-verification, handover format | Owner (changes are DECs) |
| `docs/WORK_PLAN.md` + `.csv` | All 250 work items in build order with purpose, dependencies, inputs/outputs, acceptance, paired test, cited spec sections; milestones M0–M6 with exit gates | **Generated** by `tools/generate_work_plan.py`; never hand-edited |
| `TASKBOARD.md` | Live ledger: status per item (`queued / in_progress / done / blocked / exists-unverified`), handover blocks, *Owner attention*, *Current position* | Builder, every session |
| `docs/17_ROADMAP_RISKS.md` §3/§4 | Open questions with labelled defaults; decision log | Builder appends; owner accepts/vetoes |
| `docs/CHANGELOG.md` | Every doc change, newest first | Builder |
| `evidence/` | Test outputs, acceptance reports, milestone audits, perf runs, screenshots | Builder (never edited after the fact) |
| `docs/00_INDEX.md` §10 | Current phase/milestone | Builder at gate closure |

## 2. The loop in one picture
```
session start ─► read AGENT_PROMPT + TASKBOARD ─► run tests (truth) ─► pick first startable WI
      ▲                                                                        │
      │                                                                        ▼
 commit "WI-####: path — done" ◄── handover block ◄── §6 self-verify ◄── implement ◄── tests from oracle ◄── read cited spec
                                                                                       │
                                                                 spec gap? ─► class A: OQ + default, proceed
                                                                              class B: fix doc first (+CHANGELOG/DEC), then build
                                                                              class C: BLOCKED in TASKBOARD, next item
```

## 3. Why the rules are shaped this way (lessons → rules)
| Killer from attempts 1–4 (MASTER_PLAN §1) | Rule that kills it |
|---|---|
| Scope before a working spine | Strict milestone order; M1→M2 critical path; cut line only on UI/report-builder extras |
| Incoherent sample data | Corpus generated from `plan.json` with controlled noise and a coherence test; plants only via `plant_P##()` |
| Contracts that diverged | One owner per fact (doc 00 §5); class-B rule: doc first, same session; schema/API/error parity tests at column/field/code level |
| Unverifiable code | Tests from oracles **before** code; ≥3 mutation checks per item; `scripts/check.py` has no skip flags |
| "Done" without evidence | Handover block with pasted test output; TASKBOARD `done` requires it; milestone audit session re-verifies ten items chosen by number |
| (new, single-agent) Memory loss between sessions | Repository-as-memory: re-read spec per item; cite doc §; look, don't recall; TASKBOARD *Current position* |
| (new, single-agent) Self-certification | Cold audit session per milestone (doc 34 §2) written as a stranger; owner spot-checks; second-seed audit dataset in M5 |

## 4. Commit & branch discipline
- One work item = one commit `WI-####: <path> — done|blocked`. Doc fixes = separate commits `docs: <doc> §<n> — <what>`. Regenerated WORK_PLAN = its own commit `plan: regenerate (<reason>)`.
- Never rewrite history. Never commit generated artefacts except `docs/WORK_PLAN.*` and `evidence/` reports.
- The tree is green at every commit (`python -m pytest -q`, later `scripts/check.py`). A red commit is allowed only with `blocked` in its message and a TASKBOARD row explaining it.

## 5. The TASKBOARD contract
- Rows are keyed by WI id; order is WORK_PLAN order. A row is `done` only with the full handover block (`AGENT_PROMPT.md` §8).
- `exists-unverified` marks files that pre-date the plan (the build-pause code); they are re-verified against their acceptance line before `done` — existing tests passing is not enough.
- *Owner attention* is informational since DEC-010 (owner delegated decisions): it lists the DECs taken (`auto`) with their doc locations and any class-C blocks with evidence. Nothing in it waits for approval; the owner reverses a decision by editing doc 17 §4 and the owning doc, and the builder regenerates/patches in the next session.
- *Current position* holds exactly one `in_progress` item (or none) with its next step.

## 6. Context hygiene (the single most important discipline for one agent)
Memory of a spec is not a spec. Before every item the builder re-reads the cited sections — even if it wrote the previous item against the same doc. Decisions live in docs/DECs, not in the builder's head: "I decided earlier" is not a citation. Long reasoning goes to `evidence/` notes, not to chat. When reality and plan disagree (file exists, path moved), the generator is fixed and the plan regenerated — never the plan hand-edited.

## 7. Anti-patterns (each is an automatic defect, found by the audit session or the owner)
Invented contracts · stub-as-done · weakened tests/bars · float money · mock-only paths · silent scope additions · claiming tests not run · copying code from prior attempt repos without provenance note and licence check (doc 12 §6) · hand-editing generated files · resolving a spec gap in code without an OQ/DEC · starting the next milestone with an open gate · a session that ends without updating TASKBOARD.
