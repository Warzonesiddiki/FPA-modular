"""DEC-021 document DTO/policy oracles; not a financial engine, DB or HTTP test."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

import pytest
from jsonschema import ValidationError, Draft202012Validator
from test_api_job_contract import validator

ROOT = Path(__file__).resolve().parents[2]
PID = 'prj_000000000001'
PERIOD = '2026-P01'
AT = '2026-10-14T10:00:00Z'
BEFORE = dict(snapshot_id='snapshot_old', batch_watermark='a'*64, budget_version='budget_1',
              forecast_run_id='forecast_old', layer='gl')
AFTER = dict(BEFORE, snapshot_id='snapshot_new', batch_watermark='b'*64, forecast_run_id='forecast_new')
BASELINE = dict(baseline_id='baseline_1', project_id=PID, period_id=PERIOD, unlock_version=4,
                before_snapshot=BEFORE, before_manifest_sha256='c'*64, locked_at='2026-10-13T10:00:00Z',
                lock_note=None, signoff_id='signoff_old', opened_at=AT, reason='Correct April source data.')
CREATE = dict(expected_version=4, baseline_id='baseline_1', after_snapshot_id='snapshot_new')
VALUE = dict(value='100.00', unavailable_reason=None, drill_key='drill_before_rev')
MONEY = dict(kind='statement', key='0'*64, statement='pl', line_key='rev', entity_id=None,
             account_id=None, cost_centre_id=None, measure='amount', before=VALUE,
             after=dict(value='125.00', unavailable_reason=None, drill_key='drill_after_rev'), delta='25.00')
BVA = dict(MONEY, kind='bva', key='1'*64, statement=None, line_key=None, entity_id='entity_1',
           account_id='account_rev', measure='var_abs',
           before=dict(VALUE,value='20.00',drill_key='drill_before_var'),
           after=dict(VALUE,value='45.00',drill_key='drill_after_var'))
FINDING = dict(kind='finding', key='2'*64, finding_key='EXC-001|2026-P01|entity_1|account_rev',
               change='added', before_finding_id=None, after_finding_id='finding_1',
               before_sha256=None, after_sha256='d'*64)
FORECAST = dict(kind='forecast', key='3'*64, run_id='forecast_old', change='stale')
EXPORT = dict(kind='report', key='4'*64, report_id='report_old', change='superseded')
REPORT = dict(impact_id='impact_1', project_id=PID, period_id=PERIOD, period_version=4,
              baseline_id='baseline_1', before_snapshot=BEFORE, after_snapshot=AFTER,
              before_manifest_sha256='c'*64, after_manifest_sha256='e'*64,
              changes_sha256='f'*64, counts=dict(statement=1,bva=1,finding=1,forecast=1,report=1),created_at=AT)
APPROVE = dict(expected_version=4, signer='Controller', attest=True, note='Reviewed correction against the original pack.')
APPROVAL = dict(approval_id='approval_1',project_id=PID,period_id=PERIOD,period_version=4,
                impact_id='impact_1',baseline_id='baseline_1',before_snapshot_id='snapshot_old',
                after_snapshot_id='snapshot_new',before_manifest_sha256='c'*64,
                after_manifest_sha256='e'*64,changes_sha256='f'*64,signer='Controller',
                attestation_text='I reviewed the restatement impact for 2026-P01 and approve these changes',
                note=APPROVE['note'],at=AT)
STATE = dict(project_id=PID,period_id=PERIOD,period_version=4,period_status='closing',baseline=BASELINE,
             current_impact_id='impact_1',current_approval_id='approval_1')
EXAMPLES = {'RestatementBaseline':BASELINE,'RestatementState':STATE,'ImpactCreate':CREATE,
            'ImpactCounts':REPORT['counts'],'ImpactReport':REPORT,'ImpactValue':VALUE,
            'ImpactMoneyChange':MONEY,'ImpactFindingChange':FINDING,'ImpactForecastChange':FORECAST,
            'ImpactReportChange':EXPORT,'ImpactChangePage':{'items':[],'next_cursor':None},
            'ImpactApprovalCreate':APPROVE,'ImpactApproval':APPROVAL}
NAMES = set(EXAMPLES) | {'ImpactChange','ImpactChangeQuery'}
GUARDS = ['closing','same_scope','same_cycle','same_period_version','same_before_snapshot',
          'same_before_manifest','same_after_snapshot','same_after_manifest','checked_pack',
          'never_invalidated','latest_qualifying_report']
ROUTES = {
 'GET /projects/{id}/periods/{period_id}/restatement': (None,'RestatementState','200','none',None),
 'POST /projects/{id}/periods/{period_id}/impacts': ('ImpactCreate','ImpactReport','201','required',None),
 'GET /impacts/{id}': (None,'ImpactReport','200','none',None),
 'GET /impacts/{id}/changes': (None,'ImpactChangePage','200','none','ImpactChangeQuery'),
 'POST /impacts/{id}/approve': ('ImpactApprovalCreate','ImpactApproval','201','required',None),
 'GET /impact-approvals/{id}': (None,'ImpactApproval','200','none',None),
 'GET /restatement-baselines/{id}': (None,'RestatementBaseline','200','none',None),
}


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


@pytest.fixture
def schema():
    s=json.loads((ROOT/'docs/api_job_schemas.json').read_text())
    assert NAMES <= s['$defs'].keys(), 'DEC-021 impact definitions missing'
    assert 'x-impact-endpoints' in s and 'x-impact-policy' in s, 'DEC-021 impact policy missing'
    return s


def model_current(facts, policy):
    """Synthetic policy interpreter only; does not discover facts from storage/finance."""
    return all(facts[g] for g in policy['current_report_guards'])


def bindings_valid(approval, report):
    for k in ['project_id','period_id','period_version','impact_id','baseline_id',
              'before_manifest_sha256','after_manifest_sha256','changes_sha256']:
        if approval[k] != report[k]:
            return False
    return (approval['before_snapshot_id']==report['before_snapshot']['snapshot_id'] and
            approval['after_snapshot_id']==report['after_snapshot']['snapshot_id'])


def assert_oracles(s):
    for name,value in EXAMPLES.items():
        validator(s,name).validate(value)
    validator(s,'ImpactCreate').validate(dict(CREATE,expected_version=2))
    for row in [MONEY,BVA,FINDING,FORECAST,EXPORT]:
        validator(s,'ImpactChange').validate(row)
    page={'items':[dict(FORECAST,key=f'{i:064x}',run_id=f'forecast_{i}') for i in range(1000)],'next_cursor':None}
    validator(s,'ImpactChangePage').validate(page)
    facts={g:True for g in GUARDS}
    assert model_current(facts,s['x-impact-policy'])
    for guard in GUARDS:
        assert not model_current(dict(facts,**{guard:False}),s['x-impact-policy']), guard


def test_independent_oracles(schema):
    assert_oracles(schema)


@pytest.mark.parametrize('name',sorted(EXAMPLES))
def test_closed_required_fields(schema,name):
    obj=EXAMPLES[name]
    for field in obj:
        changed=dict(obj); del changed[field]
        with pytest.raises(ValidationError): validator(schema,name).validate(changed)
    with pytest.raises(ValidationError): validator(schema,name).validate(dict(obj,actor='forged'))


@pytest.mark.parametrize('name',['ImpactCreate','ImpactApprovalCreate'])
@pytest.mark.parametrize('value',[0,1,-1,True,'4',4.5,None])
def test_unlock_version_bounds(schema,name,value):
    with pytest.raises(ValidationError):
        validator(schema,name).validate(dict(EXAMPLES[name],expected_version=value))


@pytest.mark.parametrize('patch',[{'attest':False},{'attest':1},{'note':None},{'note':''},{'note':'   '},
    {'note':'x'*501},{'note':'bad\ncontrol'},{'signer':' Controller'},{'force':True},
    {'impact_approved':True},{'before_snapshot_id':'forged'}])
def test_approval_injections(schema,patch):
    with pytest.raises(ValidationError): validator(schema,'ImpactApprovalCreate').validate(dict(APPROVE,**patch))


@pytest.mark.parametrize('note',['=formula','<script>alert("x")</script>','Approved — 確認','x'*500])
def test_hostile_literal_notes_are_data(schema,note):
    validator(schema,'ImpactApprovalCreate').validate(dict(APPROVE,note=note))


@pytest.mark.parametrize('value',['0','-125','0.00','-25.00','0.000','125.125'])
def test_decimal_money_and_exponents(schema,value):
    validator(schema,'ImpactValue').validate(dict(VALUE,value=value))


@pytest.mark.parametrize('value',[0,1.25,True,'1,250.00','1e3','NaN','Infinity','01.00','1.0','1.0000','1.00\n'])
def test_money_never_numeric_or_ambiguous(schema,value):
    with pytest.raises(ValidationError): validator(schema,'ImpactValue').validate(dict(VALUE,value=value))


@pytest.mark.parametrize('patch',[{'value':None},{'drill_key':None},{'unavailable_reason':'absent'}])
def test_value_and_provenance_cohere(schema,patch):
    with pytest.raises(ValidationError): validator(schema,'ImpactValue').validate(dict(VALUE,**patch))


def test_absent_not_zero(schema):
    absent=dict(value=None,unavailable_reason='absent',drill_key=None)
    row=dict(MONEY,before=absent,after=dict(VALUE,value='0.00'),delta=None)
    validator(schema,'ImpactMoneyChange').validate(row)
    for patch in [{'delta':'0.00'},{'before':dict(absent,unavailable_reason=None)}]:
        with pytest.raises(ValidationError): validator(schema,'ImpactMoneyChange').validate(dict(row,**patch))
    with pytest.raises(ValidationError): validator(schema,'ImpactMoneyChange').validate(dict(MONEY,delta=None))


@pytest.mark.parametrize('patch',[{'measure':'actual'},{'statement':None},{'line_key':None},
                                  {'entity_id':'entity_1'},{'account_id':'account_1'}])
def test_statement_grain(schema,patch):
    with pytest.raises(ValidationError): validator(schema,'ImpactMoneyChange').validate(dict(MONEY,**patch))


@pytest.mark.parametrize('patch',[{'measure':'amount'},{'statement':'pl'},{'line_key':'rev'},
                                  {'entity_id':None},{'account_id':None}])
def test_bva_grain(schema,patch):
    with pytest.raises(ValidationError): validator(schema,'ImpactMoneyChange').validate(dict(BVA,**patch))


@pytest.mark.parametrize('change',['added','removed','changed'])
def test_finding_sides(schema,change):
    row=dict(FINDING,change=change)
    if change!='added': row.update(before_finding_id='finding_old',before_sha256='c'*64)
    if change=='removed': row.update(after_finding_id=None,after_sha256=None)
    validator(schema,'ImpactFindingChange').validate(row)
    changed=dict(row,before_sha256=None) if change!='added' else dict(row,before_sha256='e'*64)
    with pytest.raises(ValidationError): validator(schema,'ImpactFindingChange').validate(changed)


@pytest.mark.parametrize('patch',[{'period_status':'locked'},{'period_status':'open'},
                                  {'baseline':None},{'current_impact_id':None}])
def test_history_not_current_permission(schema,patch):
    with pytest.raises(ValidationError): validator(schema,'RestatementState').validate(dict(STATE,**patch))


def test_null_and_historical_contexts(schema):
    for status in ['open','locked','closing']:
        validator(schema,'RestatementState').validate(dict(STATE,period_status=status,current_impact_id=None,current_approval_id=None))
    validator(schema,'RestatementState').validate(dict(STATE,baseline=None,current_impact_id=None,current_approval_id=None))


@pytest.mark.parametrize('patch',[{'limit':0},{'limit':1001},{'limit':True},{'kind':'all'},
                                  {'sort':'arbitrary_sql'},{'cursor':''},{'cursor':None}])
def test_invalid_query(schema,patch):
    with pytest.raises(ValidationError): validator(schema,'ImpactChangeQuery').validate(patch)


def test_paging_bounds(schema):
    for q in [{},{'limit':1},{'limit':1000,'kind':'bva'}]: validator(schema,'ImpactChangeQuery').validate(q)
    with pytest.raises(ValidationError):
        validator(schema,'ImpactChangePage').validate(dict(items=[FORECAST]*1001,next_cursor=None))


@pytest.mark.parametrize('guard',GUARDS)
def test_each_currentness_leg(schema,guard):
    assert not model_current({g:g!=guard for g in GUARDS},schema['x-impact-policy'])


@pytest.mark.parametrize('field',['project_id','period_id','period_version','impact_id','baseline_id',
    'before_snapshot_id','after_snapshot_id','before_manifest_sha256','after_manifest_sha256','changes_sha256'])
def test_approval_binding_negative_controls(field):
    assert bindings_valid(APPROVAL,REPORT)
    assert not bindings_valid(dict(APPROVAL,**{field:'different'}),REPORT)


def test_three_mutations_caught(schema):
    mutations=[]
    s=copy.deepcopy(schema); s['$defs']['ImpactForecastChange']['properties']['change']['const']='fresh';mutations.append(s)
    s=copy.deepcopy(schema); s['x-impact-policy']['current_report_guards'].remove('same_cycle');mutations.append(s)
    s=copy.deepcopy(schema); s['$defs']['ImpactCreate']['properties']['expected_version']['minimum']=3;mutations.append(s)
    for s in mutations:
        with pytest.raises((AssertionError,ValidationError)): assert_oracles(s)


def test_route_metadata_and_doc_parity(schema):
    doc=(ROOT/'docs/05_API_CONTRACT.md').read_text()
    index=(ROOT/'docs/90_API_PAYLOAD_SCHEMAS_DETAILED.md').read_text()
    assert set(schema['x-impact-endpoints'])==set(ROUTES)
    for route,(request,response,status,key,query) in ROUTES.items():
        actual=schema['x-impact-endpoints'][route]
        assert (actual['request'],actual['response'],actual['status'],actual['idempotency'],actual['query']) == (request,response,status,key,query)
        assert actual['scope']=='project' and actual['token_required'] is True
        method,path=route.split(' ',1)
        section=doc.split(f'{method} `{path}`',1)[1].split('\n### ',1)[0]
        assert response in section
        failure_line=next(x for x in section.splitlines() if x.startswith('- **Failures:**'))
        errors=set(re.findall(r'ERR-(\d{3})',failure_line))
        assert errors=={c for codes in actual['errors'].values() for c in codes}
        for http,codes in actual['errors'].items():
            # Independent normative global transport table, not another metadata copy.
            line=next(x for x in doc.splitlines() if x.startswith(f'| {http} |'))
            assert all(f'ERR-{c}' in line for c in codes)
    assert all(name in index for name in NAMES)
    Draft202012Validator.check_schema(schema)


def test_cookbook_examples(schema):
    doc=(ROOT/'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text().split('## 11. Restatement impact',1)[1]
    examples=re.findall(r'<!-- schema: (\w+) -->\n```json\n(.*?)\n```',doc,re.S)
    assert {name for name,_ in examples} >= {'RestatementState','ImpactCreate','ImpactReport','ImpactChangePage','ImpactApprovalCreate','ImpactApproval'}
    for name,body in examples: validator(schema,name).validate(json.loads(body))


def test_canonical_empty_and_identity_oracle():
    assert hashlib.sha256(canonical([])).hexdigest()=='4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'
    assert canonical(['bva','entity_1','account_rev',None,'actual']) == b'["bva","entity_1","account_rev",null,"actual"]'
    assert canonical(['statement','pl','rev']) == b'["statement","pl","rev"]'



def cookbook_objects():
    text=(ROOT/'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text().split('## 11. Restatement impact',1)[1]
    return {name:json.loads(body) for name,body in re.findall(r'<!-- schema: (\w+) -->\n```json\n(.*?)\n```',text,re.S)}


def detail_errors(report,rows):
    """Independent contextual checker for DOCUMENT fixtures, no DB access or money engine."""
    errors=[]
    identities=[]
    for row in rows:
        kind=row['kind']
        if kind=='statement': identity=[kind,row['statement'],row['line_key']]
        elif kind=='bva': identity=[kind,row['entity_id'],row['account_id'],row['cost_centre_id'],row['measure']]
        elif kind=='finding': identity=[kind,row['finding_key']]
        elif kind=='forecast': identity=[kind,row['run_id']]
        else: identity=[kind,row['report_id']]
        key=hashlib.sha256(canonical(identity)).hexdigest()
        if key!=row['key']: errors.append('key')
        identities.append((kind,row['key']))
    if identities!=sorted(set(identities)): errors.append('order/duplicates')
    if {k:sum(r['kind']==k for r in rows) for k in report['counts']}!=report['counts']:errors.append('counts')
    if hashlib.sha256(canonical(rows)).hexdigest()!=report['changes_sha256']:errors.append('hash')
    return errors


def test_complete_cookbook_identity_hash_count_and_binding_oracle():
    ex=cookbook_objects(); rows=ex['ImpactChangePage']['items']; report=ex['ImpactReport']
    assert not detail_errors(report,rows)
    assert report['changes_sha256']=='ea4dcc1c58bfceee6c0cce5852eadef0feea058032782c46d8f0050f86a8ecaa'
    assert bindings_valid(ex['ImpactApproval'],report)
    assert report['before_snapshot']==ex['RestatementState']['baseline']['before_snapshot']
    # Hand-worked doc-41 oracle: no recomputation/rounding with floats in these tests.
    money={(r['kind'],r['measure']):(r['before']['value'],r['after']['value'],r['delta']) for r in rows if r['kind'] in ['statement','bva']}
    assert money=={('statement','amount'):('100.00','125.00','25.00'),
                   ('bva','actual'):('100.00','125.00','25.00'),
                   ('bva','var_abs'):('20.00','45.00','25.00')}


@pytest.mark.parametrize('fault',['order','duplicate','key','same_count_changed_identity','count','hash'])
def test_detail_context_negative_controls(fault):
    ex=cookbook_objects();rows=ex['ImpactChangePage']['items'];report=ex['ImpactReport']
    if fault=='order': rows.reverse()
    elif fault=='duplicate':rows.append(copy.deepcopy(rows[0]))
    elif fault=='key':rows[0]['key']='0'*64
    elif fault=='same_count_changed_identity':rows[0]['account_id']='another_account'
    elif fault=='count':report['counts']['statement']+=1
    elif fault=='hash':report['changes_sha256']='0'*64
    assert detail_errors(report,rows)


def test_no_financial_invalidation_cycle_or_version_bump(schema):
    p=schema['x-impact-policy']
    assert p['generation_changes_financial_inputs'] is False
    assert p['approval_changes_financial_inputs'] is False
    assert p['financial_mutation_invalidates_permanently'] is True
    assert p['period_version_increment']==0
    assert p.get('current_record_order')=='project_audit_append', 'DEC-021 durable current-record order missing'
    assert p['approval_binding_fields']==['project_id','period_id','period_version','impact_id','baseline_id',
        'before_snapshot_id','after_snapshot_id','before_manifest_sha256','after_manifest_sha256','changes_sha256']


def test_empty_report_and_large_counts_are_not_approval(schema):
    report=dict(REPORT,counts={k:0 for k in REPORT['counts']},changes_sha256=hashlib.sha256(canonical([])).hexdigest())
    validator(schema,'ImpactReport').validate(report)
    assert not detail_errors(report,[])
    assert not model_current(dict.fromkeys(GUARDS,False),schema['x-impact-policy'])
    # Counts/schema posture only, not a 250k-row generation or perf test.
    validator(schema,'ImpactCounts').validate(dict(report['counts'],bva=250000))


@pytest.mark.parametrize('field',['statement','bva','finding','forecast','report'])
@pytest.mark.parametrize('value',[-1,True,1.5,'1'])
def test_counts_are_nonnegative_integers(schema,field,value):
    with pytest.raises(ValidationError):validator(schema,'ImpactCounts').validate(dict(REPORT['counts'],**{field:value}))



def test_labelled_unavailable_comparator_and_month_two(schema):
    missing=dict(value=None,unavailable_reason='not_available',drill_key=None)
    validator(schema,'ImpactMoneyChange').validate(dict(BVA,before=missing,delta=None))
    for name in ['RestatementBaseline','ImpactReport','ImpactApproval']:
        value=dict(EXAMPLES[name],period_id='2026-P02')
        if name=='ImpactApproval':value['attestation_text']='I reviewed the restatement impact for 2026-P02 and approve these changes'
        validator(schema,name).validate(value)
    for delta in [25,25.5,'25,00','2.5e1']:
        with pytest.raises(ValidationError):validator(schema,'ImpactMoneyChange').validate(dict(MONEY,delta=delta))
