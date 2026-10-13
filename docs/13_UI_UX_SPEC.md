# 13 — UI/UX SPECIFICATION

> Owner of: screens S01–S15, components, copy, accessibility. Audience: non-technical FP&A analyst (P7). UI formats decimal strings from the API — it never computes money (doc 04; `decimal.js` is display-only: grouping/rounding for display exactly as API strings dictate).

## 1. Global rules
- **Five states per screen, all designed + tested:** loading (skeleton), empty (plain-language "nothing here yet + what to do"), error (ErrorBanner with code-free message + hint + Retry when retryable), success, partial (e.g., some rules not_run — shown, never hidden).
- **Navigation:** left rail: Dashboard, Import, Statements, BvA, Exceptions, Forecast, Scenarios, Exports, Master Data, Settings, Audit, Help. Project + period picker pinned in header on every screen; period lock state always visible.
- **Numbers:** tabular numerals; negatives `(1,200)`; favourable/adverse shown with ▲▼ + the words "favourable/adverse" (P19); every aggregate that supports drill shows a drill affordance and opens DrillDrawer (voucher → row → source file/row).
- **Copy:** sentences, not labels-of-jargon; "potential exception" never "error/fraud"; every empty/error state ends with the next action. Buttons are verbs ("Commit import", "Run checks", "Generate Excel pack").
- **Confirmations:** destructive/irreversible actions (lock period, discard batch, delete project, supersede import) use ConfirmDialog naming the consequence; waivers require reason text (no one-click waive).
- **Accessibility (WCAG 2.2 AA):** full keyboard path, visible focus, aria labels on icon buttons, contrast-checked tokens, 200% zoom without horizontal scroll on data screens (tables may scroll with sticky first column), reduced-motion respected.
- **Design tokens:** single source `ui/src/theme/tokens.ts` + CSS bridge; token-check script fails on any referenced-but-undefined token (attempt-#2 defect class, 7 tokens/39 uses — must be impossible here).

## 2. Screens
| ID | Screen | Purpose & key elements | API |
|---|---|---|---|
| S01 | Dashboard | Close-progress checklist (import→TB→statements→exceptions→forecast→exports with real stage states), KPI tiles, top-5 variances, findings by severity/owner, forecast-accuracy badge, unassigned queue alert | GET dashboard |
| S02 | Projects | List/create/open, sample-project card ("fictional data, safe to explore"), backup/restore/delete | projects |
| S03 | Import wizard | 5 steps: Files → Preview&Profile → Map → Validate (quarantine table with fix actions) → Commit (control totals, TB result). Progress + resumable; overlap warnings before commit | imports |
| S04 | Mapping studio | Profile list, column mapping editor with confidence chips, canonical-field glossary tooltips, version history, set-default | mapping-profiles |
| S05 | Trial balance | Per-entity balance table, imbalance drill to voucher, waive-with-note flow (audited) | statements/drill |
| S06 | Statements | PL/BS/CF tabs, month/YTD toggle, ₹/₹'000 display toggle, drill on every line, "movement statement" labelling when no opening BS | statements |
| S07 | BvA explorer | Grain selector, variance table (favourable words + arrows), bridge chart when drivers exist else explicit unavailable note, commentary editor (draft→approve; AI draft button when enabled) | bva/bridge/commentary |
| S08 | Exception inbox | Filter bar (status/severity/owner/rule), finding cards with evidence summary + drill, bulk assign, transition actions per doc 07 §5, not_run rules panel | exceptions |
| S09 | Forecast studio | Group×method matrix with backtest MAPE/bias chips, run/lock, FVA history, bias advisory badges | forecast |
| S10 | Scenarios | Create from locked run (driver/% deltas), compare table + Δ vs base, assumptions summary | scenarios |
| S11 | Export centre | Generate Excel/PPT/PDF, checks panel (doc 09 §4, failures explained + blocked states), report history with hashes + re-download | exports/reports |
| S12 | Master data (owners) | Entities/accounts/cost-centres/vendors/owners CRUD, account→owner assignment, suspense/accrual tags, threshold & rule-parameter settings link | master/settings |
| S13 | Settings | Tolerances/thresholds (with "what this changes" help), AI configuration (off by default; key in keyring; test-connection), backup/restore, About (version, disclaimer, data location) | settings |
| S14 | Audit trail | Filterable audit list, chain Verify with result banner, finding-history view | audit |
| S15 | Help | Guided first-month-end walkthrough (checklist deep-linking to screens), searchable help topics mirroring doc 18, diagnostics bundle download (redacted, doc 12 §5) | — (static + logs) |

## 3. Components (ui/src/components)
DataTable (sortable, filterable, paginated, keyboard-navigable), VarianceBadge, DrillDrawer, FileDrop, WizardSteps, FindingCard, PeriodPicker, ExportButton (job progress), EmptyState, ErrorBanner, ConfirmDialog, KpiCard. Each: typed props, 5-state usage, axe test + unit test (manifest packets).

## 4. Jobs & feedback
Long operations show JobToast (stage, %, cancel); completion states survive navigation (job registry in uiStore). Success feedback names the artefact ("Excel pack generated — Checks 9/9 passed") and offers the next step ("Open Exports").

## 5. First-run experience
Launch → S02 with sample project preloaded → S15 walkthrough banner "Run your first month-end (≈10 minutes with sample data)" stepping through S03→S11 on sample data. No login, no account, no network prompt — ever.
