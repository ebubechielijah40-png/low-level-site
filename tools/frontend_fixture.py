"""Render genuine Django pages and engine results for optional DOM checks."""
import io,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='bare-metal-dom-') as tmp:
    os.environ.update(DJANGO_SETTINGS_MODULE='language.settings',DJANGO_DEBUG='1',DJANGO_DB_PATH=str(Path(tmp)/'test.sqlite3'))
    import django
    django.setup()
    from django.contrib.auth.models import User
    from django.core.management import call_command
    from django.test import Client
    from core.code_runner import execute
    from core.hardware_sim import effects
    from core.models import Lesson,HardwareChallenge
    for name in ('migrate','seed_lessons','seed_hardware'):call_command(name,verbosity=0,stdout=io.StringIO())
    client=Client();(out/'register.html').write_bytes(client.get('/register/').content)
    client.force_login(User.objects.create_user('dom_learner'))
    lesson=Lesson.objects.filter(language__engine='assembly').first();lab=HardwareChallenge.objects.get(system__slug='pc',order=2)
    for name,url in (('lesson',f'/lessons/{lesson.pk}/'),('lab',f'/hardware/pc/{lab.pk}/'),('dashboard','/dashboard/')):(out/(name+'.html')).write_bytes(client.get(url).content)
    assembly=execute('li t0,250\nagain: addi t0,t0,-1\nbnez t0,again\necall','assembly')
    assert not assembly['errors'] and len(assembly['trace'])==200
    ram=execute('int main(void){mmio_write(0xf000,512);mmio_write(0xf004,1);mmio_write(0xf008,1);}','c')
    ram.update(model=effects(lab,ram['state']),checks=[{'name':'RAM target','passed':True}],passed=True)
    (out/'results.json').write_text(json.dumps({'assembly':assembly,'ram':ram}))
