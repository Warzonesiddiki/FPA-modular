"""Doc-05 §7 contract oracles; no HTTP, filesystem, keyring or DB implementation."""
from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from jsonschema import ValidationError
from test_api_job_contract import validator
from test_api_project_contract import PROJECT, PERIOD, AT, PID, metadata_errors

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = dict(PROJECT, project_id='prj_9f2c41aa07e2', name='Sample Company', is_sample=True)
DELETE = {'expected_version': 1, 'confirmation': 'Meridian FY27'}
DELETED = {'project_id': PID, 'status': 'trashed', 'deleted_at': AT,
           'purge_after': '2026-11-13T09:00:00Z'}
START = {'expected_version': 1}
UNLOCK = {'expected_version': 3,
          'note': 'Re-import the corrected April ledger; approved by the controller.'}
CLOSING = dict(PERIOD, status='closing', version=2, updated_at='2026-10-14T09:00:01Z')
LOCKED = dict(PERIOD, status='locked', version=3, locked_at=AT, lock_note='Reviewed')
REOPENED = dict(CLOSING, version=4)
ROUTES = {
    'POST /projects/sample': ('app', 'SampleProjectCreate', 'CreatedSampleProject', '201', 'required'),
    'DELETE /projects/{id}': ('project', 'ProjectDelete', 'ProjectDeleted', '200', 'required'),
    'POST /projects/{id}/periods/{period_id}/start-close':
        ('project', 'PeriodStartClose', 'ClosingPeriod', '200', 'optional'),
    'POST /projects/{id}/periods/{period_id}/unlock':
        ('project', 'PeriodUnlock', 'ClosingPeriod', '200', 'optional'),
}


@pytest.fixture
def schema():
    s = json.loads((ROOT / 'docs/api_job_schemas.json').read_text())
    needed = {'SampleProjectCreate', 'CreatedSampleProject', 'ProjectDelete', 'ProjectDeleted',
              'PeriodStartClose', 'PeriodUnlock', 'ClosingPeriod'}
    assert needed <= s['$defs'].keys(), 'DEC-018 lifecycle DTOs missing'
    assert 'x-lifecycle-endpoints' in s, 'DEC-018 lifecycle endpoints missing'
    return s


def transition_errors(before, after, action):
    """Relational oracle for example payloads, NOT a workflow implementation."""
    errors = []
    source = {'start_close': 'open', 'unlock': 'locked'}[action]
    if before['status'] != source or after['status'] != 'closing':
        errors.append('transition')
    if after['version'] != before['version'] + 1:
        errors.append('revision')
    unchanged = {'project_id', 'period_id', 'fiscal_year', 'period_no', 'start_date', 'end_date', 'created_at'}
    if any(before[k] != after[k] for k in unchanged):
        errors.append('identity or calendar changed')
    if after['locked_at'] is not None or after['lock_note'] is not None:
        errors.append('current lock metadata')
    if datetime.fromisoformat(after['updated_at']) < datetime.fromisoformat(before['updated_at']):
        errors.append('timestamp order')
    return errors


def deletion_errors(receipt):
    deleted = datetime.fromisoformat(receipt['deleted_at'])
    purge = datetime.fromisoformat(receipt['purge_after'])
    return [] if purge - deleted == timedelta(days=30) else ['retention boundary']


def unlock_input_error(request):
    """Error-selection oracle from §7.0; JSON Schema alone has no error-code mapping."""
    if not isinstance(request, dict) or request.keys() - {'expected_version', 'note'}:
        return '002'
    version = request.get('expected_version')
    if type(version) is not int or version < 1:
        return '002'
    note = request.get('note')
    if note is None:
        return '015'
    if not isinstance(note, str) or len(note) > 500 or any(ord(c) < 32 or ord(c) == 127 for c in note):
        return '002'
    return '015' if not note.strip() else None


