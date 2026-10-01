# Bare Metal

An upgrade of the existing **CL-fromgithub** Django final-year project. Learn a focused progression of low-level and systems languages, practise beside the explanation, inspect virtual hardware components, and build a first operating-system boot image.

**Machine code → RV32I assembly → C → Rust → Verilog → operating-system foundations**

The package includes 33 authored lessons, 13 open hardware configuration labs, integrated green-and-black terminals, private drafts and progress, and per-user hosted 512-byte boot images. Hardware views are selectable, rotatable, and zoomable conceptual models. There are no external code-runner calls or editor CDN dependencies.

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

No existing account, database, password, virtual environment, or private user data is distributed in the upgraded archive. A fresh database is created by migrate. Keep your previous database backed up if upgrading an existing local installation; apply migration 0006 and the seed commands. Historical progress rows are retained, but the old ambiguous language-level counter is not converted into invented per-lesson completions.

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

The browser check was **not run successfully in the authoring environment**, where browser installation and access to local addresses were blocked. Run it against your disposable local development database to verify screenshots, password toggles, drafts, model controls, boot-image workflow, and mobile overflow:

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

See [Runner reference](docs/RUNNER_REFERENCE.md), [Setup and deployment](docs/SETUP_AND_DEPLOYMENT.md), [Project report](docs/PROJECT_REPORT.md), [Testing evidence](docs/TEST_REPORT.md), and [Project memory brief](docs/PROJECT_MEMORY.md).

The separate `examples/minikernel` builds a freestanding 32-bit Multiboot ELF kernel. Its build and link were verified; its QEMU or hardware boot was not verified here. See [the kernel guide](examples/minikernel/README.md).

## Directory map

- `core/content/`: lesson and configuration catalogues, and original authored Markdown teaching.
- `core/runtime/`: bounded C, RV32I, Rust, Verilog, and x86 boot engines.
- `core/views.py`, `core/models.py`: authentication, progress, execution, drafts, and boot ownership.
- `core/static/core/`: terminal styles, interactions, and component-model drawing.
- `core/templates/core/`: dashboard, authentication, lessons, configurations, and OS workspace.
- `core/tests.py`, `tools/`: automated verification and reproducible build scripts.
- `docs/`: audit, report, requirements, exact runner contracts, and presentation/demo guide.

This continues the supplied repository and its migration history. No GitHub changes, push, or public deployment were performed.
