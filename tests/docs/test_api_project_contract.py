"""Independent doc-05 §6 oracles; NOT project repository or HTTP runtime tests."""
from __future__ import annotations

import copy
import json
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

import pytest
from jsonschema import ValidationError
from test_api_job_contract import FORMAT, validator

ROOT = Path(__file__).resolve().parents[2]
AT = '2026-10-14T09:00:00Z'
PID = 'prj_9f2c41aa07e1'
CREATE = dict(name='Meridian FY27', base_currency='INR', fy_start_month=4,
              calendar_type='monthly', fiscal_year=2026)
PROJECT = dict(project_id=PID, name='Meridian FY27', base_currency='INR',
               currency_exponent=2, fy_start_month=4, calendar_type='monthly',
               is_sample=False, version=1, created_at=AT, updated_at=AT)
PERIOD = dict(project_id=PID, period_id='2026-P01', fiscal_year=2026, period_no=1,
              start_date='2026-04-01', end_date='2026-04-30', status='open',
              locked_at=None, lock_note=None, version=1, created_at=AT, updated_at=AT)
# Hand-written calendar oracle: FY2027 ends in a leap February / March 2028.
YEAR_DATES = [
    ('2027-04-01', '2027-04-30'), ('2027-05-01', '2027-05-31'),
    ('2027-06-01', '2027-06-30'), ('2027-07-01', '2027-07-31'),
    ('2027-08-01', '2027-08-31'), ('2027-09-01', '2027-09-30'),
    ('2027-10-01', '2027-10-31'), ('2027-11-01', '2027-11-30'),
    ('2027-12-01', '2027-12-31'), ('2028-01-01', '2028-01-31'),
    ('2028-02-01', '2028-02-29'), ('2028-03-01', '2028-03-31'),
]
YEAR = dict(project_id=PID, fiscal_year=2027, periods=[
    dict(PERIOD, period_id=f'2027-P{i:02}', fiscal_year=2027, period_no=i,
         start_date=start, end_date=end)
    for i, (start, end) in enumerate(YEAR_DATES, 1)
])
CURRENCIES = {'INR': 2, 'USD': 2, 'EUR': 2, 'GBP': 2, 'AED': 2, 'JPY': 0, 'KWD': 3}
EXPECTED_ROUTES = {
    'GET /health': ('app', None, None, {'200': 'Health'}, 'none'),
    'GET /projects': ('app', None, 'ProjectListQuery', {'200': 'ProjectPage'}, 'none'),
    'POST /projects': ('app', 'ProjectCreate', None, {'201': 'CreatedProject'}, 'required'),
    'GET /projects/{id}': ('project', None, None, {'200': 'Project'}, 'none'),
    'GET /projects/{id}/periods': ('project', None, 'PeriodListQuery', {'200': 'PeriodPage'}, 'none'),
    'POST /projects/{id}/periods': ('project', 'FiscalYearCreate', None,
                                 {'200': 'FiscalYearPeriods', '201': 'FiscalYearPeriods'}, 'optional'),
    'GET /projects/{id}/periods/{period_id}': ('project', None, None, {'200': 'Period'}, 'none'),
}


@FORMAT.checks('date', raises=(ValueError, TypeError))
def gregorian_date(value):
    return not isinstance(value, str) or date.fromisoformat(value) is not None


@pytest.fixture
def schema():
    value = json.loads((ROOT / 'docs/api_job_schemas.json').read_text())
    required = {'Health', 'ProjectName', 'ProjectId', 'ProjectCreate', 'Project', 'Period',
                'ProjectPage', 'PeriodPage', 'FiscalYearCreate', 'FiscalYearPeriods',
                'ProjectListQuery', 'PeriodListQuery'}
    assert required <= value['$defs'].keys(), 'DEC-017 project contract definitions missing'
    assert 'x-project-endpoints' in value, 'DEC-017 method/path contracts missing'
    return value


