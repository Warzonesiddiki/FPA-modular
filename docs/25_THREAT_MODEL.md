# 25 — THREAT MODEL (STRIDE, local desktop)

> Assets: financial data (GL, budgets, forecasts), credentials (AI key, Dynamics 365 connector tokens/secret), integrity of numbers/exports, audit trail. Adversaries: hostile files, hostile imported text, malicious local web pages/processes, curious/malicious insider with app access, supply-chain compromise. (Multi-user access control is out of scope v1 — OS account is the boundary; stated in-app.)

| Threat | Vector | Mitigation (owner doc) | Test |
|---|---|---|---|
| Spoofing | Local web page calls the local API | Per-launch token + 127.0.0.1 bind + CORS lock (12 §1) | API rejects token-less/local-cross-origin calls |
| Tampering | Edit DB/findings outside app; edit audit rows | Hash-chained audit, verify on S14 + before export snapshot; DB integrity check on open (12 §3) | Tamper fixture → ERR-090 path |
| Tampering | Hostile XLSX (zip bomb, formula, XXE-like payloads) | openpyxl data-only, expanded-size caps, no macro/external links, formula-injection prefixing (06, 09 §5) | Hostile corpus (06 §7) |
| Repudiation | "I never waived that" | Audit before/after + actor label + timestamp on every mutation (02, 23) | Workflow audit assertions |
| Info disclosure | AI payload leaks row data; logs leak values; diagnostics leak | Aggregate-only payloads, redacting logger, redacted diagnostics (11 §4, 12 §5) | Log/diagnostic scan tests; socket test |
| Info disclosure | Export files forwarded widely | Advisory stamps, hashes, snapshot ids (provenance, not DRM — stated honestly) | Export stamp checks |
| DoS | 1M-row/giant file freezes app | Caps ERR-021, streaming parse, background jobs w/ cancel (06 §6) | Perf + cap tests |
| Elevation | Path traversal via file names/paths; SQL injection via names | Path allow-roots, parameterised SQL (12 §4) | Injection suite |
| Supply chain | Malicious/vulnerable dep, fake installer | Pinning, licence/SBOM, payload audit, build from source (12 §6, 16) | scripts/check scans; build audit |
| Prompt injection | GL description instructs AI | Delimiting + instruction-stripping + output guardrails (11 §3) | Injection fixtures rejected/neutralised |
| Spoofing | Rogue local process answers the OAuth loopback callback, or a crafted link injects a foreign auth code | `state` + PKCE verifier bound to the in-memory sign-in attempt; callback accepted once, only on the app's own port, only while an attempt is pending (26 §8.2, 12 §1(d)) | Wrong-state / replayed callback → rejected, ERR-111 |
| Spoofing / MITM | Connector pointed at an attacker host or downgraded to plain HTTP | Egress allow-list enforced per request incl. redirects; TLS verification not configurable; `https://` required (12 §1(d)) | Non-allow-listed host and `http://` → ERR-113 before any socket opens |
| Info disclosure | Token or client secret ends up in DB, logs, job payload, diagnostics, backup | Keyring-only storage; redaction filter masks JWT/Bearer/`client_secret=`/`code=`; API never echoes secrets (12 §5) | Token-redaction + keyring-only tests (12 §8) |
| Tampering | Hostile cells arriving through the API instead of a file (formula strings, giant cells, control characters) | Snapshot workbook goes through the same hostile-input pipeline as any file: text-only cells, formula-injection prefixing, size caps (06 §1, 12 §4) | Mock page with hostile payloads lands quarantined/escaped |
| Tampering (integrity) | Ledger changes mid-pull → silently partial month | `$count` vs rows received check, one re-pull, then ERR-118; no partial snapshot is staged (26 §8.4) | Mock `count-drift` fault → ERR-118, zero batches |
| DoS | Throttling / huge entity drains the session | Retry with `Retry-After` and backoff, 5 attempts then ERR-115; `$count` volume guard ERR-116; one page in memory; cancellable job (26 §8.4, 64) | Mock 429/503/`truncate` faults; 250k-row perf run |
| Elevation (ERP side) | App used to *change* the ledger | No write endpoint exists; scopes requested are the least the product offers; the rectification journal is a file (01 §4, 26 §7) | Static scan: no POST/PATCH/DELETE to ERP hosts in `app/connectors` |

Residual risks accepted & disclosed: OS-account-level access = full data access (mitigate: encrypted drive guidance, doc 18); unsigned pilot installer (doc 16 §5); AI provider sees aggregates when user enables it (explicit consent copy in S13); the Dynamics 365 connector reads with the permissions the tenant grants the signed-in user — if IT grants a broad role, the app can read more than it needs (guidance: read-only / reporting role, doc 26 §8.9).
