"""DEC-022 document fixtures/schema/policy models; NOT close service or HTTP tests."""
from __future__ import annotations
import copy
import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path
import pytest
from jsonschema import ValidationError, Draft202012Validator
from test_api_job_contract import validator
from test_api_project_contract import PID  # registers Gregorian format validation
from test_api_close_contract import SIGNOFF, READY
from test_api_impact_contract import BASELINE

ROOT=Path(__file__).resolve().parents[2]
AT='2026-05-08T09:00:00Z'
P='2026-P01'
TITLES=['Import GL & subledgers','Trial balance balanced','Bank/AR/AP/payroll reconciliations signed',
        'Statements reviewed','Material variances explained','Exceptions triaged','Forecast refreshed & locked',
        'Board pack generated, checks green','Close sign-off','Period locked']
KINDS=['system','system','system','attest','system','system','system','system','attest','system']
DUE=[1,1,2,3,3,3,4,4,5,5]
ENTRIES=[dict(key=f'T-{i:02}',title=title,kind=kind,owner_id=None,due_offset_business_days=due,depends_on=None)
         for i,(title,kind,due) in enumerate(zip(TITLES,KINDS,DUE),1)]
RULES=dict(start_business_day=1,target_lock_business_day=5,holidays=[])
TEMPLATE=dict(project_id=PID,version=1,calendar=RULES,entries=ENTRIES,created_at=AT,updated_at=AT)
TEMPLATE_PUT=dict(expected_version=1,calendar=RULES,entries=ENTRIES)
CALENDAR=dict(project_id=PID,period_id=P,template_version=1,instantiated=True,rules=RULES,
              period_end='2026-04-30',close_start_date='2026-05-01',target_lock_date='2026-05-07')
REVIEW=dict(project_id=PID,period_id=P,period_version=2,task_id='task_custom',task_version=1,
            audit_head='a'*64,statements_fingerprint=None,dependency_status=None)
# Literal canonical bytes, independent of JSON Schema and field iteration order.
CANONICAL_REVIEW=(b'{"audit_head":"'+b'a'*64+b'","dependency_status":null,"period_id":"2026-P01",'
 b'"period_version":2,"project_id":"prj_9f2c41aa07e1","statements_fingerprint":null,'
 b'"task_id":"task_custom","task_version":1}')
TOKEN=hashlib.sha256(b'FPA-CLOSE-TASK-v1\n'+CANONICAL_REVIEW).hexdigest()
TASK=dict(task_id='task_custom',project_id=PID,period_id=P,template_key='C-review',kind='manual',
 title='Review supporting schedules',owner_id=None,due_offset_business_days=5,due_date='2026-05-07',
 depends_on=None,version=1,created_at=AT,updated_at=AT,requested_status='not_started',status='not_started',
 note=None,attestation=None,review=REVIEW,review_token=TOKEN,evaluated_on='2026-05-08',overdue=True)
ATTEST=dict(signer='Controller',at=AT,note=None,statements_fingerprint=None)
DETAILS=dict(action='details',expected_version=1,expected_period_version=2,review_token=TOKEN,
 title=TASK['title'],owner_id=None,due_offset_business_days=5,depends_on=None)
TRANSITION=dict(action='transition',expected_version=1,expected_period_version=2,review_token=TOKEN,
 to_status='done',signer='Controller',attest=True,note=None)
COUNTS=dict(not_started=2,in_progress=0,blocked=0,done=8,waived=0)
OVERVIEW=dict(project_id=PID,period_id=P,period_version=2,period_status='closing',instantiated=True,
 template_version=1,counts=COUNTS,evaluated_on='2026-05-08',readiness=READY)
LOCK=dict(project_id=PID,period_id=P,before_version=2,after_version=3,signoff_id=SIGNOFF['signoff_id'],
 snapshot=SIGNOFF['evidence']['snapshot'],force=False,note=None,locked_at=SIGNOFF['at'])