def metadata_errors(project, periods=()):
    """Independent relational oracle; these constraints also need M1/M3 implementation."""
    errors = []
    if unicodedata.normalize('NFC', project['name']) != project['name']:
        errors.append('name NFC')
    if CURRENCIES.get(project['base_currency']) != project['currency_exponent']:
        errors.append('currency exponent')
    if datetime.fromisoformat(project['updated_at']) < datetime.fromisoformat(project['created_at']):
        errors.append('project timestamp order')
    for p in periods:
        if p['project_id'] != project['project_id']:
            errors.append('period project ownership')
        if p['period_id'] != f"{p['fiscal_year']:04}-P{p['period_no']:02}":
            errors.append('period identity')
        start, end = date.fromisoformat(p['start_date']), date.fromisoformat(p['end_date'])
        offset = project['fy_start_month'] + p['period_no'] - 2
        if (start.year, start.month, start.day) != (p['fiscal_year'] + offset // 12, offset % 12 + 1, 1):
            errors.append('period start')
        # Last day predicate, not a second fiscal-calendar implementation.
        if end < start or (end.year, end.month) != (start.year, start.month):
            errors.append('period end')
        elif end.day < 28 or (end.day < 31 and date.fromordinal(end.toordinal() + 1).month == end.month):
            errors.append('period end')
        if datetime.fromisoformat(p['updated_at']) < datetime.fromisoformat(p['created_at']):
            errors.append('period timestamp order')
    return errors


def assert_project_oracles(s):
    for name, value in [('ProjectCreate', CREATE), ('Project', PROJECT), ('Period', PERIOD),
                        ('FiscalYearPeriods', YEAR), ('Health', {'status': 'ok', 'version': '0.1.0'})]:
        validator(s, name).validate(value)
    assert not year_errors(PROJECT, YEAR)
    assert not created_project_errors(PROJECT)
    with pytest.raises(ValidationError):
        validator(s, 'ProjectCreate').validate(dict(CREATE, is_sample=True))
    with pytest.raises(ValidationError):
        validator(s, 'Project').validate(dict(PROJECT, base_currency='JPY', currency_exponent=2))
    with pytest.raises(ValidationError):
        validator(s, 'FiscalYearCreate').validate({'fiscal_year': 9999})


def test_project_oracles(schema):
    assert_project_oracles(schema)


@pytest.mark.parametrize('currency,exponent', CURRENCIES.items())
def test_fixed_currency_exponents(schema, currency, exponent):
    validator(schema, 'ProjectCreate').validate(dict(CREATE, base_currency=currency))
    validator(schema, 'Project').validate(dict(PROJECT, base_currency=currency, currency_exponent=exponent))
    for wrong in {0, 2, 3} - {exponent}:
        with pytest.raises(ValidationError):
            validator(schema, 'Project').validate(dict(PROJECT, base_currency=currency, currency_exponent=wrong))


@pytest.mark.parametrize('field,value', [
    ('fiscal_year', 0), ('fiscal_year', 9999), ('fiscal_year', True), ('fiscal_year', '2026'),
    ('fy_start_month', 0), ('fy_start_month', 13), ('fy_start_month', False),
    ('calendar_type', '445'), ('base_currency', 'ZZZ'), ('base_currency', 'inr'),
    ('name', ''), ('name', ' '), ('name', 'a' * 81), ('name', ' leading'),
    ('name', 'trailing '), ('name', 'a\nb'), ('name', 'a\x00b'),
    ('project_id', PID), ('is_sample', True), ('currency_exponent', 2),
    ('version', 1), ('path', '/tmp/project'), ('created_at', AT),
])
def test_bad_create_requests(schema, field, value):
    with pytest.raises(ValidationError):
        validator(schema, 'ProjectCreate').validate(dict(CREATE, **{field: value}))


@pytest.mark.parametrize('name', ['é', '公司', '=SUM(A1:A2)', '<script>alert(1)</script>', 'a' * 80])
def test_names_are_literal_data_with_defined_bounds(schema, name):
    validator(schema, 'ProjectCreate').validate(dict(CREATE, name=name))
    assert not metadata_errors(dict(PROJECT, name=name))


@pytest.mark.parametrize('name,value', [('ProjectCreate', CREATE), ('Project', PROJECT), ('Period', PERIOD),
                                      ('FiscalYearPeriods', YEAR)])
def test_closed_objects_and_every_required_field(schema, name, value):
    for key in value:
        missing = copy.deepcopy(value)
        del missing[key]
        with pytest.raises(ValidationError):
            validator(schema, name).validate(missing)
    with pytest.raises(ValidationError):
        validator(schema, name).validate(dict(value, accidental_debug_field='no'))


@pytest.mark.parametrize('field,value', [
    ('period_id', '2026-P13'), ('period_id', '0000-P01'), ('period_no', 0), ('period_no', 13),
    ('project_id', 'prj_ABCDEF123456'), ('start_date', '2026-02-30'),
    ('end_date', '2026-04-31'), ('start_date', '2026-04-01\n'),
    ('status', 'closed'), ('status', 'locked'), ('locked_at', AT), ('lock_note', 'note'),
    ('version', 0), ('version', True), ('updated_at', '2026-10-14T25:00:00Z'),
])
def test_bad_period_metadata(schema, field, value):
    with pytest.raises(ValidationError):
        validator(schema, 'Period').validate(dict(PERIOD, **{field: value}))


def test_locked_and_closing_periods_are_readable(schema):
    validator(schema, 'Period').validate(dict(PERIOD, status='closing'))
    locked = dict(PERIOD, status='locked', locked_at=AT, lock_note='Reviewed', version=2)
    validator(schema, 'Period').validate(locked)
    validator(schema, 'Period').validate(dict(locked, lock_note=None))
    for note in ['', ' ', '\n']:
        with pytest.raises(ValidationError):
            validator(schema, 'Period').validate(dict(locked, lock_note=note))


@pytest.mark.parametrize('year', [1, 2024, 9998])
def test_fiscal_creation_boundaries(schema, year):
    validator(schema, 'FiscalYearCreate').validate({'fiscal_year': year})
    validator(schema, 'ProjectCreate').validate(dict(CREATE, fiscal_year=year))


def test_year_size_uniqueness_and_leap_oracle(schema):
    assert YEAR['periods'][10]['end_date'] == '2028-02-29'
    for periods in [[], YEAR['periods'][:11], YEAR['periods'] + [PERIOD], [PERIOD] * 12]:
        with pytest.raises(ValidationError):
            validator(schema, 'FiscalYearPeriods').validate(dict(YEAR, periods=periods))
    changed = copy.deepcopy(YEAR)
    changed['periods'][10]['end_date'] = '2028-02-28'
    assert 'period end' in metadata_errors(PROJECT, changed['periods'])


@pytest.mark.parametrize('name,item', [('ProjectPage', PROJECT), ('PeriodPage', PERIOD)])
def test_empty_single_and_page_cap(schema, name, item):
    check = validator(schema, name)
    check.validate({'items': [], 'next_cursor': None})
    check.validate({'items': [item], 'next_cursor': None})
    with pytest.raises(ValidationError):
        check.validate({'items': [item] * 1001, 'next_cursor': None})
    for value in [{'items': []}, {'items': [], 'next_cursor': ''}, {'items': [], 'next_cursor': 1}]:
        with pytest.raises(ValidationError):
            check.validate(value)


@pytest.mark.parametrize('name', ['ProjectListQuery', 'PeriodListQuery'])
def test_query_defaults_and_rejections(schema, name):
    check = validator(schema, name)
    check.validate({})
    check.validate({'limit': 1})
    check.validate({'limit': 1000, 'cursor': 'opaque-cursor'})
    assert schema['$defs'][name]['properties']['limit']['default'] == 100
    for value in [{'limit': 0}, {'limit': 1001}, {'limit': '100'}, {'limit': True},
                  {'cursor': ''}, {'cursor': None}, {'sort': 'SELECT *'}]:
        with pytest.raises(ValidationError):
            check.validate(value)
    with pytest.raises(ValidationError):
        check.validate({'status': 'draft'} if name == 'PeriodListQuery' else {'is_sample': 'true'})


def test_semantic_negative_controls(schema):
    assert metadata_errors(dict(PROJECT, name='e\u0301')) == ['name NFC']
    assert metadata_errors(dict(PROJECT, currency_exponent=3)) == ['currency exponent']
    assert metadata_errors(dict(PROJECT, updated_at='2025-01-01T00:00:00Z')) == ['project timestamp order']
    for field, value, reason in [('project_id', 'prj_000000000001', 'period project ownership'),
                                 ('period_id', '2026-P02', 'period identity'),
                                 ('start_date', '2026-04-02', 'period start'),
                                 ('end_date', '2026-04-29', 'period end')]:
        assert reason in metadata_errors(PROJECT, [dict(PERIOD, **{field: value})])


def test_three_project_schema_mutations_are_caught(schema):
    changed = copy.deepcopy(schema)
    changed['$defs']['ProjectCreate']['additionalProperties'] = True
    with pytest.raises(pytest.fail.Exception):
        assert_project_oracles(changed)
    changed = copy.deepcopy(schema)
    del changed['$defs']['Project']['allOf']
    with pytest.raises(pytest.fail.Exception):
        assert_project_oracles(changed)
    changed = copy.deepcopy(schema)
    changed['$defs']['FiscalYearCreate']['properties']['fiscal_year']['maximum'] = 9999
    with pytest.raises(pytest.fail.Exception):
        assert_project_oracles(changed)


def test_seven_endpoint_contracts_and_error_transport(schema):
    text = (ROOT / 'docs/05_API_CONTRACT.md').read_text()
    section = text.split('## 6. Health,', 1)[1]
    matches = re.findall(r'^### 6\.\d+ (GET|POST) `([^`]+)`\n(.*?)(?=^### |\Z)', section, re.M | re.S)
    assert {f'{method} {path}' for method, path, _ in matches} == set(EXPECTED_ROUTES)
    registry = schema['x-project-endpoints']
    assert set(registry) == set(EXPECTED_ROUTES)
    for method, path, body in matches:
        endpoint = registry[f'{method} {path}']
        assert (endpoint['scope'], endpoint['request'], endpoint['query'], endpoint['responses'],
                endpoint['idempotency']) == EXPECTED_ROUTES[f'{method} {path}']
        assert endpoint['token_required'] is True
        for label in ['Auth / scope', 'Request', 'Response', 'Failures', 'Pagination', 'Idempotency', 'Example']:
            assert f'**{label}:**' in body
        failures = body.split('**Failures:**', 1)[1].split('\n', 1)[0]
        actual = {}
        for status, tail in re.findall(r'(\d{3}) ([^;]+)', failures):
            actual[status] = re.findall(r'ERR-(\d{3})', tail)
        assert actual == endpoint['errors']
        for status, codes in actual.items():
            for code in codes:
                validator(schema, 'Error' + code).validate(schema['x-error-examples']['FP&A-ERR-' + code])
                mapping_line = next(line for line in text.splitlines() if line.startswith('| ' + status + ' |'))
                assert 'ERR-' + code in mapping_line


def test_project_cookbook_examples(schema):
    text = (ROOT / 'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text()
    examples = re.findall(r'<!-- contract: (\w+) -->\n```json\n(.*?)\n```', text, re.S)
    assert {name for name, _ in examples} >= {'ProjectCreate', 'Project', 'ProjectPage', 'PeriodPage',
                                           'Period', 'FiscalYearCreate', 'FiscalYearPeriods', 'Health'}
    for name, source in examples:
        example = json.loads(source)
        validator(schema, name).validate(example)
        if name == 'Project':
            assert example == PROJECT
        elif name == 'FiscalYearPeriods':
            assert example == YEAR
            assert not metadata_errors(PROJECT, example['periods'])
        elif name == 'Period':
            assert example == PERIOD


def test_create_response_cannot_impersonate_sample_or_old_revision(schema):
    assert 'CreatedProject' in schema['$defs'], 'Creation-specific response contract missing'
    validator(schema, 'CreatedProject').validate(PROJECT)
    # General reads MUST continue to support samples and later revisions.
    for change in [{'is_sample': True}, {'version': 2}]:
        value = dict(PROJECT, **change)
        validator(schema, 'Project').validate(value)
        with pytest.raises(ValidationError):
            validator(schema, 'CreatedProject').validate(value)


def test_currency_registry_matches_owner_doc(schema):
    text = (ROOT / 'docs/27_LOCALIZATION_CURRENCY_AND_UNITS.md').read_text()
    registry = {code: int(exponent) for code, exponent in re.findall(r'\b([A-Z]{3})=([023])\b', text)}
    assert registry == CURRENCIES
    assert set(schema['$defs']['ProjectCreate']['properties']['base_currency']['enum']) == set(registry)


@pytest.mark.parametrize('month,period', [
    (1, dict(PERIOD, period_id='2026-P12', period_no=12, start_date='2026-12-01', end_date='2026-12-31')),
    (12, dict(PERIOD, period_id='2026-P02', period_no=2, start_date='2027-01-01', end_date='2027-01-31')),
    (4, dict(PERIOD, period_id='0001-P12', fiscal_year=1, period_no=12, start_date='0002-03-01', end_date='0002-03-31')),
    (4, dict(PERIOD, period_id='9998-P12', fiscal_year=9998, period_no=12, start_date='9999-03-01', end_date='9999-03-31')),
])
def test_calendar_read_boundaries(schema, month, period):
    validator(schema, 'ProjectCreate').validate(dict(CREATE, fy_start_month=month))
    validator(schema, 'Period').validate(period)
    assert not metadata_errors(dict(PROJECT, fy_start_month=month), [period])


def year_errors(project, result):
    errors = metadata_errors(project, result['periods'])
    if result['project_id'] != project['project_id']:
        errors.append('year project ownership')
    if [p['period_no'] for p in result['periods']] != list(range(1, 13)):
        errors.append('year partition')
    if any(p['fiscal_year'] != result['fiscal_year'] for p in result['periods']):
        errors.append('year identity')
    return errors


def test_fiscal_year_relational_negative_controls(schema):
    assert not year_errors(PROJECT, YEAR)
    assert 'year project ownership' in year_errors(PROJECT, dict(YEAR, project_id='prj_000000000001'))
    assert 'year identity' in year_errors(PROJECT, dict(YEAR, fiscal_year=2026))
    swapped = copy.deepcopy(YEAR)
    swapped['periods'][0], swapped['periods'][1] = swapped['periods'][1], swapped['periods'][0]
    with pytest.raises(ValidationError):
        validator(schema, 'FiscalYearPeriods').validate(swapped)
    assert 'year partition' in year_errors(PROJECT, swapped)


def created_project_errors(project):
    errors = metadata_errors(project)
    if project['is_sample'] or project['version'] != 1:
        errors.append('creation flags')
    if project['created_at'] != project['updated_at']:
        errors.append('creation timestamp mismatch')
    return errors


def test_creation_timestamp_oracle_and_health_closure(schema):
    # Cross-property equality is an adapter invariant, not JSON Schema 2020-12 functionality.
    assert not created_project_errors(PROJECT)
    changed = dict(PROJECT, updated_at='2026-10-14T09:00:01Z')
    validator(schema, 'CreatedProject').validate(changed)
    assert created_project_errors(changed) == ['creation timestamp mismatch']
    for health in [{}, {'status': 'ok'}, {'status': 'failed', 'version': '0.1.0'},
                   {'status': 'ok', 'version': '0.1.0\n'}, {'status': 'ok', 'version': 1},
                   {'status': 'ok', 'version': '0.1.0', 'project_path': '/private'}]:
        with pytest.raises(ValidationError):
            validator(schema, 'Health').validate(health)


def test_scoped_http_examples_have_the_required_project_header():
    text = (ROOT / 'docs/05_API_CONTRACT.md').read_text()
    examples = re.findall(r'```http\n(.*?)\n```', text, re.S)
    assert examples
    for example in examples:
        project = re.search(r'/api/v1/projects/(prj_[0-9a-f]{12})(?:/|\s|$)', example)
        if '/api/v1/' in example.splitlines()[0]:
            assert 'X-FPA-Token:' in example
        if project:
            assert f'X-FPA-Project: {project[1]}' in example
        if '/connector/pull' in example.splitlines()[0]:
            assert 'Idempotency-Key:' in example
