# 36 — NON-FUNCTIONAL REQUIREMENTS CATALOGUE (all numbers owned here + doc 14 §4)

| ID | Requirement | Budget/test |
|---|---|---|
| NFR-01 | Import 250k rows parse+stage | ≤120s (14 §4) |
| NFR-02 | Commit 250k rows | ≤60s, atomic kill-tested |
| NFR-03 | 28-rule run incl. suggestions on 250k rows | ≤60s |
| NFR-04 | Statements/BvA render data | ≤5s API |
| NFR-05 | Excel pack (250k drill rows) | ≤60s |
| NFR-06 | UI table 10k rows filter/sort | ≤1s, virtualised |
| NFR-07 | Cold start to interactive | ≤5s on reference profile |
| NFR-08 | Project DB size guidance | 5M rows usable; vacuum/compact action in S13 with progress |
| NFR-09 | Memory ceiling during import | ≤1.5GB reference profile (streaming) |
| NFR-10 | Availability of function offline | 100% except AI calls and user-initiated Dynamics 365 pulls (socket-blocked test; the file route and the local demo ledger work offline) |
| NFR-11 | Data durability | crash/kill at any stage → no partial commit, no corrupt DB (WAL + txn tests) |
| NFR-12 | Accessibility | WCAG 2.2 AA (13) |
| NFR-13 | Compatibility | Windows 11 (Phase 3 macOS); Excel outputs open in Excel 2019+/LibreOffice; PPT in PowerPoint 2019+/LibreOffice |
| NFR-14 | Install size / time | installer ≤150MB; install ≤3 min; first pack ≤60 min for new analyst (14 §6) |
| NFR-15 | Determinism | identical inputs → identical numbers/findings (acceptance stability) |
| NFR-16 | Localisation readiness | strings externalised; number/date/currency per doc 27 |
| NFR-17 | Connector throughput & footprint (DEC-013) | 250k-row period from the local mock ≤ 300 s end-to-end incl. snapshot write; ≤ 1 server page (≤ 20k rows) resident in memory; retries bounded (5/page); a pull is cancellable within one page |
| NFR-18 | Connector safety | egress only to the allow-list, TLS always, zero network with the connector disabled, zero background calls ever; secrets only in the OS keyring; token-redaction and keyring-only tests green on every build (doc 12 §8) |
Reference profile: 4-core CPU, 16GB RAM, SSD, Windows 11 — perf tests record the machine profile in evidence so numbers are comparable across runs.