HISTORY=dict(audit_id=4,action='PERIOD_LOCK',at=LOCK['locked_at'],evidence_state='complete',record=LOCK)
EXAMPLES={'CloseCalendarRules':RULES,'CloseTemplateEntry':ENTRIES[0],'CloseTemplatePut':TEMPLATE_PUT,
 'CloseTemplate':TEMPLATE,'CloseCalendar':CALENDAR,'CloseTaskAttestation':ATTEST,'CloseTask':TASK,
 'CloseTaskDetails':DETAILS,'CloseTaskTransition':TRANSITION,'CloseTaskReview':REVIEW,
 'ClosePeriodQuery':{'period_id':P},'CloseTaskPage':{'items':[TASK],'next_cursor':None},
 'CloseTaskCounts':COUNTS,'CloseOverview':OVERVIEW,'CloseLockRecord':LOCK,'CloseHistoryItem':HISTORY,
 'CloseHistoryPage':{'items':[HISTORY],'next_cursor':None}}
NAMES=set(EXAMPLES)|{'CloseTaskKey','CloseTaskStatus','CloseTaskUpdate','CloseTaskListQuery','CloseHistoryQuery'}
ROUTES={
 'GET /projects/{id}/close':(None,'CloseOverview','ClosePeriodQuery'),
 'GET /projects/{id}/close/tasks':(None,'CloseTaskPage','CloseTaskListQuery'),
 'GET /close/tasks/{id}':(None,'CloseTask',None),
 'PUT /close/tasks/{id}':('CloseTaskUpdate','CloseTask',None),
 'GET /projects/{id}/close/template':(None,'CloseTemplate',None),
 'PUT /projects/{id}/close/template':('CloseTemplatePut','CloseTemplate',None),
 'GET /projects/{id}/close/calendar':(None,'CloseCalendar','ClosePeriodQuery'),
 'GET /projects/{id}/periods/{period_id}/close-history':(None,'CloseHistoryPage','CloseHistoryQuery')}
FLAGS=dict(closing=True,same_task_version=True,same_period_version=True,same_review=True,
           integrity_ok=True,not_busy=True,human_editable=True,dependency_satisfied=True,statements_current=True)


@pytest.fixture
def schema():
 s=json.loads((ROOT/'docs/api_job_schemas.json').read_text())
 assert NAMES<=s['$defs'].keys(),'DEC-022 close task definitions missing'
 assert 'x-task-endpoints' in s and 'x-task-policy' in s,'DEC-022 task policy missing'
 return s


def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


def graph_errors(entries,policy):
 """Independent document graph model, not repository reference/ownership validation."""
 nodes={x['key']:x for x in entries}; errors=[]
 if len(nodes)!=len(entries):errors.append('duplicate')
 if not set(policy['required_keys'])<=nodes.keys():errors.append('missing builtin')
 for entry in entries:
  key=entry['key'];dep=entry['depends_on']
  if dep in policy['forbidden_dependencies']:errors.append('outcome dependency')
  if dep is not None and dep not in nodes:errors.append('missing dependency')
  if policy['reject_cycles']:
   seen=set();p=key
   while p in nodes:
    if p in seen:errors.append('cycle');break
    seen.add(p);p=nodes[p]['depends_on']
 return errors


def model_transition_allowed(flags,policy,key='T-04'):
 # Synthetic task identity/facts, never caller-controlled production guards.
 if key!='T-04' and not key.startswith('C-'):return False
 facts=dict(flags)
 if key!='T-04':facts['statements_current']=True  # condition is only applicable to T-04
 return all(facts[g] for g in policy['terminal_transition_guards'])


def business_date(anchor,offset,holidays,policy):
 """Tiny document-policy interpreter with literal date oracles; NOT core/calendar."""
 day=date.fromisoformat(anchor);blocked=set(holidays)
 eligible=lambda d:d.weekday() in policy['weekdays'] and d.isoformat() not in blocked
 if offset==0:
  while not eligible(day):day+=timedelta(days=1)
  return day.isoformat()
 step=1 if offset>0 else -1;remaining=abs(offset)
 if policy['count_anchor_for_nonzero'] and eligible(day):remaining-=1
 while remaining:
  day+=timedelta(days=step)
  if eligible(day):remaining-=1
 return day.isoformat()


