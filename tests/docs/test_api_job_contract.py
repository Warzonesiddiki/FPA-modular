"""Document contracts, NOT registry/HTTP implementation tests (WI-0001, doc 64)."""
from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'docs/api_job_schemas.json'
P = '2025-P07'
AT = '2026-10-14T09:00:00Z'
SHA = 'a' * 64
PROJECT = 'prj_000000000001'
FORMAT = FormatChecker()


@FORMAT.checks('date-time', raises=(ValueError, TypeError))
def is_datetime(value):
    # jsonschema's optional RFC3339 extra is not installed: use stdlib, no network.
    if not isinstance(value, str):
        return True  # the schema's type check owns non-strings
    return datetime.fromisoformat(value).utcoffset() is not None

METHODS = ['naive', 'moving_average', 'exponential_smoothing', 'linear_trend',
           'driver_based', 'seasonal', 'budget_phasing', 'manual']
RULES = [f'EXC-{i:03}' for i in range(1, 29)]
SNAPSHOT = dict(snapshot_id='snapshot_1', batch_watermark=SHA,
                budget_version=None, forecast_run_id=None, layer='gl')
REPORT = dict(report_id='report_1', kind='excel', period_id=P, path='exports/pack.xlsx',
              sha256=SHA, checks=[], snapshot=SNAPSHOT)
FORECAST = dict(run_id='run_1', base_period_id=P, status='draft', created_at=AT,
                method_map={'revenue': 'naive'}, accuracy={'revenue': dict(
                    method='naive', mape='1.25', bias='-0.50', hit_rate='90.00',
                    history_months=12, excluded_zero_periods=0, na_reason=None)})
MANIFEST = dict(path='backups/backup.zip', sha256=SHA, files=3,
                created_at=AT, project_id=PROJECT, audit_head=SHA)
PULL = dict(pull_id='pul_000000000001', status='staged', snapshot_sha256=SHA,
            batches=[dict(batch_id='bat_000000000001', source_kind='gl', rows_in=100,
                          quarantined=3, status='validated')],
            row_counts={'gl': dict(status='pulled', expected=100, received=100,
                                   pages=1, retries=0, note=None),
                        'tb': dict(status='skipped', expected=0, received=0,
                                   pages=0, retries=0, note='Use the TB file export.')},
            auto_commit_job_ids=[])
# Independently authored result oracles from doc 64 §3, not read from the schema.
RESULTS = {
    'import-validate': dict(batch_id='bat_000000000001', status='validated', rows_in=100,
                           valid=97, quarantined=3, reasons=[dict(reason='OUT_OF_SCOPE_LAYER', count=3)],
                           issues=[], control=None),
    'import-commit': dict(batch_id='bat_000000000001', committed=97, quarantined=3,
                         tb_status='balanced', superseded_batch_id=None, enrichment=None),
    'import-enrich': dict(matched=7, ambiguous=1, unmatched=2, already_had_vendor=3),
    'rule-run': dict(run_id='rules_1', findings_new=36, findings_reopened=0,
                    findings_total=36, not_run=[], rules_executed=RULES),
    'forecast-run': FORECAST,
    'export-generate': dict(snapshot=SNAPSHOT, reports=[REPORT]),
    'backup': MANIFEST,
    'restore': dict(project_id=PROJECT, manifest=MANIFEST, verified=True),
    'audit-verify': dict(ok=True, rows_verified=100, head_hash=SHA),
    'connector-pull': PULL,
    'connector-check-changes': dict(changed_rows=None, last_pull_at=None),
    'allocation-run': dict(run_id='allocation_1', def_id='definition_1', period_id=P,
                           status='applied', pair_group_ids=['group_1'], total_allocated='100.00'),
    'reconcile-run': dict(recon_id='recon_1', period_id=P, kind='ap', status='open',
                          matched_groups=10, unmatched_gl=1, unmatched_subledger=1,
                          gl_total='1000.00', subledger_total='1000.00', unmatched_net='0.00', tolerance='100.00'),
    'year-end-close': dict(ye_id='year_end_1', fiscal_year=2025, closing_adjustments=3,
                           opening_batch_id='bat_000000000002', rollforward_delta='0.00', status='confirmed'),
    'planning-integrate': dict(run=FORECAST, checks=[dict(name='cash_tie', expected='480000.00',
                                                        actual='480000.00', delta='0.00', **{'pass': True})]),
    'report-render': REPORT,
    'diagnostics-bundle': dict(path='diagnostics/bundle.zip', sha256=SHA, files=3, created_at=AT, redacted=True),
    'ai-draft': dict(commentary_id='commentary_1', period_id=P, scope='exec_summary',
                     text='Revenue was ahead of plan. Review the source detail before approval.',
                     status='draft', ai_assisted=True, prompt_version='variance-v1',
                     source_refs=['finding_1'], version=1),
}


