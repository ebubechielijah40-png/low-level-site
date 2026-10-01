## A block can produce a value
Rust distinguishes statements that perform work from expressions that produce values. A function can return explicitly with return, or use a final expression without a semicolon as its return value. `fn double(x: i32) -> i32 { x * 2 }` returns the product. Adding a semicolon would change the final expression into a statement in native Rust, so punctuation carries semantic meaning.

The embedded runner supports this common trailing-expression form, typed scalar parameters, and integer returns. It is not a full native Rust type checker and does not claim unit-type validation, generic functions, traits, iterators, or heap collections. That scope keeps the project focused on the low-level ideas being taught.

## Define the range precisely
The range `1..6` visits 1 through 5 and excludes 6. The inclusive form `1..=5` visits the same values. The distinction resembles the `<` versus `<=` choice in C, but the range syntax makes it part of the source construct. A loop variable is immutable in this teaching subset; a separate accumulator can be declared mutable.

The example defines sum_to, starts total at zero, and uses an inclusive range through n. Its trailing expression returns total. With n = 5 the result is 15. For n = 0, the ascending range has no elements in this runner's implementation, so total remains zero. The contract is restricted to the nonnegative inputs used in this lesson.

## Connect back to machine behaviour
A native compiler can turn this range loop into comparisons, additions, and branches similar to the assembly track. It may also optimise the sequence. The interpreter translates the supported syntax to a bounded virtual execution model rather than claiming to reproduce the compiler's instruction selection.

Inspect Variables and Trace after running. Then switch the range to `1..n` and predict the missing final term. Try a helper that returns a doubled result using a trailing expression. Write down how the caller obtains the returned value and compare it with the a0 return-register convention in the assembly call lesson.

## Exercise
Write a function that returns the sum of squares from one through n. Calculate the expected answer for n = 3 by hand: 1 + 4 + 9 = 14. Separate the immutable parameter from the mutable accumulator. Explain the largest kind of input that could make a multiplication overflow under the chosen integer width before trying larger values.
