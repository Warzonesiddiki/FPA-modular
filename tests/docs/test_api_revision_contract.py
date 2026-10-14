"""DEC-023 storage DTO and synthetic revision models; NOT SQL/HTTP/runtime evidence."""
from __future__ import annotations
import copy
import hashlib
import json
import re
from pathlib import Path
import pytest
from jsonschema import ValidationError, Draft202012Validator
from test_api_job_contract import validator
from test_api_impact_contract import BASELINE, REPORT, APPROVAL, PID

ROOT=Path(__file__).resolve().parents[2]
MAX=9223372036854775807
COUNTERS=['statement_revision','forecast_revision','pack_revision']
EFFECTS=['statement_inputs','forecast_inputs','pack_inputs']
ALL=EFFECTS[:]
FP=EFFECTS[1:]
P=EFFECTS[2:]
EXPECTED_EFFECTS={
 'committed_source':ALL,'adjustment_change':ALL,'statement_mapping':ALL,'statement_settings':ALL,
 'forecast_assumptions':FP,'forecast_publication':P,'finding_change':P,'commentary_change':P,
 'pack_configuration':P,'project_display':P,'pack_publication':[], 'impact_publication':[],
 'close_metadata':[], 'staging_only':[], 'job_control':[], 'read_only':[]}
COLUMNS={
 'input_revisions':['project_id','statement_revision','forecast_revision','pack_revision'],
 'input_revision_events':['project_id','audit_id','advance_json'],
 'snapshot_input_bindings':['project_id','snapshot_id','period_id','binding_json'],
 'forecast_input_bindings':['project_id','run_id','forecast_revision'],
 'restatement_baselines':['project_id','baseline_id','period_id','unlock_version','before_snapshot_id','audit_id','record_json'],
 'restatement_impacts':['project_id','impact_id','period_id','period_version','baseline_id','after_snapshot_id','audit_id','record_json'],
 'restatement_changes':['project_id','impact_id','ordinal','kind','change_key','record_json'],
 'restatement_approvals':['project_id','approval_id','impact_id','audit_id','record_json'],
 'impact_invalidations':['project_id','impact_id','audit_id','pack_revision']}

def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def revisions(s,f,p):return dict(project_id=PID,statement_revision=s,forecast_revision=f,pack_revision=p)
REV=revisions(2,3,5)
ADV=dict(project_id=PID,audit_id=101,effects=ALL,before=REV,after=revisions(3,4,6))
BIND=dict(project_id=PID,snapshot_id='snapshot_new',period_id='2026-P01',revisions=REV,
          manifest_sha256='e'*64,statements_fingerprint='b'*64)
FBIND=dict(project_id=PID,run_id='forecast_new',forecast_revision=3)
INVALID=dict(project_id=PID,impact_id='impact_1',audit_id=101,pack_revision=6)
# Independent single-row retention oracle; does not recalculate finance.
ROW=dict(kind='forecast',key=hashlib.sha256(b'["forecast","forecast_old"]').hexdigest(),run_id='forecast_old',change='stale')
R=dict(REPORT,counts=dict(statement=0,bva=0,finding=0,forecast=1,report=0),
       changes_sha256=hashlib.sha256(canonical([ROW])).hexdigest())
A=dict(APPROVAL,changes_sha256=R['changes_sha256'])
BASE_RECORD=dict(project_id=PID,audit_id=80,record=BASELINE)
IMPACT_RECORD=dict(project_id=PID,audit_id=90,record=R,after_binding=BIND)
CHANGE_RECORD=dict(project_id=PID,impact_id='impact_1',ordinal=0,record=ROW)
APPROVAL_RECORD=dict(project_id=PID,audit_id=95,record=A)
EXAMPLES={'InputRevisions':REV,'InputRevisionAdvance':ADV,'SnapshotInputBinding':BIND,
 'ForecastInputBinding':FBIND,'InputInvalidation':INVALID,'RetainedBaselineRecord':BASE_RECORD,
 'RetainedImpactRecord':IMPACT_RECORD,'RetainedImpactChange':CHANGE_RECORD,'RetainedApprovalRecord':APPROVAL_RECORD}
