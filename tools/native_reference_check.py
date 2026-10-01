"""Optional oracle check for the project's seven fixed, authored hosted-C examples.
Never exposed to web users; never accepts submitted source. Requires local GCC.
"""
import json
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from core.code_runner import execute
if not shutil.which('gcc'):raise SystemExit('Install GCC to run this optional native reference check.')
track=next(t for t in json.loads((root/'core/content/catalog.json').read_text()) if t['engine']=='c')
count=0
with tempfile.TemporaryDirectory(prefix='bare-metal-native-') as tmp:
    for i,lesson in enumerate(track['lessons'][:7]):
        src=Path(tmp)/f'reference-{i}.c';exe=Path(tmp)/f'reference-{i}';src.write_text(lesson['starter_code'])
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra',str(src),'-o',str(exe)],check=True,capture_output=True,timeout=10)
        native=subprocess.run([str(exe)],check=True,capture_output=True,text=True,timeout=2)
        virtual=execute(lesson['starter_code'],'c');assert not virtual['errors'] and native.stdout==virtual['output'],lesson['title'];count+=1
print(f'PASS: {count} authored C reference outputs agree with GCC native execution.')
