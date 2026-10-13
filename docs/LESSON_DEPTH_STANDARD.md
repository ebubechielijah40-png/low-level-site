# Lesson Depth Standard

This project is for a learner with appetite, not a passive beginner. Lessons must be readable, but they must not flatten the machine into slogans. Every lesson should teach one precise mechanism and force the learner to connect cause to consequence.

## Required shape

Each lesson should answer five questions:

1. **What physical or architectural state exists before the code runs?**
   Name the relevant bits, registers, memory locations, buses, device registers, stack slots, or files. Avoid floating abstractions when a concrete state can be named.

2. **What exact rule transforms that state?**
   State the instruction format, evaluation rule, ownership rule, calling convention rule, memory rule, timing rule, or protocol rule. If the real machine differs from the teaching model, say where the boundary is.

3. **What changes after one step?**
   Identify the register, memory address, flag, pointer target, ownership state, signal, or output that changes. The learner should be able to predict a trace row before running the example.

4. **What illusion does this destroy?**
   Each lesson should attack one common false model: “hex is a number system the CPU understands,” “variables live in names,” “C pointers are just addresses,” “assembly is magic text,” “hardware configuration means real hardware control,” and so on.

5. **What experiment proves it?**
   Give a small mutation that changes one cause and asks for one measurable consequence. The learner must inspect state, not merely read output.

## Voice

Use direct, technical prose. Assume the learner is new to the topic but serious enough to tolerate precision. Do not write like a children’s tutorial. Do not pad with motivational filler. When a concept is hard, slow down by adding mechanism, not by diluting language.

Weak:

> A register stores data. We use registers to do calculations.

Strong:

> A register is a fixed-width latch-like storage location in the processor model. In this RV32I subset it holds exactly 32 bits. The register does not know whether those bits are a signed integer, an address, a mask, or an instruction fragment. The instruction currently consuming the bits supplies the interpretation.

## Example standard

Every runnable example should include:

- the starting state,
- the instruction or source line being tested,
- the predicted state after execution,
- the exact field/register/address to inspect,
- one mutation that should change the result,
- one mutation that should fail or expose a boundary.

## Progression

The progression must stay narrow and cumulative:

1. Bits as distinguishable states.
2. Bytes as grouped state.
3. Instruction words as encoded commands.
4. CPU state: registers, PC, memory.
5. Assembly as human notation for instruction words.
6. C as controlled naming over objects, storage, and calls.
7. Device foundations: address spaces, register contracts, activation, timing, DMA, protocols and resource limits.
8. Rust as restrictions over aliasing and mutation.
9. Verilog as combinational logic; clocked-state foundations distinguish the unsupported sequential layer.
10. Hardware configuration as writes to documented control surfaces, with device-specific prerequisite guides.
11. Operating-system work as controlled boot, memory, and privilege boundaries.

Each later track must explicitly reuse earlier machinery. If a C lesson introduces a pointer, it must connect back to byte-addressed memory. If a hardware lab writes MMIO, it must connect back to store instructions and alignment. If an OS lesson mentions a boot sector, it must connect back to instruction decoding and fixed memory locations.

## Executable documentation contract

Each guide starts with the knowledge needed to reason about it and links to the relevant in-site lessons. Knowledge requirements guide the learner; they never gate access. Every complete runnable program uses a fence such as `c run:reference`, `assembly run:comparison`, or `boot run:two-characters`. Partial syntax, native-only examples and notation tables must not receive a load control.

Use the catalogue's independently stated state/output targets for a reference. Register other experiments in `core/content/experiments.json`, including the expected diagnostic for deliberate failures. `core/content_checks.py` reads the program from the Markdown, executes it using the actual engine, and compares its behavior with that specification. A new block without a specification fails verification.

Do not invent a State tab subsection or a device capability. The available tabs are Console, State, Trace and Encoding. C/Rust interpretation does not emit native instruction bytes; the combinational Verilog runner does not implement sequential HDL; boot-sector emulation does not execute the freestanding ELF kernel. Hardware guides must distinguish requested profile values, calculated telemetry, model-enforced behavior and physical validation.

Word count is an inventory measure, not a depth test. Depth comes from a named mechanism, worked reasoning, observable state and a mutation with an independently predicted consequence.
