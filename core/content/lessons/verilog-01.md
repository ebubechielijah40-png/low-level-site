## Before hardware description: change your execution model

Know [bit operations](/learn/assembly/2/). Verilog is not a lower-level spelling of a C loop. A combinational description specifies a relationship among signals. After inputs change and a physical circuit settles, its output follows that relationship. Real settling involves propagation delay; this runner evaluates only the ideal logical function.

`module gate` names the design. `input a, input b` supplies two one-bit inputs. `output y` is a one-bit output. `assign y = a & b` is a continuous relationship, not a command the CPU issues once to store a permanent value. The module's source ordering does not make an input stop existing after it has been used.

## Exhaustive behavior is small enough to derive

Two one-bit inputs have four combinations. AND returns one only for a=1,b=1. The simulator enumerates the first declared input in the low position of its input vector; that is why the printed row order differs from a table sorted with a as the most significant bit. Row order is presentation, while each input-to-output mapping is the behavior being tested.

## Try two distinct output functions beside the explanation

```verilog run:two-gates
module gates(input a, input b, output both, output different);
    assign both = a & b;
    assign different = a ^ b;
endmodule
```

Expect four rows. Both is one only for 11. Different is one for 10 and 01 and zero for equal inputs. Open **State / truth_table** and inspect every case; a single favorable case would not establish either function.

## Physical design adds constraints beyond Boolean correctness

A gate network needs technology-specific implementation, power, timing, loading, placement, routing, and testing. A synthesis tool transforms supported HDL into an implementation; an FPGA toolchain generates and programs a compatible bitstream. This site's runner provides none of those stages. It also lacks four-state X/Z logic, multiple drivers, delay, clocks, and sequential assignments.

These limits do not prevent the combinational experiments from being useful. They make the exact claim clear: all enumerated Boolean inputs produce the displayed ideal outputs. After the adder and multiplexer lessons, [clocked-state foundations](/learn/device/7/) explain what changes when a controller must remember past events. Do not equate passing a truth table with a programmed controller or measured circuit.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```verilog run:reference
module gate(input a, input b, output y);
    assign y = a & b;
endmodule
```

Expected result: State / truth_table: 4 input cases; derive each output using the equations below.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## Hardware description is a different kind of language
Verilog describes digital logic. A continuous assignment expresses a relationship between signals: `assign y = a & b;` means output y follows the bitwise AND of inputs a and b. It is not a CPU loop that repeatedly runs one statement. In a combinational circuit, outputs depend on current inputs without stored state.

A module groups ports and internal behaviour. Inputs carry signals into the module; outputs carry signals out. A wire-like signal represents a connection rather than an ordinary mutable local variable. Multiple hardware descriptions can be elaborated into a model, simulated, and often synthesised into gates for a physical target.

## Separate simulation and synthesis
Simulation evaluates a model. Synthesis maps a supported description to a hardware implementation such as an FPGA netlist. Configuring an FPGA then requires the vendor's device tools and a bitstream. This site's runner performs combinational simulation only; it does not synthesise a design, generate a bitstream, model propagation delay, or program a real board.

The runner supports one ANSI-style module, input/output widths from one to four bits, at most eight total input bits, and one continuous assignment for each output. It evaluates ordinary bitwise, arithmetic, comparison, bit-selection, and conditional expressions in this documented subset. It excludes always blocks, clocks, sequential registers, X/Z logic, delays, and drive strengths. Real Verilog has a much wider semantics.

## Derive the truth table
AND is one exactly when both inputs are one. With two one-bit inputs there are 2^2 = 4 input combinations. The runner exhaustively evaluates all four. Its vector ordering makes the first declared input the least significant portion of the combined input vector, so rows appear as 00, 10, 01, 11 when read as a then b.

The editor's output y is zero in the first three rows and one in the final row. Run and open Signals to inspect the structured truth table. Compare it with your own derivation before looking at the result. An exhaustive check over a defined small input space is stronger than one attractive animation.

## Experiment and practice
Replace AND with OR, then XOR, predicting all rows before each run. Replace bitwise AND with logical AND on wider signals later and compare the results; whole-vector truth testing and bitwise combination differ. Explain why exhaustive testing grows exponentially with the number of input bits.

Your exercise is to build two outputs: one for AND and one for XOR. Write one continuous assignment per output and independently state each truth table. This is the foundation for the next lesson's adder, where arithmetic behaviour emerges from a small network of Boolean relationships.
