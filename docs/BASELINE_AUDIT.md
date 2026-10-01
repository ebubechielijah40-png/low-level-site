# Baseline audit — 1 October 2026

The input is CL-fromgithub.zip, an existing Django project. No GitHub changes were made.

## Observed defects

- Three existing tests pass but cover only a regex runner. They do not exercise pages, authentication, execution endpoints, data seeding, or hardware.
- The supplied database contains 0 languages and 0 lessons, 6 hardware systems, 13 hardware exercises, and one existing user.
- Dashboard redirects to a language list; dashboard template has no working dashboard.
- Editor sends code to a remote public Piston endpoint. There is no same-origin execution API.
- Template scripts use `extra_js`, but the base template only renders `scripts`; editors never initialise on several pages.
- The C runner matches a few source patterns, rejects valid C without explicit return zero, and does not interpret most C.
- Assembly runner recognises text without executing instructions or reporting numeric registers.
- Machine language is incorrectly sent to a NASM assembly service.
- Hardware editor explicitly says execution is unavailable. Hardware listing depends on an arbitrary five-lesson unlock.
- Lesson completion uses two conflicting current-lesson conventions. Counts reflect a language row, not individual completed lessons.
- Registration does not apply Django password validators. No password visibility controls. Logout changes state through GET.
- No requirements, setup guide, runner specification, or project report. Bundled Linux virtualenv is not portable.

## Scope decision

Preserve Django and the existing model/migration history. Add bounded educational interpreters, inspectable processor state, integrated lessons, component configuration models, and per-user hosted boot images. Native untrusted binaries must never run in the web process. Simulation boundaries are visible in the UI and report.
