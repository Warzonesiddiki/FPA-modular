# 53 — DESIGN SYSTEM & COMPONENT SPECIFICATION

## 1. Tokens (single source `ui/src/theme/tokens.ts`, doc 13)
Colour (light + dark values, contrast-verified pairs): bg/app, surface, surface-alt, border, text/primary, text/secondary, primary (actions/links), on-primary, success, warning, danger (= "needs attention", never labelled error-red for findings — severity uses amber/orange/red with text labels), info; favourable=teal-green, adverse=vermilion (colourblind-safe pair, always + word/arrow). Type scale: 12/14/16/20/24/32, tabular numerals for data. Spacing 4pt grid; radius 6/10; elevation 3 levels. Charts palette: 6 categorical (colourblind-checked order) + sequential for heatmaps; every chart has data-table alternative (a11y, doc 57).
## 2. Components (extends doc 13 §3 — states/variants/usage)
DataTable (density toggle, column chooser persisted, export-CSV), VarianceBadge (word+arrow+value), DrillDrawer (breadcrumb voucher→rows), FileDrop (drag/keyboard/paste-list), WizardSteps, FindingCard (severity chip w/ text, age, owner), KpiCard (value, Δ chip, sparkline w/ table alt), charts wrappers (Bar/Line/Waterfall with fallbacks), Toast/JobToast, Modal/ConfirmDialog (focus trap), Tabs, FilterBar (saved views), EmptyState/ErrorBanner/Skeleton patterns, PeriodPicker (lock icon + label), LayerSelector (GL/GL+Adj per doc 39).
Each component: props contract, keyboard behaviour, aria, and a paired test (one WORK_PLAN item per component) — visual regressions via screenshot fixtures on S01/S07/S08 (M4).
## 3. Iconography & imagery
Lucide icons, 16/20px, always paired with text for critical actions; no emoji in product UI/exports; logo placeholder config-driven (doc 01 §8).

## 4. Token values (normative — tokens.ts implements exactly these; contrast ratios computed in the token test)
| Token | Light | Dark | On/against | Contrast |
|---|---|---|---|---|
| bg-app | #F7F8FA | #111417 | text-primary | — |
| surface | #FFFFFF | #1B1F24 | text-primary | — |
| surface-alt | #EEF1F5 | #242A31 | text-primary | — |
| border | #D4DAE2 | #39424E | — | — |
| text-primary | #17202A | #F2F5F8 | surface | ≥12:1 |
| text-secondary | #4A5A6A | #B8C4D0 | surface | ≥7:1 |
| primary | #0B5FFF | #6EA8FF | #FFFFFF on primary | ≥4.6:1 |
| favourable | #0E7A3D | #3FB96F | surface (+ word/arrow) | ≥4.5:1 |
| adverse | #C62F3B | #FF7A85 | surface (+ word/arrow) | ≥4.5:1 |
| warning | #9A6A00 | #E3B341 | surface (+ label) | ≥4.5:1 |
| info | #0B5FFF | #6EA8FF | surface | ≥4.5:1 |
Severity chips: high = adverse colours, medium = warning, low = info — always with the severity word printed (docs 55 names).
Chart categorical order: #0B5FFF, #0E7A3D, #E07B00, #7A4FD0, #C62F3B, #00838F (tested pairwise for common colour-vision deficiencies in the token check).