FACTS=dict(same_project=True,same_pack_revision=True,no_invalidation=True,content_verified=True,
           current_cycle=True,current_period_version=True,current_checked_pack=True,time_guards=True)

@pytest.fixture
def schema():
 s=json.loads((ROOT/'docs/api_job_schemas.json').read_text())
 assert set(EXAMPLES)<=s['$defs'].keys(),'DEC-023 revision/retention definitions missing'
 assert all(k in s for k in ['x-revision-effects','x-revision-storage','x-revision-policy']),'DEC-023 metadata missing'
 return s


def model_advance(before,categories,policy,commit=True,replay=False):
 """Pure document counter model, no DB, SQL, locking, receipts or side effects."""
 selected=set()
 for category in categories:selected.update(policy[category]) # unknown fails closed, never defaults to none
 if not commit or replay:return copy.deepcopy(before)
 result=copy.deepcopy(before)
 for effect,column in zip(EFFECTS,COUNTERS):
  if effect in selected:
   if result[column]==MAX:raise OverflowError('counter exhausted')
   result[column]+=1
 return result


def model_current(facts,policy):return all(facts[k] for k in policy['required_revision_facts'])


def advance_errors(event):
 errors=[];a=event['after'];b=event['before']
 if a['project_id']!=b['project_id'] or a['project_id']!=event['project_id']:errors.append('scope')
 for effect,col in zip(EFFECTS,COUNTERS):
  if a[col]!=b[col]+(effect in event['effects']):errors.append('increment')
 for r in [a,b]:
  if not 1<=r['statement_revision']<=r['forecast_revision']<=r['pack_revision']<=MAX:errors.append('counter order')
 return errors


def retained_errors(baseline,impact,changes,approval,binding):
 """Relational oracle over synthetic records only; no historical data lookup."""
 errors=[];r=impact['record'];a=approval['record'];b=baseline['record']
 if any(x['project_id']!=r['project_id'] for x in [impact,baseline,approval,b,a,binding,binding['revisions']]+changes):errors.append('scope')
 if binding['period_id']!=r['period_id'] or b['period_id']!=r['period_id'] or a['period_id']!=r['period_id']:errors.append('period')
 if binding!=impact['after_binding']:errors.append('joined binding')
 if b['baseline_id']!=r['baseline_id'] or r['before_snapshot']!=b['before_snapshot'] or r['before_manifest_sha256']!=b['before_manifest_sha256']:errors.append('baseline')
 if r['after_snapshot']['snapshot_id']!=binding['snapshot_id'] or r['after_manifest_sha256']!=binding['manifest_sha256']:errors.append('after snapshot')
 for k in ['project_id','period_id','period_version','impact_id','baseline_id','before_manifest_sha256','after_manifest_sha256','changes_sha256']:
  if a[k]!=r[k]:errors.append('approval binding')
 if a['before_snapshot_id']!=r['before_snapshot']['snapshot_id'] or a['after_snapshot_id']!=r['after_snapshot']['snapshot_id']:errors.append('approval snapshot')
 if [c['ordinal'] for c in changes]!=list(range(len(changes))):errors.append('ordinal')
 if any(c['impact_id']!=r['impact_id'] for c in changes):errors.append('impact owner')
 rows=[c['record'] for c in changes];keys=[(row['kind'],row['key']) for row in rows]
 if keys!=sorted(set(keys)):errors.append('sort/duplicate')
 if {k:sum(row['kind']==k for row in rows) for k in r['counts']}!=r['counts']:errors.append('counts')
 if hashlib.sha256(canonical(rows)).hexdigest()!=r['changes_sha256']:errors.append('changes hash')
 if not baseline['audit_id']<impact['audit_id']<approval['audit_id']:errors.append('audit order')
 return errors


