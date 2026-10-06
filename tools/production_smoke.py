"""Test DEBUG=0/Gunicorn/WhiteNoise over loopback, emulating a trusted HTTPS proxy.
Secure browser cookies are carried explicitly across the loopback upstream hop.
All accounts, databases, secrets and images are disposable.
"""
import gzip, http.client, json, math, os, re, secrets, socket, subprocess, sys, tempfile, time, urllib.parse
from http.cookies import SimpleCookie
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='bare-metal-production-') as tmp:
    env=os.environ|{'DJANGO_DEBUG':'0','DJANGO_SECRET_KEY':secrets.token_urlsafe(48),'DJANGO_ALLOWED_HOSTS':'127.0.0.1','DJANGO_HTTPS':'1','DJANGO_TRUST_PROXY_SSL':'0','APP_REVISION':'production-smoke','DJANGO_DB_PATH':str(Path(tmp)/'test.sqlite3'),'DJANGO_STATIC_ROOT':str(Path(tmp)/'staticfiles')}
    r=subprocess.run([sys.executable,'manage.py','prepare_deployment'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stdout+r.stderr
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    log=Path(tmp)/'gunicorn.log';cookies=SimpleCookie()
    with log.open('w+') as output:
        server=subprocess.Popen([sys.executable,'-m','gunicorn','language.wsgi:application','--config','gunicorn.conf.py','--bind',f'127.0.0.1:{port}','--workers','1'],cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT)
        def fetch(path,data=None,form=False,extra=None):
            headers={'X-Forwarded-Proto':'https','Origin':f'https://127.0.0.1:{port}','Cookie':'; '.join(f'{k}={v.value}' for k,v in cookies.items())};body=None
            if data is not None:
                headers.update({'X-CSRFToken':cookies['csrftoken'].value,'Content-Type':'application/x-www-form-urlencoded' if form else 'application/json'})
                body=urllib.parse.urlencode(data) if form else json.dumps(data)
            headers.update(extra or {});connection=http.client.HTTPConnection('127.0.0.1',port,timeout=10)
            try:
                connection.request('POST' if data is not None else 'GET',path,body=body,headers=headers)
                response=connection.getresponse();payload=response.read()
                for name,value in response.getheaders():
                    if name.lower()=='set-cookie':cookies.load(value)
                return response.status,dict(response.getheaders()),payload
            finally:connection.close()
        try:
            for _ in range(50):
                try:status,headers,body=fetch('/');break
                except (ConnectionError,OSError,http.client.HTTPException):
                    if server.poll() is not None:raise AssertionError('Gunicorn exited before readiness.')
                    time.sleep(.1)
            else:raise AssertionError('Gunicorn not ready.')
            assert status==200 and headers['X-App-Revision']=='production-smoke'
            assert 'app;dur=' in headers['Server-Timing'] and 'no-store' in headers['Cache-Control']
            asset=re.search(rb'src="(/static/core/js/app\.[a-f0-9]+\.js)"',body).group(1).decode()
            status,h,compressed=fetch(asset,extra={'Accept-Encoding':'gzip'})
            assert status==200 and h['Content-Encoding']=='gzip' and b'renderResultPanel' in gzip.decompress(compressed)
            assert 'immutable' in h['Cache-Control'] and 'public' in h['Cache-Control'] and 'Set-Cookie' not in h
            assert fetch(asset,extra={'If-None-Match':h['ETag']})[0]==304
            assert fetch('/register/')[0]==200 and cookies['csrftoken']['secure']
            password=secrets.token_urlsafe(24)
            status,h,_=fetch('/register/',{'username':'production_learner','email':'production@example.invalid','password':password,'confirm_password':password},form=True)
            assert status==302 and h['Location']=='/dashboard/' and cookies['sessionid']['secure']
            assert fetch('/dashboard/')[0]==200
            times=[];app=[]
            for _ in range(30):
                start=time.perf_counter();status,h,payload=fetch('/api/execute/',{'language':'c','code':'int main(void){printf("42");}','context_kind':'free'});times.append((time.perf_counter()-start)*1000)
                assert status==200 and json.loads(payload)['output']=='42'
                app.append(float(re.search(r'app;dur=([\d.]+)',h['Server-Timing'])[1]))
            sys.path.insert(0,str(ROOT))
            from core.runtime.boot_vm import DEFAULT_BOOT
            status,_,payload=fetch('/api/boot/save/',{'name':'Production test','code':DEFAULT_BOOT});assert status==200
            status,h,image=fetch(json.loads(payload)['download'])
            assert status==200 and len(image)==512 and image[-2:]==b'\x55\xaa'
            assert 'private' in h['Cache-Control'] and 'no-store' in h['Cache-Control']
            print('Production stack PASS: HTTPS proxy, secure session/CSRF cookies, signup, execution, hashed/gzip/immutable/304 static files, private boot downloads, revision/timing headers.')
            print(json.dumps({'scope':'DEBUG=0; Gunicorn sync; loopback HTTP; 30 sequential small C runs; no WAN/browser/load','c_run_http_p95_ms':round(sorted(times)[math.ceil(len(times)*.95)-1],2),'c_run_server_p95_ms':round(sorted(app)[math.ceil(len(app)*.95)-1],2),'static_raw_bytes':len(gzip.decompress(compressed)),'static_gzip_bytes':len(compressed)},indent=2))
        except Exception:output.flush();print(log.read_text(),file=sys.stderr);raise
        finally:
            server.terminate()
            try:server.wait(timeout=5)
            except subprocess.TimeoutExpired:server.kill();server.wait(timeout=5)
