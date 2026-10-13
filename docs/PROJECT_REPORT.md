# Bare Metal
## Design and implementation of an integrated environment for learning and applying low-level programming languages

Technical final-year project report · initial implementation with documentation update, 13 October 2026

The initial upgrade was followed by [production and performance work](PERFORMANCE_AND_DEPLOYMENT.md) and the [documentation/configuration update](DOCUMENTATION_UPGRADE_REPORT.md). The current site has seven tracks, 41 lessons, 13 configuration guides and 98 runnable documentation programs; the recorded suite passed 287 tests. All original guides now include deeper state/contract reasoning and worked experiments, and eight device-foundation lessons cover the knowledge missing between a language tutorial and configuration. Browser/public-network speed, physical-device work and native kernel boot remain unverified.

## Abstract

Bare Metal continues the supplied CL-fromgithub Django project and turns its disconnected lesson pages and incomplete execution flow into an integrated learning environment. The learner reads an authored explanation beside an editable terminal, executes a supported program, and inspects output, virtual machine state, traces, and instruction bytes. A focused progression begins with machine code and RV32I assembly, then introduces C, Rust, Verilog, and operating-system foundations. Hardware configuration labs associate documented virtual registers with selectable component models. A separate OS workspace stores, imports, downloads, and emulates per-user 512-byte x86 boot images.

The current upgrade contains 41 authored lessons, 13 hardware configurations, 98 complete documentation programs, authentication with password visibility controls, individual lesson completion, private code drafts, and server-verified configuration targets. The recorded automated suite passed 287 tests. All documented programs matched their declared results or intentional diagnostics; the real HTTP, production and deployment workflows passed, and seven authored C outputs agreed with native GCC execution. The freestanding kernel's earlier compile/link milestone remains distinct from native boot, which has not been verified. Browser visual verification remains incomplete. The implemented runners are explicit educational subsets and simulations; no physical hardware control or arbitrary native-code hosting is claimed.

## 1. Introduction and problem definition

### 1.1 The problem

Low-level programming requires connecting source syntax to representation, storage, and instruction effects. A learner can copy working source without understanding what an instruction changes, why an address is valid, or how a configuration request relates to a device contract. A useful learning environment must therefore make explanation and observable execution part of one flow.

The supplied application had a useful Django foundation but did not provide that flow. Its dashboard redirected to a language list. The attached database contained no language or lesson rows. The editor depended on an external runner, several editor scripts were placed in a template block the base never rendered, and hardware execution was explicitly unavailable. A regex-based C analyser accepted only narrow text patterns, while assembly analysis did not execute instructions. Machine language was incorrectly treated as assembly input for an external service. Progress counters used inconsistent conventions and did not represent individual completed lessons.

The real constraint was the missing connection between authored teaching, executable semantics, inspectable state, and persistent user work. Restyling the pages alone would not remove that constraint.

### 1.2 Aim and objectives

The aim is an inspectable, focused web environment for learning and applying low-level and systems languages. The objectives are to establish an explicit language progression, provide self-contained worked teaching, integrate code practice beside that teaching, replace text-pattern execution with bounded models, associate configuration code with component views, preserve private progress/drafts/images, and produce reproducible evidence for the implemented behaviour.

The interface should use the requested green-and-black terminal identity consistently across login, signup, dashboard, source, and results. Hardware application should remain open rather than gated by lesson completion. Operating-system work should include a concrete first-stage image rather than only a future-project description.

### 1.3 Scope and tradeoff

The highest-leverage choice was to retain Django and the repository's migration history while replacing the broken execution, content, and user flow. A separate frontend framework or unrelated new repository would have increased integration work without solving the core constraint sooner.

The central tradeoff is execution completeness. The site uses bounded educational interpreters and emulators so supported examples work locally with inspectable state. It does not implement full native C, rustc, complete Verilog, a physical device controller, or a general virtual-machine hosting service. Those larger capabilities require independent toolchains and isolation. The report distinguishes each delivered milestone from those additional systems.

## 2. Technical background and progression

### 2.1 Representation and instruction sets

Bits acquire meaning through a defined interpretation. Bytes can represent numbers, characters, instruction fields, or parts of addresses. An instruction-set architecture specifies which state transition an encoded instruction requests. Machine code is architecture-specific; an RV32I word cannot be treated as a generic instruction for every processor.

RV32I was selected for the first two tracks because its regular integer instruction formats make decoding, register fields, immediates, and load/store behaviour tractable. The machine track derives encodings and byte order; assembly introduces names, labels, and pseudo-instruction expansion while using the same execution model. The RISC-V specification is the primary architectural reference [1].

### 2.2 Systems languages and memory access

