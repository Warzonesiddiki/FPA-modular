# TASKBOARD — live ledger of the sole agent (hand-maintained; regenerate WORK_PLAN, never this file)

Statuses: `queued` · `in_progress` · `done` (evidence pasted) · `blocked` (class-C only: evidence + next step) · `exists-unverified` (file predates this plan; re-verify before `done`).

## Owner attention (informational — the owner delegated decisions, DEC-010; list what was decided and where, never a queue)
- **DEC-010** (doc 17 §4) auto-decision mode recorded per owner instruction 2026-10-14 ("auto take best decision"). DEC-008 (bars) and DEC-009 (error catalogue) accepted; OQ-06/07/11/12/13/14 closed on their defaults. Nothing here waits for approval; reverse any DEC by editing doc 17 §4 and the owning doc.
- **DEC-011** (auto) entry-hygiene rules EXC-025…028 + rectification suggestion on every finding + ERP rectification journal file + verification loop → bars 36/36 · 0/13 · 19/19 (docs 07 §3/§7, 44, 42 §7–§8, 14 §3, 19 FR-EXC-012…015, 26 §7, 02 §7 deltas 10–12, 22 ERR-046, 62).
- **DEC-012** (auto) Dynamics 365 F&O / Business Central first-class import shapes, AP vendor enrichment, trial-balance tie-out, posting-layer scope, segmented-account transforms (docs 26 §2/§5, 06, 19 FR-IMP-016…019, 42 §4 erp_shapes, 14 §3 parity bar).
- **DEC-013** (auto) direct, read-only **Dynamics 365 connector in v1** (F&O OData v4 + Business Central API v2.0, Entra ID sign-in, connector-as-file-producer ADR-009, `msal`+`httpx` ADR-010, local mock + offline demo ledger) — docs 26 §8, 05, 12 §1(d)/§5/§8, 19 FR-CON-001…010, 22 ERR-110…118, 23 §11, 62 `connector.*`, 64, 14 §3 parity bar; OQ-15/16 closed. Owner-side residue (not a blocker): IT performs the 15-minute Entra app registration of doc 18 §8 before the pilot month; the sample project's demo ledger needs nothing.
- Prior audits (`audit/BRUTAL_AUDIT_2026-10-14.md`, `REMEDIATION`, `DOCS_AUDIT_PASS2`) are superseded by `audit/BRUTAL_AUDIT_PASS3_2026-10-14.md` (addendum 2026-10-14 b notes the DEC-011/012 bar changes); their "FIXED"/"no P0" verdicts are withdrawn.

- **DEC-014** (auto): M0 bootstrap checker is now WI-0008; full release checker retained in M6 as WI-0260. Doc 86 §1.1 defines both scopes; product code remains frozen. All later ids shifted by one; statuses preserved by path. Gate wording reconciled, no gate weakened or closed. Evidence: `evidence/session_start_2026-10-13.md`.

- **DEC-015** (auto): API error transport now covers all 73 codes; locked connector pull corrected to ERR-027/423 (docs 05 §1.1, 23 §11, 26 §8.4). WI-0001 remains in progress; remaining endpoint/job/auth/schema defects and reproducible partial checks: `evidence/WI-0001_api_contract_review.md`. No implementation or gate pass claimed.

- **Batch request (2026-10-14):** owner requested the next 30 items; track WI-0001…0030 in plan order. No gate bypass, no bulk done marking. Current item remains WI-0001.
- **DEC-016** (auto): shared API protocol and job-schema ownership fixed in docs before implementation; details doc 17 §4. No owner approval needed.
- **DEC-017** (auto): explicit FY creation, bounded Project metadata and paged Period reads; fixed currency registry and canonical names; durable app-scoped creation receipt. Doc 02 delta 14 records missing revision metadata for M1, not a product change now. Seven endpoints expanded, no WI/gate completed.

- **DEC-018** (auto): sample workspace is not pre-committed books; deletion is exact-confirmation + version + durable receipt with ≥30-day trash; start-close/unlock are deliberate versioned actions and preserve audit/old baseline. Four endpoint contracts, not runtime operations.
- **DEC-019** (auto): CLI launch descriptor is specified outside projects/install payload with owner-only ACLs, not inside a folder that backup copies. No live credential was found/handled and no runtime protection is claimed implemented.

## Current position
- Milestone: **M0** (gate open, 0/8 done) · In progress: **WI-0001** · Current checkpoint: 2026-10-14. Requested batch **WI-0001…0030: 0/30 complete**. Plan remains **267 WIs** — M0 8 · M1 53 · M2 75 · M3 44 · M4 51 · M5 26 · M6 10.
- DEC-016…019 checkpoints verified: **277 document tests + 9 unchanged product tests = 286 passing**; 230 definitions, 18 job kinds, 76 errors. Four lifecycle sections supplement seven health/project/period and three job-transport sections. Product code frozen; no runtime/gate claim.
- **Resume WI-0001**, not WI-0002: expand every remaining endpoint and request/response/error/example; finish doc 90 as index. Exact next work and limitations: `evidence/WI-0001_lifecycle_contract_2026-10-14.md` (Exact continuation).

## Items

