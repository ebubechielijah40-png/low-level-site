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
