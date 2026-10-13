# From low-level code to configuration

Machine code, assembly and C provide a way to express machine operations. They do not provide the register map, timing requirements, activation sequence or measurement procedure of every device. The site now teaches those missing foundations explicitly and links them from each configuration guide.

The goal is a focused working model of the mechanisms used by this project. It is not mastery of every processor, controller, operating system or physical quantum platform.

## Recommended progression

| Stage | What becomes understandable | Runnable environment |
|---|---|---|
| Machine code, 6 lessons | representation, decoding, fixed-width arithmetic, addresses, memory and next-PC decisions | supported RV32I words |
| Assembly, 6 lessons | symbolic encoding, masks, loops, arrays, calls, stack and MMIO | the same RV32I machine |
| C, 8 lessons | objects, type rules, control flow, bounds, pointers, frames, structures and device access | bounded C AST interpreter |
| Device foundations 1-6 | register contracts, lifecycle, timing, ownership, protocols and resource/failure constraints | bounded C experiments and explicitly authored software mocks |
| Rust, 4 lessons | mutation permissions, ranges, borrowing and buffer bounds | focused teaching subset |
| Verilog, 4 lessons | combinational gates, adders, selection and width contracts | exhaustive small truth tables |
| Device foundation 7 | clocked state, reset and controller transitions | C transition model; sequential HDL is explained but not executed |
| Device foundation 8 | amplitudes, probabilities, two-qubit gate preparation and physical-control boundaries | integer expectation experiment plus the quantum labs' ideal state model |
| OS, 5 lessons | firmware entry, x86 real-mode image, strings, stack routines and the separate freestanding-kernel path | supported 512-byte BIOS-sector emulator |

The seven displayed tracks contain 41 lessons. Hardware design and quantum foundations are branches taken when the chosen configuration needs them. All workspaces remain open; prerequisite links are guidance, not completion locks.

## What to know for each configuration

The following are the additional concepts a language tutorial alone would leave out. Every guide contains a worked explanation, complete reference programs for its actual terminal engines, predicted consequences and controlled mutations.

| Configuration | Knowledge required before interpreting its fields | What the implemented model actually checks or derives |
|---|---|---|
| CPU execution profile | core/worker distinction, ISA versus pipeline, clock units, supported operating points and thermal limits | requested cores, MHz and enable |
| RAM profile | byte capacity, address organization, timing/refresh/training, parity versus ECC, controller capabilities | capacity/enable/parity request; no physical RAM allocation or training |
| Block-device profile | block versus byte addressing, buffer length, command/DMA ownership, completion versus durability | block size, queue count and enable |
| Server workers | service rate, memory budgets, admission/backpressure and queue wait | worker/queue/enable request |
| Network profile | frames/IP/transport/messages, MTU and path limits, header budgets, buffers and routing | MTU/connection/enable request; no actual packets or sockets |
| Replication | placement, independent failure domains, durable copies, quorum and recovery | requested counts and numerical distinct-node feasibility |
| Cooling profile | watts versus temperature, thermal path, sensors, delay and a control policy | requested watt values and their headroom difference |
| Parallel compute | task/data decomposition, per-node budgets, serial fraction, synchronization and communication | requested nodes times workers per node |
| Interconnect | latency versus bandwidth, topology, message format, ownership and completion | requested paths, message bytes and enable; no link timing |
| Telemetry | units/timestamps, sampling, payload/framing rate, storage and link/energy budget | samples per second times payload bytes |
| Parity packet | bitwise derivation, error-detection limits, check region, coding versus authentication | low-byte parity and comparison with requested bit |
| Hadamard preparation | complex amplitudes, squared-magnitude probabilities, measurement and physical calibration | exact supported two-qubit state; shots are not sampled |
| Bell preparation | tensor-product basis order, controlled operation, gate order and joint versus marginal state | H then controlled-X under the documented basis order |

## Use the terminal beside the guide

Read the prerequisite explanation and predict the result before pressing Run. **Load in terminal** copies the complete program into the matching engine without executing it. **Restore draft** restores the editor source from immediately before the most recent example load. Hardware examples require the matching C or RV32I language switch; incompatible load buttons are disabled.

Use Console for output, State for registers/objects/MMIO/truth tables and telemetry, Trace for recorded transitions, and Encoding for emitted instruction/image bytes when available. C and Rust do not emit native machine code in this environment. A changed experiment can execute correctly while failing the original reference checks; compare it with the new prediction stated in the guide.

Each run has fresh virtual state. Registers written in one lab or run are not a persistent physical machine. The same virtual address can have a different meaning in another profile. A read-back is evidence of recorded state, not proof that a physical controller activated or work completed.

## What is sufficient, and for what

For the site's supported profiles, the existing C or RV32I tools plus the new foundations and component-specific guides supply the information needed to understand and reproduce the modeled configuration. Rust and HDL provide useful additional perspectives rather than universal prerequisites for writing a profile.

For an actual device, obtain its exact controller/platform contract: capabilities, resource discovery and mapping, access permissions, field meanings, legal values, ordering, prerequisites, acknowledgement, timeouts, recovery and measured validation. Physical RAM, a NIC, a server service and a quantum processor do not expose one universal three-register interface. The required implementation or platform API depends on the chosen target.

For designing a controller, continue beyond the combinational runner into sequential HDL simulation, synthesis, timing verification and the supported target toolchain. For a native operating system, continue beyond the first-stage image into loader contracts, memory management, privilege, exceptions, interrupts, drivers and scheduling. The OS guide identifies those milestones and the separate minikernel artifact explicitly.

## Authoring and maintenance

Complete runnable blocks are executed directly from Markdown by `core/content_checks.py`; reference expectations come from the catalogues and additional experiments from `core/content/experiments.json`. Deliberate failures have expected diagnostic categories. `tools/verify_examples.py` also verifies the 26 incomplete hardware starters remain executable but fail their intended targets.

The curriculum catalogue is the published source of truth. Reseeding updates canonical rows by track slug and lesson order, preserving their identities. Rows outside the catalogue are archived rather than deleted. Their old completions and private drafts remain in the database, while their teaching is removed from navigation, totals and executable lesson contexts. Add custom teaching to the catalogue if it should survive future reseeding as published content.

## Technical references

The explanations and experiments are authored for this project. The following primary materials were checked for architectural and platform boundaries; they are optional references, not substitutes for the in-site explanations or external code runners.

- RISC-V International, RV32I base integer instruction set: https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html
- WG14, N1570 C working draft, language and object rules: https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf
- GCC, volatile-access constraints: https://gcc.gnu.org/onlinedocs/gcc/Volatiles.html
- Linux kernel, bus-independent device accesses and I/O mapping: https://docs.kernel.org/driver-api/device-io.html
- Linux kernel, DMA mapping and synchronization: https://docs.kernel.org/core-api/dma-api-howto.html
- Rust project, references and borrowing: https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- RFC Editor, IPv4 protocol definition: https://www.rfc-editor.org/rfc/rfc791
- IBM Quantum Learning, multiple systems: https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/introduction

Native device work additionally requires the manual and supported software API of that specific controller. No generic reference can supply its undisclosed or platform-dependent register meanings.