| WI | Path | Milestone | Status | Evidence / note |
|---|---|---|---|---|
| WI-0001 | `docs/05_API_CONTRACT.md` | M0 | in_progress | DEC-018/019: four lifecycle contracts + private runtime-state correction; 286 tests pass. Full endpoint rewrite incomplete. Evidence: WI-0001_lifecycle_contract_2026-10-14.md; latest handover below. |
| WI-0002 | `docs/21_SCREEN_SPEC_DETAILED.md` | M0 | exists-unverified |  |
| WI-0003 | `docs/44_RULE_ALGORITHMS_DETAILED.md` | M0 | exists-unverified |  |
| WI-0004 | `docs/03_CALCULATION_SPEC.md` | M0 | exists-unverified |  |
| WI-0005 | `docs/55_COPY_AND_MICROCOPY_CATALOG.md` | M0 | exists-unverified |  |
| WI-0006 | `docs/31_GLOSSARY.md` | M0 | exists-unverified |  |
| WI-0007 | `docs/20_TRACEABILITY_MATRIX.md` | M0 | exists-unverified |  |
| WI-0008 | `scripts/docs_check.py` | M0 | queued | DEC-014: bootstrap only; build after WI-0007. |
| WI-0009 | `pyproject.toml` | M1 | exists-unverified |  |
| WI-0010 | `README.md` | M1 | exists-unverified |  |
| WI-0011 | `.gitignore` | M1 | exists-unverified |  |
| WI-0012 | `app/core/__init__.py` | M1 | exists-unverified |  |
| WI-0013 | `app/store/__init__.py` | M1 | exists-unverified |  |
| WI-0014 | `app/imports/__init__.py` | M1 | exists-unverified |  |
| WI-0015 | `app/connectors/__init__.py` | M1 | queued |  |
| WI-0016 | `app/calc/__init__.py` | M1 | exists-unverified |  |
| WI-0017 | `app/rules/__init__.py` | M1 | queued |  |
| WI-0018 | `app/forecast/__init__.py` | M1 | queued |  |
| WI-0019 | `app/planning/__init__.py` | M1 | queued |  |
| WI-0020 | `app/adjustments/__init__.py` | M1 | queued |  |
| WI-0021 | `app/exports/__init__.py` | M1 | queued |  |
| WI-0022 | `app/ai/__init__.py` | M1 | queued |  |
| WI-0023 | `app/api/__init__.py` | M1 | queued |  |
| WI-0024 | `app/services/__init__.py` | M1 | queued |  |
| WI-0025 | `app/jobs/__init__.py` | M1 | queued |  |
| WI-0026 | `app/desktop/__init__.py` | M1 | queued |  |
| WI-0027 | `app/cli/__init__.py` | M1 | queued |  |
| WI-0028 | `app/__init__.py` | M1 | exists-unverified |  |
| WI-0029 | `app/core/errors.py` | M1 | exists-unverified |  |
| WI-0030 | `app/core/money.py` | M1 | exists-unverified |  |
| WI-0031 | `app/core/calendar.py` | M1 | exists-unverified |  |
| WI-0032 | `app/core/ids.py` | M1 | exists-unverified |  |
| WI-0033 | `app/core/hashing.py` | M1 | exists-unverified |  |
| WI-0034 | `app/core/audit.py` | M1 | exists-unverified |  |
| WI-0035 | `app/core/config.py` | M1 | exists-unverified |  |
| WI-0036 | `app/core/logging.py` | M1 | queued |  |
| WI-0037 | `app/core/license.py` | M1 | queued |  |
| WI-0038 | `app/store/schema.sql` | M1 | exists-unverified |  |
| WI-0039 | `app/store/db.py` | M1 | exists-unverified |  |
| WI-0040 | `app/store/migrations/__init__.py` | M1 | queued |  |
| WI-0041 | `app/store/migrations/m0001_initial.py` | M1 | queued |  |
| WI-0042 | `app/store/import_repo.py` | M1 | queued |  |
| WI-0043 | `app/store/gl_repo.py` | M1 | queued |  |
| WI-0044 | `app/store/mapping_repo.py` | M1 | queued |  |
| WI-0045 | `app/store/master_repo.py` | M1 | queued |  |
| WI-0046 | `app/store/budget_repo.py` | M1 | queued |  |
| WI-0047 | `app/store/forecast_repo.py` | M1 | queued |  |
| WI-0048 | `app/store/exception_repo.py` | M1 | queued |  |
| WI-0049 | `app/store/report_repo.py` | M1 | queued |  |
| WI-0050 | `app/store/period_repo.py` | M1 | queued |  |
| WI-0051 | `app/store/connector_repo.py` | M1 | queued |  |
| WI-0052 | `sample-data/generate_sample_data.py` | M1 | queued |  |
| WI-0053 | `sample-data/answer_key.json` | M1 | queued |  |
| WI-0054 | `sample-data/malformed/` | M1 | queued |  |
| WI-0055 | `packs/general.json` | M1 | queued |  |
| WI-0056 | `packs/manufacturing.json` | M1 | queued |  |
| WI-0057 | `packs/saas.json` | M1 | queued |  |
| WI-0058 | `packs/retail.json` | M1 | queued |  |
| WI-0059 | `packs/pack.schema.json` | M1 | queued |  |
| WI-0060 | `tests/fixtures/README.md` | M1 | queued |  |
| WI-0061 | `tests/acceptance/test_acceptance.py` | M1 | queued |  |
| WI-0062 | `app/imports/models.py` | M2 | exists-unverified |  |
| WI-0063 | `app/imports/parser_csv.py` | M2 | exists-unverified |  |
| WI-0064 | `app/imports/parser_xlsx.py` | M2 | queued |  |
| WI-0065 | `app/imports/profiler.py` | M2 | queued |  |
| WI-0066 | `app/imports/mapping.py` | M2 | queued |  |
| WI-0067 | `app/imports/mapping_suggest.py` | M2 | queued |  |
| WI-0068 | `app/imports/validation.py` | M2 | exists-unverified |  |
| WI-0069 | `app/imports/control_totals.py` | M2 | queued |  |
| WI-0070 | `app/imports/enrichment.py` | M2 | queued |  |
| WI-0071 | `app/imports/tb_check.py` | M2 | queued |  |
| WI-0072 | `app/imports/commit.py` | M2 | exists-unverified |  |
| WI-0073 | `app/imports/trial_balance.py` | M2 | exists-unverified |  |
| WI-0074 | `app/imports/reconcile.py` | M2 | queued |  |
| WI-0075 | `app/calc/statements.py` | M2 | exists-unverified |  |
| WI-0076 | `app/calc/kpis.py` | M2 | queued |  |
| WI-0077 | `app/calc/bva.py` | M2 | exists-unverified |  |
| WI-0078 | `app/calc/attribution.py` | M2 | queued |  |
| WI-0079 | `app/calc/drilldown.py` | M2 | queued |  |
| WI-0080 | `app/calc/quality_score.py` | M2 | queued |  |
| WI-0081 | `app/rules/exc_001.py` | M2 | queued |  |
| WI-0082 | `app/rules/exc_002.py` | M2 | queued |  |
| WI-0083 | `app/rules/exc_003.py` | M2 | queued |  |
| WI-0084 | `app/rules/exc_004.py` | M2 | queued |  |
| WI-0085 | `app/rules/exc_005.py` | M2 | queued |  |
| WI-0086 | `app/rules/exc_006.py` | M2 | queued |  |
| WI-0087 | `app/rules/exc_007.py` | M2 | queued |  |
| WI-0088 | `app/rules/exc_008.py` | M2 | queued |  |
| WI-0089 | `app/rules/exc_009.py` | M2 | queued |  |
| WI-0090 | `app/rules/exc_010.py` | M2 | queued |  |
| WI-0091 | `app/rules/exc_011.py` | M2 | queued |  |
| WI-0092 | `app/rules/exc_012.py` | M2 | queued |  |
| WI-0093 | `app/rules/exc_013.py` | M2 | queued |  |
| WI-0094 | `app/rules/exc_014.py` | M2 | queued |  |
| WI-0095 | `app/rules/exc_015.py` | M2 | queued |  |
| WI-0096 | `app/rules/exc_016.py` | M2 | queued |  |
| WI-0097 | `app/rules/exc_017.py` | M2 | queued |  |
| WI-0098 | `app/rules/exc_018.py` | M2 | queued |  |
| WI-0099 | `app/rules/exc_019.py` | M2 | queued |  |
| WI-0100 | `app/rules/exc_020.py` | M2 | queued |  |
| WI-0101 | `app/rules/exc_021.py` | M2 | queued |  |
| WI-0102 | `app/rules/exc_022.py` | M2 | queued |  |
| WI-0103 | `app/rules/exc_023.py` | M2 | queued |  |
| WI-0104 | `app/rules/exc_024.py` | M2 | queued |  |
| WI-0105 | `app/rules/exc_025.py` | M2 | queued |  |
| WI-0106 | `app/rules/exc_026.py` | M2 | queued |  |
| WI-0107 | `app/rules/exc_027.py` | M2 | queued |  |
| WI-0108 | `app/rules/exc_028.py` | M2 | queued |  |
| WI-0109 | `app/rules/suggestions.py` | M2 | queued |  |
| WI-0110 | `app/rules/engine.py` | M2 | queued |  |
| WI-0111 | `app/rules/owner_resolver.py` | M2 | queued |  |
| WI-0112 | `app/forecast/naive.py` | M2 | queued |  |
| WI-0113 | `app/forecast/moving_average.py` | M2 | queued |  |
| WI-0114 | `app/forecast/exponential_smoothing.py` | M2 | queued |  |
| WI-0115 | `app/forecast/linear_trend.py` | M2 | queued |  |
| WI-0116 | `app/forecast/driver_based.py` | M2 | queued |  |
| WI-0117 | `app/forecast/seasonal.py` | M2 | queued |  |
| WI-0118 | `app/forecast/budget_phasing.py` | M2 | queued |  |
| WI-0119 | `app/forecast/manual.py` | M2 | queued |  |
| WI-0120 | `app/forecast/engine.py` | M2 | queued |  |
| WI-0121 | `app/forecast/scenarios.py` | M2 | queued |  |
| WI-0122 | `app/forecast/rolling.py` | M2 | queued |  |
| WI-0123 | `tests/integration/test_erp_shape_parity.py` | M2 | queued |  |
| WI-0124 | `app/planning/drivers.py` | M2 | queued |  |
| WI-0125 | `app/planning/headcount.py` | M2 | queued |  |
| WI-0126 | `app/planning/capex.py` | M2 | queued |  |
| WI-0127 | `app/planning/debt.py` | M2 | queued |  |
| WI-0128 | `app/planning/working_capital.py` | M2 | queued |  |
| WI-0129 | `app/planning/cash13.py` | M2 | queued |  |
| WI-0130 | `app/planning/sensitivity.py` | M2 | queued |  |
| WI-0131 | `app/planning/goal_seek.py` | M2 | queued |  |
| WI-0132 | `app/planning/integrate.py` | M2 | queued |  |
| WI-0133 | `app/planning/assumptions.py` | M2 | queued |  |
| WI-0134 | `app/adjustments/engine.py` | M2 | queued |  |
| WI-0135 | `app/rules/workflow.py` | M2 | queued |  |
| WI-0136 | `app/planning/allocations.py` | M2 | queued |  |
| WI-0137 | `app/connectors/models.py` | M3 | queued |  |
| WI-0138 | `app/connectors/profiles/d365fo.json` | M3 | queued |  |
| WI-0139 | `app/connectors/profiles/d365bc.json` | M3 | queued |  |
| WI-0140 | `app/connectors/transport.py` | M3 | queued |  |
| WI-0141 | `app/connectors/auth.py` | M3 | queued |  |
| WI-0142 | `app/connectors/odata.py` | M3 | queued |  |
| WI-0143 | `app/connectors/snapshot.py` | M3 | queued |  |
| WI-0144 | `app/connectors/d365fo.py` | M3 | queued |  |
| WI-0145 | `app/connectors/d365bc.py` | M3 | queued |  |
| WI-0146 | `tools/mock_d365.py` | M3 | queued |  |
| WI-0147 | `tests/fixtures/connectors/README.md` | M3 | queued |  |
| WI-0148 | `app/jobs/registry.py` | M3 | queued |  |
| WI-0149 | `app/services/connector_service.py` | M3 | queued |  |
| WI-0150 | `app/services/month_end.py` | M3 | queued |  |
| WI-0151 | `app/services/dashboard.py` | M3 | queued |  |
| WI-0152 | `app/services/close_service.py` | M3 | queued |  |
| WI-0153 | `app/services/alerts.py` | M3 | queued |  |
| WI-0154 | `app/services/year_end.py` | M3 | queued |  |
| WI-0155 | `app/api/main.py` | M3 | queued |  |
| WI-0156 | `app/api/routes_health.py` | M3 | queued |  |
| WI-0157 | `app/api/routes_projects.py` | M3 | queued |  |
| WI-0158 | `app/api/routes_imports.py` | M3 | queued |  |
| WI-0159 | `app/api/routes_statements.py` | M3 | queued |  |
| WI-0160 | `app/api/routes_bva.py` | M3 | queued |  |
| WI-0161 | `app/api/routes_exceptions.py` | M3 | queued |  |
| WI-0162 | `app/api/routes_forecast.py` | M3 | queued |  |
| WI-0163 | `app/api/routes_exports.py` | M3 | queued |  |
| WI-0164 | `app/api/routes_settings.py` | M3 | queued |  |
| WI-0165 | `app/api/routes_adjustments.py` | M3 | queued |  |
| WI-0166 | `app/api/routes_allocations.py` | M3 | queued |  |
| WI-0167 | `app/api/routes_assumptions.py` | M3 | queued |  |
| WI-0168 | `app/api/routes_year_end.py` | M3 | queued |  |
| WI-0169 | `app/api/routes_close.py` | M3 | queued |  |
| WI-0170 | `app/api/routes_reconcile.py` | M3 | queued |  |
| WI-0171 | `app/api/routes_alerts.py` | M3 | queued |  |
| WI-0172 | `app/api/routes_planning.py` | M3 | queued |  |
| WI-0173 | `app/api/routes_reports_builder.py` | M3 | queued |  |
| WI-0174 | `app/api/routes_connector.py` | M3 | queued |  |
| WI-0175 | `app/cli/main.py` | M3 | queued |  |
| WI-0176 | `app/desktop/shell.py` | M3 | queued |  |
| WI-0177 | `app/ai/client.py` | M3 | queued |  |
| WI-0178 | `app/ai/guardrails.py` | M3 | queued |  |
| WI-0179 | `app/ai/commentary.py` | M3 | queued |  |
| WI-0180 | `app/ai/prompts.py` | M3 | queued |  |
| WI-0181 | `ui/package.json` | M4 | queued |  |
| WI-0182 | `ui/vite.config.ts` | M4 | queued |  |
| WI-0183 | `ui/tsconfig.json` | M4 | queued |  |
| WI-0184 | `ui/tsconfig.node.json` | M4 | queued |  |
| WI-0185 | `ui/index.html` | M4 | queued |  |
| WI-0186 | `ui/eslint.config.js` | M4 | queued |  |
| WI-0187 | `ui/src/main.tsx` | M4 | queued |  |
| WI-0188 | `ui/src/App.tsx` | M4 | queued |  |
| WI-0189 | `ui/src/lib/format.ts` | M4 | queued |  |
| WI-0190 | `ui/src/api/client.ts` | M4 | queued |  |
| WI-0191 | `ui/src/theme/tokens.ts` | M4 | queued |  |
| WI-0192 | `ui/src/components/DataTable.tsx` | M4 | queued |  |
| WI-0193 | `ui/src/components/VarianceBadge.tsx` | M4 | queued |  |
| WI-0194 | `ui/src/components/DrillDrawer.tsx` | M4 | queued |  |
| WI-0195 | `ui/src/components/FileDrop.tsx` | M4 | queued |  |
| WI-0196 | `ui/src/components/WizardSteps.tsx` | M4 | queued |  |
| WI-0197 | `ui/src/components/FindingCard.tsx` | M4 | queued |  |
| WI-0198 | `ui/src/components/PeriodPicker.tsx` | M4 | queued |  |
| WI-0199 | `ui/src/components/ExportButton.tsx` | M4 | queued |  |
| WI-0200 | `ui/src/components/EmptyState.tsx` | M4 | queued |  |
| WI-0201 | `ui/src/components/ErrorBanner.tsx` | M4 | queued |  |
| WI-0202 | `ui/src/components/ConfirmDialog.tsx` | M4 | queued |  |
| WI-0203 | `ui/src/components/KpiCard.tsx` | M4 | queued |  |
| WI-0204 | `ui/src/components/LayerSelector.tsx` | M4 | queued |  |
| WI-0205 | `ui/src/components/JobToast.tsx` | M4 | queued |  |
| WI-0206 | `ui/src/components/ConnectionCard.tsx` | M4 | queued |  |
| WI-0207 | `ui/src/stores/projectStore.ts` | M4 | queued |  |
| WI-0208 | `ui/src/stores/periodStore.ts` | M4 | queued |  |
| WI-0209 | `ui/src/stores/importStore.ts` | M4 | queued |  |
| WI-0210 | `ui/src/stores/findingStore.ts` | M4 | queued |  |
| WI-0211 | `ui/src/stores/forecastStore.ts` | M4 | queued |  |
| WI-0212 | `ui/src/stores/uiStore.ts` | M4 | queued |  |
| WI-0213 | `ui/src/pages/S01-dashboard/index.tsx` | M4 | queued |  |
| WI-0214 | `ui/src/pages/S02-projects/index.tsx` | M4 | queued |  |
| WI-0215 | `ui/src/pages/S03-import/index.tsx` | M4 | queued |  |
| WI-0216 | `ui/src/pages/S04-mapping/index.tsx` | M4 | queued |  |
| WI-0217 | `ui/src/pages/S05-trial-balance/index.tsx` | M4 | queued |  |
| WI-0218 | `ui/src/pages/S06-statements/index.tsx` | M4 | queued |  |
| WI-0219 | `ui/src/pages/S07-bva/index.tsx` | M4 | queued |  |
| WI-0220 | `ui/src/pages/S08-exceptions/index.tsx` | M4 | queued |  |
| WI-0221 | `ui/src/pages/S09-forecast/index.tsx` | M4 | queued |  |
| WI-0222 | `ui/src/pages/S10-scenarios/index.tsx` | M4 | queued |  |
| WI-0223 | `ui/src/pages/S11-exports/index.tsx` | M4 | queued |  |
| WI-0224 | `ui/src/pages/S12-owners/index.tsx` | M4 | queued |  |
| WI-0225 | `ui/src/pages/S13-settings/index.tsx` | M4 | queued |  |
| WI-0226 | `ui/src/pages/S14-audit/index.tsx` | M4 | queued |  |
| WI-0227 | `ui/src/pages/S15-help/index.tsx` | M4 | queued |  |
| WI-0228 | `ui/src/pages/S16-close/index.tsx` | M4 | queued |  |
| WI-0229 | `ui/src/pages/S17-planning/index.tsx` | M4 | queued |  |
| WI-0230 | `ui/src/pages/S18-reconcile/index.tsx` | M4 | queued |  |
| WI-0231 | `ui/src/pages/S19-alerts/index.tsx` | M4 | queued |  |
| WI-0232 | `app/exports/sheet_cover.py` | M5 | queued |  |
| WI-0233 | `app/exports/sheet_contents.py` | M5 | queued |  |
| WI-0234 | `app/exports/sheet_pl.py` | M5 | queued |  |
| WI-0235 | `app/exports/sheet_bs.py` | M5 | queued |  |
| WI-0236 | `app/exports/sheet_cf.py` | M5 | queued |  |
| WI-0237 | `app/exports/sheet_bva.py` | M5 | queued |  |
| WI-0238 | `app/exports/sheet_exceptions.py` | M5 | queued |  |
| WI-0239 | `app/exports/sheet_forecast.py` | M5 | queued |  |
| WI-0240 | `app/exports/sheet_kpis.py` | M5 | queued |  |
| WI-0241 | `app/exports/sheet_drilldata.py` | M5 | queued |  |
| WI-0242 | `app/exports/sheet_checks.py` | M5 | queued |  |
| WI-0243 | `app/exports/sheet_sources.py` | M5 | queued |  |
| WI-0244 | `app/exports/excel_pack.py` | M5 | queued |  |
| WI-0245 | `app/exports/slide_title.py` | M5 | queued |  |
| WI-0246 | `app/exports/slide_summary.py` | M5 | queued |  |
| WI-0247 | `app/exports/slide_pl.py` | M5 | queued |  |
| WI-0248 | `app/exports/slide_bridge.py` | M5 | queued |  |
| WI-0249 | `app/exports/slide_exceptions.py` | M5 | queued |  |
| WI-0250 | `app/exports/slide_forecast.py` | M5 | queued |  |
| WI-0251 | `app/exports/slide_risks.py` | M5 | queued |  |
| WI-0252 | `app/exports/slide_appendix.py` | M5 | queued |  |
| WI-0253 | `app/exports/ppt_pack.py` | M5 | queued |  |
| WI-0254 | `app/exports/journal_export.py` | M5 | queued |  |
| WI-0255 | `app/exports/pdf_report.py` | M5 | queued |  |
| WI-0256 | `app/exports/report_builder.py` | M5 | queued |  |
| WI-0257 | `tests/integration/test_cross_artifact.py` | M5 | queued |  |
| WI-0258 | `scripts/check.py` | M6 | queued |  |
| WI-0259 | `scripts/acceptance.py` | M6 | queued |  |
| WI-0260 | `scripts/docs_check_release.py` | M6 | queued |  |
| WI-0261 | `packaging/fpa.spec` | M6 | queued |  |
| WI-0262 | `packaging/installer.iss` | M6 | queued |  |
| WI-0263 | `scripts/build.py` | M6 | queued |  |
| WI-0264 | `.github/workflows/ci.yml` | M6 | queued |  |
| WI-0265 | `docs/18_USER_GUIDE.md` | M6 | exists-unverified |  |
| WI-0266 | `docs/00_INDEX.md` | M6 | exists-unverified |  |
| WI-0267 | `tests/perf/test_perf.py` | M6 | queued |  |

