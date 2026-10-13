# Documentation and configuration upgrade

Final-year project implementation update, 13 October 2026.

## Problem and resulting behavior

The previous guides named many relevant topics but did not consistently connect prerequisite knowledge, machine state, a precise transformation, and observable evidence. Screenshots also showed historical x86 machine-language material opening in a C terminal and old lesson rows appearing beside the authored replacements. Updating source files alone did not remove that stale database teaching.

The upgrade expands all 33 existing language/OS guides and all 13 hardware guides, adds eight device-foundation lessons, embeds complete runnable examples, and provides a load/restore interaction within the existing split workspace. Every component guide explains the relevant prerequisite concepts and the difference between a stored request and physical operation. All configurations remain accessible without completion locks.

The current inventory is seven tracks, 41 lessons, 13 hardware guides, and 98 runnable documentation programs. Six of those programs deliberately demonstrate diagnostics. The new explanations include derivations, boundary inputs, state inspection and controlled mutations; word count is not used as evidence of learning effectiveness.

## Missing knowledge added

Languages can express operations but do not contain the configuration procedure of every device. The new focused device track adds address spaces/register contracts; activation, acknowledgement and timeouts; electrical timing and refresh budgets; interrupt/DMA/cache ownership; byte formats, blocks and network budgets; queue/parallel/failure-domain constraints; clocked-state/reset distinctions; and the two-qubit quantum-state foundations required by the existing ideal demonstrations.

The detailed configuration map is in `CURRICULUM_AND_CONFIGURATION.md`. No extra language was added merely to increase breadth. Software can reproduce the site's profiles using the existing C or RV32I engines. Real controller work still requires target-specific capabilities, platform APIs, sequencing and measurements; the site does not operate physical devices.

## Implementation

### Executable documentation

Runnable Markdown fences carry an engine and an experiment identifier. The renderer preserves literal source and exposes a load button only for complete marked programs. The frontend accepts only the active workspace engine, loads without executing, and retains the immediately preceding draft for restoration. Hardware C and assembly references use the existing language switch. On narrow layouts, loading brings the terminal into view.

`core/content_checks.py` reads the actual program from Markdown and runs it through the same engine as the site. It compares output/state with independently declared catalogue or experiment expectations. Additional truth-table programs have explicit expected output sequences; intentional failures compare diagnostic categories. Missing, duplicated or engine-incompatible runnable specifications fail verification.

The escaping-first renderer now handles permitted relative in-site and HTTPS links so prerequisite references work. Unsafe schemes and protocol-relative links are not rendered as clickable links; code remains literal. Content caching remains bounded and keyed by full text.

### Correct deployment of the authored curriculum

Migration 0007 adds archive flags to languages and lessons. Reseeding resolves canonical tracks by slug, updates current lesson rows, and archives catalogue-external historical rows without deleting their completions or drafts. Navigation, progress totals and execution contexts use active material. An old lesson link returns to the learning path instead of launching mismatched stale source.

The catalogue is the published curriculum. Custom teaching outside it remains stored but is archived on reseeding; include it in the catalogue if it should remain published. This is an explicit maintenance tradeoff in exchange for reliably removing stale teaching during upgrades.

`prepare_deployment` continues to take an owner-readable coherent SQLite backup before migration/seeding and collects production assets. The upgrade therefore changes both source and seeded teaching; a Git push by itself does not activate either the process or the database content on the owner's server.

### Telemetry corrections

RAM activation now uses the enable register at 0xF004, independently of the parity flag at 0xF008. Quantum shots are no longer reported as a generic Boolean enable state. Unsupported gate masks, non-two-qubit requests, and zero-shot profiles receive an explicit invalid-profile note without a misleading probability table. Valid profiles retain the exact ideal-state calculation and do not sample shots.

## Verification

| Check | Observed result |
|---|---|
| Django behavior suite | 287 tests passed in the recorded run |
| Documentation programs | all 98 matched declared output/state or intentional diagnostic |
| Catalogue starters | 41 lesson references passed |
| Hardware references | 26 C/assembly references passed for 13 profiles |
| Deliberately incomplete starters | 26 executed and failed the intended target checks |
| Legacy curriculum regression | stale rows archived; private drafts/completions retained; published totals corrected; wrong-engine old lesson blocked |
| Prerequisite routes | authored in-site links resolved to seeded workspaces |
| Telemetry behavior | RAM enable/parity separation, all supported gate masks, invalid profiles and shot-count invariance checked |
| Frontend DOM behavior | load/restore, engine matching, no implicit execution, and existing result/draft/model interactions passed |
| System and migration consistency | no issues; no model changes pending |
| Real HTTP workflow | registration, cookies/CSRF, lesson run, RAM targets, boot save/download/run passed |
| Deployment upgrades | fresh/repeated installs, known legacy/renamed index collision, preserved completions/accounts, coherent protected backups and partial-schema rejection passed |
| Production serving | HTTPS proxy, secure cookies, execution, hashed/compressed/cacheable static assets, private downloads and revision/timing headers passed |
| Native C comparison | seven authored outputs matched GCC execution |

The 98 documentation executions repeat some starter/reference behavior already covered elsewhere in the suite; the counts are overlapping inventories, not independent evidence totals. The complete current logs are under `evidence/documentation/`.

System/migration consistency, real HTTP registration/execution/RAM/boot workflows, production/static checks, deployment upgrade scenarios and the native C comparison passed. The production smoke run's 30 sequential small C requests had loopback HTTP p95 of 31.02 ms and application p95 of 15.26 ms. Those measurements exclude WAN, real browser, concurrency and physical hardware; they do not verify a universal 300 ms deployment target. Reproduce with the commands below.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
python tools/verify_examples.py
python tools/http_smoke.py
python tools/deployment_smoke.py
python tools/production_smoke.py
python tools/native_reference_check.py
python tools/frontend_fixture.py /tmp/bare-metal-dom
node tools/frontend_dom_smoke.cjs /tmp/bare-metal-dom
```

## Limitations

Full browser verification remains incomplete: the recorded Playwright launch could not find its Chromium executable. DOM checks establish event and source behavior, not rendered pixels, mobile layout, scrolling, accessibility, or browser paint timing. Run the browser smoke script with Chromium installed to check example loading, restoration, and the rendered layout.

The runners remain documented educational subsets. The software mocks explain controller lifecycle, events, ownership and state transitions without introducing a physical bus, interrupt controller, DMA engine or clocked HDL simulator. There is no real-device validation, user-learning study, QPU calibration, full native kernel execution, or new live-network speed measurement. The documentation was published to GitHub on 13 October 2026; whether the running site has loaded it remains unverified.

## Deploy a repository update

On the deployed checkout, stop the app server, pull the latest `main`, load the existing deployment environment, run `python manage.py prepare_deployment`, then restart with the existing service command or `bash tools/start_server.sh`. If development mode is being used, the same migration/seeding preparation runs before `python manage.py runserver`. See [Setup and deployment](SETUP_AND_DEPLOYMENT.md) for environment settings.

The backup created before preparation contains the prior database. Verify the new learning path contains seven tracks and 41 lessons, a device-foundation lesson opens in C, an old stale lesson link returns to the current path, and RAM/quantum telemetry matches the corrected meanings. Preserve the owner's private database and environment while applying source updates.