def custom(key='C-review',dep=None):
 return dict(key=key,title='Review supporting schedules',kind='manual',owner_id=None,due_offset_business_days=5,depends_on=dep)


def assert_oracles(s):
 for name,value in EXAMPLES.items():validator(s,name).validate(value)
 for value in [DETAILS,TRANSITION]:validator(s,'CloseTaskUpdate').validate(value)
 validator(s,'CloseTemplateEntry').validate(ENTRIES[9])
 p=s['x-task-policy'];assert not graph_errors([custom(dep='T-04')]+ENTRIES,p)
 assert graph_errors([custom(dep='T-09')]+ENTRIES,p)
 assert model_transition_allowed(FLAGS,p)
 for g in FLAGS:assert not model_transition_allowed(dict(FLAGS,**{g:False}),p),g
 assert business_date('2026-01-30',1,['2026-02-02'],p)=='2026-02-03'


def test_independent_oracles(schema):assert_oracles(schema)


@pytest.mark.parametrize('name',sorted(EXAMPLES))
def test_required_and_closed(schema,name):
 obj=EXAMPLES[name]
 for field in obj:
  changed=dict(obj);del changed[field]
  with pytest.raises(ValidationError):validator(schema,name).validate(changed)
 with pytest.raises(ValidationError):validator(schema,name).validate(dict(obj,actor='forged'))


@pytest.mark.parametrize('key',['T-00','T-11','C-','C-1a','C-UPPER','C-a'*25,'T-09\n'])
def test_task_keys(schema,key):
 with pytest.raises(ValidationError):validator(schema,'CloseTaskKey').validate(key)


@pytest.mark.parametrize('patch',[{'key':'T-09','kind':'manual'},{'key':'T-10','kind':'manual'},
 {'depends_on':'T-09'},{'depends_on':'T-10'},{'kind':'attest'},{'due_offset_business_days':61},
 {'due_offset_business_days':-61},{'due_offset_business_days':True},{'title':'x'*81},{'title':'bad\ntext'}])
def test_template_entry_negatives(schema,patch):
 with pytest.raises(ValidationError):validator(schema,'CloseTemplateEntry').validate(dict(custom(),**patch))


@pytest.mark.parametrize('patch',[{'title':'Renamed'},{'depends_on':'C-review'},{'kind':'manual'}])
def test_builtins_are_not_redefined(schema,patch):
 with pytest.raises(ValidationError):validator(schema,'CloseTemplateEntry').validate(dict(ENTRIES[0],**patch))


@pytest.mark.parametrize('offset',[-60,-1,0,1,60])
def test_due_offset_bounds(schema,offset):validator(schema,'CloseTemplateEntry').validate(dict(custom(),due_offset_business_days=offset))


@pytest.mark.parametrize('patch',[{'holidays':['2026-02-30']},{'holidays':['2026-01-01']*2},
 {'start_business_day':0},{'target_lock_business_day':61},{'start_business_day':False}])
def test_calendar_shape(schema,patch):
 with pytest.raises(ValidationError):validator(schema,'CloseCalendarRules').validate(dict(RULES,**patch))


@pytest.mark.parametrize('case',['self','two_cycle','long_cycle','missing','outcome9','outcome10','duplicate','missing_builtin'])
def test_graph_negative_controls(schema,case):
 extra=[custom()];rows=copy.deepcopy(ENTRIES)
 if case=='self':extra[0]['depends_on']='C-review'
 if case=='two_cycle':extra=[custom('C-one','C-two'),custom('C-two','C-one')]
 if case=='long_cycle':extra=[custom('C-one','C-two'),custom('C-two','C-three'),custom('C-three','C-one')]
 if case=='missing':extra[0]['depends_on']='C-missing'
 if case=='outcome9':extra[0]['depends_on']='T-09'
 if case=='outcome10':extra[0]['depends_on']='T-10'
 if case=='duplicate':extra.append(copy.deepcopy(extra[0]))
 if case=='missing_builtin':rows=rows[:-1]
 assert graph_errors(extra+rows,schema['x-task-policy'])