def assert_oracles(s):
 for n,x in EXAMPLES.items():validator(s,n).validate(x)
 assert not advance_errors(ADV)
 assert not retained_errors(BASE_RECORD,IMPACT_RECORD,[CHANGE_RECORD],APPROVAL_RECORD,BIND)
 p=s['x-revision-effects'];r=revisions(1,1,1)
 for category,expected in [('committed_source',(2,2,2)),('forecast_assumptions',(2,3,3)),
                           ('forecast_publication',(2,3,4)),('commentary_change',(2,3,5))]:
  r=model_advance(r,[category],p);assert r==revisions(*expected)
 for category in ['pack_publication','impact_publication','close_metadata','read_only']:
  assert model_advance(r,[category],p)==r
 assert model_current(FACTS,s['x-revision-policy'])
 for fact in FACTS:assert not model_current(dict(FACTS,**{fact:False}),s['x-revision-policy']),fact


def test_independent_oracles(schema):assert_oracles(schema)


@pytest.mark.parametrize('name',sorted(EXAMPLES))
def test_closed_required_internal_shapes(schema,name):
 value=EXAMPLES[name]
 for k in value:
  obj=dict(value);del obj[k]
  with pytest.raises(ValidationError):validator(schema,name).validate(obj)
 with pytest.raises(ValidationError):validator(schema,name).validate(dict(value,actor='forged'))


@pytest.mark.parametrize('field',COUNTERS)
@pytest.mark.parametrize('value',[0,-1,True,'1',1.5,MAX+1,None])
def test_revision_wire_bounds(schema,field,value):
 with pytest.raises(ValidationError):validator(schema,'InputRevisions').validate(dict(REV,**{field:value}))


@pytest.mark.parametrize('effects',[[],['statement_inputs'],['forecast_inputs'],['pack_inputs','forecast_inputs'],
 ['pack_inputs','pack_inputs'],['read_only'],['statement_inputs','pack_inputs']])
def test_effects_are_closed_normalised_nonempty(schema,effects):
 with pytest.raises(ValidationError):validator(schema,'InputRevisionAdvance').validate(dict(ADV,effects=effects))


@pytest.mark.parametrize('category',list(EXPECTED_EFFECTS))
def test_each_effect_class(schema,category):
 assert schema['x-revision-effects'][category]==EXPECTED_EFFECTS[category]
 expected={**REV,**{col:REV[col]+(effect in EXPECTED_EFFECTS[category]) for effect,col in zip(EFFECTS,COUNTERS)}}
 assert model_advance(REV,[category],schema['x-revision-effects'])==expected


def test_union_once_not_per_row_or_period(schema):
 p=schema['x-revision-effects']
 assert model_advance(REV,['committed_source']*250000+['finding_change'],p)==revisions(3,4,6)
 assert model_advance(REV,['pack_publication','finding_change'],p)==revisions(2,3,6) # journal export side effect
 assert model_advance(REV,['forecast_assumptions','adjustment_change'],p)==revisions(3,4,6)


@pytest.mark.parametrize('commit,replay',[(False,False),(True,True),(False,True)])
def test_rejected_rollback_replay_model_preserves_input(schema,commit,replay):
 old=copy.deepcopy(REV)
 assert model_advance(old,['committed_source'],schema['x-revision-effects'],commit=commit,replay=replay)==REV
 assert old==REV # model has no side effects, NOT real crash-recovery proof


def test_aba_cannot_reuse_old_binding(schema):
 p=schema['x-revision-effects']
 changed=model_advance(REV,['committed_source'],p)
 reverted=model_advance(changed,['committed_source'],p)
 assert reverted==revisions(4,5,7) and reverted!=REV


def test_forecast_publication_does_not_stale_itself(schema):
 current=model_advance(REV,['forecast_publication'],schema['x-revision-effects'])
 assert current['forecast_revision']==FBIND['forecast_revision']
 assert current['pack_revision']!=BIND['revisions']['pack_revision']
 for category in ['finding_change','commentary_change','impact_publication','close_metadata']:
  current=model_advance(current,[category],schema['x-revision-effects'])
  assert current['forecast_revision']==FBIND['forecast_revision']
  assert current['statement_revision']==REV['statement_revision']