def error(code='008'):
    return dict(code=f'FP&A-ERR-{code}', message='This task stopped when the app closed.' if code == '008'
                else 'This task was cancelled.', hint='Start it again when ready.', retryable=True,
                details={'reason': 'interrupted' if code == '008' else 'user_cancelled'})


def done(kind):
    return dict(job_id='job_1', project_id=PROJECT, kind=kind, status='done', stage='done',
                progress_pct=100, progress=None, created_at=AT, started_at=AT, finished_at=AT,
                cancellable=False, error=None, result=copy.deepcopy(RESULTS[kind]))


@pytest.fixture
def schema():
    assert SCHEMA.is_file(), 'WI-0001 typed job schema missing (contract not implemented)'
    return json.loads(SCHEMA.read_text())


def validator(schema, definition=None):
    def local_only(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in ('$ref', '$dynamicRef'):
                    assert isinstance(child, str) and child.startswith('#/$defs/'), 'external schema reference'
                    assert child.split('/')[-1] in schema['$defs'], 'unresolved schema reference'
                local_only(child)
        elif isinstance(value, list):
            for child in value:
                local_only(child)
    local_only(schema)  # Fail before constructing a resolver: tests cannot fetch schemas.
    target = schema if definition is None else {'$ref': '#/$defs/' + definition, '$defs': schema['$defs']}
    return Draft202012Validator(target, format_checker=FORMAT)


def semantic_errors(job):
    """Independent doc-64 invariants JSON Schema cannot express with sibling arithmetic."""
    problems = []
    for before, after in [('created_at', 'started_at'), ('created_at', 'finished_at'),
                          ('started_at', 'finished_at')]:
        if job[before] and job[after] and datetime.fromisoformat(job[before]) > datetime.fromisoformat(job[after]):
            problems.append('timestamp order')
    if job['status'] != 'done':
        return problems
    result = job['result']
    kind = job['kind']
    if kind == 'import-validate':
        if result['rows_in'] != result['valid'] + result['quarantined']:
            problems.append('validation count conservation')
        if result['quarantined'] != sum(row['count'] for row in result['reasons']):
            problems.append('quarantine reason conservation')
        if len({row['reason'] for row in result['reasons']}) != len(result['reasons']):
            problems.append('duplicate quarantine reason')
        if (result['status'] == 'validated') != (not result['issues']):
            problems.append('validation issue state')
    if kind == 'rule-run':
        keys = result['rules_executed'] + [row['rule_id'] for row in result['not_run']]
        if sorted(keys) != RULES:
            problems.append('rule partition')
    if kind in ('forecast-run', 'planning-integrate'):
        run = result if kind == 'forecast-run' else result['run']
        if set(run['method_map']) != set(run['accuracy']):
            problems.append('forecast group keys')
        for group, metric in run['accuracy'].items():
            if run['method_map'].get(group) != metric['method']:
                problems.append('forecast method')
            if any(metric[key] is None for key in ('mape', 'bias', 'hit_rate')) and not metric['na_reason']:
                problems.append('unexplained unavailable metric')
    if kind == 'export-generate':
        if any(report['snapshot'] != result['snapshot'] for report in result['reports']):
            problems.append('export snapshot mismatch')
        if len({report['period_id'] for report in result['reports']}) != 1:
            problems.append('export period mismatch')
        kinds = [report['kind'] for report in result['reports']]
        if len(kinds) != 1 and kinds != ['excel', 'pptx', 'pdf']:
            problems.append('partial board pack')
    if kind == 'connector-pull':
        for counts in result['row_counts'].values():
            if counts['status'] == 'pulled' and counts['expected'] != counts['received']:
                problems.append('incomplete connector source')
        if result['auto_commit_job_ids'] and any(row['quarantined'] for row in result['batches']):
            problems.append('auto commit with quarantine')
        for batch in result['batches']:
            if batch['quarantined'] > batch['rows_in']:
                problems.append('pull count conservation')
    return problems


def assert_oracles(schema):
    Draft202012Validator.check_schema(schema)
    check = validator(schema)
    for kind in RESULTS:
        job = done(kind)
        check.validate(job)
        assert not semantic_errors(job), kind
    # Sensitive boundary probes used by mutation tests as well as normal tests.
    with pytest.raises(ValidationError):
        validator(schema, 'Money').validate(100)
    with pytest.raises(ValidationError):
        check.validate(dict(done('import-commit'), status='running', stage='writing_rows',
                            finished_at=None, result=None, progress_pct=101))
    with pytest.raises(ValidationError):
        check.validate(dict(done('import-commit'), result=RESULTS['forecast-run']))


def test_document_schema_exists_and_all_kind_oracles(schema):
    assert_oracles(schema)
    assert set(schema['x-job-results']) == set(RESULTS)


@pytest.mark.parametrize('kind', RESULTS)
def test_every_kind_all_lifecycle_states(schema, kind):
    job = done(kind)
    validator(schema).validate(job)
    for state, code in [('failed', '008'), ('cancelled', '004')]:
        terminal = dict(job, status=state, stage=state, progress_pct=None, error=error(code), result=None)
        if state == 'cancelled' and kind in ('backup', 'restore'):
            terminal['started_at'] = None  # Only a queued backup/restore can be cancelled.
        validator(schema).validate(terminal)
    queued = dict(job, status='queued', stage='queued', progress_pct=None, progress=None,
                  started_at=None, finished_at=None, result=None, cancellable=True)
    validator(schema).validate(queued)
    running = dict(queued, status='running', stage=schema['x-job-stages'][kind][0], started_at=AT,
                   cancellable=kind not in ('backup', 'restore'))
    validator(schema).validate(running)
    for field in job:
        missing = dict(job)
        del missing[field]
        with pytest.raises(ValidationError):
            validator(schema).validate(missing)
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(job, undeclared='not silently ignored'))


