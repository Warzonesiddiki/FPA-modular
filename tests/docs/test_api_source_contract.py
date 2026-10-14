"""DEC-024 closed source codec + independent pure models; no product/SQL/file/HTTP proof."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import re
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator, ValidationError
from test_api_job_contract import validator

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'docs/retained_source_schemas.json'
PID='prj_000000000001'
MIN=-9223372036854775808
MAX=9223372036854775807
PREFIX=b'FPA-SOURCE-IMAGE-v1\n'
PRIMITIVES=['Id','ProjectId','PeriodId','Sha256','Timestamp','CalendarDate','DecimalString']
# Hand-authored source data, not extracted from the schema. Bytes are synthetic,
# not a claim that a CSV/XLSX parser or original-file retention has been exercised.
FILE_BYTES=b'2026-04-03,JV-1,-12500050\n'
FILE_SHA='db173783f4f0097d4b3895065d9e2d4db732f71c4026fe4fe4390b015224d837'
ORIGIN=dict(kind='file',source='file',batch_file_sha256=FILE_SHA,artifact_sha256=FILE_SHA,
            byte_length=26,sheet_name='GL')
GENERATED=dict(kind='generated',generator='year_end',year_end_run_id='ye_2025')
GL=dict(gl_row_id='7cc3cd113cc886ae0f0bd1bd855943ef',project_id=PID,period_id='2026-P01',
 batch_id='bat_000000000001',entity_id='IN01',account_id='ACC-5100',cost_centre_id=None,
 vendor_id=None,voucher_no='JV-1',document_date='2026-04-03',posting_date='2026-04-03',
 description='Accrual ₹125,000.50',amount_minor=-12500050,quantity_decimal=None,
 fx_currency=None,fx_amount_minor=None,fx_rate=None,layer='gl',posted_by=None,posted_at=None,
 posting_layer='Current',source_account_ref='5100-IN01',vendor_source=None,
 source_file='ledger.csv',source_row=142,origin=ORIGIN)
ADJ=dict(adj_id='adj_1',project_id=PID,period_id='2026-P01',entity_id='IN01',account_id='ACC-6200',
 cost_centre_id=None,amount_minor=200000,kind='reclass',label='Management reclass',reason='Move cost to rent',
 pair_group_id='group_1',contra_account_id=None,status='applied',reverses_adj_id=None,source='manual',
 created_by='Analyst',created_at='2026-10-15T10:00:00Z',updated_at='2026-10-15T10:00:00Z',version=1)
IMAGE=dict(codec='fpa-source-v1',kind='gl',row=GL)
ADJ_IMAGE=dict(codec='fpa-source-v1',kind='adjustment',row=ADJ)
FIRST=dict(GL,gl_row_id='3c9549118ab0ebdc7f44d6da91961b5f',source_row=1)
OPENING=dict(GL,layer='opening',origin=GENERATED)
CONNECTOR=dict(GL,origin=dict(ORIGIN,source='connector',batch_file_sha256='a'*64))


def canonical(value):
 """Small reference encoder from 24 §6.1, not an app codec implementation."""
 def check(x):
  if x is None or type(x) in [bool,int]:return
  if isinstance(x,str):x.encode('utf-8');return
  if isinstance(x,list):
   for item in x:check(item)
   return
  if isinstance(x,dict):
   for key,item in x.items():
    if not isinstance(key,str):raise ValueError('non-string key')
    check(key);check(item)
   return
  raise ValueError('non-integer number or unsupported JSON value')
 check(value)
 return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')


def strict_decode(data):
 def pairs(items):
  result={}
  for key,val in items:
   if key in result:raise ValueError('duplicate key')
   result[key]=val
  return result
 def forbidden(token):raise ValueError('forbidden numeric token')
 obj=json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_float=forbidden,parse_constant=forbidden)
 if canonical(obj)!=data:raise ValueError('noncanonical bytes')
 return obj


def digest(image):return hashlib.sha256(PREFIX+canonical(image)).hexdigest()
def record(image):return dict(project_id=image['row']['project_id'],content_sha256=digest(image),image=image)
EXAMPLES={'RetainedFileOrigin':ORIGIN,'RetainedGeneratedOrigin':GENERATED,'RetainedGLRow':GL,
 'RetainedAdjustmentRow':ADJ,'RetainedSourceImage':IMAGE,'RetainedSourceRecord':record(IMAGE)}

@pytest.fixture
def schema():
 assert PATH.is_file(),'DEC-024 retained source schema missing'
 s=json.loads(PATH.read_text())
 assert set(EXAMPLES)<=s['$defs'].keys(),'DEC-024 source definitions missing'
 return s


def relational_errors(rec):
 """Only document relational checks; does not authenticate original inputs."""
 errors=[];image=rec['image'];r=image['row']
 if rec['project_id']!=r['project_id']:errors.append('project')
 if rec['content_sha256']!=digest(image):errors.append('digest')
 if image['kind']=='gl' and r['origin']['kind']=='file':
  o=r['origin']
  if o['source']=='file' and o['batch_file_sha256']!=o['artifact_sha256']:errors.append('file identity')
  expected=hashlib.sha256(f"{r['batch_id']}|{o['sheet_name']}|{r['source_row']}".encode()).hexdigest()[:32]
  if r['gl_row_id']!=expected:errors.append('row identity')
 return errors


def model_lookup(rec,project,membership,files,year_ends):
 """Synthetic already-authorized membership/file/run inputs; no I/O or auth."""
 if rec['project_id']!=project or (project,rec['content_sha256']) not in membership:raise ValueError('scope/membership')
 if relational_errors(rec):raise ValueError('retained record')
 image=rec['image'];row=image['row']
 if image['kind']=='gl':
  o=row['origin']
  if o['kind']=='file':
   data=files.get((project,o['artifact_sha256']))
   if data is None or len(data)!=o['byte_length'] or hashlib.sha256(data).hexdigest()!=o['artifact_sha256']:raise ValueError('artifact')
  elif (project,o['year_end_run_id']) not in year_ends:raise ValueError('generation provenance')
 return copy.deepcopy(row)


def assert_oracles(s):
 for name,value in EXAMPLES.items():validator(s,name).validate(value)
 for row in [FIRST,OPENING,CONNECTOR]:validator(s,'RetainedGLRow').validate(row)
 validator(s,'RetainedSourceImage').validate(ADJ_IMAGE)
 assert not validator(s,'RetainedGLRow').is_valid(dict(GL,vendor_id='Vendor unresolved',vendor_source=None))
 assert not validator(s,'RetainedGLRow').is_valid(dict(GL,vendor_source='ap_match'))
 assert not validator(s,'RetainedGLRow').is_valid(dict(GL,origin=GENERATED))
 assert not relational_errors(record(IMAGE))
 assert digest(IMAGE)==GL_DIGEST


# Literal complete-image digest, fixed before the schema implementation.
GL_DIGEST='31673f761383c6aae3af28c7dae684fe4a5ab16af3b7f22ae0a7f49647ecd937'


def test_independent_oracles(schema):assert_oracles(schema)


@pytest.mark.parametrize('name',list(EXAMPLES))
def test_closed_required_layouts(schema,name):
 for key in EXAMPLES[name]:
  changed=copy.deepcopy(EXAMPLES[name]);del changed[key]
  with pytest.raises(ValidationError):validator(schema,name).validate(changed)
 with pytest.raises(ValidationError):validator(schema,name).validate(dict(EXAMPLES[name],token='forged'))


@pytest.mark.parametrize('amount',[MIN,MAX,0,-1,1])
@pytest.mark.parametrize('name',['RetainedGLRow','RetainedAdjustmentRow'])
def test_exact_signed_minor_units(schema,name,amount):
 validator(schema,name).validate(dict(EXAMPLES[name],amount_minor=amount))
 assert strict_decode(canonical(amount))==amount


@pytest.mark.parametrize('amount',[MIN-1,MAX+1,True,False,'1',None,0.5])
@pytest.mark.parametrize('name',['RetainedGLRow','RetainedAdjustmentRow'])
def test_bad_minor_units_reject(schema,name,amount):
 with pytest.raises(ValidationError):validator(schema,name).validate(dict(EXAMPLES[name],amount_minor=amount))


@pytest.mark.parametrize('name,field',[('RetainedGLRow','source_row'),('RetainedFileOrigin','byte_length'),('RetainedAdjustmentRow','version')])
@pytest.mark.parametrize('value',[0,-1,MAX+1,True,None,'1',1.5])
def test_positive_integer_boundaries(schema,name,field,value):
 with pytest.raises(ValidationError):validator(schema,name).validate(dict(EXAMPLES[name],**{field:value}))


@pytest.mark.parametrize('name,field',[('RetainedGLRow','source_row'),('RetainedFileOrigin','byte_length'),('RetainedAdjustmentRow','version')])
@pytest.mark.parametrize('value',[1,MAX])
def test_positive_integer_endpoints(schema,name,field,value):
 validator(schema,name).validate(dict(EXAMPLES[name],**{field:value}))


@pytest.mark.parametrize('field',['quantity_decimal','fx_rate'])
@pytest.mark.parametrize('value',['0','-0','1.00','-1.25',None])
def test_decimal_reference_text_preserved(schema,field,value):
 row=dict(GL,**{field:value});validator(schema,'RetainedGLRow').validate(row)
 assert strict_decode(canonical(row))[field]==value


@pytest.mark.parametrize('value',['1e2','+1','01.2',1.25,True,'NaN','1\n'])
def test_invalid_decimal_reference(schema,value):
 with pytest.raises(ValidationError):validator(schema,'RetainedGLRow').validate(dict(GL,fx_rate=value))


@pytest.mark.parametrize('text',['',"' =SUM(A1) <script> & ₹",'a'*10000,'a'*10001,'e\u0301','é','\tline\n\u0000'])
def test_source_text_is_not_normalised_truncated_or_executed(schema,text):
 row=dict(GL,description=text);validator(schema,'RetainedGLRow').validate(row)
 assert strict_decode(canonical(row))['description']==text
 assert canonical(row)==canonical(dict(reversed(list(row.items()))))


@pytest.mark.parametrize('value',['draft','applied','reversed'])
def test_status_captured_not_invented_financial_membership(schema,value):
 validator(schema,'RetainedAdjustmentRow').validate(dict(ADJ,status=value))
 assert strict_decode(canonical(dict(ADJ_IMAGE,row=dict(ADJ,status=value))))['row']['status']==value


def test_nullable_fx_is_not_fabricated(schema):
 for field,value in [('fx_currency','KWD'),('fx_amount_minor',-1),('fx_rate','0')]:
  row=dict(GL,**{field:value});validator(schema,'RetainedGLRow').validate(row)
  for other in set(['fx_currency','fx_amount_minor','fx_rate'])-{field}:assert row[other] is None


@pytest.mark.parametrize('value',['inr','US','USDD','INR\n',1])
def test_currency_reference_syntax(schema,value):
 with pytest.raises(ValidationError):validator(schema,'RetainedGLRow').validate(dict(GL,fx_currency=value))


def test_vendor_label_mode_and_source_timezone_text(schema):
 row=dict(GL,vendor_id='Vendor ₹ Private Ltd',vendor_source='column',posted_at='03/04/2026 09:00 local')
 validator(schema,'RetainedGLRow').validate(row)
 assert strict_decode(canonical(row))==row


@pytest.mark.parametrize('field,value',[('gl_row_id','a'*31),('gl_row_id','A'*32),('gl_row_id','a'*32+'\n'),
 ('layer','gl_adj'),('vendor_source','guessed'),('origin',None),('posting_date','2026-02-30'),('document_date','03/04/26')])
def test_invalid_source_fields(schema,field,value):
 with pytest.raises(ValidationError):validator(schema,'RetainedGLRow').validate(dict(GL,**{field:value}))


@pytest.mark.parametrize('value',[{'codec':'fpa-source-v2','kind':'gl','row':GL},
 {'codec':'fpa-source-v1','kind':'gl','row':ADJ},{'codec':'fpa-source-v1','kind':'adjustment','row':GL}])
def test_kind_codec_pairing(schema,value):
 with pytest.raises(ValidationError):validator(schema,'RetainedSourceImage').validate(value)


@pytest.mark.parametrize('value',[b'{"a":1,"a":2}',b'{"a":1,"\\u0061":2}',b'{"a":1.0}',b'{"a":1e0}',
 b'{"a":NaN}',b'{"a":Infinity}',b'{"a":-Infinity}',b'\xef\xbb\xbf{}',b'{"x":"\xff"}',
 b'{"x":"\\ud800"}',b'{"x":"\\udfff"}',b'{"a":-0}',b'{ "a":1}',b'{"a":1}\n',
 b'{"z":null,"a":1}',b'{"a":"\\u20b9"}'])
def test_strict_retained_decode_rejects_noncanonical_or_lossy_input(value):
 with pytest.raises((ValueError,UnicodeError)):strict_decode(value)


@pytest.mark.parametrize('value',[1.0,1.25,math.nan,math.inf,{1:'bad'},'\ud800'])
def test_encoder_refuses_lossy_or_nonunicode_objects(value):
 with pytest.raises((ValueError,UnicodeError)):canonical(value)


@pytest.mark.parametrize('obj,data,sha',[
 ({},b'{}','44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a'),
 ({'z':None,'a':1},b'{"a":1,"z":null}','d898aa36fe59fe1b7fcbcad5943548b75b80e65bf34a76b209c9eae8086dd0d0'),
 ({'text':'₹','n':-1},'{"n":-1,"text":"₹"}'.encode(),'032160d745bcea79142858f5764010c5712e6ffbb1cdb463a2827eb4c798f883')])
def test_literal_canonical_vectors(obj,data,sha):
 assert canonical(obj)==data
 assert hashlib.sha256(data).hexdigest()==sha
 assert strict_decode(data)==obj


def test_literal_control_escaping_and_array_order():
 assert canonical({'text':'\b\t\n\f\r\u0000/"\\'})==b'{"text":"\\b\\t\\n\\f\\r\\u0000/\\"\\\\"}'
 assert canonical([2,1])==b'[2,1]'
 assert canonical('é')!=canonical('e\u0301')
 assert canonical('1.0')!=canonical('1.00')


def test_historical_image_survives_live_enrichment_and_supersession():
 old=record(IMAGE);live=copy.deepcopy(GL)
 live.update(vendor_id='V01',vendor_source='ap_match')
 new=record(dict(IMAGE,row=live))
 assert old['content_sha256']!=new['content_sha256']
 assert old['image']['row']['vendor_id'] is None
 member={(PID,old['content_sha256'])}
 assert model_lookup(old,PID,member,{(PID,FILE_SHA):FILE_BYTES},set())==GL
 assert digest(dict(ADJ_IMAGE,row=dict(ADJ,status='reversed',version=2)))!=digest(ADJ_IMAGE)


@pytest.mark.parametrize('fault',['project','membership','missing_file','file_corrupt','byte_length','row_identity','digest','ordinary_file_hash'])
def test_contextual_failures_never_fall_back_to_current_data(fault):
 rec=copy.deepcopy(record(IMAGE));member={(PID,rec['content_sha256'])};files={(PID,FILE_SHA):FILE_BYTES};project=PID
 if fault=='project':project='prj_000000000002'
 elif fault=='membership':member=set()
 elif fault=='missing_file':files={}
 elif fault=='file_corrupt':files[(PID,FILE_SHA)]=b'x'*26
 elif fault=='byte_length':rec['image']['row']['origin']['byte_length']=25
 elif fault=='row_identity':rec['image']['row']['gl_row_id']='0'*32
 elif fault=='digest':rec['content_sha256']='0'*64;member={(PID,'0'*64)}
 elif fault=='ordinary_file_hash':rec['image']['row']['origin']['batch_file_sha256']='a'*64
 # Rehash malformed context cases so a digest mismatch cannot mask the target failure.
 if fault in ['byte_length','row_identity','ordinary_file_hash']:
  rec['content_sha256']=digest(rec['image']);member={(PID,rec['content_sha256'])}
 with pytest.raises(ValueError):model_lookup(rec,project,member,files,set())


def test_connector_content_hash_is_not_a_byte_hash(schema):
 rec=record(dict(IMAGE,row=CONNECTOR));validator(schema,'RetainedSourceRecord').validate(rec)
 assert not relational_errors(rec)
 assert model_lookup(rec,PID,{(PID,rec['content_sha256'])},{(PID,FILE_SHA):FILE_BYTES},set())==CONNECTOR
 assert rec['image']['row']['origin']['batch_file_sha256']!=hashlib.sha256(FILE_BYTES).hexdigest()


def test_generated_opening_requires_real_same_project_run(schema):
 rec=record(dict(IMAGE,row=OPENING));validator(schema,'RetainedSourceRecord').validate(rec)
 membership={(PID,rec['content_sha256'])}
 with pytest.raises(ValueError):model_lookup(rec,PID,membership,{},set())
 assert model_lookup(rec,PID,membership,{}, {(PID,'ye_2025')})==OPENING


def test_prior_period_and_month_two_rows_keep_their_own_period(schema):
 for period in ['2025-P12','2026-P02']:
  row=dict(GL,period_id=period);validator(schema,'RetainedGLRow').validate(row)
  assert record(dict(IMAGE,row=row))['image']['row']['period_id']==period


def test_three_mutations_caught(schema):
 mutants=[]
 s=copy.deepcopy(schema);s['$defs']['RetainedSourceImage']['properties']['codec']={'const':'fpa-source-v0'};mutants.append(s)
 s=copy.deepcopy(schema);s['$defs']['RetainedGLRow']['allOf'][0]['else']={};mutants.append(s)
 s=copy.deepcopy(schema);s['$defs']['RetainedGLRow']['properties']['source_row']['minimum']=2;mutants.append(s)
 for mutant in mutants:
  with pytest.raises((ValidationError,AssertionError)):assert_oracles(mutant)
 assert_oracles(schema)


def test_attachment_is_internal_and_shared_primitives_match(schema):
 public=json.loads((ROOT/'docs/api_job_schemas.json').read_text())
 for name in PRIMITIVES:assert schema['$defs'][name]==public['$defs'][name]
 assert set(EXAMPLES).isdisjoint(public['$defs'])
 Draft202012Validator.check_schema(schema)
 validator(schema,'RetainedSourceRecord').validate(record(IMAGE)) # validates every local ref
 doc=(ROOT/'docs/02_DATA_DICTIONARY.md').read_text()
 index=(ROOT/'docs/90_API_PAYLOAD_SCHEMAS_DETAILED.md').read_text()
 for name in EXAMPLES:assert name in doc and name in index
 assert 'never UNIQUE(project_id,row_kind,source_row_id)' in doc
 gen=(ROOT/'tools/generate_work_plan.py').read_text()
 assert 'retained_source_rows' in gen and 'test_api_source_contract.py' in gen
 assert '§7 deltas 1–16 and delta 17' in (ROOT/'docs/WORK_PLAN.md').read_text()


def projection(rec):
 image=rec['image'];row=image['row']
 return dict(project_id=rec['project_id'],content_sha256=rec['content_sha256'],row_kind=image['kind'],
             source_row_id=row['gl_row_id'] if image['kind']=='gl' else row['adj_id'],
             period_id=row['period_id'],payload_json=canonical(image).decode('utf-8'))


def model_insert(store,rec,schema):
 """Copy-on-write map oracle only, NOT SQLite transactions or crash recovery."""
 validator(schema,'RetainedSourceRecord').validate(rec)
 if relational_errors(rec):raise ValueError('record mismatch')
 row=projection(rec);key=(rec['project_id'],rec['content_sha256'])
 if key in store and store[key]!=row:raise ValueError('existing bytes/scalars differ')
 result=copy.deepcopy(store);result[key]=row
 return result


def test_deduplication_compares_bytes_and_every_scalar(schema):
 rec=record(IMAGE);stored=model_insert({},rec,schema)
 assert model_insert(stored,rec,schema)==stored
 for column in projection(rec):
  corrupt=copy.deepcopy(stored);corrupt[(PID,rec['content_sha256'])][column]='corrupt'
  before=copy.deepcopy(corrupt)
  with pytest.raises(ValueError):model_insert(corrupt,rec,schema)
  assert corrupt==before


def test_same_source_id_can_retain_multiple_images(schema):
 a=record(IMAGE);b=record(dict(IMAGE,row=dict(GL,vendor_id='V01',vendor_source='ap_match')))
 store=model_insert(model_insert({},a,schema),b,schema)
 assert len(store)==2
 assert store[(PID,a['content_sha256'])]['source_row_id']==store[(PID,b['content_sha256'])]['source_row_id']
 assert strict_decode(store[(PID,a['content_sha256'])]['payload_json'].encode())['row']['vendor_id'] is None


@pytest.mark.parametrize('field',['created_by','reason'])
@pytest.mark.parametrize('value',['',None])
def test_adjustment_attribution_not_omitted(schema,field,value):
 with pytest.raises(ValidationError):validator(schema,'RetainedAdjustmentRow').validate(dict(ADJ,**{field:value}))


@pytest.mark.parametrize('field,value',[('reason',' \t\n'),('status','deleted'),('source','connector'),('kind','automatic'),
 ('created_at','2026-10-15T10:00:00+00:00'),('updated_at','2026-02-30T10:00:00Z')])
def test_bad_adjustment_fields(schema,field,value):
 with pytest.raises(ValidationError):validator(schema,'RetainedAdjustmentRow').validate(dict(ADJ,**{field:value}))


@pytest.mark.parametrize('field',['description','posted_by','source_file','vendor_id'])
def test_lone_surrogates_rejected_by_internal_text_schema(schema,field):
 row=dict(GL,**{field:'bad\ud800'} )
 if field=='vendor_id':row['vendor_source']='column'
 with pytest.raises(ValidationError):validator(schema,'RetainedGLRow').validate(row)


def test_integral_looking_float_tokens_rejected_before_row_validation(schema):
 data=canonical(IMAGE)
 for token in [b'-12500050.0',b'-12500050e0',b'NaN']:
  damaged=data.replace(b'"amount_minor":-12500050',b'"amount_minor":'+token)
  assert damaged!=data
  with pytest.raises(ValueError):strict_decode(damaged)
 validator(schema,'RetainedSourceImage').validate(strict_decode(data))


def test_digest_binds_codec_kind_scope_origin_and_every_source_field():
 # Every captured field matters even if displayed monetary value is unchanged.
 for field in GL:
  altered=copy.deepcopy(IMAGE)
  value=altered['row'][field]
  altered['row'][field]=None if value is not None else 'different'
  assert digest(altered)!=GL_DIGEST,field
 assert hashlib.sha256(canonical(IMAGE)).hexdigest()!=GL_DIGEST # domain separator matters
 assert digest(dict(IMAGE,codec='fpa-source-v2'))!=GL_DIGEST
 assert digest(dict(IMAGE,kind='adjustment'))!=GL_DIGEST


def test_wrapper_project_equality_is_relational_not_just_schema(schema):
 rec=dict(record(IMAGE),project_id='prj_000000000002')
 validator(schema,'RetainedSourceRecord').validate(rec) # structurally well formed, still invalid
 assert relational_errors(rec)==['project']
 with pytest.raises(ValueError):model_insert({},rec,schema)


def test_retained_file_names_never_choose_file_lookup(schema):
 row=dict(GL,source_file='../../private/<script>=cmd.csv')
 rec=record(dict(IMAGE,row=row));validator(schema,'RetainedSourceRecord').validate(rec)
 assert model_lookup(rec,PID,{(PID,rec['content_sha256'])},{(PID,FILE_SHA):FILE_BYTES},set())==row


def test_stored_period_and_payload_columns_match_declared_table():
 doc=(ROOT/'docs/02_DATA_DICTIONARY.md').read_text()
 line=next(line for line in doc.splitlines() if line.startswith('| retained_source_rows |'))
 assert re.findall(r'([a-z_][a-z_0-9]*) TEXT',line.split('|')[2])==list(projection(record(IMAGE)))
 assert projection(record(IMAGE))['payload_json']==canonical(IMAGE).decode()
 assert 'content_sha256' not in strict_decode(projection(record(IMAGE))['payload_json'].encode())


def test_canonical_key_order_is_unicode_scalar_order():
 # Supplementary scalar sorts after U+E000 (not UTF-16 surrogate order).
 assert canonical({'😀':2,'\ue000':1})=='{"\ue000":1,"😀":2}'.encode()
 assert strict_decode(canonical({'😀':2,'\ue000':1}))=={'\ue000':1,'😀':2}


def test_three_more_encoder_faults_fail_literal_digest_oracles():
 with pytest.raises(AssertionError):
  assert hashlib.sha256(b'FPA-SOURCE-IMAGE-v0\n'+canonical(IMAGE)).hexdigest()==GL_DIGEST
 with pytest.raises(AssertionError):
  assert json.dumps({'text':'₹'},ensure_ascii=True,separators=(',',':')).encode()==b'{"text":"\xe2\x82\xb9"}'
 with pytest.raises(AssertionError):
  changed=copy.deepcopy(IMAGE);changed['row']['source_row']+=1
  assert digest(changed)==GL_DIGEST
