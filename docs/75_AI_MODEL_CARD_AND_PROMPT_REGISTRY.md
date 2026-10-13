# 75 — AI MODEL CARD & PROMPT REGISTRY

Registry (one card per PROMPT-01…06, doc 11 §6; card updated on every prompt/model change; eval artefact per doc 77):
| Field | Content per prompt |
|---|---|
| Purpose / never-use | e.g. PROMPT-01 drafts variance commentary; never forecasts, never judges a finding |
| Payload schema + minimisation | fields sent; why each is needed (11 §4) |
| Provider/model tested | name + version + date (provider-agnostic: card per configured provider at pilot) |
| Guardrails | number-provenance, register ban-list, injection handling (11 §3) with test ids |
| Evaluation | golden-set score (11 §7), date, known failure modes observed |
| Human gate | draft→approve path; exports read approved only |
Known limitations (stated on every card + S13 AI panel): output quality varies by provider/model; drafts may mischaracterise cause (the *Why* is always analyst-edited); numbers cannot be invented *and pass* — but tone errors can, hence the human gate; disabling AI removes none of the product's analytical capability. Incident process: a guardrail escape found in use = S1 defect (72) + golden-set addition + card update.
