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
