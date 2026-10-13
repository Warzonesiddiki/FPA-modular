# 68 — COMPATIBILITY MATRIX (tested combinations; anything unlisted = untested, stated in Help)

| Dimension | Supported (tested in Wave 6 / CI where automatable) |
|---|---|
| OS | Windows 11 23H2+ (x64); Windows 10 22H2 best-effort (labelled) |
| Excel (open generated .xlsx) | Microsoft 365 Excel, Excel 2019/2021, LibreOffice 7.6+ (formulas re-perform, AUD-I) |
| PowerPoint | Microsoft 365, PowerPoint 2019/2021, LibreOffice Impress (layout check) |
| Import files | CSV (UTF-8/BOM, UTF-16, Latin-1; , ; tab |), XLSX (Excel 2007+, LibreOffice, Google Sheets export), per doc 06 caps |
| ERP presets | Doc 26 preset versions pinned; preset change = data PR + changelog |
| Display | ≥1280×720; scaling 100–200% (57) |
| Python/Node (dev only) | 3.12.x / 22 LTS (60) |
Unsupported explicitly: XLS (legacy binary) — error message tells the user to Save-As xlsx/csv; macros-enabled files opened data-only; ARM Windows (Phase 3 note). Matrix reviewed per release; fidelity failures are S2 defects (72).