def assert_lifecycle_oracles(s):
    pairs = [('SampleProjectCreate', {'name': 'Sample Company'}), ('CreatedSampleProject', SAMPLE),
             ('ProjectDelete', DELETE), ('ProjectDeleted', DELETED), ('PeriodStartClose', START),
             ('PeriodUnlock', UNLOCK), ('ClosingPeriod', CLOSING), ('ClosingPeriod', REOPENED)]
    for name, value in pairs:
        validator(s, name).validate(value)
    assert not sample_errors(SAMPLE)
    assert not transition_errors(PERIOD, CLOSING, 'start_close')
    assert not transition_errors(LOCKED, REOPENED, 'unlock')
    assert not deletion_errors(DELETED)
    with pytest.raises(ValidationError):
        validator(s, 'ClosingPeriod').validate(PERIOD)
    with pytest.raises(ValidationError):
        validator(s, 'PeriodUnlock').validate(dict(UNLOCK, note='x' * 501))


def test_independent_lifecycle_oracles(schema):
    assert_lifecycle_oracles(schema)


@pytest.mark.parametrize('name,value', [
    ('SampleProjectCreate', {'name': 'Sample Company'}), ('CreatedSampleProject', SAMPLE),
    ('ProjectDelete', DELETE), ('ProjectDeleted', DELETED), ('PeriodStartClose', START),
    ('PeriodUnlock', UNLOCK), ('ClosingPeriod', CLOSING),
])
def test_every_required_field_and_unknown_field(schema, name, value):
    for field in value:
        changed = dict(value)
        del changed[field]
        with pytest.raises(ValidationError):
            validator(schema, name).validate(changed)
    with pytest.raises(ValidationError):
        validator(schema, name).validate(dict(value, actor='forged'))


@pytest.mark.parametrize('field,value', [('is_sample', True), ('project_id', PID), ('seed', 99),
    ('fiscal_year', 2026), ('base_currency', 'USD'), ('path', '/private'), ('client_secret', 'fake')])
def test_sample_create_cannot_choose_server_fields(schema, field, value):
    with pytest.raises(ValidationError):
        validator(schema, 'SampleProjectCreate').validate({'name': 'Sample Company', field: value})


@pytest.mark.parametrize('field,value', [('is_sample', False), ('version', 2), ('base_currency', 'USD'),
                                        ('fy_start_month', 1), ('calendar_type', '445')])
def test_sample_response_fixed_defaults(schema, field, value):
    with pytest.raises(ValidationError):
        validator(schema, 'CreatedSampleProject').validate(dict(SAMPLE, **{field: value}))


@pytest.mark.parametrize('name', ['ProjectDelete', 'PeriodStartClose', 'PeriodUnlock'])
@pytest.mark.parametrize('version', [0, -1, True, '1', 1.5])
def test_expected_version_is_positive_integer(schema, name, version):
    base = {'ProjectDelete': DELETE, 'PeriodStartClose': START, 'PeriodUnlock': UNLOCK}[name]
    with pytest.raises(ValidationError):
        validator(schema, name).validate(dict(base, expected_version=version))


@pytest.mark.parametrize('value', ['', 'meridian FY27', ' Meridian FY27', 'Meridian FY27 '])
def test_delete_confirmation_does_not_normalise(schema, value):
    # Wrong-but-well-shaped confirmation is the ERR-013 comparison, not ERR-002.
    request = dict(DELETE, confirmation=value)
    validator(schema, 'ProjectDelete').validate(request)
    assert request['confirmation'] != PROJECT['name']


@pytest.mark.parametrize('value', [None, True, 123, 'a' * 81])
def test_delete_confirmation_bad_type_or_length(schema, value):
    with pytest.raises(ValidationError):
        validator(schema, 'ProjectDelete').validate(dict(DELETE, confirmation=value))


@pytest.mark.parametrize('payload,code', [
    ({'expected_version': 3}, '015'), ({'expected_version': 3, 'note': None}, '015'),
    ({'expected_version': 3, 'note': ''}, '015'), ({'expected_version': 3, 'note': '   '}, '015'),
    ({'expected_version': 3, 'note': '\n'}, '002'), ({'expected_version': 3, 'note': True}, '002'),
    ({'expected_version': 3, 'note': 'x' * 501}, '002'),
    ({'expected_version': True, 'note': 'Approved'}, '002'),
    ({'expected_version': 3, 'note': 'Approved', 'force': True}, '002'), ({}, '002'),
    ({'expected_version': 3, 'note': 'Approved'}, None),
])
def test_unlock_error_selection_oracle(schema, payload, code):
    assert unlock_input_error(payload) == code
    if code:
        with pytest.raises(ValidationError):
            validator(schema, 'PeriodUnlock').validate(payload)
    else:
        validator(schema, 'PeriodUnlock').validate(payload)


