# 53 — DESIGN SYSTEM & COMPONENT SPECIFICATION

## 1. Tokens (single source `ui/src/theme/tokens.ts`, doc 13)
Colour (light + dark values, contrast-verified pairs): bg/app, surface, surface-alt, border, text/primary, text/secondary, primary (actions/links), on-primary, success, warning, danger (= "needs attention", never labelled error-red for findings — severity uses amber/orange/red with text labels), info; favourable=teal-green, adverse=vermilion (colourblind-safe pair, always + word/arrow). Type scale: 12/14/16/20/24/32, tabular numerals for data. Spacing 4pt grid; radius 6/10; elevation 3 levels. Charts palette: 6 categorical (colourblind-checked order) + sequential for heatmaps; every chart has data-table alternative (a11y, doc 57).
## 2. Components (extends doc 13 §3 — states/variants/usage)
DataTable (density toggle, column chooser persisted, export-CSV), VarianceBadge (word+arrow+value), DrillDrawer (breadcrumb voucher→rows), FileDrop (drag/keyboard/paste-list), WizardSteps, FindingCard (severity chip w/ text, age, owner), KpiCard (value, Δ chip, sparkline w/ table alt), charts wrappers (Bar/Line/Waterfall with fallbacks), Toast/JobToast, Modal/ConfirmDialog (focus trap), Tabs, FilterBar (saved views), EmptyState/ErrorBanner/Skeleton patterns, PeriodPicker (lock icon + label), LayerSelector (GL/GL+Adj per doc 39).
Each component: props contract, keyboard behaviour, aria, and a test (manifest) — visual regressions via screenshot fixtures on S01/S07/S08 (Wave 4).
## 3. Iconography & imagery
Lucide icons, 16/20px, always paired with text for critical actions; no emoji in product UI/exports; logo placeholder config-driven (doc 01 §8).
