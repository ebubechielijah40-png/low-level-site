## Before byte order: distinguish three representations

You should understand [instruction fields](/learn/machine/2/). The printed word, its bytes in memory, and the value decoded from those bytes are related but distinct. Printed hex normally places the most significant digit on the left. Byte order describes which byte occupies the lowest address. Neither rule changes the underlying number when encoding and decoding agree.

For the first program word `02a00293`, the instruction-image bytes are `93 02 a0 02`. Reconstruct them as `0x93 + (0x02 << 8) + (0xA0 << 16) + (0x02 << 24)`. Notice that `0x2A`, the immediate 42, does not appear as an isolated data byte in that listing: it is packed into instruction field positions. Searching an image for the visible number is not instruction decoding.

The image's first sixteen bytes contain four words. The first two words initialize x5=42 and x6=1. The third reads both registers and writes x7=43. The fourth requests the teaching stop. Execution order follows addresses 0, 4, 8, 12 unless an instruction changes control flow.

## Dependencies explain which reorderings matter

Swapping the first two words preserves 43 because they write different registers and neither reads the other's result. Moving ADD before the x6 initialization produces 42 because x6 still contains its initial zero at that moment. The later assignment x6=1 does not retroactively recompute x7. A stored result records a past computation, not a formula that continuously watches its operands.

Open **Encoding** and label each four-byte group. Rewrite the first word as binary `00000010101000000000001010010011` and leave the other words unchanged. The result must still be 43: that is a change in textual notation, not a change in encoded bits. Then feed `9302a002` as if the byte string were a word. You have changed the decoder input, so there is no reason to expect the original instruction or result.

## Addresses carry units and boundaries

Address 4 means the fifth byte in a zero-based byte-addressed space, not the fifth instruction. A 64 KiB RAM contains 65536 bytes at addresses 0 through 65535. The last aligned four-byte start is 65532. An address can be within RAM while its multi-byte access extends past the end; both starting location and total access size matter.

These distinctions recur in disk offsets, packet fields, array indexing, and MMIO registers. In each case, ask whether a quantity counts bits, bytes, words, or elements before using it in an address calculation. The next lesson isolates the arithmetic operations; the load/store lesson applies the same representation rules to data memory.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```machine run:reference
02a00293
00100313
006283b3
00000073
```

Expected result: State / registers: `x7 = 43`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## Four bytes are not four instructions
A 32-bit instruction word contains four bytes. The printed word `00500293` shows the most significant hex digits first. Our RV32I memory is little-endian: at address zero the byte is 93, at address one it is 02, at address two it is 50, and at address three it is 00. Reconstructing the word means `0x93 + (0x02 << 8) + (0x50 << 16) + (0x00 << 24)`.

Endianness describes byte order within a multi-byte value. It does not reverse every bit in a byte and does not change the order of instructions. If instruction A is at address zero and instruction B at address four, A still executes before B when control flows sequentially.

## The unit of an address
Byte-addressed memory assigns one address to each byte. An aligned 32-bit word uses addresses 0, 1, 2, and 3, while the next word starts at 4. This is why a word address and a word index differ by a factor of four. Alignment means the starting address is a multiple of the access size. Our runner rejects unaligned word loads and stores, making a frequent low-level mistake visible.

A program counter is an address, not an instruction count. After three sequential four-byte instructions, it has advanced twelve bytes. Registers store values; memory addresses identify locations containing values. Confusing a location with its contents is the root of many pointer errors.

## Trace a small program
The example writes 42 into x5, 1 into x6, and then adds x5 and x6 into x7. The final register value is 43. Each line in the editor is a word, even though the stored image returned by the runner is a byte sequence. This distinction is explicit because a hex dump from a debugger normally shows bytes, while an ISA manual often prints complete instruction words.

Open Trace and write down PC, word, and destination for each instruction. Rewrite the first word as a 32-character binary string; the runner accepts either representation. The result should remain unchanged. Then intentionally swap the first two words. The result remains the same in this example because the two initial loads are independent. Swapping the ADD with one initial load changes the result, exposing a data dependency.

## Apply the model
Draw a table containing eight addresses and the two first instruction words' bytes. Verify it by converting the runner's image hex back into groups of four bytes. Explain why a 64 KiB memory has 65536 byte addresses, rather than 65536 possible 32-bit words. The exercise is to make representation, storage, and execution three separate parts of your reasoning.