@pytest.mark.parametrize('note', ['x', 'x' * 500, '批准更正', '<script>review</script>', '=SUM(A1:A2)'])
def test_notes_are_bounded_literal_data(schema, note):
    validator(schema, 'PeriodUnlock').validate(dict(UNLOCK, note=note))
    assert unlock_input_error(dict(UNLOCK, note=note)) is None


@pytest.mark.parametrize('action,before,after', [('start_close', PERIOD, CLOSING), ('unlock', LOCKED, REOPENED)])
def test_transition_relational_negative_controls(schema, action, before, after):
    assert not transition_errors(before, after, action)
    for changed, reason in [(dict(after, version=before['version']), 'revision'),
                            (dict(after, period_id='2026-P02'), 'identity or calendar changed'),
                            (dict(after, locked_at=AT), 'current lock metadata'),
                            (dict(after, updated_at='2020-01-01T00:00:00Z'), 'timestamp order')]:
        assert reason in transition_errors(before, changed, action)
    assert 'transition' in transition_errors(dict(before, status='closing'), after, action)
    for wrong in ['open', 'locked']:
        with pytest.raises(ValidationError):
            validator(schema, 'ClosingPeriod').validate(dict(after, status=wrong))


@pytest.mark.parametrize('deleted,purge', [('2026-10-14T09:00:00Z', '2026-11-13T09:00:00Z'),
    ('2024-01-31T23:59:59Z', '2024-03-01T23:59:59Z'),
    ('2024-02-01T00:00:00Z', '2024-03-02T00:00:00Z')])
def test_retention_utc_calendar_oracles(schema, deleted, purge):
    receipt = dict(DELETED, deleted_at=deleted, purge_after=purge)
    validator(schema, 'ProjectDeleted').validate(receipt)
    assert not deletion_errors(receipt)
    for seconds in [-1, 1]:
        changed = (datetime.fromisoformat(purge) + timedelta(seconds=seconds)).isoformat().replace('+00:00', 'Z')
        assert deletion_errors(dict(receipt, purge_after=changed)) == ['retention boundary']


def test_three_lifecycle_schema_mutations_are_caught(schema):
    changed = copy.deepcopy(schema)
    changed['$defs']['CreatedSampleProject']['allOf'][1]['properties']['is_sample']['const'] = False
    with pytest.raises(ValidationError):
        assert_lifecycle_oracles(changed)
    changed = copy.deepcopy(schema)
    del changed['$defs']['ClosingPeriod']['allOf'][1]['properties']['status']
    with pytest.raises(pytest.fail.Exception):
        assert_lifecycle_oracles(changed)
    changed = copy.deepcopy(schema)
    changed['$defs']['PeriodNote']['maxLength'] = 501
    with pytest.raises(pytest.fail.Exception):
        assert_lifecycle_oracles(changed)


def test_endpoint_catalogue_and_errors(schema):
    text = (ROOT / 'docs/05_API_CONTRACT.md').read_text()
    section = text.split('## 7. Sample,', 1)[1]
    matches = re.findall(r'^### 7\.\d+ (POST|DELETE) `([^`]+)`\n(.*?)(?=^### |\Z)', section, re.M | re.S)
    registry = schema['x-lifecycle-endpoints']
    assert {f'{method} {path}' for method, path, _ in matches} == set(ROUTES) == set(registry)
    for method, path, body in matches:
        route = registry[f'{method} {path}']
        assert (route['scope'], route['request'], route['response'], route['status'], route['idempotency']) == ROUTES[f'{method} {path}']
        assert route['token_required'] and route['query'] is None
        for label in ['Auth / scope', 'Request', 'Response', 'Failures', 'Pagination', 'Idempotency', 'Example']:
            assert f'**{label}:**' in body
        failures = body.split('**Failures:**', 1)[1].split('\n', 1)[0]
        actual = {status: re.findall(r'ERR-(\d{3})', tail)
                  for status, tail in re.findall(r'(\d{3}) ([^;]+)', failures)}
        assert actual == route['errors']
        for status, codes in actual.items():
            mapping = next(line for line in text.splitlines() if line.startswith('| ' + status + ' |'))
            for code in codes:
                assert 'ERR-' + code in mapping
                validator(schema, 'Error' + code).validate(schema['x-error-examples']['FP&A-ERR-' + code])


