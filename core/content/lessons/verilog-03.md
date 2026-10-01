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