@pytest.mark.parametrize('value', ['0', '-1', '0.00', '-125000.50', '1.234', '0.000'])
def test_money_valid_exponents_and_signs(schema, value):
    validator(schema, 'Money').validate(value)


@pytest.mark.parametrize('value', [0, -1, 1.25, None, '', 'NaN', '1e2', '+1.00', '01.00',
                                  '1,000.00', '1.0', '1.0000', '₹100.00', '100.00\n', '0\r'])
def test_money_invalid_wire_values(schema, value):
    with pytest.raises(ValidationError):
        validator(schema, 'Money').validate(value)


@pytest.mark.parametrize('field,value', [('progress_pct', -1), ('progress_pct', 101),
    ('progress_pct', '50'), ('progress_pct', 1.5), ('cancellable', True),
    ('finished_at', None), ('started_at', None), ('result', None), ('error', error()),
    ('created_at', '14/10/2026'), ('created_at', '2026-02-30T09:00:00Z'),
    ('created_at', '2026-10-14T25:00:00Z'), ('created_at', '2026-10-14T09:00:00+05:30'),
    ('status', 'success'), ('stage', 'writing_rows'), ('kind', 'backup/restore')])
def test_terminal_invalid_combinations(schema, field, value):
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(done('import-commit'), **{field: value}))


