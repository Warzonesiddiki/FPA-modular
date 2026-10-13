# 91 — PACKET DEPENDENCY SPECIFICATION (machine-checkable dispatch)

> Closes brutal-audit B6 properly: deps in the generator are prose; this doc defines the enforceable rule the integrator applies, and DEPENDENCY_GRAPH.csv is its machine-readable form.

## Rules
1. Every packet has a WAVE (DEPENDENCY_GRAPH.csv). A packet may be dispatched only if (a) its wave is open and (b) every packet in a lower wave that owns a contract it cites is tester-SIGNED.
2. Contract ownership: a contract (table, endpoint, function, component) is owned by exactly one packet — find it by searching FILE_MANIFEST.csv paths (`app/store/schema.sql` owns tables; `app/api/routes_*.py` owns endpoints; the module named in a dep string owns its functions). Prose deps are resolved by this lookup, and the integrator records the resolved packet ids in TASKBOARD's `depends_on` column at wave opening — that record, not the prose, is binding.
3. UI screens depend on: api/client packet + their route packets + theme/tokens + the components they list in doc 21. Exports depend on calc + forecast packets. Rules depend on schema + money + calendar. NOTHING depends on a docs packet at build time (docs are baselined, DEC-006).
4. A dependency cycle, or a dep on a packet in a higher wave, is a generator defect: fix the generator, regenerate, and note it in the wave review.
5. When a contract must change mid-wave: doc 72 RFC → DEC → affected packets (found via DEPENDENCY_GRAPH reverse lookup on the owning packet) are re-issued; already-signed packets citing it return to tester-review.
