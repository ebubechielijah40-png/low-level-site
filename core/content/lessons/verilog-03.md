## Before selection: identify both data and control

Review [continuous assignments](/learn/verilog/1/). A multiplexer receives candidate data and a control value selecting which candidate reaches an output. Input a does not disappear when b is selected. Its changes simply do not influence y under that selection.

For `select ? b : a`, the precise contract is y=a when select=0 and y=b when select=1. With three one-bit inputs there are eight cases. Compare rows that hold select and the selected input constant while changing the unselected input; y must stay unchanged. That property captures the isolation the mux is supposed to provide.

## Try a bus-sized selection in the terminal beside you

```verilog run:bus-mux
module mux2(input [1:0] a, input [1:0] b, input select, output [1:0] y);
    assign y = select ? b : a;
endmodule
```

Expect thirty-two input rows because the design has five total input bits. Each two-bit data input has four possible values, and select has two. For a=1,b=2, y must be one with select zero and two with select one. Check those cases and the endpoint values zero and three in **State / truth_table**.

## Width changes the control-mask derivation

The one-bit identity `(~select & a) | (select & b)` relies on a one-bit selection mask. For a multi-bit bus, an asserted selection signal must select all the intended bus positions. A one-bit mask value one has only its low bit set. Applying it directly to a wider bus can retain only that bit, rather than forwarding the whole value. The conditional expression expresses the intended selection more clearly in this subset.

In a processor, muxes can select an ALU operand, writeback source, or next PC. Decoder fields influence control, and stored instruction operands provide data. Choosing a correct result is as necessary as computing it. A wrong control signal can route a valid but unintended value to a destination register.

No storage is implied by this mux: it does not remember an earlier selection after inputs change. Registers and clocked state require sequential logic beyond this runner. Four-bit a and b plus select need nine input bits, exceeding the site's eight-bit exhaustive limit; the larger design is not made invalid HDL by the teaching resource bound. Distinguish language validity, tool support, and physical implementation constraints.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```verilog run:reference
module mux(input a, input b, input select, output y);
    assign y = select ? b : a;
endmodule
```

Expected result: State / truth_table: 8 input cases; derive each output using the equations below.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## A multiplexer selects data
A two-to-one multiplexer has two data inputs, one selection signal, and one output. If select is zero it forwards input a; if select is one it forwards input b. Both inputs still exist. The circuit changes which input influences the output, not whether the inputs are present in the wider machine.

The Verilog conditional expression `select ? b : a` describes that relationship. A logically equivalent one-bit form is `(~select & a) | (select & b)`, with the result restricted to the declared width. For wider buses, the conditional forwards the whole selected value. Bitwise control equations require carefully replicated masks to behave the same way.

## Why processors need selection
A processor datapath often has several candidates for one destination: an ALU result, a memory-loaded value, or a return address. Control logic chooses which candidate reaches the destination register. A multiplexer is one conceptual building block for that choice. Describing this functional role does not establish the exact layout of any particular commercial CPU.

The earlier instruction decoder extracted opcode fields. Those fields can influence control signals that select ALU operations, register writes, and next-PC sources. Instruction execution therefore depends on both computing possible values and selecting the appropriate one. This lesson focuses on selection in isolation so each cause is easy to inspect.

## Exhaustive cases
There are three one-bit inputs, so eight input combinations. Four have select zero and must produce output equal to a; four have select one and must produce output equal to b. The runner lists every case. The unselected input can change without affecting the output, a useful property you can inspect directly.

Run and compare paired rows where only the unselected input differs. Then reverse a and b in the conditional and identify exactly which rows change. Replace the select signal with its logical negation and derive the resulting mapping before execution. These experiments make a control inversion visible without requiring a complete processor model.

## Exercise
Create a four-bit two-to-one multiplexer with two four-bit inputs. That would use nine total input bits including selection, beyond this runner's eight-bit exhaustive bound. Explain why the model rejects it even though it is a valid native Verilog design. Use two-bit inputs instead, requiring five total bits and thirty-two cases. Test the identity y = a whenever select is zero and y = b otherwise.

Bounds are part of a teaching tool's interface. They limit computational effort and scope, while the language and real synthesis tools remain broader than the embedded exercise.
