# WI-0001 — input revision / retained impact contract checkpoint

**Status:** in_progress. M0 open, **0/8**; requested WI-0001…0030 batch **0/30**. This is a bounded document/schema checkpoint, not a completed WI, storage implementation or milestone audit.

## 1. Baseline and docs-first decisions

The restored workspace had stale Git metadata at 4257b5a but the retained files matched pushed **6d68929**. Fetched only `origin arena/5165fe46-fpa-modular`, verified every remote tracked file byte-for-byte (including locally untracked prior tests/evidence), used mixed reset to restore metadata, then reverified all bytes unchanged. Recreated the ignored `.venv` with `python -m venv .venv` and `.venv/bin/python -m pip install -r tests/docs/requirements.txt`. Fresh pre-edit `.venv/bin/python -m pytest -q`: **694 passed in 18.90s**. No checker exists. The older 694/21.18s continuation result is not this session's baseline.

DEC-023 (auto), doc 17 §4: project-wide positive signed-int64 statement/forecast/pack revisions; trusted effect union advances once per command; permanent first invalidation and T-04 stale marking in the same transaction; immutable retained impact records; no derived-output self-staling. Alternatives/reversal cost are recorded there. Watermark-only statement memoisation in doc 04 §4 was unsafe after mapping/adjustment/prior-period changes and is now explicitly prohibited.

Docs-first commits:
- `dc15d23`: docs 02 §5/24 §5/05 §11, architecture/cache, close/restatement/migration/index, DEC/CHANGELOG, existing-module owners and stronger M1 delta-16 gate; generated plans, no schema implementation.
- `b9f36cf`: existing ERR-003 detail mapping (expected_version=captured relevant counter, actual_version=current counter), internal metadata index, project initial counters and immutable-table metadata exception; corrected baseline handover.
- `ddd2fd2`: explicit UNIQUE(project_id,audit_id) and UNIQUE(project_id,run_id) parent constraints for same-project audit/forecast FKs; no SQL changes.

The earlier scratch editing script had not run at handover. This session ran it after baseline verification, then reviewed/corrected its owning-doc contracts before constructing the schema definitions. Its execution is not evidence of contract completeness. Dates here use local **2026-10-15**.

## 2. Tests executed

All commands below used the repository root and the pinned document environment.

| Command | Exact observed result |
|---|---|
| `.venv/bin/python -m pytest -q` before edits | **694 passed in 18.90s** |
| `.venv/bin/python -m pytest tests/docs/test_api_revision_contract.py -q --tb=short` before schema | **17 passed, 75 errors in 0.89s**; fixture assertion `DEC-023 revision/retention definitions missing`, not an import failure |
| Same paired command after nine definitions | **92 passed in 1.14s** |
| Same paired command with adversarial edge tests | **173 passed in 1.79s** |
| `.venv/bin/python -m pytest tests/docs -q --tb=short` | **858 passed in 20.66s** |
| `.venv/bin/python -m pytest -q --tb=short` | **867 passed in 19.93s** |
| Paired command, fresh repeat | **173 passed in 1.73s** |
| Full command, fresh repeat | **867 passed in 21.10s** |
| `git diff --check` | clean |

Initial red was captured in `/home/user/revision_red.txt`; its assertion/counts are recorded above rather than relying on scratch retention. Assertions/oracles preceded schemas. Adversarial expansion did not require weakening any assertion. There are **285 definitions (+9), 18 job kinds and 76 error codes**; all 276 earlier definitions and all earlier top-level attachment metadata remain exactly unchanged.

### Independent oracles and mutation checks

New tests use literal counter/effect/column expectations from docs 02/24, a synthetic retained forecast-change sequence, and existing hand-authored public impact fixtures (not generated from the schema under test). Pure models do **not** import product code, execute SQL, fetch snapshots, validate a real audit chain or prove transaction rollback. Cross-field/cross-row checks are explicitly relational models; JSON Schema does not enforce equality between independently supplied properties.

Doc-24 counter oracle: (1,1,1) → source (2,2,2) → assumptions (2,3,3) → forecast publication (2,3,4) → commentary (2,3,5). Pack/impact/approval/sign-off/lock alone leave counters unchanged. Source correction then value reversion yields (4,5,7), never the former review state. A compound source/finding command advances once to (3,4,6).

`test_three_mutations_caught` / `assert_oracles` catches each isolated in-memory mutant; a separate executed probe confirmed:
1. Replace ForecastInputBinding.forecast_revision with constant 1 → **ValidationError: 1 was expected**, against independent revision 3 fixture.
2. Drop `same_pack_revision` from required conjuncts → **AssertionError: same_pack_revision**, when that fact is false and all others true.
3. Change RetainedImpactChange.ordinal minimum 0→1 → **ValidationError: 0 is less than the minimum of 1**, against first-row ordinal 0.

Original attachment passed after every probe; no mutant was written to it. These are schema/document-model mutations, not runtime mutations.

## 3. Self-verification

### Universal edges

