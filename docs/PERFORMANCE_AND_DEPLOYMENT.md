# Response-time and deployment update — 1 October 2026

Prepared against `main` at `ba486026` in `ebubechielijah40-png/low-level-site`. The screenshot shows the upgraded interface on the supplied tunnel. Live browser navigation timed out here; a later HTTP attempt failed at this environment's proxy connection before reaching the site. This is not proof that the owner's site is down. These new changes have not been pushed or activated remotely.

## Built changes

- Navigation fetches displayed lesson fields instead of full teaching/source/state. Dashboard total comes from those lessons: 8 queries instead of the baseline's 9.
- Teaching Markdown has an escaping-first, bounded 128-entry cache keyed by full text. Changed content produces a new result. Private pages and learner code are not cached.
- Console/checks update first; state, 200-row trace and encoding build on tab selection, once per result. Reset clears previous results.
- Models combine updates into one draw per frame; canvas buffers resize only when dimensions change. Decorative pixels run at most about 30 frames/second for ten seconds, pause offscreen/hidden, and are static for reduced motion.
- Pending status updates immediately. A 20-second request timeout restores controls and reports connection failure.
- Response headers expose application duration (`Server-Timing`) and running Git revision (`X-App-Revision`). Private pages, APIs and downloads use `private, no-store`.
- Debug-off WhiteNoise serves compressed, hashed, immutable static assets. Fresh HTML references new hashes after an update. Gunicorn replaces public `runserver` use.
- `window.bareMetalPerformance.snapshot()` holds diagnostics in this tab's memory: request time, application time, paint-opportunity estimates and supported event/long-task entries. It never uploads code or identities; navigation clears it and it retains 100 entries.
- Upgrade/start scripts, exact tunnel configuration, private coherent SQLite backups, legacy completion repair, an optional systemd example, and GitHub verification make releases repeatable.

## Measurements and evidence

The final check used Python 3.12.14, Django 6.1.1, pycparser 2.23, Gunicorn 26.2.0 and WhiteNoise 6.12.0. Thirty sequential samples per request used a disposable SQLite DB, `DEBUG=0`, and warmed templates. Other validation processes were also running. p95 uses nearest rank. Application timings exclude sockets, public network, browser rendering and field/concurrent-user load. Authentication includes normal password hashing/validation.

| Request | Application p95 |
|---|---:|
| Dashboard | 6.56 ms |
| C lesson | 3.87 ms |
| RAM configuration | 4.12 ms |
| Login | 276.09 ms |
| Signup | 257.38 ms |
| Small C run | 3.69 ms |

All sampled application paths passed the 300 ms budget locally. Over actual loopback HTTP through Gunicorn, 30 small C runs measured **12.97 ms p95**, with **12.17 ms application p95**. Gzip reduced the main script from **13,630 to 5,093 bytes**. See `evidence/performance-after.json`, `performance-production.txt`, `performance-tests.txt` and `performance-frontend.txt`.

Login leaves little room for network/paint in that budget. The site is not certified below 300 ms on the public URL. Deliberately expensive programs can take longer within the existing bounded runner contract. Keep pending feedback and completed-result time separate. These small before/after samples do not prove a universal percentage speedup.

Passed: 167 Django tests; system/migration checks; all 33 lesson and 26 lab references; 26 intentional lab-target failures; development HTTP smoke; production HTTPS-proxy/secure-cookie/static/compression/cache checks; fresh/repeated upgrades; known legacy and already-renamed completion/index recovery; deduplication with retained audit rows; account preservation; owner-readable coherent backups; partial-schema rejection; JavaScript/shell checks.

DOM checks pass using genuine Django pages and engine results, with jsdom mocking observers, canvas and network. They cover password eyes, pending state, lazy 200-row tables, refreshed results, tab reuse, reset, timeout recovery, local diagnostics, RAM telemetry, batched draws and buffer reuse. This is not pixel/layout/paint/INP proof. Chromium installation returned an unusable archive, and cloud browser navigation timed out. Actual browser/mobile/live latency remains unverified. The browser script records timings and screenshots when run in a working local browser. GitHub Actions has not run until this update is pushed.