C adds structured expressions, types, arrays, pointers, structures, and functions above instruction sequences. Its language rules are not identical to the raw processor's arithmetic. For example, signed overflow must not be taught as automatically guaranteed wrapping merely because an ADD instruction keeps low bits. The lessons make that distinction explicit and the interpreter reports such overflow.

Rust introduces another source-level access model, including immutable bindings and limited borrowing demonstrations. Native Rust ownership and lifetime analysis is broader than the local teaching checker. Its conservative lexical-borrow implementation is identified as a subset; the Rust Book supplies primary conceptual background [2].

### 2.3 Hardware description and device interfaces

Verilog describes logic relationships rather than ordinary CPU procedures. The authored exercises derive gates, a half adder, a multiplexer, and width-sensitive comparators, then inspect exhaustive truth tables. Simulation, synthesis, and programming physical hardware are separate activities. The site implements the first for a small combinational subset; Verilator and Yosys documentation provide broader toolchain context [3,4].

Software configures a device through a documented interface rather than through a language name alone. The configuration labs specify word-aligned virtual register addresses, meanings, units, reset values, and target states. The same lab can be implemented with C accessor calls or RV32I stores. These are educational contracts, not real vendor register maps.

### 2.4 Bootstrapping an operating system

Firmware and a loader establish the conditions under which initial code runs. The OS workspace deliberately uses a small x86 BIOS-sector convention, with the architecture switch stated explicitly. The site's assembler produces actual supported x86 instruction bytes and a 55 AA sector signature. Its emulator supplies a limited BIOS output service.

A separate freestanding C example progresses to an assembly entry, stack, linker layout, Multiboot header, and VGA output. It compiles and links without a hosted library. Compilation, linking, loading, and executed boot are distinct evidence stages. Intel architecture documentation, GNU assembler documentation, and GCC dialect/environment options are the relevant primary references [5–7].

## 3. Requirements, analysis, and design

### 3.1 Functional requirements

| ID | Requirement | Delivered behaviour |
|---|---|---|
| F01 | Authentication and visible passwords | Validated signup, login, per-field eye controls, POST logout |
| F02 | Coherent dashboard | Next unmarked lesson, actual completion counts, ordered path, open system links |
| F03 | Progressive authored teaching | 7 tracks, 41 lessons, explicit prerequisites and device foundations |
| F04 | Practice beside documentation | 98 runnable documentation programs, matching-engine load, draft restore, Run/reset, console, state, trace, and encoding |
| F05 | Local execution | Same-origin bounded interpreters/emulators; no public runner/CDN dependency |
| F06 | Open hardware configuration | 13 labs, no prerequisite gate, C and assembly variants, server target checks |
| F07 | Component inspection | Selection, rotation, zoom, labels, associated configurations, last-run telemetry |
| F08 | OS first-stage hosting | Private save/import/download/boot of supported 512-byte images |
| F09 | Persistent work | Per-user drafts, exact per-lesson completion, configuration progress |
| F10 | Reproducible reporting | Audit, runner contracts, tests, HTTP check, native references, kernel build, demo guide |

### 3.2 Learner workflow

The dashboard recommends the first unmarked lesson. A lesson presents its explanation and practice task on the left and an editable terminal on the right. The learner predicts behaviour, runs code, and inspects a result. A lesson review may be marked independently of target checks; the interface states that this is a review record rather than a mastery certificate.

The system overview exposes component models and available configurations. Selecting a configured component opens its associated workspace. The same pane arrangement preserves explanation, model, source, and state. Configuration completion is recorded only when the server compares actual virtual writes with the declared target successfully.

The OS workspace supports source-based builds and imported images. An imported image has no recovered source. Its saved bytes can be booted directly; the editor's example source is kept separate so saving it does not overwrite the imported artifact accidentally.

### 3.3 Application architecture

Django templates and local static files provide the frontend. The browser submits authenticated, CSRF-protected requests to execution and persistence endpoints. Views validate context and ownership, dispatch to a selected runtime, compare reference state, and return structured JSON. Interpreters expose virtual state without executing submitted source as host code.

The C engine uses pycparser's syntax tree. RV32I combines a two-pass assembler with byte-addressed instruction emulation. Rust parses its supported syntax and applies local mutability/borrow rules before virtual execution. Verilog exhaustively evaluates its bounded combinational input space. The boot engine assembles a sector and emulates a small x86/BIOS subset. These distinct engines share result shape and resource bounds, but not a claim of identical language semantics.

### 3.4 Data model

