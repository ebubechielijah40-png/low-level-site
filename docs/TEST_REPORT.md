# Verification report — 1 October 2026

The initial upgrade's results follow. The [performance/deployment follow-up](PERFORMANCE_AND_DEPLOYMENT.md) records 167 passing Django tests and production, upgrade and DOM checks. Actual live browser latency remains unverified.

## Passed

| Check | Observed result | Evidence |
|---|---|---|
| Django system check | No issues | Automated-test log |
| Migration consistency | No changes detected | makemigrations --check --dry-run |
| Django test suite | **163 tests passed** in the recorded run | evidence/automated-tests.txt |
| Authored lesson references | **33** passed declared result checks | evidence/reference-checks.json |
| Configuration references | **26** passed: 13 labs × C/RV32I | evidence/reference-checks.json |
| Incomplete configuration starters | **26** executed without syntax errors and failed target checks as intended | evidence/reference-checks.json |
| Page integration | **82** page/language-variant responses rendered successfully | WorkspaceTests.test_all_pages_render |
| Real HTTP workflow | Registration, session cookies, CSRF, dashboard, code execution, RAM target checks, image save/download/boot passed | evidence/http-smoke.txt |
| Native C reference comparison | **7** authored C outputs matched GCC native output | evidence/native-reference-checks.txt |
| Kernel toolchain | Freestanding C/assembly compiled and linked to an ELF32 i386 executable | evidence/kernel-build.txt |
| JavaScript syntax | app.js, model.js, and browser_smoke.cjs parsed successfully | node --check |
| HTML structure | No duplicate IDs in login, signup, dashboard, lesson, RAM, and OS rendered templates | lxml structure check |
| Seeding | 6 tracks, 33 lessons, 6 systems, 13 configurations; rerun does not duplicate supplied catalogue | WorkspaceTests.test_seeds_are_idempotent |

The 59 authored reference tests are included in the 163-test suite. The reference script repeats those specific examples for a concise independently reproducible inventory; the totals are not added together as if they were distinct test cases.

## Meaningful failure coverage

C tests cover missing/implicit entry returns, multiple output calls, lexical scopes, pointer writes and lifetimes, array bounds, uninitialised locals, signed overflow, unsigned wrap, divide by zero, shift ranges, output/loop/call-depth limits, unsupported headers/formats/host functions, MMIO alignment, and structures. RV32I tests cover encoding, equivalence of assembly/machine execution, x0, signed/unsigned comparisons, shifts, loads/stores/endian order, branch budgets, labels, and malformed instructions. Rust tests cover immutability, conflicting borrows, direct owner access during mutable borrowing, shared-reference writes, and bounds. Verilog tests cover truth tables and unsupported/budgeted constructs. Boot tests cover signature, size, unsupported BIOS calls, and loops.

Application tests cover password policy/mismatch/duplicate names, login errors and safe redirects, POST-only logout, CSRF, authenticated APIs, invalid requests, request limits, exact lesson completion, private drafts, private image ownership, escaping, downloads, uploads, and server-verified configuration completion. The quantum model has a probability-normalisation and Bell-state result check.

## Not passed or not attempted

**Real-browser visual and interaction verification remains incomplete.** Playwright had no installed browser binary. Downloading Chromium returned an unusable blocked download. The available cloud browser rejected the local URL with ERR_BLOCKED_BY_CLIENT. No screenshot is presented as a rendered application screenshot. The included tools/browser_smoke.cjs is an executable future check, not a passed result.

**The freestanding ELF kernel was not booted in QEMU or on hardware.** QEMU and the GRUB rescue toolchain were unavailable. Compile/link and file-header inspection do not establish an executed native boot.

There was no physical-device validation, user learning study, formal accessibility audit, distributed-rate-limit/concurrency test, performance benchmark, penetration test, or external public deployment. The cooperative interpreter bounds are not a claim of a hardened native execution sandbox.

## Reproduce

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python tools/verify_examples.py
python tools/http_smoke.py
python tools/native_reference_check.py
bash tools/build_kernel.sh
node --check core/static/core/js/app.js
node --check core/static/core/js/model.js
```

Use README for the optional real-browser test and minikernel guide for native boot steps. Maintain the distinction between a passing current check and a planned future check when defending the project.