## Session evidence — housekeeping, 2026-10-13 UTC
- Baseline: `git fetch origin && git log --oneline -3` → `6cc5776`; pytest initially absent, installed in sandbox; `python -m pytest -q` → **9 passed in 0.40s**. Frozen code untouched.
- Three housekeeping changes completed; DEC-014 scope and alternatives in doc 17 §4, checker contracts in doc 86 §1.1. Neither checker implemented yet.
- `python tools/generate_work_plan.py` → **267 items; M0=8 M1=53 M2=75 M3=44 M4=51 M5=26 M6=10**. Inline assertions → **267/267 ledger identities, 266/266 inherited statuses preserved, 7/7 gate strings identical, 2/2 regenerated files byte-identical**; CSV LF-only after correcting the generator's CRLF default.
- Dependency mutation probes: unresolved path → `resolve_deps` failure; cycle → `check_graph` failure; M0→M6 dependency → `check_graph` failure. All three caught, isolated fixtures only.
- Final `python -m pytest -q` → **9 passed in 0.10s**; `git diff --check` → exit 0. Details/limits: `evidence/session_start_2026-10-13.md`. No milestone gate claimed clean.

## WI-0001 handover — partial, 2026-10-13 UTC

WI-0001  `docs/05_API_CONTRACT.md`
STATUS: in_progress
CONTRACT:
- Expand every method/path with auth, request/response field constraints, statuses/error details, pagination, idempotency and complete examples (WORK_PLAN WI-0001; docs 05/90/63).
- Money at the public boundary is major-unit decimal strings; storage remains integer minor units (docs 05 introduction, 02 §1, 90). No product arithmetic in this WI.
- Exhaustive doc-22 error transport; project ownership before state disclosure; connector stage/commit uses the file pipeline's lock guard (docs 05 §1.1, 23 §11, 26 §8.4, DEC-015).
- Every async operation needs a typed terminal result, incl. connector-pull/check-changes (docs 05/64/90). Full catalogue still unfinished.
TESTS RUN:
- Partial doc assertions: `python -c 'from pathlib import Path; exec(Path("evidence/WI-0001_api_contract_review.md").read_text().split("```python\n", 1)[1].split("\n```", 1)[0])'` → **73/73 codes exactly once, 45/45 old statuses retained; lock guard agrees across 05/23/26; JSON example parses; 3/3 mutation probes caught**. Executed twice, identical output. This is not an API runtime test or full docs-gate pass.
- `python -m pytest -q` → **9 passed in 0.12s**; `git diff --check` → exit 0. `scripts/check.py` and docs checker do not exist; not run. Paired test is “none” in the WI; reproducible doc assertions are in the evidence instead.
MUTATIONS: remove ERR-118 → code-set mismatch; duplicate ERR-030 → duplicate mapping; revert doc-23 locked connector guard to ERR-030 → lock-code drift. Isolated text copies, no un-restored repository mutation.
EDGES: locked period PASS (doc conformance only); duplicate/missing error definitions PASS (mutation checks); deterministic repeat PASS. Monetary zero/negative/denominator/exponent cases, empty/single/250k financial rows, missing optional data, locked versions, superseded batches, expired waivers, hostile financial text, ambiguous dates/amounts, month-2 reuse: N/A to error-transport-only sub-scope, **still to be covered by full WI contract/examples**; no runtime coverage claimed.
SPEC CHECKS: doc 22 §2 code-set equality 73/73; docs 22 ERR-027/030 and 26 §8.4 lock preflight agree; doc 05 §1.1 preserves all 45 prior statuses and distinguishes job polling from business success. The public-money rule is stated, but remaining legacy payload violations are enumerated in evidence §4, not claimed fixed.
FILES TOUCHED: docs/05, docs/17, docs/23, docs/26, docs/90, docs/CHANGELOG, TASKBOARD, evidence/WI-0001_api_contract_review.md.
DEVIATIONS: DEC-015 resolves missing mappings and wrong connector-lock error in owning docs before implementation. No product code or new error code. Completion requires the remaining work below, so no WI done commit yet (this sub-scope is a docs-fix commit).
DECISIONS TAKEN: DEC-015 (auto) · OWNER-ONLY ITEMS: no new items; existing Entra app registration (doc 18 §8) needed only before a real tenant pull, not this WI.
NEXT: continue WI-0001 using evidence §4: expand method/path inventory; resolve callback auth/base path/project scope; reconcile all job kinds/results with doc 64; converge doc 90 fields and complete doc 63 examples; cover per-endpoint errors/pagination/idempotency and money strings. **Do not start WI-0002 or WI-0008 yet.** M0 gate open (0/8 done, 1 in progress).

