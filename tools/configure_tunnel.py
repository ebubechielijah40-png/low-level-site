"""Create an owner-readable environment for the existing HTTPS dev tunnel."""
import os
import re
import secrets
import sys
from pathlib import Path
from urllib.parse import urlsplit
if len(sys.argv)!=2:raise SystemExit('Usage: python tools/configure_tunnel.py https://YOUR-TUNNEL.devtunnels.ms/')
try:
    url=urlsplit(sys.argv[1]);port=url.port
except ValueError:raise SystemExit('Use a valid HTTPS development-tunnel address.')
host=url.hostname or ''
if url.scheme!='https' or not re.fullmatch(r'[a-z0-9.-]+\.devtunnels\.ms',host) or url.username or url.password or port or url.path not in ('','/') or url.query or url.fragment:
    raise SystemExit('Use the exact HTTPS devtunnels.ms address without credentials, port, query or extra path.')
target=Path(__file__).resolve().parents[1]/'.env.deploy'
if target.exists():raise SystemExit('Existing .env.deploy kept unchanged. Reuse it; update its host/origin if the tunnel changed. Keep the saved secret.')
key=os.environ.get('DJANGO_SECRET_KEY','')
if not key or key=='local-development-only-change-before-deployment':key=secrets.token_urlsafe(48)
if not re.fullmatch(r'[A-Za-z0-9_!@%^*()+,.:/=-]+',key):raise SystemExit('Your exported key needs custom quoting. Configure .env.deploy manually using .env.example.')
values={'DJANGO_DEBUG':'0','DJANGO_SECRET_KEY':key,'DJANGO_ALLOWED_HOSTS':f'127.0.0.1,localhost,{host}',
        'DJANGO_CSRF_TRUSTED_ORIGINS':'https://'+host,'DJANGO_HTTPS':'0','DJANGO_TRUST_PROXY_SSL':'0',
        'GUNICORN_BIND':'127.0.0.1:8000','WEB_CONCURRENCY':'2'}
with open(target,'x',opener=lambda path,flags:os.open(path,flags,0o600)) as file:
    file.write('# Private tunnel environment. Keep the secret stable across restarts.\n')
    for name,value in values.items():file.write(f"{name}='{value}'\n")
print('Created .env.deploy with exact tunnel hosts and a stable private secret. Load it before preparing/starting the server.')
