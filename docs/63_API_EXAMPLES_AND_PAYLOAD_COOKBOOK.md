# 63 — API EXAMPLES & PAYLOAD COOKBOOK (companion to doc 05)

> Conventions doc 05 §1 (money as decimal strings, cursor pagination, job pattern, error shape). Below: canonical examples the route and UI work items copy — payloads here are normative for field names.

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

**Dynamics 365 connector — configure, sign in, test, pull** (doc 05 connector routes, doc 26 §8)
```json
PUT /projects/{id}/connector
{"kind":"d365fo","base_url":"https://meridian-prod.operations.dynamics.com","tenant_id":"3f1a…","client_id":"9b7e…","auth_mode":"delegated","company":"IN01"}
→ 200 {"enabled":true,"kind":"d365fo","base_url":"https://meridian-prod.operations.dynamics.com","tenant_id":"3f1a…","client_id":"9b7e…","auth_mode":"delegated","company":"IN01","state":"configured","profile":{"version":1}}
POST /projects/{id}/connector/sign-in → 200 {"authorize_url":"https://login.microsoftonline.com/3f1a…/oauth2/v2.0/authorize?…","port":51873}
   (system browser opens; Microsoft redirects to http://localhost:51873/connector/callback?code=…&state=… ; the API exchanges the code, stores the MSAL cache in the keyring and renders con.callback.page)
POST /projects/{id}/connector/test → 200 {"companies":[{"id":"IN01","name":"Meridian Trading Mumbai"},{"id":"IN02","name":"Meridian Trading Bengaluru"}],"entity_check":{"ok":false,"checked_at":"2026-10-14T09:12:04+05:30","missing":[{"source":"ap","entity":"VendorTransactions","candidates":["VendorTransactionsV2","VendTransBiEntities"]}]}}
PUT /projects/{id}/connector/profile {"version":2,"kind":"d365fo","sources":{"ap":{"entity":"VendorTransactionsV2","filter":"TransactionDate ge {start} and TransactionDate le {end}","sort_key":"RecId","fields":{"VendorAccount":"Vendor account","Voucher":"Voucher","TransactionDate":"Date","Invoice":"Invoice","AccountingCurrencyAmount":"Amount","CurrencyCode":"Currency","Txt":"Description"}}, "…":"unchanged sources omitted"}} → 200 {"version":2,"entity_check":{"ok":true,"missing":[]}}
POST /projects/{id}/connector/pull {"period_id":"2025-P07","sources":["gl","ap","tb"]} → 202 {"job_id":"job_…"}
GET /jobs/{id} → {"status":"running","stage":"con.pull.progress","progress":{"source":"gl","page":3,"pages":5,"rows":30000,"count":48213}}
GET /jobs/{id} → {"status":"done","result":{"pull_id":"pul_7c0d12e4aa91","status":"staged","snapshot_sha256":"5e1c…","batches":[{"batch_id":"bat_a91f…","source_kind":"gl","rows_in":48213,"quarantined":3},{"batch_id":"bat_b02e…","source_kind":"subledger","rows_in":1120,"quarantined":0}],"row_counts":{"gl":{"expected":48213,"received":48213,"pages":5,"retries":1},"ap":{"expected":1120,"received":1120,"pages":1,"retries":0},"tb":{"expected":0,"received":0,"pages":0,"retries":0,"note":"no standard F&O trial-balance entity — use the file export"}}}}
   (the 3 quarantined rows are the Tax-layer rows: OUT_OF_SCOPE_LAYER; commit is the normal POST /imports/{batch_id}/commit)
POST /projects/{id}/connector/pull {"period_id":"2025-P07","sources":["gl","ap"]} (nothing changed) → job done {"pull_id":"pul_…","status":"no_change","snapshot_sha256":"5e1c…","batches":[],"row_counts":{…}}
Failure shapes (job failed): {"code":"FP&A-ERR-115","message":"Dynamics 365 is busy and kept asking us to wait.","hint":"Try again in a few minutes; pulling outside business hours is faster","retryable":true,"details":{"source":"gl","page":4,"attempts":5,"last_status":429}}
                             {"code":"FP&A-ERR-118","message":"Dynamics 365 changed while we were reading it, so nothing was imported.","retryable":true,"details":{"source":"gl","expected":48213,"received":48219,"re_pulled":true}}
POST /projects/{id}/connector/disconnect → 200 {"state":"disconnected"}
```
A response body of any connector route containing a token-shaped string (`eyJ…`, `Bearer `) fails the contract test.