## WI-0001 continuation — 2026-10-14
STATUS: in_progress
CONTRACT: docs 05 §1.2–1.4 / 12 §1.1: explicit local token + project context, root callback only with state/PKCE; doc 22: 76 known errors; doc 64: every job has a closed, typed result; money is a decimal string. Schema attachment + paired doc tests permitted by DEC-016; no product imports.
BASELINE: `python -m pytest -q` → 9 passed in 0.12s. Thirty-item request is not a waiver of M0 or its cold audit.

TESTS RUN: `python -m pytest tests/docs/test_api_job_contract.py -q --tb=short` → **120 passed**; `python -m pytest -q --tb=short` → **129 passed** (9 frozen nucleus + 120 docs). `git diff --check` clean. Plan generator repeat byte-identical, 267 WIs. Fresh isolated install of tests/docs/requirements.txt also passes all 120 docs tests (Linux/Python 3.11, not Windows certification). Evidence includes actual failing-before-fix runs and limitations.
MUTATIONS: numeric Money → oracle fails; percent maximum 101 → boundary rejection fails; remove kind/result discriminator → wrong-kind rejection fails. Isolated schema copies; three caught by the same oracle. Additional negative controls for conservation, rule partition, board pack, timestamp ordering.
EDGES: document-only zero/negative money, exponents 0/2/3, null-denominator reasons, empty/single/250k counts (not perf), missing/skipped data, all kind/state combinations, hostile text/unsafe paths, invalid dates/periods and duplicate partition: PASS. Runtime locking/idempotency/waiver/locale/month-2/security/escaping: pending later implementation; no runtime claim. Full per-line checklist in evidence §3.
SPEC CHECKS: docs 22/05 exactly 76 codes + retry flags; doc 64 all 18 typed results/stages and cancel guards; docs 12/26 no secret-field shapes or resolver network and honest no_change/count semantics. HTTP auth/ownership, clock injection, persistence and redaction still require runtime tests.
FILES TOUCHED: docs 05/07/12/17/19/22/23/26/60/63/64/81/90/CHANGELOG, schema attachment, tests/docs test + pinned requirements, generator/WORK_PLAN, TASKBOARD and two evidence files (cumulative DEC-016 scope). No app or original tests modified.
DEVIATIONS: DEC-016 authorises the document schema and paired tests within WI-0001, with docs-first commit 674dfb8. Follow-up contradictions corrected in owning docs; no product feature, formula, bar or gate changed. This is a partial docs checkpoint, not a WI completion commit.
DECISIONS TAKEN: DEC-016 (auto) · OWNER-ONLY ITEMS: none for this work; existing Entra registration only before a real tenant pilot.
NEXT: evidence/WI-0001_job_contract_2026-10-14.md §4. Still **WI-0001 in_progress; 0/30 complete**, M0 open. Historical DEC-015/73-code evidence above is not the current verifier.