def test_running_result_and_wrong_stage_rejected(schema):
    job = dict(done('import-commit'), status='running', stage='writing_rows', finished_at=None,
               result=None, progress_pct=50)
    validator(schema).validate(job)
    for patch in [dict(result=RESULTS['import-commit']), dict(stage='pulling'),
                  dict(error=error()), dict(cancellable=True)]:
        with pytest.raises(ValidationError):
            validator(schema).validate(dict(job, **patch))


def test_pull_no_change_skipped_and_auto_commit(schema):
    result = dict(PULL, status='no_change', snapshot_sha256=None, batches=[], row_counts={}, auto_commit_job_ids=[])
    job = dict(done('connector-pull'), result=result)
    validator(schema).validate(job)
    for patch in [dict(batches=PULL['batches']), dict(auto_commit_job_ids=['job_2'])]:
        with pytest.raises(ValidationError):
            validator(schema).validate(dict(job, result=dict(result, **patch)))
    for patch in [dict(snapshot_sha256=None), dict(batches=[])]:
        with pytest.raises(ValidationError):
            validator(schema).validate(dict(done('connector-pull'), result=dict(PULL, **patch)))
    counts = copy.deepcopy(PULL)
    counts['row_counts']['tb']['note'] = None
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(done('connector-pull'), result=counts))
    counts = copy.deepcopy(PULL)
    counts['row_counts']['unexpected_source'] = counts['row_counts']['gl']
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(done('connector-pull'), result=counts))
    counts = copy.deepcopy(PULL)
    counts['row_counts']['gl']['received'] -= 1
    assert semantic_errors(dict(done('connector-pull'), result=counts)) == ['incomplete connector source']
    counts = dict(PULL, auto_commit_job_ids=['job_2'])
    assert semantic_errors(dict(done('connector-pull'), result=counts)) == ['auto commit with quarantine']


def test_empty_and_single_row_validation_and_rule_partition(schema):
    job = done('import-validate')
    for size in (0, 1, 250000):
        job['result'].update(rows_in=size, valid=size, quarantined=0, reasons=[])
        validator(schema).validate(job)
        assert semantic_errors(job) == []
    job['result']['valid'] -= 1
    assert semantic_errors(job) == ['validation count conservation']
    rules = done('rule-run')
    rules['result']['rules_executed'] = RULES[1:]
    rules['result']['not_run'] = [dict(rule_id=RULES[0], reason='No prior batch')]
    validator(schema).validate(rules)
    assert not semantic_errors(rules)
    rules['result']['rules_executed'] = RULES
    assert semantic_errors(rules) == ['rule partition']


def test_forecast_null_metrics_require_reason_and_method_parity(schema):
    job = done('forecast-run')
    job['result']['accuracy']['revenue']['mape'] = None
    validator(schema).validate(job)  # sibling-dependent requirement checked separately
    assert semantic_errors(job) == ['unexplained unavailable metric']
    job['result']['accuracy']['revenue']['na_reason'] = 'All test actuals were zero.'
    assert not semantic_errors(job)
    job['result']['method_map']['revenue'] = 'manual'
    assert semantic_errors(job) == ['forecast method']


