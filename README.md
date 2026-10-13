# Bare Metal

Bare Metal is a Django learning environment for low-level programming and computer systems. Work through a focused sequence, run code beside each explanation, inspect virtual components, and build a first operating-system boot image.

**Machine code → RV32I assembly → C → device foundations**, with branches into **Rust access rules**, **Verilog logic**, and **operating-system foundations**.

The curriculum includes 41 lessons in seven tracks, 13 open hardware configuration labs, and 98 runnable programs in the documentation. Every guide identifies prerequisites, explains the mechanism, and connects a predicted result to the terminal beside it. **Load in terminal** loads a matching example without executing it; **Restore draft** restores the source present before the most recent example load.

The eight device-foundation lessons cover register contracts, activation/timeout, physical timing, interrupts/DMA/caches, byte protocols, resource/failure limits, clocked state, and the two-qubit quantum model. C and assembly can express the site's virtual profiles; actual hardware additionally requires the controller/platform contract and observed validation. Read [the curriculum and configuration map](docs/CURRICULUM_AND_CONFIGURATION.md) for the exact progression and boundaries.

The integrated green-and-black workspaces retain private drafts, progress, and per-user hosted 512-byte boot images. Hardware views are selectable, rotatable, and zoomable conceptual models. There are no external code-runner calls or editor CDN dependencies.

## Run on Linux / macOS

Use Python 3.12 or newer. Initial dependency installation needs internet access; the application then uses its local content and runners.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_lessons
.venv/bin/python manage.py seed_hardware
.venv/bin/python manage.py runserver
```

Open **http://127.0.0.1:8000/** and create your own account. To manage content through Django admin, run `.venv/bin/python manage.py createsuperuser` and visit `/admin/`.

## Run on Windows / PowerShell

Activation is optional; these commands use the environment's interpreter directly.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_lessons
.\.venv\Scripts\python.exe manage.py seed_hardware
.\.venv\Scripts\python.exe manage.py runserver
```

No account, database, password, virtual environment, or private user data is stored in this repository. A fresh database is created by migrate. For an existing installation, stop the app server and run `python manage.py prepare_deployment`: it backs up SQLite, applies the full migration history through 0007, seeds the current catalogue, collects static files, and checks Django. Historical lessons outside the catalogue are archived from navigation; their database rows, completions, and drafts are retained. Old x86 lessons can no longer open in the C terminal. The old ambiguous language-level counter is not converted into invented per-lesson completions.

## Verify

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python tools/verify_examples.py
python tools/http_smoke.py
```

Optional native toolchain checks on Linux:

```bash
python tools/native_reference_check.py
bash tools/build_kernel.sh
```

The recorded browser check could not run because Chromium was unavailable. Run it against a disposable local development database to verify password toggles, drafts, model controls, the boot-image workflow, and mobile layout:

```bash
npm install --no-save playwright
npx playwright install chromium
node tools/browser_smoke.cjs
```

The script creates a synthetic QA account and its own test boot images. It writes results to `evidence/browser/`. Do not treat the included script as evidence that browser checks already passed.

## What execution means

| Environment | Implemented execution | Boundary |
|---|---|---|
| Machine code | Real RV32I word decoding and instruction emulation | Documented integer subset, virtual RAM, teaching ECALL ABI |
| Assembly | Two-pass RV32I assembler plus the same emulator | No x86/NASM in this track; supported pseudo instructions only |
| C | Parsed syntax-tree interpretation with virtual objects | Bounded integer dialect; not a compiler or complete C implementation |
| Rust | Parsed teaching subset with limited mutability/borrow checks | Not rustc; conservative lexical borrow lifetimes |
| Verilog | Exhaustive combinational truth tables | No clocks, sequential HDL, synthesis, X/Z states, or FPGA programming |
| OS workspace | Actual x86 16-bit BIOS sector bytes and a boot-subset emulator | Private 512-byte images; no complete kernel/ELF execution in the site |
| Hardware | Virtual register writes, target checks, component telemetry | No physical RAM, server, satellite, cooling, or QPU control |

See [Runner reference](docs/RUNNER_REFERENCE.md), [Setup and deployment](docs/SETUP_AND_DEPLOYMENT.md), [Project report](docs/PROJECT_REPORT.md), [Documentation upgrade report](docs/DOCUMENTATION_UPGRADE_REPORT.md), and [Testing evidence](docs/TEST_REPORT.md).

The separate `examples/minikernel` builds a freestanding 32-bit Multiboot ELF kernel. Its build and link were verified; its QEMU or hardware boot was not verified here. See [the kernel guide](examples/minikernel/README.md).

## Directory map

- `core/content/`: lesson and configuration catalogues and Markdown teaching.
- `core/runtime/`: bounded C, RV32I, Rust, Verilog, and x86 boot engines.
- `core/views.py`, `core/models.py`: authentication, progress, execution, drafts, and boot ownership.
- `core/static/core/`: terminal styles, interactions, and component-model drawing.
- `core/templates/core/`: dashboard, authentication, lessons, configurations, and OS workspace.
- `core/tests.py`, `tools/`: automated verification and reproducible build scripts.
- `docs/`: audit, report, requirements, exact runner contracts, and presentation/demo guide.

The repository preserves the project's migration history. See [Performance and deployment](docs/PERFORMANCE_AND_DEPLOYMENT.md) for measurements and service update steps. Pushing a commit does not update a running server: pull it into the deployed checkout, prepare the database and static files, then restart the process.
