## Before an adder: derive the arithmetic invariant

Review [signals and exhaustive gates](/learn/verilog/1/). A one-bit result cannot represent all sums of two one-bit inputs. Maximum input sum is two, binary `10`, which needs a low sum bit and a carry bit. Naming both outputs makes the representation complete.

The four cases establish `sum=a^b` and `carry=a&b`. Test them against the identity `a+b = sum + 2*carry`. For inputs 1 and 1, sum is zero and carry is one, so the represented result is two. Replacing XOR with OR makes that same case represent three; the other three cases alone would not catch the defect.

## Try the complete full adder in the terminal beside you

```verilog run:full-adder
module full_adder(input a, input b, input cin, output sum, output carry);
    assign sum = a ^ b ^ cin;
    assign carry = (a & b) | (cin & (a ^ b));
endmodule
```

Expect eight rows. For every row, check `a+b+cin = sum+2*carry`. For three ones, the sum bit and carry are both one, representing three. For a=1,b=0,cin=1, sum is zero and carry one, representing two. Derive the other cases before inspecting **State / truth_table**.

## Connect a local bit rule to a word operation

A ripple-carry adder connects each position's carry output to the next position's carry input. The least significant position starts with a chosen incoming carry, usually zero for ordinary addition. A word-wide unsigned addition can discard a final carry to retain fixed width, matching the modular RV32I result from the machine track.

Physical implementation adds a delay through the carry path. Other adder structures can trade area, wiring, and timing to improve it. The functional equations alone do not predict clock frequency or power. Synthesis can choose a mapping based on constraints and target technology.

The site's truth table checks a combinational equation, not a CPU pipeline or clocked register update. The [clocked-controller lesson](/learn/device/7/) adds stored state and transition rules; [timing foundations](/learn/device/3/) explain why a correct Boolean equation can still fail a physical timing requirement. Keep the layers connected without claiming the simplified runner models all of them.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```verilog run:reference
module half_adder(input a, input b, output sum, output carry);
    assign sum = a ^ b;
    assign carry = a & b;
endmodule
```

Expected result: State / truth_table: 4 input cases; derive each output using the equations below.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
