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