| Entity | Purpose and relationships |
|---|---|
| User | Django account owning all personal work |
| Language | Ordered track with engine, slug, description, and lessons |
| Lesson | Authored content, starter, practice, time estimate, expected output/state |
| LessonCompletion | Unique user–lesson review record with timestamp |
| UserProgress | Retained historical language counter for repository compatibility |
| HardwareSystem | Original six system identities and conceptual model categories |
| HardwareChallenge | Retained database model name backing the new component configurations |
| HardwareProgress | Unique user–configuration completion recorded on successful target checking |
| CodeDraft | Unique user–workspace code, updated on autosave |
| BootProject | User-owned source where available and exact stored sector bytes |

Migrations 0006 and 0007 extend rather than replace the original 0001–0005 history. Migration 0007 adds archive flags so stale historical teaching is retained as data while removed from published navigation, totals and executable lesson contexts. The attached source database and its existing account are excluded from the delivery archive. Seed commands update canonical tracks by slug and lesson order; custom teaching belongs in the catalogue to remain published across reseeding.

### 3.5 Bounds and trust

Source, nesting, interpreter work, call depth, arrays, output, trace length, and virtual memory are bounded. File, shell, network, and host-address APIs are not exposed through the teaching runner. Authentication, CSRF, escaping, and ownership checks protect application state. These controls do not establish a hardened operating-system sandbox: cooperative limits do not replace hard worker memory/time limits, public-service abuse controls, or independent security evaluation.

## 4. Implementation and changes

### 4.1 Repairing execution

The external try-it page was removed and its legacy URL redirects to the integrated lesson. C source is interpreted from actual syntax nodes rather than recognised by a handful of regular expressions. It supports the lesson's integer/control-flow/object forms and reports unsupported syntax honestly. Tests cover pointer lifetime, uninitialised objects, lexical scope, arithmetic limits, and bounds.

RV32I output includes numeric register values, memory bytes, traces, and assembler listings. Machine input uses real 32-bit instruction words. Teaching ECALL service numbers are explicitly documented and distinguished from Linux ABI values. The two tracks share state semantics, which the tests compare directly.

Rust and Verilog add relevant systems/hardware perspectives without broadening the site into unrelated high-level languages. Both expose exact subset contracts. Their accepted examples are tested against independently stated outputs or truth tables rather than against source patterns.

### 4.2 Authored teaching

The machine and assembly tracks each have six lessons. C has eight, device foundations eight, Rust four, Verilog four, and OS foundations five. Every original language and hardware guide has been expanded with prerequisites, causal reasoning, complete runnable programs, expected observations and controlled mutations. Device foundations add register/lifecycle/timing/DMA/protocol/resource knowledge, a clocked-state software model and the mathematics needed for the site's ideal two-qubit demonstrations. The detailed curriculum map states the narrow scope of each branch.

A useful lesson includes a mechanism, worked prediction, observable result, controlled failure, and independent practice. Marked Markdown programs are loaded into the matching terminal without implicit execution and are tested directly from the authored source. File/word counts are only an inventory; the successful references and explicit explanations are the substantive evidence. Further experiments may intentionally produce a different result from the page's fixed reference checks.

### 4.3 Interface

The requested green-and-black identity extends across authentication, a persistent navigation rail, ordered dashboard cards, source, and result views. Password buttons change input visibility independently. Code supports indentation and a run shortcut; drafts save to the user's server workspace with a local pending backup for failed autosaves.

The component canvas uses orthographic projection, sorted faces, simple boxes/rings, labels, structural detail, and selection highlights. Geometry is conceptual and not to scale. Mouse/touch interaction rotates, scroll/buttons zoom, and component buttons provide another selection method. Responsive CSS stacks panes and uses a navigation toggle on small screens. These behaviours are implemented but final real-browser visual quality is unverified in this environment.

### 4.4 Hardware and quantum models

The six retained systems are a personal computer, server, data centre, compute cluster, satellite, and quantum concept. Each configuration supplies three virtual registers, units, and a target. Derived telemetry illustrates a requested worker total, payload rate, cooling headroom, distinct-node replication possibility, or parity result where applicable.

The quantum model starts from |00>, applies a requested ideal Hadamard and optionally controlled-X, and reports exact two-qubit basis probabilities. It does not sample the requested shot count, model noise/decoherence, calibrate pulses, control a QPU, or simulate physical cooling. Its component geometry is illustrative. The mathematical result is independently checked for normalisation and the expected correlated state.

### 4.5 OS artifacts

The site stores exact user-owned sector bytes and can emulate supported imported images. Save validates that the source builds and boots in the small model; download returns 512 bytes. A valid BIOS signature does not guarantee support for every image opcode, so imported unsupported images receive a clear error on execution.

The separate minikernel builds a statically linked ELF32 i386 executable with a Multiboot header. Build/link and header inspection passed. QEMU/loader execution did not occur here and must not be described as completed. The boot-image host is an implemented first-stage milestone; a full kernel host remains a separate architecture requirement.

