#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -x .venv/bin/python ]]; then
  echo 'Create .venv and install requirements.txt first.' >&2
  exit 1
fi
export APP_REVISION="$(git rev-parse --short=12 HEAD)"
if [[ "${DJANGO_DEBUG:-1}" != 0 ]]; then
  echo 'Load your deployment environment (DJANGO_DEBUG=0) before starting.' >&2
  exit 1
fi
exec .venv/bin/python -m gunicorn language.wsgi:application --config gunicorn.conf.py "$@"
