"""DEC-020 document/schema/model oracles; NOT HTTP or financial guard implementation."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

import pytest
from jsonschema import ValidationError
from test_api_job_contract import validator
from test_api_project_contract import PERIOD, PID, AT

ROOT = Path(__file__).resolve().parents[2]
CODES = sorted(['audit_integrity', 'busy', 'period_state', 'no_gl', 'trial_balance', 'tb_tie_out',
                'reconciliations', 'statements_review', 'material_variances', 'rules', 'high_findings',
                'aged_corrections', 'forecast', 'board_pack', 'manual_tasks', 'restatement_review'])
SOFT = ['high_findings', 'manual_tasks']
EMPTY_FINGERPRINT = '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'
AFTER_TOKEN = '03b75d6416cd895a4dcd3a50cab9dd50af6373ca24789b43c73d4aa00ea93f5c'
TOKEN = '4dae58139f4db3910d02eec2df87b14fab580f74a6a7df512b13fee454c6a0eb'
REVIEW = dict(project_id=PID, period_id='2026-P01', period_version=2, audit_head='a'*64,
              snapshot_id='snapshot_close_1', blocker_fingerprint=EMPTY_FINGERPRINT)
SNAPSHOT = dict(snapshot_id='snapshot_close_1', batch_watermark='d'*64,
                budget_version='budget_1', forecast_run_id='forecast_1', layer='gl')
EVIDENCE = dict(review=REVIEW, snapshot=SNAPSHOT, override_note=None, overridden_blockers=[])
SIGNOFF = dict(signoff_id='signoff_1', project_id=PID, period_id='2026-P01', signer='Controller',
               attestation_text='I confirm the pack for 2026-P01 is complete and reviewed', at=AT, evidence=EVIDENCE)
CREATE = dict(period_id='2026-P01', expected_version=2, review_token=TOKEN, signer='Controller',
              attest=True, override_note=None)
READY = dict(review=REVIEW, review_token=TOKEN, period_status='closing', blockers=[],
             current_signoff=None, ready_to_sign_off=True, ready_to_lock=False)
LOCK = dict(expected_version=2, review_token=AFTER_TOKEN, signoff_id='signoff_1', force=False, note=None)
LOCKED = dict(PERIOD, status='locked', version=3, locked_at=AT)
LEGACY_LOCKED = dict(LOCKED, version=2)
FLAGS = dict(latest_project_audit=True, same_period_version=True, same_snapshot=True, same_blocker_fingerprint=True)
ROUTES = {
    'GET /projects/{id}/periods/{period_id}/close-readiness': (None, 'CloseReadiness', '200', 'none'),
    'POST /close/sign-off': ('CloseSignoffCreate', 'CloseSignoff', '201', 'required'),
    'POST /projects/{id}/periods/{period_id}/lock': ('PeriodLock', 'LockedPeriod', '200', 'required'),
}


@pytest.fixture
def schema():
    s = json.loads((ROOT/'docs/api_job_schemas.json').read_text())
    names = {'CloseBlockerCode', 'CloseBlocker', 'CloseReview', 'CloseSignoffEvidence', 'CloseSignoff',
             'CloseReadiness', 'CloseSignoffCreate', 'PeriodLock', 'LockedPeriod'}
    assert names <= s['$defs'].keys(), 'DEC-020 close definitions missing'
    assert 'x-close-endpoints' in s and 'x-close-policy' in s, 'DEC-020 metadata missing'
    return s


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def review_token(review):
    return hashlib.sha256(b'FPA-CLOSE-REVIEW-v1\n'+canonical(review)).hexdigest()


def fingerprint(pairs):
    return hashlib.sha256(canonical(sorted(set(pairs)))).hexdigest()


def model_lock_allowed(codes, flags, policy, force=False, note=None, override=False):
    """Interpret the declared guard policy over synthetic facts; no DB/engine evaluation."""
    if not all(flags[k] for k in policy['current_signoff_guards']):
        return False
    if set(codes) - set(policy['overridable_codes']):
        return False
    if codes and not override:
        return False
    if 'high_findings' in codes and not (force and note and note.strip()):
        return False
    return True


def signoff_errors(record):
    e = record['evidence']; r = e['review']; errors = []
    if record['project_id'] != r['project_id'] or record['period_id'] != r['period_id']:
        errors.append('scope')
    if e['snapshot']['snapshot_id'] != r['snapshot_id']:
        errors.append('snapshot')
    expected = f"I confirm the pack for {record['period_id']} is complete and reviewed"
    if record['attestation_text'] != expected:
        errors.append('attestation')
    codes = [x['code'] for x in e['overridden_blockers']]
    if codes != sorted(set(codes)) or set(codes)-set(SOFT):
        errors.append('overrides')
    if codes and not e['override_note']:
        errors.append('override note')
    return errors


def readiness_errors(value):
    errors = []
    codes = [x['code'] for x in value['blockers']]
    if codes != sorted(set(codes)):
        errors.append('blocker order/uniqueness')
    if any(x['overridable'] != (x['code'] in SOFT) for x in value['blockers']):
        errors.append('override classification')
    if review_token(value['review']) != value['review_token']:
        errors.append('review token')
    base = value['period_status'] == 'closing' and value['review']['snapshot_id'] is not None
    if value['ready_to_sign_off'] != bool(base and not codes):
        errors.append('signoff readiness')
    signoff = value['current_signoff']
    if signoff:
        if value['period_status'] != 'closing':
            errors.append('historical signoff not current')
        old = signoff['evidence']['review']
        if any(old[k] != value['review'][k] for k in ['project_id', 'period_id', 'period_version', 'snapshot_id', 'blocker_fingerprint']):
            errors.append('current signoff binding')
    overridden = set() if signoff is None else {x['code'] for x in signoff['evidence']['overridden_blockers']}
    can_lock = bool(base and signoff and set(codes) <= (overridden & {'manual_tasks'}))
    if value['ready_to_lock'] != can_lock:
        errors.append('lock readiness')
    return errors


def assert_oracles(s):
    for name, value in [('CloseReview', REVIEW), ('CloseSignoffEvidence', EVIDENCE), ('CloseSignoff', SIGNOFF),
                        ('CloseReadiness', READY), ('CloseSignoffCreate', CREATE), ('PeriodLock', LOCK),
                        ('LockedPeriod', LOCKED), ('LockedPeriod', LEGACY_LOCKED)]:
        validator(s, name).validate(value)
    assert not signoff_errors(SIGNOFF) and not readiness_errors(READY)
    p = s['x-close-policy']
    assert model_lock_allowed([], FLAGS, p)
    for guard in FLAGS:
        assert not model_lock_allowed([], dict(FLAGS, **{guard: False}), p), guard
    for code in set(CODES)-set(SOFT):
        assert not model_lock_allowed([code], FLAGS, p, force=True, note='Approved', override=True), code


def test_independent_oracles(schema):
    assert_oracles(schema)


@pytest.mark.parametrize('name,value', [('CloseReview', REVIEW), ('CloseSignoffEvidence', EVIDENCE),
    ('CloseSignoff', SIGNOFF), ('CloseReadiness', READY), ('CloseSignoffCreate', CREATE),
    ('PeriodLock', LOCK), ('LockedPeriod', LOCKED)])
def test_missing_and_invented_fields(schema, name, value):
    for field in value:
        payload = dict(value); del payload[field]
        with pytest.raises(ValidationError):
            validator(schema, name).validate(payload)
    with pytest.raises(ValidationError):
        validator(schema, name).validate(dict(value, actor='forged'))


@pytest.mark.parametrize('code', CODES)
def test_every_blocker_classification(schema, code):
    value = dict(code=code, count=1, overridable=code in SOFT)
    validator(schema, 'CloseBlocker').validate(value)
    with pytest.raises(ValidationError):
        validator(schema, 'CloseBlocker').validate(dict(value, overridable=not value['overridable']))
    with pytest.raises(ValidationError):
        validator(schema, 'CloseBlocker').validate(dict(value, count=0))


@pytest.mark.parametrize('code', sorted(set(CODES)-set(SOFT)))
def test_force_never_bypasses_hard_blockers(schema, code):
    assert not model_lock_allowed([code], FLAGS, schema['x-close-policy'], force=True, note='Approved', override=True)


@pytest.mark.parametrize('force,note,override,expected', [
    (False, None, False, False), (True, 'Approved', False, False), (False, None, True, False),
    (True, None, True, False), (True, '  ', True, False), (True, 'Approved', True, True)])
def test_high_finding_force_needs_both_signoff_and_note(schema, force, note, override, expected):
    assert model_lock_allowed(['high_findings'], FLAGS, schema['x-close-policy'], force, note, override) is expected


@pytest.mark.parametrize('guard', list(FLAGS))
def test_each_current_signoff_guard(schema, guard):
    assert not model_lock_allowed([], dict(FLAGS, **{guard: False}), schema['x-close-policy'])


def test_acyclic_prerequisites_and_policy(schema):
    p = schema['x-close-policy']
    assert p['prerequisite_tasks'] == [f'T-{i:02}' for i in range(1, 9)]
    assert p['outcome_tasks'] == ['T-09', 'T-10']
    assert not set(p['outcome_tasks']) & set(p['prerequisite_tasks'])
    assert p['overridable_codes'] == SOFT
    assert p['current_signoff_guards'] == list(FLAGS)
    assert model_lock_allowed(['manual_tasks'], FLAGS, p, override=True)
    assert not model_lock_allowed(['manual_tasks'], FLAGS, p)


def test_canonical_golden_token_and_order():
    assert fingerprint([]) == EMPTY_FINGERPRINT
    assert review_token(dict(REVIEW, audit_head='c'*64)) == AFTER_TOKEN
    assert review_token(REVIEW) == TOKEN  # Literal from separately authored canonical byte vector.
    assert review_token(dict(reversed(list(REVIEW.items())))) == TOKEN
    assert fingerprint([('high_findings', 'f2'), ('high_findings', 'f1'), ('high_findings', 'f1')]) == fingerprint([('high_findings', 'f1'), ('high_findings', 'f2')])
    assert fingerprint([('high_findings', 'f1')]) != fingerprint([('high_findings', 'f2')])


@pytest.mark.parametrize('field,value', [('project_id', 'prj_000000000001'), ('period_id', '2026-P02'),
    ('period_version', 3), ('audit_head', 'c'*64), ('snapshot_id', 'snapshot_close_2'),
    ('blocker_fingerprint', 'f'*64)])
def test_each_review_component_invalidates_token(field, value):
    assert review_token(dict(REVIEW, **{field: value})) != TOKEN


@pytest.mark.parametrize('name', ['CloseSignoffCreate', 'PeriodLock'])
@pytest.mark.parametrize('version', [0, -1, True, '2', 1.5])
def test_bad_expected_version(schema, name, version):
    base = CREATE if name == 'CloseSignoffCreate' else LOCK
    with pytest.raises(ValidationError):
        validator(schema, name).validate(dict(base, expected_version=version))


@pytest.mark.parametrize('value', [False, 1, 'true', None])
def test_attestation_is_explicit_boolean_true(schema, value):
    with pytest.raises(ValidationError):
        validator(schema, 'CloseSignoffCreate').validate(dict(CREATE, attest=value))


@pytest.mark.parametrize('note', [None, '', ' ', '\n', 'x'*501, True])
def test_force_needs_valid_note_shape(schema, note):
    with pytest.raises(ValidationError):
        validator(schema, 'PeriodLock').validate(dict(LOCK, force=True, note=note))


@pytest.mark.parametrize('note', ['Approved', 'x'*500, '批准', '<script>text</script>', '=SUM(A1:A2)'])
def test_notes_are_literal_data(schema, note):
    validator(schema, 'PeriodLock').validate(dict(LOCK, force=True, note=note))


def test_no_raw_financial_or_completed_task_injection(schema):
    for name, payload in [('CloseSignoffCreate', CREATE), ('PeriodLock', LOCK)]:
        for field in ['snapshot', 'amount_minor', 'completed_tasks', 'impact_approved', 'actor', 'locked_at']:
            with pytest.raises(ValidationError):
                validator(schema, name).validate(dict(payload, **{field: True}))


def test_relational_negative_controls(schema):
    changed = copy.deepcopy(SIGNOFF); changed['evidence']['snapshot']['snapshot_id'] = 'other'
    validator(schema, 'CloseSignoff').validate(changed)
    assert signoff_errors(changed) == ['snapshot']
    assert signoff_errors(dict(SIGNOFF, period_id='2026-P02')) == ['scope', 'attestation']
    assert signoff_errors(dict(SIGNOFF, attestation_text='AI approves')) == ['attestation']
    assert readiness_errors(dict(READY, ready_to_lock=True)) == ['lock readiness']
    assert readiness_errors(dict(READY, review_token='f'*64)) == ['review token']
    assert 'signoff readiness' in readiness_errors(dict(READY, period_status='open'))
    row = dict(code='manual_tasks', count=1, overridable=True)
    assert 'blocker order/uniqueness' in readiness_errors(dict(READY, blockers=[row, row]))


def test_three_mutations_caught(schema):
    changed = copy.deepcopy(schema)
    changed['$defs']['LockedPeriod']['allOf'][1]['properties']['status']['const'] = 'open'
    with pytest.raises(ValidationError):
        assert_oracles(changed)
    changed = copy.deepcopy(schema)
    changed['x-close-policy']['current_signoff_guards'].remove('same_snapshot')
    with pytest.raises(AssertionError, match='same_snapshot'):
        assert_oracles(changed)
    changed = copy.deepcopy(schema)
    changed['$defs']['LockedPeriod']['allOf'][1]['properties']['version']['minimum'] = 3
    with pytest.raises(ValidationError):
        assert_oracles(changed)


def test_high_error_cannot_claim_zero_findings(schema):
    v = validator(schema, 'ErrorDetails011')
    v.validate({'n': 1, 'finding_ids': ['finding_1']})
    v.validate({'n': 250000, 'finding_ids': [f'finding_{i:06}' for i in range(100)]})
    for value in [{'n': 0, 'finding_ids': []}, {'n': 1, 'finding_ids': []},
                  {'n': 101, 'finding_ids': [f'f{i}' for i in range(101)]}]:
        with pytest.raises(ValidationError):
            v.validate(value)
    example = schema['x-error-examples']['FP&A-ERR-011']
    assert example['details']['n'] >= 1 and len(example['details']['finding_ids']) >= 1


def test_bounded_blockers_and_override_records(schema):
    with pytest.raises(ValidationError):
        validator(schema, 'CloseReadiness').validate(dict(READY, blockers=[dict(code='busy', count=1, overridable=False)]*17))
    e = copy.deepcopy(EVIDENCE)
    e['overridden_blockers'] = [dict(code='trial_balance', count=1, overridable=False)]
    e['override_note'] = 'Approved'
    with pytest.raises(ValidationError):
        validator(schema, 'CloseSignoffEvidence').validate(e)
    e['overridden_blockers'] = [dict(code='high_findings', count=1, overridable=True)]
    validator(schema, 'CloseSignoffEvidence').validate(e)
    e['override_note'] = None
    with pytest.raises(ValidationError):
        validator(schema, 'CloseSignoffEvidence').validate(e)


def test_routes_and_owner_blocker_table(schema):
    text = (ROOT/'docs/05_API_CONTRACT.md').read_text().split('## 8. Close readiness', 1)[1]
    entries = re.findall(r'^### 8\.\d+ (GET|POST) `([^`]+)`\n(.*?)(?=^### |\Z)', text, re.M|re.S)
    registry = schema['x-close-endpoints']
    assert set(registry) == set(ROUTES) == {f'{m} {p}' for m,p,_ in entries}
    for method, path, body in entries:
        entry = registry[f'{method} {path}']
        assert (entry['request'], entry['response'], entry['status'], entry['idempotency']) == ROUTES[f'{method} {path}']
        assert entry['scope'] == 'project' and entry['token_required'] and entry['query'] is None
        for label in ['Auth / scope', 'Request', 'Response', 'Failures', 'Pagination', 'Idempotency', 'Example']:
            assert '**'+label+':**' in body
        line = body.split('**Failures:**')[1].split('\n')[0]
        parsed = {status: re.findall(r'ERR-(\d{3})', tail) for status,tail in re.findall(r'(\d{3}) ([^;]+)', line)}
        assert parsed == entry['errors']
        full_contract = (ROOT/'docs/05_API_CONTRACT.md').read_text()
        for status, codes in parsed.items():
            mapping = next(line for line in full_contract.splitlines() if line.startswith('| '+status+' |'))
            for code in codes:
                assert 'ERR-'+code in mapping
                validator(schema, 'Error'+code).validate(schema['x-error-examples']['FP&A-ERR-'+code])
    owner = (ROOT/'docs/30_CLOSE_MANAGEMENT_SPEC.md').read_text().split('## 6.')[1].split('## 7.')[0]
    rows = re.findall(r'^\| (\w+) \| .*? \| (yes|no) \|$', owner, re.M)
    assert sorted(k for k,_ in rows) == CODES
    assert sorted(k for k,v in rows if v == 'yes') == SOFT


def test_cookbook(schema):
    text = (ROOT/'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text().split('## 10.', 1)
    assert len(text) == 2, 'Complete close examples missing'
    blocks = re.findall(r'<!-- contract: (\w+) -->\n```json\n(.*?)\n```', text[1], re.S)
    assert {n for n,_ in blocks} >= {'CloseReadiness','CloseSignoffCreate','CloseSignoff','PeriodLock','LockedPeriod'}
    signed = None
    for name, body in blocks:
        example = json.loads(body); validator(schema, name).validate(example)
        if name == 'CloseReadiness':
            assert not readiness_errors(example)
        elif name == 'CloseSignoff':
            assert example == SIGNOFF and not signoff_errors(example); signed = example
        elif name == 'PeriodLock':
            assert example == LOCK
            assert signed and example['signoff_id'] == signed['signoff_id']
            assert example['review_token'] != TOKEN, 'Must refresh review after sign-off changes audit head'


def lock_input_error(payload):
    # Special ERR-015 selection, not a production request parser.
    if not isinstance(payload, dict) or payload.keys()-{'expected_version','review_token','signoff_id','force','note'}:
        return '002'
    if type(payload.get('expected_version')) is not int or payload['expected_version'] < 1:
        return '002'
    if type(payload.get('force')) is not bool or not isinstance(payload.get('signoff_id'), str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}',payload['signoff_id']):
        return '002'
    if not isinstance(payload.get('review_token'), str) or not re.fullmatch('[0-9a-f]{64}', payload['review_token']):
        return '002'
    if 'note' not in payload:
        return '015' if payload['force'] else '002'
    note = payload['note']
    if note is None:
        return '015' if payload['force'] else None
    if not isinstance(note, str) or len(note)>500 or any(ord(c)<32 or ord(c)==127 for c in note):
        return '002'
    if not note.strip():
        return '015' if payload['force'] else '002'
    return None


@pytest.mark.parametrize('patch,code', [({'force':True,'note':None},'015'), ({'force':True,'note':''},'015'),
    ({'force':True,'note':' '},'015'), ({'force':True,'note':'\n'},'002'), ({'force':True,'note':True},'002'),
    ({'force':True,'note':'x'*501},'002'), ({'force':False,'note':''},'002'),
    ({'force':True,'expected_version':True},'002'), ({'force':True,'note':'approved','actor':'forged'},'002'),
    ({'force':True,'note':'approved'},None), ({'force':False,'note':None},None)])
def test_lock_note_error_precedence(schema, patch, code):
    value = dict(LOCK, **patch)
    assert lock_input_error(value) == code
    if code:
        with pytest.raises(ValidationError):
            validator(schema, 'PeriodLock').validate(value)
    else:
        validator(schema, 'PeriodLock').validate(value)


def test_missing_lock_note_priority(schema):
    value = dict(LOCK); del value['note']
    assert lock_input_error(value) == '002'
    value['force'] = True
    assert lock_input_error(value) == '015'
    with pytest.raises(ValidationError):
        validator(schema, 'PeriodLock').validate(value)


@pytest.mark.parametrize('patch', [{'ready_to_lock':True}, {'period_status':'open'},
                                  {'period_status':'locked'}, {'blockers':[{'code':'busy','count':1,'overridable':False}]}])
def test_ready_flags_cannot_lie_about_static_prerequisites(schema, patch):
    with pytest.raises(ValidationError):
        validator(schema, 'CloseReadiness').validate(dict(READY, **patch))


def test_duplicate_codes_cannot_hide_behind_different_counts(schema):
    a = dict(code='manual_tasks',count=1,overridable=True)
    b = dict(a,count=2)
    with pytest.raises(ValidationError):
        validator(schema, 'CloseReadiness').validate(dict(READY, ready_to_sign_off=False, blockers=[a,b]))
    with pytest.raises(ValidationError):
        validator(schema, 'CloseSignoffEvidence').validate(dict(EVIDENCE, override_note='Reviewed',overridden_blockers=[a,b]))


def test_locked_readiness_does_not_reauthorise_historical_signoff(schema):
    data = dict(READY,period_status='locked',ready_to_sign_off=False,current_signoff=SIGNOFF)
    assert 'historical signoff not current' in readiness_errors(data)
    with pytest.raises(ValidationError):
        validator(schema,'CloseReadiness').validate(data)


def test_current_signoff_binding_negative_control():
    r = dict(REVIEW, audit_head='c'*64)
    data = dict(READY,review=r,review_token=AFTER_TOKEN,current_signoff=SIGNOFF,ready_to_lock=True)
    assert not readiness_errors(data)
    changed = copy.deepcopy(data); changed['current_signoff']['evidence']['review']['snapshot_id']='old'
    assert 'current signoff binding' in readiness_errors(changed)


def test_lock_version_increment_oracle(schema):
    # Includes legacy closing/version-1 rows: first lock returns version 2, not a reset or minimum 3.
    for before,after in [(1,LEGACY_LOCKED),(2,LOCKED)]:
        validator(schema,'LockedPeriod').validate(after)
        assert after['version'] == before+1
        assert after['locked_at'] == after['updated_at'] == AT
        for key in ['project_id','period_id','fiscal_year','period_no','start_date','end_date','created_at']:
            assert after[key] == PERIOD[key]
