## Before a call: define what the caller can rely on

Review [branches](/learn/assembly/3/) and [memory addressing](/learn/assembly/4/). A callable routine needs inputs, outputs, clobbered registers, preserved registers, and stack requirements. The ISA supplies jump instructions. The calling convention supplies the cooperation rule among routines.

This example passes 21 in a0 and returns 42 in a0. ra initially holds the address after the caller's JAL. `double_value` is not a leaf: its own CALL to `helper` replaces ra. It therefore saves the old ra to its stack frame before the nested call. The helper is a leaf and can return directly through its incoming ra.

## Account for the exact stack addresses

Initial sp is 0xE000. Reserving sixteen bytes changes it to 0xDFF0. Saving ra at `12(sp)` writes at 0xDFFC through 0xDFFF. The helper's return address remains in ra while it runs. After it returns, LW restores the outer saved address, and adding sixteen to sp returns the boundary to 0xE000. RET now reaches the original caller.

The frame size exceeds the one saved four-byte object because the example maintains a sixteen-byte stack alignment convention. A native ABI can assign further rules for saved registers, arguments, and stack layout. This site illustrates the standard RV32 integer register roles but provides a separate teaching ECALL convention, not a complete operating-system ABI.

## A result can be correct while the protocol is broken

Returning 42 does not prove the stack was restored or a promised preserved register survived. Check final x2=57344 in **State / registers** as well as the console. In **Trace**, find the two call destinations, the save/load pair, and the final return. The saved address and the returned numeric value are different pieces of state.

Remove both ra save and restore. The nested call then destroys the address needed by the outer routine. Its RET can return into its own epilogue repeatedly; successive stack updates do not restore the original protocol. The budget makes this faulty sequence bounded, not correct.

A larger system also needs a valid mapped stack, guard or overflow handling, interrupt/context-switch conventions, and rules for concurrent execution. This emulator's fixed initial stack address does not implement those systems. The C function lesson abstracts parameters and frames, while the OS boot stack lesson changes the architecture explicitly and compares x86 stack-based CALL with RV32I's link register.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```assembly run:reference
li a0,21
call double_value
li a7,1
ecall
li a7,10
ecall
double_value:
addi sp,sp,-16
sw ra,12(sp)
call helper
lw ra,12(sp)
addi sp,sp,16
ret
helper:
add a0,a0,a0
ret
```

Expected result: Console: `42`. State / registers: `x2 = 57344`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