def test_board_pack_and_failure_verdicts(schema):
    job = done('export-generate')
    job['result']['reports'] = [dict(copy.deepcopy(REPORT), kind=k) for k in ('excel', 'pptx', 'pdf')]
    validator(schema).validate(job)
    assert not semantic_errors(job)
    job['result']['reports'][1]['snapshot']['snapshot_id'] = 'other'
    assert semantic_errors(job) == ['export snapshot mismatch']
    for kind, field in [('audit-verify', 'ok'), ('restore', 'verified'), ('diagnostics-bundle', 'redacted')]:
        broken = done(kind)
        broken['result'][field] = False
        with pytest.raises(ValidationError):
            validator(schema).validate(broken)
    broken = done('year-end-close')
    broken['result']['rollforward_delta'] = '0.01'
    with pytest.raises(ValidationError):
        validator(schema).validate(broken)
    broken = done('planning-integrate')
    broken['result']['checks'][0]['pass'] = False
    with pytest.raises(ValidationError):
        validator(schema).validate(broken)


def test_error_catalogue_and_status_mapping_parity(schema):
    catalogue = (ROOT / 'docs/22_ERROR_CATALOG.md').read_text()
    codes = re.findall(r'^\| (ERR-\d{3}) \|', catalogue, re.M)
    assert len(codes) == len(set(codes)) == 76
    assert set(schema['x-error-codes']) == {f'FP&A-{c}' for c in codes}
    assert len(schema['x-error-codes']) == len(codes)
    assert set(schema['x-error-examples']) == set(schema['x-error-codes'])
    refs = schema['$defs']['ErrorBody']['oneOf']
    actual_codes = {schema['$defs'][r['$ref'].split('/')[-1]]['properties']['code']['const'] for r in refs}
    assert actual_codes == set(schema['x-error-codes']) and len(refs) == len(codes)
    mapped = []
    for row in (ROOT / 'docs/05_API_CONTRACT.md').read_text().splitlines():
        if re.match(r'\| (\d{3}|Job error only) \|', row):
            mapped.extend(re.findall(r'ERR-\d{3}', row.split('|')[2]))
    assert sorted(mapped) == sorted(codes)
    for code, example in schema['x-error-examples'].items():
        assert code == example['code']
        row = next(row for row in catalogue.splitlines() if row.startswith(f'| {code.removeprefix("FP&A-")} |'))
        assert row.rstrip().endswith(('| yes |', '| no |'))
        assert example['retryable'] is (row.rstrip().endswith('| yes |'))
        validator(schema, 'ErrorBody').validate(example)
        with pytest.raises(ValidationError):
            validator(schema, 'ErrorBody').validate(dict(example, retryable=not example['retryable']))
    with pytest.raises(ValidationError):
        validator(schema, 'ErrorBody').validate(dict(error(), code='FP&A-ERR-009'))
    with pytest.raises(ValidationError):
        validator(schema, 'ErrorBody').validate(dict(error(), details={'token': 'not allowed'}))


def test_structural_money_closure_local_refs_and_doc_catalogue(schema):
    definitions = schema['$defs']
    def walk(value):
        if isinstance(value, dict):
            if '$ref' in value:
                assert value['$ref'].startswith('#/$defs/')
                assert value['$ref'].split('/')[-1] in definitions
            if value.get('type') == 'object':
                assert value.get('additionalProperties') is False or isinstance(value.get('additionalProperties'), dict)
            for key, child in value.items():
                if key == 'properties':
                    assert not any(name.endswith('_minor') for name in child)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(schema)
    kinds = re.findall(r'^\| ([a-z]+(?:-[a-z]+)*) \|', (ROOT / 'docs/64_JOB_AND_BACKGROUND_PROCESS_SPEC.md').read_text(), re.M)
    assert set(kinds) == set(RESULTS)
    rows = [line.split('|') for line in (ROOT / 'docs/64_JOB_AND_BACKGROUND_PROCESS_SPEC.md').read_text().splitlines()
            if line.startswith('|') and line.split('|')[1].strip() in RESULTS]
    assert len(rows) == len(RESULTS)
    assert {row[1].strip(): row[4].strip() for row in rows} == schema['x-job-results']
    assert {row[1].strip(): [stage.strip() for stage in row[2].split(',')] for row in rows} == schema['x-job-stages']
    for kind, result in schema['x-job-results'].items():
        assert result in definitions
        assert schema['x-job-stages'][kind]