## WI-0001 continuation — project/period contracts, 2026-10-14
STATUS: in_progress (0/30 batch items done).
BASELINE: stale local Git metadata recovered with mixed reset to pushed fc736ff; working files unchanged. System pytest absent; system pip protected (PEP 668). Created ignored .venv and installed tests/docs/requirements.txt; `.venv/bin/python -m pytest -q` → 129 passed in 8.83s.
CONTRACT: doc 05 §6 / DEC-017: seven explicit health/project/period endpoints; closed metadata DTOs, fixed currency exponents (27), initial FY and repeat-safe atomic 12-period creation (02), no reads creating data, scoped durable receipt, no server-controlled create fields. Doc 02 revision metadata delta 14 is M1 work; frozen app code untouched.
TESTS RUN: `.venv/bin/python -m pytest tests/docs/test_api_project_contract.py -q --tb=short` → **77 passed in 1.31s**; `.venv/bin/python -m pytest tests/docs -q --tb=short` → **197 passed in 9.46s**; `.venv/bin/python -m pytest -q --tb=short` → **206 passed in 9.78s**. `git diff --check` clean. Evidence records test-first failures, parser correction, creation-response restriction and missing HTTP-header regression.
MUTATIONS: allow server-controlled request fields; drop currency/exponent constraint; FY upper-bound off-by-one → all caught by the same independent oracle. Existing three job-schema probes still pass; isolated copies only.
EDGES: schema/oracle PASS for currency 0/2/3, empty/single/capped pages, unknown/missing fields, partial/duplicate FY, lock-state shape, Unicode/control/oversized names, leap/year/date boundaries and relational negative controls. N/A to financial arithmetic/denominators/credit accounts/superseded batches/waivers here. Actual HTTP parsing/ownership, persistence, locks, deletion/restore and escaping remain M1/M3 work; no runtime/perf claim.
SPEC CHECKS: docs 05 §6/27 §1 server-controlled fields + exact exponent registry; docs 02/05 §6 twelve-period dates/identity/ownership and readable locked shapes; docs 05/22 method/path/scope/response/error transport parity. Six schema mutation probes across the two modules; 267 WI identities unchanged, seven gate strings equal, plan regeneration byte-identical.
FILES TOUCHED: docs 02/05/17/18/19/27/63/86/90/CHANGELOG, shared schema attachment, new tests/docs/test_api_project_contract.py, generator/WORK_PLAN.md/.csv, TASKBOARD, evidence/WI-0001_project_contract_2026-10-14.md. App/original tests unchanged against fc736ff.
DEVIATIONS: DEC-017, spec commits 221fc3d and e6ae4bf precede schema additions. Project/period revision fields explicitly recorded as M1 delta 14 and M1 gate wording aligned; no gate/bar weakened. This remains a partial documentation checkpoint, not a WI completion.
DECISIONS TAKEN: DEC-017 (auto) · OWNER-ONLY ITEMS: none for this work; existing Entra setup only before real tenant pilot.
NEXT: finish project sample/delete/backup/restore and period start/lock/unlock, including doc-41 impact review; then remaining route families/field tables/examples. Reconcile the missing project_repo plan ownership before WI-0001 sign-off; frozen calendar low-year padding needs M1 verification. Details and limits: evidence/WI-0001_project_contract_2026-10-14.md. **Still WI-0001 in_progress; 0/30 done, M0 open.**

