"""Reproduce all authored reference checks without relying on a seeded database."""
import json
import os
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','language.settings')
import django;django.setup()
from core.code_runner import execute
from core.views import state_checks
counts={'lesson_examples':0,'lab_reference_examples':0,'intentional_lab_failures':0}
for track in json.loads((root/'core/content/catalog.json').read_text()):
    for lesson in track['lessons']:
        r=execute(lesson['starter_code'],track['engine']);checks=state_checks(r,lesson['expected_state'])
        assert not r['errors'] and checks and all(x['passed'] for x in checks),(lesson['title'],r['errors'],checks)
        counts['lesson_examples']+=1
for system in json.loads((root/'core/content/hardware.json').read_text()):
    for lab in system['labs']:
        for engine in ('c','assembly'):
            r=execute(lab['reference_'+engine],engine)
            assert not r['errors'] and all(x['passed'] for x in state_checks(r,lab['expected_state'])),lab['title']
            counts['lab_reference_examples']+=1
            starter=lab['starter_code_c'] if engine=='c' else lab['starter_code_asm'];r=execute(starter,engine)
            assert not r['errors'] and not all(x['passed'] for x in state_checks(r,lab['expected_state'])),lab['title']
            counts['intentional_lab_failures']+=1
print(json.dumps({'status':'PASS',**counts},indent=2))
