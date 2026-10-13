# 69 — KPI EXPRESSION GRAMMAR SPECIFICATION (safe formula language, doc 19J)

## Grammar (EBNF; implemented as a recursive-descent parser in report_builder.py — eval() of any kind is forbidden)
```
expr   := term (('+'|'-') term)*
term   := factor (('*'|'/') factor)*
factor := NUMBER | NAME | NAME '(' expr (',' expr)* ')' | '(' expr ')' | '-' factor
NAME   := [A-Za-z][A-Za-z0-9_.]*    NUMBER := decimal literal
```
Names resolve only against the KPI/account-line registry (doc 43 keys + statement line keys, doc 45) — unknown name = validation error listing close matches. Functions (fixed set): `abs, min, max, avg(expr,…), pct_change(a,b), ytd(name), py(name), budget(name), forecast(name)`. No strings, no attribute access, no indexing, no conditionals in v1.
## Semantics & safety
Evaluated in Decimal over calc-provided values (the evaluator receives a value map; it computes only the analyst's arithmetic on already-computed aggregates — this is analyst-authored math, still routed through money rounding at the end). Division by zero → KPI `n/a` (doc 03 rule). Parse/validation on save with position-marked errors; execution depth ≤ 32, name count ≤ 50 (complexity caps, error not crash). Custom KPIs carry author + formula text into exports (KPIs sheet shows the formula — board-visible, by design).
Tests: grammar acceptance/rejection corpus (including injection attempts: `__import__`, `1;DROP`, nested-call bombs), precedence fixtures, zero-division, registry rename impact (referencing KPIs flagged broken, never silently zero).
