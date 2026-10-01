## Addition has a local bit rule
Adding two one-bit numbers gives a result from zero through two. Two needs two binary places: binary 10. The low result bit is the sum, while the high bit is the carry. The four cases are 0+0=0, 1+0=1, 0+1=1, and 1+1=2. This complete case analysis gives the circuit's behaviour before any code is written.

The sum bit is one when the two inputs differ, which is XOR. The carry bit is one when both inputs are one, which is AND. Therefore `sum = a ^ b` and `carry = a & b`. Two simple Boolean expressions implement one step of binary arithmetic.

## Why it is called a half adder
The circuit adds two bits but has no incoming carry. A full adder accepts a third bit representing carry from a less significant position. Multiple full adders can be connected to form a multi-bit adder. The connection pattern and propagation delays influence the physical design; the combinational truth-table runner does not estimate those delays.

A common misconception is that an arithmetic operator in an HDL necessarily describes one particular physical circuit. Synthesis can choose different implementations consistent with constraints and supported semantics. Here we deliberately state the Boolean equations so the functional structure is easy to inspect.

## Test a property, not just an example
For each input combination, the arithmetic identity `a + b = sum + 2 × carry` must hold. This is an independently derived property of the intended behaviour. A circuit can pass one sample but fail that identity elsewhere. Because the half adder has only four cases, exhaustive checking is inexpensive.

Run the editor, inspect all four rows, and verify the identity by hand. Then intentionally replace XOR with OR. Three cases remain correct, but when both inputs are one the low bit incorrectly becomes one and the encoded result becomes three. This is a useful demonstration of why a familiar-looking expression is not adequate evidence of correctness.

## Exercise
Build a full adder with inputs a, b, and cin. The sum is `a ^ b ^ cin`; one carry expression is `(a & b) | (cin & (a ^ b))`. Derive all eight rows before testing. Check `a + b + cin = sum + 2 × carry` on each row. Explain how a ripple-carry chain uses the output carry from one position as the next position's incoming carry.

This small design directly connects the instruction-level addition you studied with a possible logic-level building block, while preserving the distinction between functional simulation and a measured physical implementation.
