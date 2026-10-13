# 10 — POWERPOINT OUTPUT SPECIFICATION

> Owner of: the management deck (`app/exports/ppt_pack.py` + `slide_*.py`, python-pptx). Generated from the same snapshot as the Excel pack (doc 09); cross-artifact test proves deck number == Excel cell == API value (doc 14).

## 1. Deck contract
16:9, `<Project>_Board_<YYYY-P##>.pptx`, template-less (all layout in code; no external template file dependency). Fonts: Calibri (present on target machines); fallback list documented. Every data slide carries: title, period stamp, source line ("Source: GL batches … · Forecast run … · Generated <date>"), and speaker notes containing the drill reference (statement line keys / finding keys / BvA grain) so a presenter can answer "where from?" live. Advisory line on title slide. Numbers formatted exactly as Excel PL (doc 09 §3); negatives parenthesised, never colour-only.

## 2. Slides (8 types; order fixed; a type is omitted only with an explicit "not available" placeholder slide — never silently dropped)
| # | Slide (packet) | Content | Chart (native pptx) |
|---|---|---|---|
| 1 | title | Project, period, prepared-for, advisory, snapshot stamps | — |
| 2 | summary | Exec summary: 4 KPI tiles (Revenue, EBITDA, Net, Cash), top-3 variances (favourable/adverse labelled in words), open high findings count, forecast outlook line; commentary text (analyst-approved version only, doc 11) | — |
| 3 | pl | P&L summary table (Actual/Budget/Var/PY, month+YTD) | bar: Actual vs Budget by line |
| 4 | bridge | Variance bridge for the selected account group (doc 03 §6) or BvA top movers waterfall when no drivers | waterfall |
| 5 | exceptions | Findings by severity/rule/owner aging table; top-5 by amount with owner + due date + suggested-fix kind; count of corrections queued/exported for the ERP; wording: "potential exceptions for review" | bar: count by rule |
| 6 | forecast | Remaining-year forecast vs budget, method + MAPE per group, scenario band if scenarios selected | line: actual→forecast continuity |
| 7 | risks | Risks & actions: expired waivers, stale suspense (EXC-007), bias advisories (doc 08 §6), checklist blockers | — |
| 8 | appendix | Checks summary (doc 09 §4 pass/fail), sources & hashes, definitions of KPIs/rules referenced | — |

## 3. Data rules
Charts are native (editable) with data tables embedded; no chart images. Any figure that fails a doc-09 check blocks deck generation (ERR-060) — a deck with wrong numbers is worse than no deck. Long tables paginate across continuation slides with repeated headers. Text overflow policy: shrink-to-fit floor 10pt, then split slide; truncation of numbers is forbidden.

## 4. Tests
Golden deck: slide count/order, every numeric cell vs Excel golden values, notes presence, blocked-generation case (failed check), no-driver bridge fallback slide.
