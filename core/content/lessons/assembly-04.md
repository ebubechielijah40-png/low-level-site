## Before an array walk: supply both a base and a length

You need [word loads](/learn/machine/5/) and [bounded branches](/learn/assembly/3/). The array's base identifies its first byte, element width is four bytes, and logical length is four elements. The complete object occupies sixteen bytes. None of that logical length is encoded in LW; the loop must maintain it separately.

The reference places 4, 8, 12, and 16 at 0x2000, 0x2004, 0x2008, and 0x200C. The last four-byte access uses addresses 0x200C through 0x200F. After the final pointer advance, t0 is 0x2010, one past the object. That is a useful stopping position, not another element.

## Derive the state at every iteration

| Completed loads | Next pointer | Remaining | Sum |
|---|---|---|---|
| 0 | 0x2000 | 4 | 0 |
| 1 | 0x2004 | 3 | 4 |
| 2 | 0x2008 | 2 | 12 |
| 3 | 0x200C | 1 | 24 |
| 4 | 0x2010 | 0 | 40 |

The invariant is that the sum contains exactly the words preceding the current pointer within the intended object. The count decreases toward zero. Pointer and count must agree; merely maintaining one without the other can hide a boundary bug.

## Memory-map validity is weaker than object validity

Change the count to five. The extra LW can read valid RAM after the object and contribute zero because this model initializes surrounding bytes to zero. The final sum can remain 40, so checking only that output misses the error. Inspect the addresses touched and the remaining count. A favorable surrounding value is not evidence that the access belonged to the array.

Change the increment from four to one and the second word load is unaligned. Change it to eight and you skip every other element. A load error, a skipped-value wrong sum, and an extra valid-RAM read demonstrate three different failed assumptions.

When a value has to cross an external interface, the memory layout also needs explicit width and byte order. A `.word` array in this little-endian emulator is not automatically a network packet. [Buffer and protocol foundations](/learn/device/5/) connect this lesson to storage blocks and network fields. For independent work, save the total in a declared result word and show the exact bytes that changed; no source-text comparison can replace that state observation.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```assembly run:reference
.data
numbers: .word 4,8,12,16
.text
la t0,numbers
li t1,4
li t2,0
loop:
lw t3,0(t0)
add t2,t2,t3
addi t0,t0,4
addi t1,t1,-1
bne t1,zero,loop
mv a0,t2
li a7,1
ecall
li a7,10
ecall
```

Expected result: Console: `40`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