def test_mappings_without_new_batch_invalidate(schema):
 after=model_advance(REV,['statement_mapping'],schema['x-revision-effects'])
 assert after==revisions(3,4,6) # no batch watermark argument can mask this change


@pytest.mark.parametrize('category',['committed_source','forecast_assumptions','forecast_publication'])
def test_counter_overflow_fails_before_publication(schema,category):
 old=revisions(MAX,MAX,MAX)
 validator(schema,'InputRevisions').validate(old)
 with pytest.raises(OverflowError):model_advance(old,[category],schema['x-revision-effects'])
 assert old==revisions(MAX,MAX,MAX)


def test_unknown_category_cannot_fall_back_to_no_effect(schema):
 with pytest.raises(KeyError):model_advance(REV,['unregistered_mutation'],schema['x-revision-effects'])


@pytest.mark.parametrize('fault',['scope','increment_twice','omit_increment','counter_order'])
def test_advance_relational_negative_controls(fault):
 event=copy.deepcopy(ADV)
 if fault=='scope':event['after']['project_id']='prj_000000000002'
 if fault=='increment_twice':event['after']['pack_revision']=7
 if fault=='omit_increment':event['after']['statement_revision']=2
 if fault=='counter_order':event['after']['statement_revision']=20
 assert advance_errors(event)


@pytest.mark.parametrize('fact',list(FACTS))
def test_revision_match_alone_is_not_authority(schema,fact):
 assert not model_current(dict(FACTS,**{fact:False}),schema['x-revision-policy'])


@pytest.mark.parametrize('fault',['scope','period','baseline','snapshot','manifest','approval','ordinal','missing_row','duplicate','counts','hash','audit'])
def test_retention_relational_negative_controls(fault):
 b,r,c,a,bind=copy.deepcopy((BASE_RECORD,IMPACT_RECORD,[CHANGE_RECORD],APPROVAL_RECORD,BIND))
 if fault=='scope':a['project_id']='prj_000000000002'
 elif fault=='period':bind['period_id']='2026-P02'
 elif fault=='baseline':b['record']['baseline_id']='wrong_baseline'
 elif fault=='snapshot':r['record']['after_snapshot']['snapshot_id']='old_snapshot'
 elif fault=='manifest':bind['manifest_sha256']='0'*64
 elif fault=='approval':a['record']['changes_sha256']='0'*64
 elif fault=='ordinal':c[0]['ordinal']=1
 elif fault=='missing_row':c=[]
 elif fault=='duplicate':c.append(copy.deepcopy(c[0]))
 elif fault=='counts':r['record']['counts']['forecast']=0
 elif fault=='hash':r['record']['changes_sha256']='0'*64
 elif fault=='audit':a['audit_id']=89
 assert retained_errors(b,r,c,a,bind)


def test_three_mutations_caught(schema):
 changes=[]
 s=copy.deepcopy(schema);s['$defs']['ForecastInputBinding']['properties']['forecast_revision']={'const':1};changes.append(s)
 s=copy.deepcopy(schema);s['x-revision-policy']['required_revision_facts'].remove('same_pack_revision');changes.append(s)
 s=copy.deepcopy(schema);s['$defs']['RetainedImpactChange']['properties']['ordinal']['minimum']=1;changes.append(s)
 for s in changes:
  with pytest.raises((ValidationError,AssertionError)):assert_oracles(s)


def test_storage_columns_and_effects_match_owning_docs(schema):
 doc=(ROOT/'docs/02_DATA_DICTIONARY.md').read_text()
 assert set(schema['x-revision-storage'])==set(COLUMNS)
 for table,cols in COLUMNS.items():
  line=next(x for x in doc.splitlines() if x.startswith('| '+table+' |'))
  assert re.findall(r'([a-z_]+) (?:TEXT|INTEGER)',line.split('|')[2])==cols
  assert schema['x-revision-storage'][table]['columns']==cols
 effects_doc=(ROOT/'docs/24_DATA_FLOWS_ERD_AND_SEQUENCES.md').read_text()
 assert set(schema['x-revision-effects'])==set(EXPECTED_EFFECTS)
 for category,expected in EXPECTED_EFFECTS.items():
  line=next(x for x in effects_doc.splitlines() if x.startswith('| '+category+' |'))
  declared=line.split('|')[2].strip()
  assert declared==(', '.join(expected) if expected else 'none')
 index=(ROOT/'docs/90_API_PAYLOAD_SCHEMAS_DETAILED.md').read_text()
 assert all(n in index for n in EXAMPLES)
 Draft202012Validator.check_schema(schema)