def test_lifecycle_cookbook(schema):
    text = (ROOT / 'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text().split('## 9.', 1)
    assert len(text) == 2, 'Complete lifecycle examples missing'
    blocks = re.findall(r'<!-- contract: (\w+) -->\n```json\n(.*?)\n```', text[1], re.S)
    assert {name for name, _ in blocks} >= {'SampleProjectCreate', 'CreatedSampleProject', 'ProjectDelete',
                                        'ProjectDeleted', 'PeriodStartClose', 'PeriodUnlock', 'ClosingPeriod'}
    closings = []
    for name, body in blocks:
        example = json.loads(body)
        validator(schema, name).validate(example)
        if name == 'CreatedSampleProject':
            assert example == SAMPLE
        elif name == 'ProjectDeleted':
            assert example == DELETED and not deletion_errors(example)
        elif name == 'ClosingPeriod':
            closings.append(example)
    assert closings == [CLOSING, REOPENED]


def test_period_mutations_declare_audit_integrity_guard(schema):
    for name in ['start-close', 'unlock']:
        endpoint = schema['x-lifecycle-endpoints'][f'POST /projects/{{id}}/periods/{{period_id}}/{name}']
        assert endpoint['errors'].get('422') == ['090'], 'Audit-broken project must remain read-only'


def test_launch_credential_location_contract_is_outside_projects():
    security = (ROOT / 'docs/12_SECURITY_PRIVACY.md').read_text()
    assert 'runtime file in the project folder' not in security, 'Launch credential would enter whole-folder backups'
    assert 'session.json' in security and 'outside every project' in security


def sample_errors(project):
    errors = metadata_errors(project)
    if project['created_at'] != project['updated_at']:
        errors.append('creation timestamps')
    return errors


def test_sample_and_retention_policy_oracles(schema):
    assert not sample_errors(SAMPLE)
    assert sample_errors(dict(SAMPLE, updated_at='2026-10-14T09:00:01Z')) == ['creation timestamps']
    policy = schema['x-lifecycle-policies']
    assert policy['sample_fiscal_years'] == [2024, 2025, 2026]
    assert policy['sample_financial_rows_preloaded'] is False
    assert policy['trash_retention_seconds'] == 30 * 24 * 60 * 60
    assert policy['period_transitions'] == {'start_close': {'from': 'open', 'to': 'closing'},
                                            'unlock': {'from': 'locked', 'to': 'closing'}}


@pytest.mark.parametrize('action,source', [('start_close', 'open'), ('unlock', 'locked')])
@pytest.mark.parametrize('state', ['open', 'closing', 'locked'])
def test_transition_oracle_all_source_states(action, source, state):
    before = dict(PERIOD, status=state)
    errors = transition_errors(before, CLOSING, action)
    assert ('transition' in errors) is (state != source)


@pytest.mark.parametrize('extra', [{'name': 'Meridian FY27'}, {'path': '../private'}, {'token': 'fake'}])
def test_deleted_receipt_does_not_expose_name_path_or_credential(schema, extra):
    assert set(schema['$defs']['ProjectDeleted']['properties']) == {'project_id', 'status', 'deleted_at', 'purge_after'}
    with pytest.raises(ValidationError):
        validator(schema, 'ProjectDeleted').validate(dict(DELETED, **extra))


def test_trash_is_not_claimed_as_permanent_erasure(schema):
    with pytest.raises(ValidationError):
        validator(schema, 'ProjectDeleted').validate(dict(DELETED, status='permanently_deleted'))
