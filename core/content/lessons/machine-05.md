## Before memory access: separate pointer and payload

You need [byte-addressed memory](/learn/machine/3/) and [register arithmetic](/learn/machine/4/). A register holding `0x2000` contains an integer bit pattern used as an address. A register holding 42 contains a payload. Hardware does not attach a pointer type to an RV32I integer register; the selected instruction gives the pattern its role.

The program forms x5=0x2000 with LUI, sets x6=42, stores x6 through the address in x5, then loads from that address into x10. A store transfers data to memory; it does not replace the pointer register with the stored value. The four stored bytes are `2a 00 00 00` at addresses 8192 through 8195. Loading those bytes reconstructs 42.

## Derive a store's split immediate

SW uses S-type encoding: immediate bits 11-5 occupy word bits 31-25 and immediate bits 4-0 occupy bits 11-7. rs2 holds the payload register, rs1 the base, funct3=2 selects a word, and opcode=0x23 selects store. The immediate is an address offset, not the value written. The source x6=42 is independent of offset zero.

LW uses an I-type immediate and a destination register. Its effective address is still base plus signed offset. Changing the load's offset to four reads a different word, initialized to zero in the model. Changing it to one requests an unaligned four-byte access and is rejected by this teaching environment. Real ISA environments can have different misalignment support; do not generalize the runner's policy to every processor.

## Try the alignment failure beside the explanation

```machine run:unaligned-load
000022b7
0012a503
00000073
```

The first instruction gives x5=0x2000. The second asks for LW at 0x2001. Expect an alignment error, with no successful reference completion. This is a deliberate failing experiment: a parser accepted the words, but the requested memory operation violated the engine's access contract.

## The bus path adds behavior the ISA alone cannot describe

A memory access is routed by a platform's address map. It can reach RAM, a mapped device, or an invalid region. Caches, translation, bus transactions, permissions, and device side effects can affect a real system. Our model provides fresh byte RAM and simple aligned MMIO storage; it has no cache timing, page translation, or physical bus measurements.

Use **State / memory** for the modified data bytes, **registers** for the payload, and **mmio** for device writes. Do not confuse a valid RAM address with the bounds of a logical array. The assembly array lesson will show an extra load that remains inside RAM while going beyond the intended object. The [device-foundations map lesson](/learn/device/1/) then adds register permissions and side effects.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```machine run:reference
000022b7
02a00313
0062a023
0002a503
00000073
```

Expected result: State / registers: `x10 = 42`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## Registers are not the whole machine
A processor normally works with more data than its registers can hold. A load copies bytes from memory into a register. A store copies register bits into memory. In RV32I, ordinary ALU instructions operate on registers; memory must first be loaded if its value is needed in a calculation. This is a load/store architecture.

The address of a word access is a base register plus a signed immediate offset. For `sw x6, 0(x5)`, x5 supplies an address and x6 supplies the value. The zero offset leaves the address unchanged. `lw x10, 0(x5)` reads four bytes from that location and reconstructs one 32-bit value. Reading a pointer value is different from reading the memory to which it points.

## An address space with a map
Our virtual RAM has 65536 bytes. Code begins at zero, lesson data uses 0x2000, and the initial stack pointer is 0xE000. Device registers occupy the separate teaching window 0xF000–0xF0FC. These are educational choices, not addresses for real RAM controllers. The hardware configuration labs document exactly what each simulated register means.

The editor uses LUI to put 2 into the upper twenty bits of x5. That produces `0x00002000`, or decimal 8192. It then loads 42 into x6, stores it through x5, and reads the same location into x10. Inspect Memory: the first four bytes at 0x2000 should be `2a 00 00 00`. Registers x6 and x10 contain equal values because the store and load refer to the same address.

## Errors that teach something
Change the load offset from zero to four. The new location begins as zero, so x10 becomes zero. Change the offset to one: a word load is now unaligned and the runner reports the exact category of error. Change the base to an address outside the model and execution fails instead of accessing host memory. A failed access is evidence about the program's assumptions.

## Exercise
Store 11 at 0x2000 and 22 at 0x2004, then load them into separate registers and add them. Predict both the byte layout and the final sum. Explain why the second location advances by four even though it is the next word. When you can move between addresses, bytes, and values deliberately, pointers in C become far less mysterious.