def test_schema_examples_and_cookbook_full_jobs(schema):
    for job in schema['examples']:
        validator(schema).validate(job)
        assert not semantic_errors(job)
    assert {job['kind'] for job in schema['examples'] if job['status'] == 'done'} == set(RESULTS)
    blocks = re.findall(r'```json\n(.*?)\n```', (ROOT / 'docs/63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK.md').read_text(), re.S)
    checked = 0
    for block in blocks:
        example = json.loads(block)
        if 'job_id' in example and 'status' in example:
            validator(schema).validate(example)
            assert not semantic_errors(example)
            checked += 1
        elif 'pull_id' in example:
            validator(schema, 'PullResult').validate(example)
            checked += 1
        elif 'code' in example:
            validator(schema, 'ErrorBody').validate(example)
            checked += 1
    assert checked >= 4


def test_three_schema_mutations_are_caught(schema):
    # Exercise the SAME contract oracle assertions, not merely detect an edited byte.
    changed = copy.deepcopy(schema)
    changed['$defs']['Money'] = {'type': 'number'}
    with pytest.raises((AssertionError, ValidationError)):
        assert_oracles(changed)
    changed = copy.deepcopy(schema)
    changed['$defs']['ProgressPercent']['maximum'] = 101
    with pytest.raises(pytest.fail.Exception) as caught:
        assert_oracles(changed)
    assert 'DID NOT RAISE' in str(caught.value)
    changed = copy.deepcopy(schema)
    changed['$defs']['JobDone']['properties']['result'] = {}
    del changed['$defs']['JobDone']['allOf']
    with pytest.raises(pytest.fail.Exception) as caught:
        assert_oracles(changed)
    assert 'DID NOT RAISE' in str(caught.value)


@pytest.mark.parametrize('kind', RESULTS)
def test_closed_nested_results_and_all_other_kind_results(schema, kind):
    job = done(kind)
    result = dict(job['result'], accidental_debug_field='not a public API field')
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(job, result=result))
    for other in RESULTS:
        if other == kind:
            continue
        with pytest.raises(ValidationError):
            validator(schema).validate(dict(job, result=copy.deepcopy(RESULTS[other])))


@pytest.mark.parametrize('value', ['../secret', '/etc/passwd', 'C:/secret', 'a/../../secret',
                                  'http://example.com/file', 'a\\secret', 'exports/pack.xlsx\n'])
def test_unsafe_artifact_paths(schema, value):
    with pytest.raises(ValidationError):
        validator(schema, 'ArtifactPath').validate(value)


def test_external_refs_rejected_before_resolver_or_socket(schema, monkeypatch):
    import socket
    def forbidden(*args, **kwargs):
        raise AssertionError('network attempted')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    changed = copy.deepcopy(schema)
    changed['$defs']['Money'] = {'$ref': 'https://example.com/not-a-local-schema'}
    with pytest.raises(AssertionError, match='external schema reference'):
        validator(changed)
    validator(schema).validate(done('connector-pull'))


def test_hostile_text_is_data_not_executable(schema):
    job = done('ai-draft')
    job['result']['text'] = '=formula <script>wrong()</script> "quoted" ₹ Unicode\n' + 'x' * 9000
    validator(schema).validate(job)
    # Validation accepts data; UI/export escaping is a separate, still-unbuilt M3/M5 test.
    assert '<script>' in job['result']['text']
    job['result']['text'] = 'x' * 10001
    with pytest.raises(ValidationError):
        validator(schema).validate(job)


def test_queued_cancel_and_started_backup_cannot_cancel(schema):
    for kind in ('backup', 'restore'):
        job = dict(done(kind), status='cancelled', stage='cancelled', started_at=None,
                   progress_pct=None, result=None, error=error('004'))
        validator(schema).validate(job)
        with pytest.raises(ValidationError):
            validator(schema).validate(dict(job, started_at=AT))
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(done('import-commit'), status='failed', stage='failed',
                                        result=None, error=error('004')))