| Edge | Evidence / limit |
|---|---|
| Zero amounts / zero denominators | TEST-ONLY: retained zero decimal-string payload accepted; no division exists in this slice, denominator arithmetic N/A. |
| Negative / credit-normal amounts | TEST-ONLY: negative decimal-string payload retained, float payload rejected; credit-normal calculation remains owned by money/calculation modules, untested here. |
| Empty input | MODEL: empty/no-effect category list does not advance, including exhausted counters; missing required fields reject. No empty historical snapshot fallback allowed by docs. |
| Single row | SCHEMA/MODEL: complete one-row retained change sequence, ordinal 0, full changes hash/counts and approval bindings. |
| Duplicate input | MODEL: repeated categories union once; duplicate retained ordinals/keys reject in relational oracle. Actual SQL uniqueness/idempotency still unbuilt. |
| 250k-row posture | MODEL only: 250,000 duplicate effect declarations advance once. This is **not** a 250k-row database, financial or performance benchmark. |
| Missing optional data | SCHEMA: internal records have explicit required fields and closed objects; missing record/manifest/binding rejects. Rule not_run coverage is an input effect in owner docs, not a rule implementation. |
| Locked period / locked version | MODEL/DOC: false current-cycle/version/pack facts reject; immutable DTO remains unchanged on first-marker projection. Actual lock/read/history guards need later service tests. |
| Superseded batch | MODEL/DOC: source/mapping changes invalidate without depending on batch watermark; correction/reversion cannot restore the old counters. No import executed. |
| Expired waiver | MODEL: false time_guards rejects even with matching revisions. This test supplies the fact; no live expiry clock is evaluated by it. Prior document tests remain unchanged. |
| Hostile text | SCHEMA: path-like, newline, executable-looking and oversized ids reject; bad hashes reject. No SQL or browser execution is exercised. User notes reuse the existing public DTOs. |
| Ambiguous dates / amounts | SCHEMA: noninteger/boolean/string counters reject and public money stays decimal-string. No new date/amount parser here. |
| Currency exponent 0/2/3 | N/A: no monetary formatting, conversion or arithmetic added; reused public money schema only. |
| Month-2 reuse | SCHEMA/MODEL: full synthetic records also bind 2026-P02; foreign-project invalidation excluded. No hardcoded month-one permission. |
| Deterministic repeat | PASS for document tests: paired 173 and full 867 repeat; generated plan byte-identical. Export/snapshot byte reproducibility is not claimed. |

### Three highest-risk spec checks

1. **Docs 24 §5/§5.2, 41 §5:** effect closure, overflow, union once, conservative mappings/source invalidation and no forecast/pack/impact self-staling. Explicit expected counter sequence, each of 16 categories, replay/rejection model and int64 boundaries pass.
2. **Docs 02 §5.1, 24 §5.1–§5.2:** first invalidation remains permanent; approval/scope/snapshot/hash/ordinal/count/audit-order negative controls reject. Simulated first marker retains audit 101/pack 6 after later event; original report untouched. SQL atomicity, foreign keys and crash recovery are **requirements, not verified implementations**.
3. **Docs 05 §11, 24 §5.2–§5.3, 04 §4:** current revision is necessary but insufficient; every required fact tested false in isolation; ERR-003 retains existing fields; watermark-only cache text removed. Complete content verification, viewer/layer binding and restore-epoch validation remain unbuilt.

### Scope, money, no-invention and plan checks

- Only WI-0001 owning/repeating docs, its new document test/schema attachment, generator/derived plans, TASKBOARD and this evidence changed. No app/SQL or prior test file differs byte-for-byte from 6d68929.
- Money grep executed: `grep -nE 'float\(|Decimal\(|amount_minor[[:space:]]*[+*/=-]' tests/docs/test_api_revision_contract.py docs/api_job_schemas.json` → no matches. Test-only fractional literals are invalid-input probes, not money calculations. All retained public monetary values reuse ImpactChange's decimal-string contract.
- Nine record layouts come from doc 02 §5.1; effect categories and metadata from doc 24 §5; IDs/hashes/public impact DTOs are unchanged references. No endpoint, caller-supplied field, error or job was added. Relational invariants are not misrepresented as JSON Schema capabilities.
- Existing db/report_repo/forecast_repo/period_repo/close_service ownership is explicit. db's mechanical invalidation does not classify business inputs or import repositories; all share caller-owned transactions. Missing lifecycle/receipt coordinator is **not** assigned to close_service implicitly.
- 267 plan IDs/paths/layers/milestones unchanged. Only dependency delta: WI-0152 adds WI-0049 (report_repo) and WI-0047 (forecast_repo), preserving WI-0001/0050/0031. Generator regenerated markdown/CSV byte-identically. All seven gate strings exactly equal doc 86. Only M1 delta coverage strengthened 1–15→1–16; other clauses retained, no gate closed.

## 4. Exact continuation — still WI-0001

Do not start WI-0002 or the WI-0008 bootstrap checker; no M1 product implementation yet.