def test_bounded_template_and_page(schema):
 rows=[custom(f'C-task{i}',f'C-task{i-1}' if i else 'T-04') for i in range(990)]
 entries=sorted(rows+ENTRIES,key=lambda r:r['key'])
 assert not graph_errors(entries,schema['x-task-policy'])
 validator(schema,'CloseTemplatePut').validate(dict(TEMPLATE_PUT,entries=entries))
 for invalid in [ENTRIES[:-1],entries+[custom('C-extra')]]:
  with pytest.raises(ValidationError):validator(schema,'CloseTemplatePut').validate(dict(TEMPLATE_PUT,entries=invalid))
 validator(schema,'CloseTaskPage').validate({'items':[],'next_cursor':None})
 with pytest.raises(ValidationError):validator(schema,'CloseTaskPage').validate({'items':[TASK]*1001,'next_cursor':None})


@pytest.mark.parametrize('patch',[{'attest':False},{'signer':None},{'force':True},{'completed_by':'fake'},
 {'expected_version':0},{'expected_period_version':True},{'to_status':'locked'},
 {'to_status':'waived','note':None},{'note':' '},{'note':'x'*501}])
def test_transition_negatives(schema,patch):
 with pytest.raises(ValidationError):validator(schema,'CloseTaskUpdate').validate(dict(TRANSITION,**patch))


@pytest.mark.parametrize('status',['not_started','in_progress','blocked','done','waived'])
def test_human_transition_shapes(schema,status):
 terminal=status in ['done','waived'];note='Reason supplied' if status in ['blocked','waived'] else None
 obj=dict(TRANSITION,to_status=status,signer='Controller' if terminal else None,attest=terminal,note=note)
 validator(schema,'CloseTaskTransition').validate(obj)
 if not terminal:
  with pytest.raises(ValidationError):validator(schema,'CloseTaskTransition').validate(dict(obj,attest=True))


@pytest.mark.parametrize('key',['T-01','T-02','T-03','T-05','T-06','T-07','T-08','T-09','T-10'])
def test_system_and_outcome_cannot_carry_manual_completion(schema,key):
 e=next(x for x in ENTRIES if x['key']==key)
 task=dict(TASK,template_key=key,title=e['title'],kind=e['kind'],requested_status=None,attestation=None,note=None,
           status='not_started' if key in ['T-09','T-10'] else 'blocked')
 validator(schema,'CloseTask').validate(task)
 for patch in [{'requested_status':'done'},{'attestation':ATTEST},{'note':'Override'}]:
  with pytest.raises(ValidationError):validator(schema,'CloseTask').validate(dict(task,**patch))


def test_t04_binding_and_custom_terminal_shape(schema):
 a=dict(ATTEST,statements_fingerprint='c'*64)
 t=dict(TASK,template_key='T-04',title=TITLES[3],kind='attest',requested_status='done',status='done',attestation=a,overdue=False,review=dict(REVIEW,statements_fingerprint='c'*64))
 t['review_token']=hashlib.sha256(b'FPA-CLOSE-TASK-v1\n'+canonical(t['review'])).hexdigest()
 validator(schema,'CloseTask').validate(t)
 validator(schema,'CloseTask').validate(dict(t,status='blocked',overdue=True))  # retained but stale
 for patch in [{'attestation':ATTEST},{'requested_status':'waived'},{'status':'waived'}]:
  with pytest.raises(ValidationError):validator(schema,'CloseTask').validate(dict(t,**patch))
 validator(schema,'CloseTask').validate(dict(TASK,requested_status='done',status='done',attestation=ATTEST,overdue=False))


@pytest.mark.parametrize('g',list(FLAGS))
def test_each_terminal_guard(schema,g):assert not model_transition_allowed(dict(FLAGS,**{g:False}),schema['x-task-policy'])