## WI-0001 continuation — lifecycle commands, 2026-10-14
STATUS: in_progress; M0 open, 0/30 completed.
BASELINE: fetch/log/status clean at 8b00506; `.venv/bin/python -m pytest -q` → 206 passed in 10.44s.
CONTRACT: doc 05 §7 / DEC-018: four explicit metadata commands, source-controlled sample defaults, exact-name/version delete + durable replay/30-day trash (12 §2.1), open→closing and locked→closing with atomic pre-change baseline (23/41). DTO verification is not runtime filesystem/transaction proof.
TESTS RUN: `.venv/bin/python -m pytest tests/docs/test_api_lifecycle_contract.py -q --tb=short` → **80 passed**; `.venv/bin/python -m pytest tests/docs -q --tb=short` → **277 passed**; `.venv/bin/python -m pytest -q --tb=short` → **286 passed**, repeat same count. `git diff --check` clean. Evidence records the actual pre-schema 67 assertion failures and the two caught safety-spec omissions; an earlier pytest-reserved parameter collection error was fixed and not counted as contract red.
MUTATIONS: sample result flag true→false; drop ClosingPeriod status leg; note max 500→501 — same independent oracle catches all three on isolated copies. Six prior schema probes still pass.
EDGES: metadata/oracle PASS for missing/unknown fields, exact confirmation, source states, versions, note types/bounds/hostile literals, month/leap/UTC retention ±1-second controls, minimal deletion response and sample defaults. N/A to money arithmetic/denominators/credit accounts; no 250k-row throughput claim. Actual leases, ACLs, filesystem/keyring/crash recovery, raw parsing and sample imports remain runtime work.
SPEC CHECKS: 05 §7/42 sample uses the ordinary pipeline; 05 §7.2/12 §2.1 honest trash/retention/replay and no credential-bearing response; 05 §7.3–7.4/23/41/12 period transitions retain baseline and audit-broken guard. Private runtime descriptor contradiction corrected in 04/12/70 (DEC-019).
FILES TOUCHED: docs 02/04/05/12/17/18/19/23/30/41/42/63/70/90/CHANGELOG, shared schema, new tests/docs/test_api_lifecycle_contract.py, generator/WORK_PLAN.md/.csv, TASKBOARD, evidence/WI-0001_lifecycle_contract_2026-10-14.md. Product/original tests unchanged against 8b00506.
DEVIATIONS: DEC-018/019, docs-first commits e5bb560/438e13d before schema changes. No new error/job kind/WI, no bar or gate change; 267 identities stable, all seven gates equal, regenerated files repeat-identical. Scope is still only WI-0001.
DECISIONS TAKEN: DEC-018, DEC-019 (auto) · OWNER-ONLY ITEMS: none for this work; existing Entra setup only before real tenant pilot.
NEXT: backup/restore archive/transport/rollback/receipt safety; lock/re-lock/sign-off/impact guards without circular dependencies; remaining endpoint families/index/examples; resolve project persistence ownership in plan. Exact gaps in evidence. **WI-0001 in_progress; 0/30 done; M0 open.**

## WI-0001 continuation — close readiness, 2026-10-14
STATUS: in_progress, M0 open, 0/30 complete.
BASELINE: fetch/status clean at 7b9a34f; `.venv/bin/python -m pytest -q` → 286 passed in 10.66s.
CONTRACT: DEC-020, docs 05 §8/30 §6–§7: read-only bounded readiness, immutable explicit sign-off, separate versioned lock; no T-09/T-10 cycle or blanket hard-guard override. Doc 41 requires current impact approval, not arbitrary lock-note text. Product frozen.
NEXT: independent DTO/token/guard tests before schema extension; evidence and full checks, then continue unresolved WI-0001 contracts.