## Apply and push

Save `Bare-Metal-Performance-Update.patch` to Downloads. Begin with your existing clean repository. These checks preserve local work and fail if it differs from the patch's base:

```bash
cd ~/low-level-site
git status --short
git pull --ff-only origin main
git apply --check ~/Downloads/Bare-Metal-Performance-Update.patch
git apply --index ~/Downloads/Bare-Metal-Performance-Update.patch
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py test --noinput
git commit -m "Improve response times and deployment updates"
git push origin main
```

If the patch check fails, keep the local changes and inspect the difference. Do not reset `.git` or the learner database. The patch changes the existing project in place and leaves the migration files intact.

## Activate the running tunnel

Stop the current app with Ctrl+C in its terminal, keeping the tunnel session running. Then:

```bash
cd ~/low-level-site
.venv/bin/python tools/configure_tunnel.py https://vzgspgkx-8000.uks1.devtunnels.ms/
set -a
source .env.deploy
set +a
.venv/bin/python manage.py prepare_deployment
bash tools/start_server.sh
```

The configuration helper runs once and refuses to overwrite a saved `.env.deploy`. Later, source the existing file. Preserve its secret; edit the exact host/origin if your tunnel changes. Changing the original development secret requires signing in again; accounts, drafts and progress remain in SQLite. Keep the backup path printed by preparation.

Upstream binds to `127.0.0.1:8000`; public access remains the existing HTTPS tunnel. Its upstream redirect is disabled to avoid a scheme-header loop, while cookies remain secure. A permanent HTTPS host should use `DJANGO_HTTPS=1`, its correctly trusted proxy, and persistent database/backups storage.

Pushing to GitHub does not restart the process behind the tunnel. The app, tunnel and computer must stay running. For future pushes to a separate server checkout, stop the app, load its existing environment, run `bash tools/update_server.sh`, then `bash tools/start_server.sh`. The updater requires clean work and fast-forward history; it does not reset files. If editing/running in the same checkout, prepare and restart the already-present code.

The optional systemd service example requires confirming its user/paths/environment. Once installed, use systemctl to stop/start that service around preparation; do not launch a second server on port 8000.

## Check the release and speed

```bash
curl -I https://vzgspgkx-8000.uks1.devtunnels.ms/
git rev-parse --short=12 HEAD
```

After restarting, `X-App-Revision` should match the new hash and `Server-Timing` should appear. Browser Network tools should show hashed static URLs and immutable caching. Run small examples and read elapsed time in the terminal footer.

In browser console:

```javascript
window.bareMetalPerformance.snapshot()
```

`request.ms` includes fetch and JSON parsing. `server_ms` comes from the header. Their difference includes transport and client processing, not exact network-only time. Two animation frames estimate a paint opportunity for `run_feedback`/`run_result`; this is not certified paint or INP. Event/long-task entries require browser support. Review warm/cold navigation and p95 across learner devices/connections. Keep normal password hashing intact.

Reproduce locally with disposable data:

```bash
.venv/bin/python tools/benchmark_requests.py --output evidence/performance-local.json --fail
.venv/bin/python tools/deployment_smoke.py
.venv/bin/python tools/production_smoke.py
npm install --no-save jsdom@30.1.1
.venv/bin/python tools/frontend_fixture.py /tmp/bare-metal-dom
node tools/frontend_dom_smoke.cjs /tmp/bare-metal-dom
```

Run `tools/browser_smoke.cjs` on a disposable local development DB/server; it creates its own QA account/images. The existing run quota is process-local; multiple workers do not share one global 60-run limit. Shared atomic rate limiting remains separate work. A worker timeout bounds stuck processes; it does not promise every program finishes below the interaction target.

References: [Django deployment](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/), [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html), [Gunicorn](https://gunicorn.org/reference/settings/), [Microsoft tunnels](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/security).

The initial report remains the original upgrade's evidence; this follow-up adds observed results without inventing browser, publishing, kernel-boot or live deployment outcomes.
