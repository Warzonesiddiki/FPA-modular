# 25 — THREAT MODEL (STRIDE, local desktop)

> Assets: financial data (GL, budgets, forecasts), credentials (AI key), integrity of numbers/exports, audit trail. Adversaries: hostile files, hostile imported text, malicious local web pages/processes, curious/malicious insider with app access, supply-chain compromise. (Multi-user access control is out of scope v1 — OS account is the boundary; stated in-app.)

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

Residual risks accepted & disclosed: OS-account-level access = full data access (mitigate: encrypted drive guidance, doc 18); unsigned pilot installer (doc 16 §5); AI provider sees aggregates when user enables it (explicit consent copy in S13).