def test_plan_owners_and_gate_are_explicit():
 gen=(ROOT/'tools/generate_work_plan.py').read_text();plan=(ROOT/'docs/WORK_PLAN.md').read_text()
 for word in ['input revisions/events','restatement_baselines/impacts/changes/approvals','forecast_input_bindings']:
  assert word in gen
 assert 'docs/24 §5' in plan or '24 §5' in plan
 assert '§7 deltas 1–16' in plan
 arch=(ROOT/'docs/04_TECHNICAL_ARCHITECTURE.md').read_text()
 assert 'cache invalidation by watermark change only' not in arch
 assert 'statement_revision' in arch


def model_invalidate(markers, impacts, event):
 """Synthetic first-marker projection. No SQL/rollback/locking is exercised."""
 if advance_errors(event):raise ValueError('invalid revision event')
 result=copy.deepcopy(markers)
 for impact in impacts:
  pid=impact['project_id']; iid=impact['record']['impact_id']
  if pid==event['project_id'] and impact['after_binding']['revisions']['pack_revision']<event['after']['pack_revision']:
   result.setdefault((pid,iid),dict(project_id=pid,impact_id=iid,audit_id=event['audit_id'],pack_revision=event['after']['pack_revision']))
 return result


def test_first_invalidation_permanent_across_reversion(schema):
 record=copy.deepcopy(IMPACT_RECORD)
 first=model_invalidate({},[record],ADV)
 assert first=={(PID,'impact_1'):INVALID}
 later=dict(ADV,audit_id=102,before=ADV['after'],after=revisions(4,5,7))
 assert model_invalidate(first,[record],later)==first
 assert record==IMPACT_RECORD # retained report is never rewritten
 validator(schema,'InputInvalidation').validate(first[(PID,'impact_1')])


def test_invalidation_scope_and_capture_boundary():
 foreign=copy.deepcopy(IMPACT_RECORD);foreign['project_id']='prj_000000000002'
 exact=copy.deepcopy(IMPACT_RECORD);exact['after_binding']['revisions']=ADV['after']
 assert model_invalidate({},[foreign],ADV)=={}
 assert model_invalidate({},[exact],ADV)=={}
 with pytest.raises(ValueError):model_invalidate({},[IMPACT_RECORD],dict(ADV,after=REV))


@pytest.mark.parametrize('counter',COUNTERS)
def test_minimum_and_maximum_revision(schema,counter):
 # JSON shape bounds only; ordering across columns is the relational oracle's job.
 for boundary in [1,MAX]:validator(schema,'InputRevisions').validate(dict(REV,**{counter:boundary}))


def test_empty_command_and_no_effect_at_exhaustion(schema):
 policy=schema['x-revision-effects']
 for value in [REV,revisions(MAX,MAX,MAX)]:
  assert model_advance(value,[],policy)==value
  assert model_advance(value,['pack_publication','close_metadata'],policy)==value
  assert model_advance(value,['committed_source'],policy,replay=True)==value


@pytest.mark.parametrize('effects,before,after',[
 (P,REV,revisions(2,3,6)), (FP,REV,revisions(2,4,6)), (ALL,REV,revisions(3,4,6))])
def test_all_normalised_event_shapes(schema,effects,before,after):
 event=dict(ADV,effects=effects,before=before,after=after)
 validator(schema,'InputRevisionAdvance').validate(event)
 assert not advance_errors(event)


