## Before MMIO: the address map chooses the receiver

Review [load/store addressing](/learn/machine/5/) and [bit masks](/learn/assembly/2/). A device register is addressed through a platform-defined interface. SW still expresses a store, but the selected target can interpret the transaction as a configuration request, command, or acknowledgement rather than normal RAM storage.

`lui t0,15` forms 15 shifted left by twelve, giving 0xF000. `sw t1,4(t0)` therefore writes at 0xF004. Offset four selects the second four-byte register, not the fourth register. The reference writes capacity 512 and enable one, then reads enable into a0 and prints one. It does not write the parity register; this page's checks intentionally cover only the two operations shown. The full RAM lab also requires parity one.

## ISA knowledge cannot replace a controller manual

For a real register, you need its width, alignment, units, allowed values, reset state, permission, reserved-bit rules, side effects, and sequencing constraints. A CPU's store format tells you how to send bits; it does not tell you whether writing one starts work, clears an event, or resets the controller. Two devices can assign completely different meanings to the same field position.

This teaching window implements plain word storage reset to zero for every run. It does not enforce a real controller's activation sequence, bus posting, electrical prerequisites, or asynchronous completion. A matching read-back proves the virtual write was recorded. A model highlight reflects returned state. Neither demonstrates reliable operation of physical RAM.

## Connect the terminal result to a lifecycle

Try the reference in the terminal beside the documentation and inspect **State / mmio**. Then add a parity write of one at offset eight and compare the final state with the C RAM reference. The syntax differs, but both leave the same three virtual register values. If you write an unaligned offset, expect an access error before target checking.

An actual controller may require configuration while disabled, a commit, a readiness poll, and a timeout policy. Memory ordering and access APIs depend on the platform. Our assembly subset does not provide privileged control registers, real interrupts, caches, or the full synchronization instruction set; do not claim these properties from a passing store.

Continue through [register contracts](/learn/device/1/) and [activation with acknowledgement](/learn/device/2/) before attempting the hardware profiles. Those pages explain the missing knowledge without locking the labs. Languages give you a way to express the actions; device knowledge determines which actions are legal and what evidence establishes success.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```assembly run:reference
lui t0,15
li t1,512
sw t1,0(t0)
li t1,1
sw t1,4(t0)
lw a0,4(t0)
li a7,1
ecall
li a7,10
ecall
```

Expected result: Console: `1`. State / mmio: `0xF000 = 512`, `0xF004 = 1`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## An address can select a device
Memory-mapped I/O, abbreviated MMIO, gives a device registers in the processor's address space. A store to one of those addresses can request a device action rather than write ordinary RAM. The load/store instruction is the same kind of instruction; the memory map determines the destination's behaviour.

This runner has a virtual device register window from 0xF000 through 0xF0FC. Registers are four-byte aligned. The hardware configuration labs assign meanings within that window. For the RAM lab, 0xF000 is the requested capacity in MiB, 0xF004 is an enable control word, and 0xF008 is a parity-mode request. These addresses are chosen for the teaching model. They must never be copied into a real hardware program without the real vendor's register map.

## Configure, then read back
The example forms base address 0xF000 with LUI, stores 512 into the capacity register, and stores one into the enable register. It then reads the enable register back and prints one. Reading back proves that the simulation recorded the write. It does not prove physical memory training, real timing stability, or successful operation of a real RAM module.

A complete real configuration workflow includes prerequisites such as clocks and power, legal values, ordering constraints, acknowledgement, timeouts, and error reporting. A device can reject a request even when the instruction and address are correct. The labs model a limited set of such values so you can learn to distinguish requested state from the assumptions that make it legal.

## Why documentation matters here
For every register you touch, identify its width, reset value, read/write permissions, bit meanings, and side effects. Read-modify-write may be unsafe for registers whose bits are cleared by writing one or whose reads acknowledge an interrupt. An ordinary-looking integer assignment can therefore carry a device-specific meaning. The instruction set alone does not tell you that meaning.

## Work the example and continue
Inspect the MMIO tab after execution. It should show capacity 512 and enable 1. Change the base to a non-aligned address and observe the failure. Change the capacity to another value: the generic runner records it, while the RAM configuration lab's target checks decide whether it meets that lab's requirement.

Open Hardware configuration from the sidebar and select a model component. The next step is to use this exact load/store reasoning while watching the associated component's state. Every lab remains accessible; the progression guides understanding without locking the application behind lesson completion.
