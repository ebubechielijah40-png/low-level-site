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
