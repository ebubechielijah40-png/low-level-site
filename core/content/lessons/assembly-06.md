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
