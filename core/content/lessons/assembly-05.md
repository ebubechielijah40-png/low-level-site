## A function is a protocol around control flow
A call jumps to another sequence while preserving the address to which execution should return. In RV32I, JAL writes the next instruction address to a destination register and jumps to a target. The convention uses ra/x1 for the saved return address. `call name` is our assembler's shorthand for `jal ra,name`; `ret` expands to a JALR through ra without retaining another return address.

If a function calls a second function, the new call overwrites ra. The first function must save its old return address somewhere before doing that. The stack is a conventional region used for these temporary values. sp/x2 points to its current boundary. In this runner sp begins at 0xE000 and the example subtracts sixteen to reserve a frame.

## Save, call, restore
The editor calls `double_value` with 21 in a0. That function reserves sixteen bytes, stores ra at offset twelve, calls a helper that doubles a0, then reloads ra and restores sp. The helper returns to `double_value`, and that function returns to the original caller. The result, 42, remains in a0 and is printed by the caller.

The sixteen-byte reservation demonstrates an alignment convention. The saved value itself occupies four bytes. A calling convention may impose frame alignment larger than any single saved object so separately compiled code can cooperate. We are illustrating the standard RV32 register roles without claiming the teaching ECALL convention is a Linux ABI.

## Observe both addresses and values
Run and inspect the trace around JAL and JALR. Write down the caller's return address, the nested call's return address, and the memory location storing the first one. Inspect final x2: it should equal the initial stack pointer. A function that returns the right numeric result but fails to restore sp can still break later calls.

Remove the store and load of ra. The nested call overwrites the function's original return address, and the resulting control flow no longer returns correctly. The execution limit makes the failure bounded. This failure demonstrates why stack discipline is part of correctness, rather than an optional stylistic choice.

## Practice
Implement a helper that triples its argument with additions. Call it from another function that also adds one afterward. List the registers each helper may change and the values it must preserve. Draw two nested stack frames. The central idea is that a call is not magical; it is an agreed arrangement of registers, memory, and jumps.
