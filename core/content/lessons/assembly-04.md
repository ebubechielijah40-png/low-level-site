## An array is a layout rule
An array stores equal-sized elements contiguously. For four-byte integers, element i begins at base + 4 × i. The multiplication is a consequence of the element size. It is not a universal pointer rule: a byte array advances by one byte, while an eight-byte array advances by eight.

The data section in the editor defines four words: 4, 8, 12, and 16. The assembler places lesson data at virtual address 0x2000. The label `numbers` names that first byte. `la t0,numbers` creates an address, while `lw t3,0(t0)` retrieves the value at that address. Replacing LA with a literal load of the first value would turn a pointer into data and make the later memory access wrong.

## Walk a pointer through the array
The program keeps a pointer, a remaining-element count, and a sum in registers. Each iteration loads one word, adds it, advances the pointer by four, and decrements the count. Four iterations produce 40. Memory does not change because the loop only loads. Register t0 ends sixteen bytes beyond the base, pointing just past the last element. A one-past pointer can be a useful stopping marker, but it must not be dereferenced.

## Bytes reveal the representation
Inspect the memory rows after execution. The first value, decimal 4, occupies `04 00 00 00`; the second occupies `08 00 00 00`. Little-endian order explains the zero bytes. A debugger's raw byte view and an array's integer view are two renderings of the same storage.

Change the pointer increment to one. The next word access becomes unaligned and the emulator reports it. Change the loop count to five. The model's surrounding memory starts at zero, so the extra access may silently contribute zero rather than fail. This is a valuable distinction: an address can be inside physical RAM while being outside the logical object you intended to access. Array bounds are additional knowledge beyond the memory map.

## Exercise
Modify the array values and compute their expected sum independently. Then store the sum into a separate word named `result`, and load it back before printing. Draw the memory map and specify the exact byte addresses touched by each load and store. Understanding this model prepares you for C arrays, buffer boundaries, binary formats, and memory-mapped device structures.
