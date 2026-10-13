## Before buses: width is part of the contract

You need [gates](/learn/verilog/1/) and [selection](/learn/verilog/3/). `[1:0]` names two bit positions, giving unsigned values zero through three. A two-bit output cannot retain every sum of two two-bit inputs, since maximum sum six needs three bits. Output masking in this model makes truncation observable.

The reference compares a and b for equality and less-than. Its sixteen rows come from four possible values for each input. Equality occurs on four diagonal cases. Strict less-than occurs on six cases. Derive that count from the pairs: for b=1 there is one smaller a, for b=2 two, and for b=3 three.

## Try a complete range-validation circuit beside you

```verilog run:range-check
module range_check(input [3:0] capacity, output valid);
    assign valid = (capacity >= 4) & (capacity <= 12);
endmodule
```

Expect sixteen rows, with valid one for capacity 4 through 12 inclusive and zero for the other seven values. Both comparisons produce one-bit results in this teaching model. The capacity bus still contains the original four-bit input; checking its range does not change it.

## Distinguish truncation from truth testing

A one-bit output assigned numeric two becomes zero after masking because two's low bit is zero. A comparison testing whether two is nonzero gives one. Those are different operations. Similarly, a bitwise inversion of a bus depends on its width. Native Verilog has detailed rules for operand widths, signedness, unsized literals, and expression context; the site's small unsigned signal model does not establish complete compliance with those rules.

## Validation logic is one part of a controller

A range checker can reject an unsupported requested field. A controller still needs state for reset, busy, completion, and fault; storage for configuration; bus-interface semantics; clock-domain handling; and physical timing constraints. HDL syntax can express those designs in a full toolchain, but passing this truth table does not implement that larger controller.

The hardware configuration labs use C or RV32I to write a software-facing interface. This Verilog branch explores logic that might underlie such an interface. One describes the circuitry's relationship; the other requests behavior through registers. Continue to [state machines and reset](/learn/device/7/) and [timing budgets](/learn/device/3/) to connect them without assuming they are interchangeable.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```verilog run:reference
module compare(input [1:0] a, input [1:0] b, output equal, output less);
    assign equal = a == b;
    assign less = a < b;
endmodule
```

Expected result: State / truth_table: 16 input cases; derive each output using the equations below.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## A bus carries several bits together
The declaration `[1:0]` describes two bit positions, one and zero. Such a signal can represent unsigned values from zero through three in this lesson. A declaration `[3:0]` has four positions, not three, because both endpoints count. Width mistakes often originate in confusing a highest index with a number of elements.

Comparisons produce one-bit results. `a == b` indicates equality; `a < b` indicates an unsigned ordering in this teaching model. Native Verilog has detailed signedness and sizing rules, including distinctions between signed signals and unsized constants. Our subset documents its simpler unsigned signal model and masks every output to its declared width.

## Separate arithmetic width from result width
An output wider than one bit can retain more result information. A one-bit output receiving a numeric expression keeps only one bit after masking in this simulator. That is not the same as asking whether the expression is nonzero. Bit truncation and Boolean interpretation must therefore be distinguished, just as they were in the C and machine tracks.

The editor compares two two-bit inputs and produces equal and less outputs. There are four choices for a and four choices for b, yielding sixteen cases. Each row's equal output must be one exactly when the input values match. Each less output must be one exactly when a is numerically smaller than b. The expected table comes from those contracts.

## Work and inspect
Run the design and find the four equality rows. Find the rows with a = 3; none should report a < b because b cannot exceed three. Find the rows with b = 0; none should report a < b because a cannot be negative in this signal model.

Change the comparison from < to <= and predict that the equality rows now also produce one on that output. Change one input width and recalculate the number of exhaustive cases before running. Input-space size grows as two to the sum of input widths; doubling a numeric range adds bits and can multiply the number of rows substantially.

## Exercise and transition to hardware configuration
Build a range checker for a four-bit capacity selector using one input bus and one valid output. State a legal interval and derive all sixteen outcomes. Explain how such a circuit could contribute to validation logic without claiming it configures physical RAM by itself.

From here the hardware configuration labs combine software-facing registers with component models. Verilog describes logic that could implement a controller, while C or assembly interacts with a documented controller interface. These are related layers, not interchangeable names for the same activity.
