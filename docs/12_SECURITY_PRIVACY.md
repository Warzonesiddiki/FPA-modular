# 12 — SECURITY & PRIVACY SPECIFICATION

> Owner of: local-only guarantees, data protection, hostile-input handling, supply chain. Posture: the app's promise is "your financial data never leaves this laptop" — any feature breaking it is a release blocker.

## 1. Data & network guarantees
All data in the project folder (doc 04 §5). Network: (a) API binds 127.0.0.1 only, ephemeral port, per-launch token required: the desktop shell generates a random 32-byte token at startup, passes it to the API process via environment variable, and injects it into the served UI's in-memory config (never to disk, never in a URL); the UI sends it as `X-FPA-Token` on every request and the API rejects requests without it (constant-time compare); CLI reads the token from a 0600-permission runtime file in the project folder written by the shell; CORS locked to the local UI origin; (b) AI calls only when enabled (doc 11); (c) no telemetry, analytics, crash upload, or update phone-home in v1 (update = manual installer download). A CI test greps for outbound-call libraries/URLs outside the AI client allowlist.

## 2. At-rest protection
Project folder inherits OS user permissions (documented in doc 18 with a "store on an encrypted drive" recommendation). Optional project passphrase (Settings): DB encrypted via SQLCipher-compatible layer **only if** the dependency clears the tech budget (doc 04 §6) — otherwise v1 ships OS-permission posture honestly labelled in UI, and passphrase encryption is a Phase-2 ADR. Never claim encryption we don't ship (attempt-#4 truth rule). Backups are copies of the same folder; restore verifies hashes + audit chain before opening.

## 3. Audit integrity
audit_log hash chain (doc 02); S14 "Verify" recomputes the chain; a break → banner, exports blocked, restore guidance shown, incident note auto-drafted in logs. Findings workflow, locks, waivers, settings/threshold changes, mapping changes, imports, exports are all audited with before/after.

## 4. Hostile input (P18)
Files: size/row caps (doc 06), parser in streaming mode, XLSX zip-bomb guard (expanded-size cap, sheet/row caps), no macro execution ever (openpyxl data-only), file names sanitised before path use. Text: descriptions/vendor names escaped in UI, API JSON, Excel (formula-injection prefix, doc 09 §5), PPT, logs, and AI prompts (doc 11 §3). SQL: parameterised everywhere (store layer lint + injection tests with hostile account names). Paths: all user-supplied paths resolved under allowed roots (project folder / chosen export folder) — traversal attempts → ERR with hint.

## 5. Secrets
AI key in OS keyring (keyring lib) or env var; never in settings.json, DB, logs, exports, or diagnostics bundles (diagnostics = logs + versions + hashes, with financial values redacted by the logger's redaction filter, tested).

## 6. Supply chain (P17)
Pinned versions + lockfiles committed (pip + npm); licence allowlist (MIT/BSD/Apache-2.0/PSF; copyleft requires ADR); SBOM-lite generated at build (scripts/build) listing name/version/licence; no binary blobs committed; installer built from source in CI-equivalent script, payload-audited (no project data, no keys) before release (doc 16).

## 7. Privacy & advisory
Vendor/personal names appear only where operationally needed (findings, drill). AI payload minimisation per doc 11 §4. Exports carry the advisory disclaimer (doc 01 §8). Retention/deletion = project folder deletion; "Delete project" in S02 requires typed confirmation and removes folder contents (audited in app-level log).

## 8. Security tests (doc 14)
Socket-blocked full run; injection suite (SQL/formula/prompt/path); hostile-file corpus (doc 06 §7 + zip bomb + 1M-row sheet); audit-tamper detection; API token/CORS checks; secret-scan + telemetry-scan in scripts/check (no skipped gates).