@pytest.mark.parametrize('name,field',[('InputRevisionAdvance','audit_id'),('InputInvalidation','audit_id'),
 ('RetainedBaselineRecord','audit_id'),('RetainedImpactRecord','audit_id'),('RetainedApprovalRecord','audit_id'),
 ('ForecastInputBinding','forecast_revision'),('InputInvalidation','pack_revision')])
@pytest.mark.parametrize('invalid',[0,-1,True,None,'1',1.25])
def test_positive_integer_fields(schema,name,field,invalid):
 with pytest.raises(ValidationError):validator(schema,name).validate(dict(EXAMPLES[name],**{field:invalid}))


@pytest.mark.parametrize('invalid',[-1,True,None,'0',0.5])
def test_ordinal_is_nonnegative_integer(schema,invalid):
 with pytest.raises(ValidationError):validator(schema,'RetainedImpactChange').validate(dict(CHANGE_RECORD,ordinal=invalid))


@pytest.mark.parametrize('invalid',['','x'*64,'a'*63,'a'*65,'a'*64+'\n','A'*64,'<script>'])
@pytest.mark.parametrize('field',['manifest_sha256','statements_fingerprint'])
def test_binding_requires_exact_digests(schema,invalid,field):
 with pytest.raises(ValidationError):validator(schema,'SnapshotInputBinding').validate(dict(BIND,**{field:invalid}))


@pytest.mark.parametrize('invalid',['../escape','/abs','name\nforged','<script>','=SUM(A1)','a'*129])
def test_binding_ids_not_paths_or_executable_text(schema,invalid):
 with pytest.raises(ValidationError):validator(schema,'SnapshotInputBinding').validate(dict(BIND,snapshot_id=invalid))


def test_second_period_does_not_require_month_one(schema):
 binding=dict(BIND,period_id='2026-P02');validator(schema,'SnapshotInputBinding').validate(binding)
 b,r,c,a,bind=copy.deepcopy((BASE_RECORD,IMPACT_RECORD,[CHANGE_RECORD],APPROVAL_RECORD,BIND))
 for record in [b,r,a]:record['record']['period_id']='2026-P02'
 bind['period_id']='2026-P02';r['after_binding']=copy.deepcopy(bind)
 assert not retained_errors(b,r,c,a,bind)


def test_wire_conflict_details_unchanged(schema):
 validator(schema,'ErrorDetails003').validate({'expected_version':3,'actual_version':4})
 with pytest.raises(ValidationError):
  validator(schema,'ErrorDetails003').validate({'captured_revision':3,'current_revision':4})


def test_scalar_storage_owners(schema):
 for table,entry in schema['x-revision-storage'].items():
  expected=('app/store/db.py' if table in ['input_revisions','input_revision_events','impact_invalidations']
            else 'app/store/forecast_repo.py' if table=='forecast_input_bindings' else 'app/store/report_repo.py')
  assert entry=={'columns':COLUMNS[table],'owner':expected}
 assert set(schema['x-revision-policy']['required_revision_facts'])==set(FACTS)


def test_cross_scope_binding_and_event_fail_relational_checks():
 e=copy.deepcopy(ADV);e['before']['project_id']='prj_000000000002'
 assert advance_errors(e)
 binding=copy.deepcopy(BIND);binding['revisions']['project_id']='prj_000000000002'
 assert retained_errors(BASE_RECORD,IMPACT_RECORD,[CHANGE_RECORD],APPROVAL_RECORD,binding)


def test_zero_and_negative_money_remain_decimal_strings(schema):
 from test_api_impact_contract import MONEY
 for amount in ['0.00','-125.00']:
  row=copy.deepcopy(MONEY)
  row['before']['value']=amount;row['after']['value']=amount;row['delta']='0.00'
  validator(schema,'RetainedImpactChange').validate(dict(CHANGE_RECORD,record=row))
  row['after']['value']=0.5 # forbidden float wire value, no calculation
  with pytest.raises(ValidationError):validator(schema,'RetainedImpactChange').validate(dict(CHANGE_RECORD,record=row))
