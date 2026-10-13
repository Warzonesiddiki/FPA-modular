# 11 — AI INTEGRATION SPECIFICATION

> Owner of: the AI boundary. Principle P3: **AI never computes, approves, posts, or decides.** It drafts words around numbers the deterministic engine already verified. AI is OFF by default; the product is complete without it (every packet must pass tests with AI disabled).

## 1. What AI may do (exhaustive)
1. Draft variance commentary from a verified BvA table (scope: one account group or exec summary).
2. Draft an executive summary from the approved KPI/variance/finding aggregates.
3. Rephrase a finding into a plain-language explanation + suggested owner questions (rule logic stays deterministic; AI only words it).
4. Draft forecast narrative from a locked run + its backtest metrics.
5. Answer analyst questions *over the exported aggregates* (Q&A) with citations to line/finding keys.
6. Suggest import column mappings (ranking hint only; analyst confirms; deterministic suggester works without AI).

## 2. What AI must never do
Produce a number not present in its input payload; compute totals/percentages; select or suppress findings; set statuses/owners; approve commentary (human approves, doc 02 commentary.status); contact any endpoint when disabled; receive row-level personal data beyond vendor names needed for commentary (payloads are aggregates + labels, minimised per §4).

## 3. Guardrails (`app/ai/guardrails.py` — the gate every draft passes)
- **Number provenance check:** extract all numeric tokens from the draft; each must match (value, after format normalisation) a number in the input payload. Any invented/altered number → whole draft rejected (ERR-071) with the offending tokens listed; rejection is logged. No partial auto-fixes.
- **Banned-content check:** accusatory language list ("fraud", "error by <person>", "manipulation") → reject; required register: "potential exception", "variance", "to review".
- **Injection defence (P18):** GL descriptions/vendor names are data, delimited and instruction-stripped in prompts; system prompt states imported text is never an instruction; output is treated as untrusted text (escaped everywhere).
- **Human gate:** drafts land as commentary `status=draft, ai_assisted=1, prompt_version` — exports use only `approved` versions.

## 4. Payloads (versioned schemas in code)
`VarianceCommentaryPayload{variance_rows:[{label, actual, budget, var_abs, var_pct, favourable}], period, currency}` — money as decimal strings; max 50 rows (top by |contribution|, remainder summarised as one "all other" row computed by calc, not AI). ExecSummary, FindingExplain, ForecastNarrative, QA payloads analogous; each schema documented in `app/ai/prompts.py` and snapshot-tested.

## 5. Provider & configuration
Provider-agnostic client (`app/ai/client.py`): base_url + model + key via OS keyring/env; timeout 30s; 1 retry; every call logged locally (prompt hash, payload hash, token usage, latency — never payload contents at INFO). No key configured → AI buttons show "AI is off — add a key in Settings or continue without it" and everything else works. Network is used *only* for these calls and only when enabled (test: socket-blocked suite passes with AI off; with AI on, only configured host is contacted).

## 6. Prompts PROMPT-01…06 (`app/ai/prompts.py`, versioned `v1`)
01 variance commentary · 02 exec summary · 03 finding explanation · 04 forecast narrative · 05 Q&A · 06 board highlights. Each: purpose, payload schema, system text (incl. number-provenance instruction + register rules), output shape (paragraphs + bullet drivers), snapshot test. Prompt changes bump version and are recorded on stored commentary (reproducibility).

## 7. Evaluation (before any prompt ships)
Golden set: 20 payloads with human-written reference commentary; checks = guardrail pass, no invented numbers (scripted), register compliance, analyst rating ≥ "usable with light edits" on 16/20 in tabletop review (doc 14). Re-run on prompt/model change; results filed in evidence/.