@pytest.mark.parametrize('anchor,offset,holidays,expected',[
 ('2026-01-30',0,['2026-02-02'],'2026-01-30'),('2026-01-30',1,['2026-02-02'],'2026-02-03'),
 ('2026-01-30',5,['2026-02-02'],'2026-02-09'),('2026-01-30',-1,[],'2026-01-29'),
 ('2026-01-31',0,['2026-02-02'],'2026-02-03'),('2026-01-31',1,['2026-02-02'],'2026-02-03'),
 ('2026-01-31',-1,[],'2026-01-30'),('2028-02-29',1,[],'2028-03-01'),
 ('2026-04-30',1,[],'2026-05-01'),('2026-04-30',5,[],'2026-05-07'),
 ('2026-01-30',1,['2026-01-31'],'2026-02-02'),('2025-12-31',1,['2026-01-01'],'2026-01-02')])
def test_hand_worked_business_dates(schema,anchor,offset,holidays,expected):
 assert business_date(anchor,offset,holidays,schema['x-task-policy'])==expected


@pytest.mark.parametrize('anchor,offset',[('9999-12-31',1),('0001-01-01',-1)])
def test_date_overflow_not_clipped(schema,anchor,offset):
 with pytest.raises(OverflowError):business_date(anchor,offset,[],schema['x-task-policy'])


@pytest.mark.parametrize('evaluation,status,overdue',[
 ('2026-05-06','not_started',False),('2026-05-07','not_started',False),('2026-05-08','blocked',True),
 ('2026-05-08','done',False),('2026-05-08','waived',False)])
def test_overdue_boundary(evaluation,status,overdue):
 assert (date.fromisoformat(evaluation)>date(2026,5,7) and status not in ['done','waived'])==overdue


def test_review_binding_canonical():
 assert canonical(REVIEW)==CANONICAL_REVIEW
 assert TOKEN=='72b90e097d6a3780b6775897effc3d71294c62648c7c98ba435f766ea876a21d'
 assert TOKEN==hashlib.sha256(b'FPA-CLOSE-TASK-v1\n'+canonical(REVIEW)).hexdigest()
 for k,v in [('task_version',2),('period_version',3),('audit_head','b'*64),('dependency_status','blocked'),
             ('statements_fingerprint','c'*64),('project_id','prj_000000000001'),('period_id','2026-P02'),('task_id','task_other')]:
  assert hashlib.sha256(b'FPA-CLOSE-TASK-v1\n'+canonical(dict(REVIEW,**{k:v}))).hexdigest()!=TOKEN


@pytest.mark.parametrize('action,record',[('CLOSE_SIGNOFF',SIGNOFF),('PERIOD_LOCK',LOCK),('RESTATE_OPEN',BASELINE)])
def test_history_typed_and_legacy(schema,action,record):
 record=dict(record,project_id=PID,period_id=P)
 field={'CLOSE_SIGNOFF':'at','PERIOD_LOCK':'locked_at','RESTATE_OPEN':'opened_at'}[action]
 event=dict(HISTORY,action=action,record=record,at=record[field])
 validator(schema,'CloseHistoryItem').validate(event)
 validator(schema,'CloseHistoryItem').validate(dict(event,evidence_state='legacy',record=None))
 for patch in [{'record':None},{'evidence_state':'legacy'},{'current':True}]:
  with pytest.raises(ValidationError):validator(schema,'CloseHistoryItem').validate(dict(event,**patch))
 if action!='PERIOD_LOCK':
  with pytest.raises(ValidationError):validator(schema,'CloseHistoryItem').validate(dict(event,record=LOCK))


@pytest.mark.parametrize('patch',[{'force':True},{'after_version':1},{'signoff_id':None}])
def test_lock_history_guarded_shape(schema,patch):
 with pytest.raises(ValidationError):validator(schema,'CloseLockRecord').validate(dict(LOCK,**patch))


