"""Exercise the real WSGI stack over HTTP using an isolated temporary database."""
import json
import os
import re
import tempfile
import threading
import urllib.request
import http.cookiejar
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory(prefix='bare-metal-http-') as tmp:
    os.environ['DJANGO_DB_PATH']=str(Path(tmp)/'test.sqlite3')
    os.environ['DJANGO_SETTINGS_MODULE']='language.settings'
    import django
    django.setup()
    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application
    from wsgiref.simple_server import make_server,WSGIRequestHandler
    from core.models import Lesson,HardwareChallenge
    from core.runtime.boot_vm import DEFAULT_BOOT
    call_command('migrate',verbosity=0);call_command('seed_lessons',verbosity=0);call_command('seed_hardware',verbosity=0)
    class QuietHandler(WSGIRequestHandler):
        def log_message(self,*args):pass
    server=make_server('127.0.0.1',0,get_wsgi_application(),handler_class=QuietHandler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}';cookies=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    def fetch(path,data=None,kind='application/json'):
        headers={}
        if data is not None:
            body=json.dumps(data).encode() if kind=='application/json' else urllib.parse.urlencode(data).encode()
            token=next(c.value for c in cookies if c.name=='csrftoken');headers={'Content-Type':kind,'X-CSRFToken':token}
        else:body=None
        return client.open(urllib.request.Request(base+path,data=body,headers=headers),timeout=10)
    try:
        assert fetch('/register/').status==200
        r=fetch('/register/',{'username':'http_learner','email':'http@example.invalid','password':'HttpHarness#4920','confirm_password':'HttpHarness#4920'},'application/x-www-form-urlencoded');assert r.geturl().endswith('/dashboard/')
        lesson=Lesson.objects.filter(language__engine='c').first()
        r=json.load(fetch('/api/execute/',{'code':lesson.starter_code,'language':'c','context_kind':'lesson','context_id':lesson.pk}));assert r['passed']
        lab=HardwareChallenge.objects.get(system__slug='pc',order=2)
        code='int main(void){mmio_write(0xf000,512);mmio_write(0xf004,1);mmio_write(0xf008,1);}'
        r=json.load(fetch('/api/execute/',{'code':code,'language':'c','context_kind':'lab','context_id':lab.pk}));assert r['passed']
        project=json.load(fetch('/api/boot/save/',{'name':'HTTP smoke image','code':DEFAULT_BOOT}));image=fetch(project['download']).read();assert len(image)==512 and image[-2:]==b'\x55\xaa'
        r=json.load(fetch(f'/os/{project["id"]}/boot/',{}));assert 'BARE METAL OS' in r['screen']
        assert fetch('/hardware/').status==200
        print('HTTP smoke PASS: registration, session cookies, CSRF, dashboard, execution, hardware checks, boot save/download/run.')
    finally:server.shutdown();server.server_close();thread.join(timeout=5)