## 5. Testing, evaluation, and remaining work

### 5.1 Method and results

Testing combines direct runtime behaviour, adverse inputs, application integration, ownership/CSRF checks, complete authored documentation, real HTTP requests, deployment upgrades, and an independent native C output comparison. The recorded Django suite passed **287 tests**. The page integration check renders all current lesson, track, system and configuration-language variants. The verifier passed **41** lesson examples, **26** configuration references and **98** documented programs, including **6** intentional diagnostics; it also confirmed **26** incomplete configuration starters fail their targets while executing valid code. These counts overlap rather than representing independent additive totals.

The real HTTP check used a temporary database and exercised registration, cookies, CSRF, dashboard, lesson execution, RAM targets, boot save, exact image download, and emulated boot. Production/static and fresh/legacy/repeated deployment checks passed. Seven hosted-C lesson outputs matched GCC-native results. The earlier freestanding kernel compile/link verification remains recorded. Migration consistency, JavaScript syntax and example load/restore DOM behavior passed. The current documentation report and evidence distinguish these checks from visual and physical validation.

### 5.2 What the evidence establishes

These results establish the defined examples and tested boundaries in the implemented environment. They do not prove full language compliance, general security, physical hardware behaviour, native kernel execution, improved student learning, or production performance. Passing a reference output is evidence about a stated program result, while the teaching's explanation and independent exercise require additional learner reasoning.

### 5.3 Blocked and untested work

Real-browser verification remains blocked: the current Playwright launch cannot find its Chromium executable. Earlier attempts also had an unusable download and a cloud-browser local-address rejection. No rendered application screenshot, mobile layout result, browser accessibility audit or paint measurement is claimed. DOM checks verify example load/restore, engine matching and existing event behavior; the supplied real-browser script must run with a browser installed to establish rendered behavior.

QEMU and the GRUB rescue toolchain were unavailable for the native ELF kernel, whose boot remains unverified. There has been no physical-device validation, user-learning study, penetration test, concurrent-load benchmark or distributed rate-limit validation. Local production timing was measured for 30 sequential small C requests, with loopback HTTP p95 31.02 ms and application p95 15.26 ms; this excludes WAN, browser and load. The owner previously used a development tunnel, but its current availability and this documentation update's deployed revision have not been verified.

### 5.4 Ordered next steps

Run the browser script on a disposable development installation and inspect desktop/mobile behavior. Boot the native kernel with a compatible loader and capture its actual output. Conduct a learner evaluation with fixed pre/post tasks and recorded observations. Full native language/kernel hosting needs separate isolated workers or a compatible browser emulator. Complete quotas, backups, shared atomic rate limiting and concurrency/security evaluation before a public launch.

## References

The initial primary references were consulted on 1 October 2026; the documentation update adds device I/O, DMA and C language-contract references. Teaching and implementation explanations are original; these are contextual references rather than reproduced book or manual passages. The curriculum map contains the additional technical source list.

[1] RISC-V International. RV32I Base Integer Instruction Set. https://docs.riscv.org/reference/isa/unpriv/rv32.html

[2] The Rust Project. The Rust Programming Language: What Is Ownership? https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html

[3] Verilator. User guide: Overview. https://verilator.org/guide/latest/overview.html

[4] YosysHQ. Synthesis in detail. https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/synthesis/index.html

[5] Intel. Intel 64 and IA-32 Architectures Software Developer Manuals. https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html

[6] GNU Binutils. GNU assembler: i386 16-bit code. https://sourceware.org/binutils/docs/as/i386_002d16bit.html

[7] GNU Compiler Collection. C dialect options. https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html

[8] Django Software Foundation. Password management in Django. https://docs.djangoproject.com/en/5.2/topics/auth/passwords/

[9] Linux kernel documentation. Bus-independent device accesses. https://docs.kernel.org/driver-api/device-io.html

[10] Linux kernel documentation. Dynamic DMA mapping guide. https://docs.kernel.org/core-api/dma-api-howto.html

[11] WG14. N1570 C working draft. https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf

## Deliverable inventory and provenance

The repository contains the continued Django app/migrations, curriculum/configurations, local frontend assets, runtime engines, tests, reproduction/build scripts, native kernel milestone, and public audit/report/setup/demo guides. The original input archive remains unchanged. Its SHA-256 is `3c4bdb8fdbe63c0bf2acfb9ae34db7e068fe4b64b3a10510fd238643768610b7`.

The documentation update was published to GitHub on 13 October 2026. A running deployment still requires a pull, database preparation and process restart; its active revision has not been verified.