def test_semantic_oracle_negative_controls(schema):
    job = done('import-validate')
    job['result']['reasons'][0]['count'] = 2
    assert semantic_errors(job) == ['quarantine reason conservation']
    job = done('rule-run')
    job['result']['rules_executed'] = RULES[1:]
    assert semantic_errors(job) == ['rule partition']
    job = done('export-generate')
    job['result']['reports'] = [REPORT, dict(REPORT, kind='pptx')]
    assert semantic_errors(job) == ['partial board pack']
    job = done('import-commit')
    job['finished_at'] = '2026-10-14T08:00:00Z'
    assert semantic_errors(job) == ['timestamp order', 'timestamp order']


@pytest.mark.parametrize('state,requested,cancellable', [
    ('running', True, True), ('running', False, False), ('done', False, False),
    ('failed', False, False), ('cancelled', True, False), ('cancelled', False, False)])
def test_cancel_response_valid_variants(schema, state, requested, cancellable):
    validator(schema, 'CancelResponse').validate(dict(job_id='job_1', status=state,
        cancel_requested=requested, cancellable=cancellable))


@pytest.mark.parametrize('state,requested,cancellable', [
    ('queued', True, True), ('running', False, True), ('running', True, False),
    ('done', True, False), ('done', False, True), ('failed', True, False),
    ('cancelled', True, True)])
def test_cancel_response_impossible_variants(schema, state, requested, cancellable):
    with pytest.raises(ValidationError):
        validator(schema, 'CancelResponse').validate(dict(job_id='job_1', status=state,
            cancel_requested=requested, cancellable=cancellable))


def test_job_schema_has_no_credential_fields(schema):
    forbidden = {'access_token', 'refresh_token', 'client_secret', 'pkce_verifier', 'authorization_code'}
    def walk(value):
        if isinstance(value, dict):
            assert not (forbidden & set(value.get('properties', {})))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(schema['$defs'])


@pytest.mark.parametrize('period', ['2025-P00', '2025-P13', '2025-P1', 'FY26-P07', '0000-P01', '2025-P07\n'])
def test_period_identity_invalid_boundaries(schema, period):
    with pytest.raises(ValidationError):
        validator(schema, 'PeriodId').validate(period)


@pytest.mark.parametrize('period', ['2025-P01', '2025-P12', '0001-P01', '9999-P12'])
def test_period_identity_valid_boundaries(schema, period):
    validator(schema, 'PeriodId').validate(period)


def test_job_page_and_receipt_schema(schema):
    validator(schema, 'JobReceipt').validate({'job_id': 'job_1'})
    validator(schema, 'JobPage').validate({'items': [], 'next_cursor': None})
    validator(schema, 'JobPage').validate({'items': [done('connector-pull')], 'next_cursor': None})
    for invalid in [{'job_id': 'job_1', 'token': 'no'}, {}]:
        with pytest.raises(ValidationError):
            validator(schema, 'JobReceipt').validate(invalid)
    for invalid in [{'items': [], 'next_cursor': 123}, {'items': []},
                    {'items': [dict(done('connector-pull'), result=None)], 'next_cursor': None}]:
        with pytest.raises(ValidationError):
            validator(schema, 'JobPage').validate(invalid)
    assert schema['$defs']['JobPage']['properties']['items']['maxItems'] == 1000


def test_human_commentary_read_model_is_not_an_ai_job_result(schema):
    human = copy.deepcopy(RESULTS['ai-draft'])
    human.update(status='approved', ai_assisted=False, prompt_version=None)
    validator(schema, 'Commentary').validate(human)
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(done('ai-draft'), result=human))
    human['status'] = 'draft'
    validator(schema, 'Commentary').validate(human)
    with pytest.raises(ValidationError):
        validator(schema).validate(dict(done('ai-draft'), result=human))