1. Complete retained **manifest/view/source storage codecs** and release identities: statements/BvA/forecast/finding business state, canonical field encodings, row-version provenance and historical source/file/row drill. SnapshotInputBinding is only metadata, not a replayable snapshot. The nine persistence DTOs/tables do not make the entire retention design complete.
2. Complete statement-only **T-04 fingerprint**, including prior-period/mapping/adjustment/settings inputs and exact viewer/layer/scope binding; revisions cannot supply omitted read-set content. Finish authentic legacy baseline/calendar/evidence repair instead of fabricating bindings from today's state.
3. Assign missing **project lifecycle and durable receipt coordinator/control-plane schema**, then safe backup/restore: bounded server-issued selection (never arbitrary filesystem `{path}`), SQLite/WAL-consistent capture, archive validation/exclusions, durable jobs/receipts, target ownership/pre-restore preservation and external restore epoch/stale-write fencing. Restoring old database counters is not itself rollback protection. Keep launch descriptor/credentials outside copied project content; preserve deletion trash/recovery guarantees.
4. Continue remaining endpoint families, annual-planning transport/persistence, and migration of doc 90's residual field ownership into doc 05. Every planned M3 route must become implementable without guessed fields before WI-0001 closes.
5. Keep currentness/time/audit/readiness guards conjunctive. Historical reads/replays never revive approval; sign-off still requires rereading readiness before lock; T-09/T-10 remain outcomes and force cannot bypass hard guards.

DECISIONS TAKEN: DEC-023 (auto) · OWNER-ONLY ITEMS: none for this scope · NEXT WI: WI-0001 (continue, not complete).

## 5. Executed one-off scope/mutation probe

This is the actual scratch verification source, retained here for reproducibility, **not** the planned bootstrap checker or a gate pass. Command: `.venv/bin/python /home/user/check_revision_scope.py`.

```python
import ast,copy,csv,io,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tests/docs')
from test_api_revision_contract import assert_oracles
from jsonschema import ValidationError
base='6d68929'
def original(p):return subprocess.check_output(['git','show',base+':'+p])
s=json.loads(Path('docs/api_job_schemas.json').read_text());old=json.loads(original('docs/api_job_schemas.json'))
assert all(s['$defs'][k]==v for k,v in old['$defs'].items())
assert all(s[k]==v for k,v in old.items() if k!='$defs')
print('Schema: all 276 old definitions and every old top-level key unchanged;',len(s['$defs']),'definitions;',len(s['x-job-results']),'jobs;',len(s['x-error-codes']),'errors.')
oldrows=list(csv.DictReader(io.StringIO(original('docs/WORK_PLAN.csv').decode())))
newrows=list(csv.DictReader(io.StringIO(Path('docs/WORK_PLAN.csv').read_text())))
assert len(oldrows)==len(newrows)==267
for a,b in zip(oldrows,newrows):
 assert all(a[k]==b[k] for k in ['id','path','layer','milestone'])
 if a['depends_on']!=b['depends_on']:print('Dependency change:',a['id'],a['depends_on'],'->',b['depends_on'])
for p in subprocess.check_output(['git','ls-tree','-r','--name-only',base,'app','tests']).decode().splitlines():
 assert Path(p).read_bytes()==original(p),p
print('Product/SQL/all existing tests byte-unchanged; plan IDs, paths, layers and milestones unchanged.')
before={p:Path(p).read_bytes() for p in ['docs/WORK_PLAN.md','docs/WORK_PLAN.csv']}
subprocess.run([sys.executable,'tools/generate_work_plan.py'],check=True)
assert all(Path(p).read_bytes()==b for p,b in before.items())
print('Plan regeneration byte-identical.')
tree=ast.parse(Path('tools/generate_work_plan.py').read_text())
gates=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GATES' for t in n.targets))
doc=Path('docs/86_WBS_AND_AGENT_WAVE_PLAN_DETAILED.md').read_text()
for name,gate in gates.items():
 line=next(line for line in doc.splitlines() if line.startswith('| **'+name+' —'))
 assert line.split('|')[-2].strip()==gate,name
print('All 7 gate strings exactly match doc 86; no gate closure claimed.')
for kind in ['constant','conjunct','ordinal']:
 mutant=copy.deepcopy(s)
 if kind=='constant':mutant['$defs']['ForecastInputBinding']['properties']['forecast_revision']={'const':1}
 if kind=='conjunct':mutant['x-revision-policy']['required_revision_facts'].remove('same_pack_revision')
 if kind=='ordinal':mutant['$defs']['RetainedImpactChange']['properties']['ordinal']['minimum']=1
 try:assert_oracles(mutant)
 except (ValidationError,AssertionError) as exc:print('Caught',kind,'mutation:',type(exc).__name__,str(exc).splitlines()[0])
 else:raise AssertionError('SURVIVING MUTATION '+kind)
assert_oracles(s)
print('Original oracle passes; mutants confined to isolated in-memory copies.')

```