@pytest.mark.parametrize('name,obj',[('CloseHistoryQuery',{'action':'unknown'}),('CloseHistoryQuery',{'limit':1001}),
 ('CloseHistoryQuery',{'cursor':None}),('CloseTaskListQuery',{}),('CloseTaskListQuery',{'period_id':P,'limit':0}),
 ('CloseTaskListQuery',{'period_id':P,'status':'done'})])
def test_queries_closed(schema,name,obj):
 with pytest.raises(ValidationError):validator(schema,name).validate(obj)


def test_three_mutations_caught(schema):
 copies=[]
 s=copy.deepcopy(schema);s['$defs']['CloseTemplateEntry']['allOf'][-1]['then']['properties']['kind']={'const':'manual'};copies.append(s)
 s=copy.deepcopy(schema);s['x-task-policy']['terminal_transition_guards'].remove('same_period_version');copies.append(s)
 s=copy.deepcopy(schema);s['x-task-policy']['count_anchor_for_nonzero']=True;copies.append(s)
 for s in copies:
  with pytest.raises((AssertionError,ValidationError)):assert_oracles(s)


def test_endpoint_index_errors_and_policy_parity(schema):
 doc=(ROOT/'docs/05_API_CONTRACT.md').read_text();index=(ROOT/'docs/90_API_PAYLOAD_SCHEMAS_DETAILED.md').read_text()
 assert set(schema['x-task-endpoints'])==set(ROUTES)
 for route,(req,res,query) in ROUTES.items():
  e=schema['x-task-endpoints'][route]
  assert (e['request'],e['response'],e['query'],e['status'],e['scope'],e['token_required'])==(req,res,query,'200','project',True)
  assert e['idempotency']==('required' if req else 'none')
  method,path=route.split(' ',1);section=doc.split(f'{method} `{path}`',1)[1].split('\n### ',1)[0]
  line=next(x for x in section.splitlines() if x.startswith('- **Failures:**'))
  assert set(re.findall(r'ERR-(\d{3})',line))=={x for codes in e['errors'].values() for x in codes}
  for status,codes in e['errors'].items():
   global_line=next(x for x in doc.splitlines() if x.startswith(f'| {status} |'))
   assert all('ERR-'+c in global_line for c in codes)
 assert all(name in index for name in NAMES)
 p=schema['x-task-policy']
 assert p['template_edits_affect_existing_periods'] is False and p['get_writes'] is False
 assert p['t04_binding']=='statements_only' and p['history_grants_authority'] is False
 assert p['required_keys']==[f'T-{i:02}' for i in range(1,11)]
 Draft202012Validator.check_schema(schema)


