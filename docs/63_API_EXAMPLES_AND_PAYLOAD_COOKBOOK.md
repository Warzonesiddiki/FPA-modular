# 63 — API EXAMPLES & PAYLOAD COOKBOOK (companion to doc 05)

> Conventions doc 05 §1 (money as decimal strings, cursor pagination, job pattern, error shape). Below: canonical examples implementers and UI agents copy — payloads here are normative for field names.

**Create project** `POST /api/v1/projects`
```json
{"name":"Meridian FY27","base_currency":"INR","fy_start_month":4,"calendar_type":"monthly"}
→ 201 {"project_id":"prj_9f2c41aa07e1","name":"Meridian FY27","base_currency":"INR","fy_start_month":4}
```
**Stage import** `POST /projects/{id}/imports` (multipart: file + fields) → `201 {"batch_id":"bat_41c2…","status":"staged","profile":{"columns":[{"source":"Amt","suggested":"amount","confidence":0.93}],"row_count_in":10422}}`
**Commit** `POST /imports/{batch}/commit` → `202 {"job_id":"job_…"}` → `GET /jobs/{id}` → `{"status":"done","result":{"committed":10410,"quarantined":12,"tb_status":"balanced"}}`. Control-total failure → job `failed` with `{"code":"FP&A-ERR-023","message":"…","hint":"…","retryable":false,"details":{"declared_debit":"…","actual_debit":"…"}}`.
**Statements** `GET /projects/{id}/statements?period_id=2026-P01&statement=pl` → `{"lines":[{"line_key":"rev","label":"Revenue","amount":"6350000.00","drill_key":"eyJ…"}, …],"checks":{"tb":"balanced"}}`
**BvA row** `{"grain":{"entity_id":"IN01","account_id":"6100"},"actual":"125000.50","budget":"100000.00","var_abs":"25000.50","var_pct":"25.0","favourable":false,"material":true,"drill_key":"…"}` (var_pct `null` + `"var_pct_reason":"zero_budget"` when budget 0).
**Finding transition** `POST /exceptions/{fid}/transition {"to_status":"waived","waive_reason":"Timing — reverses in May","waive_days":30}` → updated finding; missing reason → ERR-041 body per doc 22.
**Forecast run** `POST /projects/{id}/forecast/run {"base_period_id":"2026-P06"}` → job → run `{"run_id":"…","accuracy":{"revenue":{"method":"seasonal","mape":"3.1","bias":"-0.8"}}}`.
**Exports** `POST /projects/{id}/exports {"kind":"pptx","period_id":"2026-P01"}` → job failed ERR-060 with `details.checks[{name:"cf_tie",expected:"…",actual:"…"}]` when blocked.
**Pagination:** `GET …/drill?drill_key=…&limit=100&cursor=…` → `{"items":[…],"next_cursor":"…"}` (`null` = end).
Idempotency replay: same `Idempotency-Key` on commit/exports returns the original job/result, no duplicate artefacts.
