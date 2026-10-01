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
