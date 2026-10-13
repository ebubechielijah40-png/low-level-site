## Before masks: choose the operation's interpretation

You need [register aliases and encoding](/learn/assembly/1/) and [fixed-width ALU rules](/learn/machine/4/). Bits do not carry a universal signedness tag. An operation selects how they are interpreted. That is why comparison and shift instructions need distinctions even though ADD keeps the same low bits for signed and unsigned readings.

The original program starts at binary `011`, ORs `100` to obtain `111`, then ANDs with the 32-bit pattern for -3, `fffffffd`, to obtain `101`. Only bit one is zero in that mask. Every other bit is preserved by AND with one. The final result is five. Clearing a bit is a mask operation, not subtracting its numeric weight unconditionally: subtraction would borrow if the bit were already clear.

For a selected mask M: `value | M` sets its selected bits, `value & ~M` clears them, `value ^ M` toggles them, and `value & M` tests the selected positions. The final test result is a masked integer, not necessarily the Boolean integer one. Convert it to a Boolean comparison when that is what your API promises.

## Try signed and unsigned comparison side by side

```assembly run:comparison
li t0,-1
li t1,0
slt t2,t0,t1
sltu t3,t0,t1
mv a0,t2
li a7,1
ecall
mv a0,t3
li a7,1
ecall
li a7,10
ecall
```

Try this in the terminal beside the documentation. Expect console `10`, x7=1, and x28=0. The two prints have no separator. The signed comparison asks whether -1<0, which is true. The unsigned comparison asks whether 4294967295<0, which is false. Inputs are unchanged between comparisons; only the interpretation rule differs.

Logical right shift of `ffffffff` by one produces `7fffffff`; arithmetic right shift preserves the leading one and produces `ffffffff`. Before using a shift for division, consider negative inputs and rounding rules. Before applying a register mask to a device, read its access semantics: write-one-to-clear and reserved-bit rules can make ordinary read-modify-write unsuitable. [Device register contracts](/learn/device/1/) explain that boundary in detail.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```assembly run:reference
li t0,3
ori t1,t0,4
andi t1,t1,-3
mv a0,t1
li a7,1
ecall
li a7,10
ecall
```

Expected result: Console: `5`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## Bits can have multiple numeric readings
A 32-bit pattern represents an unsigned number from 0 through 4294967295. Two's-complement signed interpretation represents -2147483648 through 2147483647. The pattern ffffffff is the unsigned maximum and signed -1. Neither reading changes the physical bits.

RV32I offers distinct operations where interpretation matters. SLT compares signed values; SLTU compares unsigned values. Logical right shift fills the left with zero; arithmetic right shift copies the sign bit. ADD keeps the low 32 bits in either case, so its encoding does not need signed and unsigned variants.

## A device-control word
Suppose bit zero enables a virtual device, bit one enables notifications, and bit two indicates a diagnostic mode. These are independent flags packed into one integer. A value of 3 enables the first two flags because binary 011 has two low one-bits. To set bit two without clearing others, OR with 4. To test it, AND with 4 and compare the result with zero. To toggle it, XOR with 4.

The example starts with 3, sets bit two to obtain 7, then clears bit one using AND with -3. The 32-bit pattern of -3 is fffffffd: every bit is one except bit one. AND therefore preserves all other bits and clears only that flag. The final value is 5, or binary 101.

## Predict before execution
Write the initial, intermediate, and final patterns using eight bits. Run the program and check t1/x6 and a0/x10. Replace OR with XOR and explain why it gives the same answer when the selected bit initially equals zero, but a different answer when it initially equals one. This is a reason to choose an operation from the desired rule, not from one successful test.

Now load -1 and zero into two registers. Use SLT and SLTU to compare them. Under signed comparison -1 is less than zero. Under unsigned comparison ffffffff is greater than zero. The resulting one-bit comparison values make interpretation directly observable.

## Exercise
Model four independent switches in a word. Turn two on, toggle one, and test the remaining switch without changing the control word. Document the meaning of each bit. This same discipline appears in permissions, status flags, network headers, and device registers; the notation is small, but the obligation to define it precisely is substantial.
