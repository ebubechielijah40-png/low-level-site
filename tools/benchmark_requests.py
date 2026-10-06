"""Measure application responses on a disposable DB, excluding network/browser/load."""
import argparse, io, json, math, os, platform, secrets, sys, tempfile, time
from itertools import count
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--samples',type=int,default=30)
parser.add_argument('--budget-ms',type=float,default=300)
parser.add_argument('--output',type=Path)
parser.add_argument('--fail',action='store_true')
args=parser.parse_args()
if not 5<=args.samples<=50:parser.error('Use 5–50 samples to stay inside the per-user execution quota.')
with tempfile.TemporaryDirectory(prefix='bare-metal-benchmark-') as tmp:
    os.environ.update(DJANGO_SETTINGS_MODULE='language.settings',DJANGO_DEBUG='0',DJANGO_SECRET_KEY=secrets.token_urlsafe(48),DJANGO_HTTPS='0',DJANGO_ALLOWED_HOSTS='testserver',DJANGO_DB_PATH=str(Path(tmp)/'bench.sqlite3'))
    import django
    django.setup()
    from django.conf import settings
    from django.contrib.auth.models import User
    from django.core.management import call_command
    from django.db import connection
    from django.test import Client
    from django.test.utils import CaptureQueriesContext
    from core.models import Lesson, HardwareChallenge
    settings.STATIC_ROOT=Path(tmp)/'staticfiles'
    for command in ('migrate','seed_lessons','seed_hardware','collectstatic'):
        options={'interactive':False} if command in ('migrate','collectstatic') else {}
        call_command(command,verbosity=0,stdout=io.StringIO(),**options)
    rows=[]
    def measure(label,client,method,url,data=None,prepare=None,expected=200):
        def fetch():
            payload=data() if callable(data) else data
            if method=='FORM':return client.post(url,payload,HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
            if method=='POST':return client.post(url,json.dumps(payload),content_type='application/json',HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
            return client.get(url)
        if prepare:prepare()
        start=time.perf_counter();response=fetch();cold=(time.perf_counter()-start)*1000
        assert response.status_code==expected,(label,response.status_code)
        if method=='POST':assert not response.json().get('errors'),label
        for _ in range(3):
            if prepare:prepare()
            fetch()
        times=[]
        for _ in range(args.samples):
            if prepare:prepare()
            start=time.perf_counter();response=fetch();times.append((time.perf_counter()-start)*1000)
            assert response.status_code==expected,(label,response.status_code)
        if prepare:prepare()
        with CaptureQueriesContext(connection) as queries:fetch()
        values=sorted(times)
        rows.append({'request':label,'samples':len(values),'cold_ms':round(cold,2),'p50_ms':round(values[len(values)//2],2),'p95_ms':round(values[math.ceil(len(values)*.95)-1],2),'max_ms':round(max(values),2),'queries':len(queries),'response_bytes':len(response.content)})
    client=Client(enforce_csrf_checks=True)
    measure('GET landing',client,'GET','/');measure('GET login',client,'GET','/login/')
    password=secrets.token_urlsafe(24);User.objects.create_user('benchmark_auth',password=password)
    def auth_page(url):client.logout();client.get(url)
    measure('POST login',client,'FORM','/login/',{'username':'benchmark_auth','password':password},prepare=lambda:auth_page('/login/'),expected=302)
    accounts=count()
    measure('POST signup',client,'FORM','/register/',lambda:{'username':f'benchmark_signup_{next(accounts)}','email':'bench@example.invalid','password':password,'confirm_password':password},prepare=lambda:auth_page('/register/'),expected=302)
    client.force_login(User.objects.create_user('benchmark_pages'))
    lesson=Lesson.objects.filter(language__engine='c').first();lab=HardwareChallenge.objects.get(system__slug='pc',order=2)
    for label,url in (('GET dashboard','/dashboard/'),('GET learning path','/languages/'),('GET C lesson',f'/lessons/{lesson.pk}/'),('GET RAM configuration',f'/hardware/pc/{lab.pk}/'),('GET OS workspace','/os/')):measure(label,client,'GET',url)
    for engine in ('machine','assembly','c','rust','verilog','boot'):
        client.force_login(User.objects.create_user('benchmark_'+engine));client.get('/playground/')
        lesson=Lesson.objects.filter(language__engine=engine).first()
        measure('POST execute '+engine,client,'POST','/api/execute/',{'language':engine,'code':lesson.starter_code,'context_kind':'free'})
    report={'date_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':platform.python_version(),'django':django.get_version(),'scope':'Django test client; DEBUG=0; fresh SQLite; sequential warmed requests; no network/browser/load','budget_ms':args.budget_ms,'results':rows,'passes_application_budget':all(r['p95_ms']<args.budget_ms for r in rows)}
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if args.fail and not report['passes_application_budget']:sys.exit(1)
