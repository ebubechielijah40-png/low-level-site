#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  echo 'Commit or save local repository changes before updating the server.' >&2
  exit 1
fi
if [[ "${DJANGO_DEBUG:-1}" != 0 ]]; then
  echo 'Load your deployment environment (DJANGO_DEBUG=0) before preparing.' >&2
  exit 1
fi
git pull --ff-only origin main
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py prepare_deployment
echo 'Update prepared. Restart your service, or run bash tools/start_server.sh.'