def test_cookbook_examples(schema):
 text=(ROOT/'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text().split('## 12. Close task',1)[1]
 pairs=re.findall(r'<!-- schema: (\w+) -->\n```json\n(.*?)\n```',text,re.S)
 assert {n for n,_ in pairs}>= {'CloseOverview','CloseTaskPage','CloseTaskTransition','CloseTemplate','CloseCalendar','CloseHistoryPage'}
 for n,body in pairs:validator(schema,n).validate(json.loads(body))


def template_errors(template,policy):
 errors=graph_errors(template['entries'],policy)
 if [e['key'] for e in template['entries']]!=sorted(e['key'] for e in template['entries']):errors.append('entry order')
 r=template['calendar']
 if r['target_lock_business_day']<r['start_business_day']:errors.append('calendar order')
 if r['holidays']!=sorted(set(r['holidays'])):errors.append('holiday order/duplicate')
 for e in template['entries']:
  if e['key'] in ['T-09','T-10'] and e['due_offset_business_days']!=r['target_lock_business_day']:errors.append('outcome due')
 return errors


def task_context_errors(task,period_version):
 r=task['review'];errors=[]
 for k in ['project_id','period_id','task_id']:
  if r[k]!=task[k]:errors.append(k)
 if r['task_version']!=task['version'] or r['period_version']!=period_version:errors.append('version')
 if hashlib.sha256(b'FPA-CLOSE-TASK-v1\n'+canonical(r)).hexdigest()!=task['review_token']:errors.append('token')
 overdue=task['evaluated_on']>task['due_date'] and task['status'] not in ['done','waived']
 if task['overdue']!=overdue:errors.append('overdue')
 if task['template_key']=='T-04' and task['status']=='done':
  if task['attestation']['statements_fingerprint']!=r['statements_fingerprint']:errors.append('stale statements')
 return errors


def history_errors(items,project,period):
 errors=[];ids=[x['audit_id'] for x in items]
 if ids!=sorted(set(ids)):errors.append('audit order/duplicate')
 for item in items:
  record=item['record']
  if record is None:continue  # explicitly labelled legacy by schema
  if record['project_id']!=project or record['period_id']!=period:errors.append('scope')
  field={'CLOSE_SIGNOFF':'at','PERIOD_LOCK':'locked_at','RESTATE_OPEN':'opened_at'}[item['action']]
  if record[field]!=item['at']:errors.append('timestamp')
  if item['action']=='PERIOD_LOCK' and record['after_version']!=record['before_version']+1:errors.append('lock increment')
 return errors


@pytest.mark.parametrize('fault',['entry_order','holiday_order','target_before_start','outcome_due','duplicate_custom'])
def test_template_context_negative_controls(schema,fault):
 assert not template_errors(TEMPLATE,schema['x-task-policy'])
 t=copy.deepcopy(TEMPLATE)
 if fault=='entry_order':t['entries'].reverse()
 elif fault=='holiday_order':t['calendar']['holidays']=['2026-02-02','2026-01-01']
 elif fault=='target_before_start':t['calendar']['start_business_day']=6
 elif fault=='outcome_due':t['entries'][9]['due_offset_business_days']=4
 else:t['entries']=[custom(),dict(custom(),title='Different title, same key')]+t['entries']
 assert template_errors(t,schema['x-task-policy'])


@pytest.mark.parametrize('fault',['project_id','period_id','task_id','task_version','period_version','audit_head','token','overdue'])
def test_review_context_negative_controls(fault):
 assert not task_context_errors(TASK,2)
 t=copy.deepcopy(TASK)
 if fault=='token':t['review_token']='0'*64
 elif fault=='overdue':t['overdue']=False
 else:t['review'][fault]=99 if fault.endswith('version') else 'other'
 assert task_context_errors(t,2)


@pytest.mark.parametrize('fault',['scope','timestamp','lock_increment','duplicate','audit_order'])
def test_history_context_negative_controls(fault):
 rows=[copy.deepcopy(HISTORY)]
 assert not history_errors(rows,PID,P)
 if fault=='scope':rows[0]['record']['project_id']='prj_000000000001'
 elif fault=='timestamp':rows[0]['at']=AT
 elif fault=='lock_increment':rows[0]['record']['after_version']=4
 elif fault=='duplicate':rows.append(copy.deepcopy(rows[0]))
 else:rows.append(dict(copy.deepcopy(rows[0]),audit_id=3))
 assert history_errors(rows,PID,P)


def test_t04_does_not_approve_old_display():
 t=dict(TASK,template_key='T-04',kind='attest',title=TITLES[3],requested_status='done',status='done',overdue=False,
        attestation=dict(ATTEST,statements_fingerprint='c'*64),review=dict(REVIEW,statements_fingerprint='c'*64))
 t['review_token']=hashlib.sha256(b'FPA-CLOSE-TASK-v1\n'+canonical(t['review'])).hexdigest()
 assert not task_context_errors(t,2)
 t['attestation']=dict(t['attestation'],statements_fingerprint='d'*64)
 assert 'stale statements' in task_context_errors(t,2)


def test_cookbook_context_and_task_update_result(schema):
 text=(ROOT/'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text().split('## 12. Close task',1)[1]
 examples={name:json.loads(body) for name,body in re.findall(r'<!-- schema: (\w+) -->\n```json\n(.*?)\n```',text,re.S)}
 returned=examples['CloseTask'];before=examples['CloseTaskPage']['items'][0]
 assert not task_context_errors(before,2) and not task_context_errors(returned,2)
 assert returned['version']==before['version']+1 and returned['review']['period_version']==2
 assert returned['status']=='done' and returned['attestation']['signer']=='Controller'
 assert returned['review_token']!=before['review_token']
 assert not template_errors(examples['CloseTemplate'],schema['x-task-policy'])
 assert not history_errors(examples['CloseHistoryPage']['items'],PID,P)
 assert examples['CloseTaskPage']['next_cursor'] is not None


@pytest.mark.parametrize('text',['=formula','<script>literal</script>','Review — 確認'])
def test_hostile_titles_and_notes_are_literal(schema,text):
 validator(schema,'CloseTemplateEntry').validate(dict(custom(),title=text))
 validator(schema,'CloseTaskTransition').validate(dict(TRANSITION,note=text))


def test_empty_close_is_not_ready(schema):
 ready=copy.deepcopy(READY);ready.update(ready_to_sign_off=False,ready_to_lock=False)
 ready['blockers']=[dict(code='statements_review',count=1,overridable=False)]
 overview=dict(OVERVIEW,instantiated=False,template_version=None,counts={k:0 for k in COUNTS},readiness=ready)
 validator(schema,'CloseOverview').validate(overview)
 for patch in [{'counts':COUNTS},{'template_version':1},{'readiness':READY}]:
  with pytest.raises(ValidationError):validator(schema,'CloseOverview').validate(dict(overview,**patch))



def test_done_t04_cannot_omit_current_statement_binding(schema):
 t=dict(TASK,template_key='T-04',title=TITLES[3],kind='attest',requested_status='done',status='done',overdue=False,
        attestation=dict(ATTEST,statements_fingerprint='c'*64))
 with pytest.raises(ValidationError):validator(schema,'CloseTask').validate(t)
 # A historical attestation can be retained with no current statements, but it is blocked.
 validator(schema,'CloseTask').validate(dict(t,status='blocked',overdue=True))


def test_custom_waiver_requires_retained_reason(schema):
 a=dict(ATTEST,note='Controller-approved exception')
 t=dict(TASK,requested_status='waived',status='waived',overdue=False,note=a['note'],attestation=a)
 validator(schema,'CloseTask').validate(t)
 for patch in [{'note':None},{'attestation':ATTEST}]:
  with pytest.raises(ValidationError):validator(schema,'CloseTask').validate(dict(t,**patch))


def test_nonstatement_task_cannot_claim_statement_review(schema):
 with pytest.raises(ValidationError):
  validator(schema,'CloseTask').validate(dict(TASK,review=dict(REVIEW,statements_fingerprint='c'*64)))


def test_conditional_statement_guard_and_outcome_protection(schema):
 p=schema['x-task-policy']
 assert model_transition_allowed(dict(FLAGS,statements_current=False),p,key='C-review')
 assert not model_transition_allowed(dict(FLAGS,statements_current=False),p,key='T-04')
 for key in ['T-01','T-02','T-03','T-05','T-06','T-07','T-08','T-09','T-10']:
  assert not model_transition_allowed(FLAGS,p,key=key)


def test_task_cursor_expiry_does_not_invent_row_revisions():
 from datetime import datetime
 # Independent signed-cursor contract facts, not an expiry scheduler/HTTP parser.
 retention=datetime.fromisoformat('2026-05-15T09:00:00+00:00')
 waiver=datetime.fromisoformat('2026-05-08T10:00:00+00:00')
 deadline=min(retention,waiver)
 assert deadline==waiver
 assert datetime.fromisoformat('2026-05-08T09:59:59+00:00')<deadline
 assert datetime.fromisoformat('2026-05-08T10:00:00+00:00')>=deadline
 assert (0+1,4+1)==(1,5)  # empty/current audit-head positions map to positive versions
 doc=(ROOT/'docs/05_API_CONTRACT.md').read_text().split('Live task pages bind',1)[1].split('### 10.1',1)[0]
 assert 'expired cursor (ERR-002)' in doc and 'audit_id + 1' in doc
