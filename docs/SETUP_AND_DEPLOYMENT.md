# Setup, upgrades, and deployment

Follow the exact Linux or PowerShell commands in README. Python 3.12 is the recommended baseline. The verification environment used Python 3.12.14, Django 6.1.1 from the supplied dependency archive, and pycparser from the available runtime. The requirements range also permits supported Django 5.2/6.0 installations, but those additional versions were not separately tested here.

## Existing installation

Keep this repository's complete migration history, ending at `0006_alter_language_options_hardwarechallenge_component_and_more`. A different old branch used other 0005/0006 files: do not mix those files into this graph or fake all migrations.

Stop the app server, load your deployment environment, then run `python manage.py prepare_deployment`. It makes an owner-readable SQLite snapshot, handles the known existing completion-table/index collision, migrates, restores unique valid completions, seeds teaching, collects versioned compressed assets, and checks Django. It retains old completion rows and refuses unrelated/partial schemas. See [the follow-up guide](PERFORMANCE_AND_DEPLOYMENT.md). Seeds update the supplied catalogue and preserve unrelated custom lessons.

The attached database had no languages, lessons, lesson progress, or hardware progress. It had six systems and thirteen legacy hardware exercises. Those system/order identities are reused for the new configurations. The archive intentionally excludes the user's original database and account. Historical language counters in other installations remain present but are not treated as individual lesson-completion evidence. If other installations have old hardware-completion records, review them when replacing the exercises: their historical task meaning may differ from the new target.

## Environment variables

Settings reads operating-system environment variables, not a .env file automatically. See .env.example. For a local Bash session:

```bash
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DJANGO_ALLOWED_HOSTS=your-host.example
export DJANGO_HTTPS=1
```

Use the included Linux Gunicorn setup behind HTTPS and WhiteNoise for collected static assets. Keep the same private secret across restarts. `bash tools/start_server.sh` starts the service with its Git hash in `X-App-Revision`. The GitHub workflow tests pushes; it does not restart the owner's computer.

```bash
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Debug-off settings enable secure cookies and HTTPS redirect by default and refuse the bundled development secret. Configure trusted proxy headers only for a proxy you actually control. Do not broaden allowed hosts or CSRF origins merely to hide a routing problem.

For the existing tunnel, the helper in the follow-up guide creates an ignored `.env.deploy` once, with exact hosts/origin and an upstream bound to loopback. Its upstream HTTPS redirect is disabled to avoid scheme-header loops; public HTTPS and secure cookies remain. Other permanent HTTPS hosts should use `DJANGO_HTTPS=1` and configure their trusted proxy. Keep SQLite/backups on persistent storage.

## Before a public launch

The implementation is a final-year teaching platform, with bounded interpreters rather than arbitrary native-code execution. A public service still needs production session/storage configuration, atomic shared rate limiting, account abuse controls, quotas, backup/restore, request concurrency and hard process-resource limits, independent security review, and a completed browser/accessibility test run.

General native C/Rust/HDL execution requires a separate worker architecture: authenticated jobs, isolated nonprivileged workers, no exposed host paths, bounded CPU/RAM/storage, controlled network access, clean workspaces, and recorded results. Do not add `subprocess` execution of student code to the Django request handler.

Full native-kernel hosting similarly needs a compatible loader and a separate browser emulator or isolated VM worker. The current site hosts its documented first-stage BIOS image format. The included kernel's compile/link milestone must not be described as a verified VM boot.

## Troubleshooting

- Empty language list: run seed_lessons, then seed_hardware.
- ModuleNotFoundError: use the interpreter inside the virtual environment and install requirements there.
- Invalid host: add your actual hostname through DJANGO_ALLOWED_HOSTS; localhost is included for development.
- Missing editor styling: confirm `/static/core/css/style.css` is served and collect static for production. The site uses local files, not CDN assets.
- CSRF error: load the form/page from the same host before POSTing, and keep cookies enabled.
- Unsupported code: compare the construct with RUNNER_REFERENCE; the embedded interpreters deliberately accept subsets.
- Bad boot image: confirm exact 512-byte size and final 55 AA. Signature validity does not guarantee opcode support.
- Kernel build failure: the native example needs GNU assembler/linker and GCC with 32-bit freestanding output support; it is optional for the web application.
