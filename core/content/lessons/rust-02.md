## Before expressions: track the returned value

You need [bindings and mutation](/learn/rust/1/) and [function contracts](/learn/c/6/). A Rust block can produce a value through its final expression. An explicit return also ends a function with a value. Statements, expressions, and the punctuation separating them are semantic distinctions; they are not formatting preferences.

In the reference, `total` without a trailing semicolon is the value returned by sum_to. The caller binds that returned scalar to answer, then prints it. The parameter n and accumulator total belong to the call. The input need not be mutable because the algorithm changes its accumulator rather than changing the problem definition.

## Derive the visited range

`1..=5` includes both endpoints and visits five terms. `1..5` excludes five and visits four. At the start of each iteration in the reference, total is the sum of earlier positive terms; adding i maintains that relationship. The independently expected result for n=5 is fifteen. For n=0, this ascending range contributes no values in the documented subset, so total remains zero.

The interpretation is an integer sequence, not an array allocation containing every term. A native compiler may transform or optimize it. This site's engine interprets the supported syntax, so its step count cannot be compared directly with RV32I instruction counts as a performance measurement.

## Try a nontrivial independently calculated result

```rust run:squares
fn sum_squares(n: i32) -> i32 {
    let mut total: i32 = 0;
    for i in 1..=n {
        total += i * i;
    }
    total
}
fn main() {
    let answer: i32 = sum_squares(3);
    println!("squares={}", answer);
}
```

Try this in the terminal beside the documentation. Expect `squares=14` because 1+4+9=14. Change the inclusive range to an exclusive range and predict five. That is valid execution with a changed algorithm, not a syntax failure. The page's original reference target describes sum_to, so use your new prediction for the experiment.

Returning a computed value and performing effects are different contracts. A real device function can return a status after issuing a write; the status still needs a defined meaning, such as invalid parameters, acknowledged completion, or timeout. [Lifecycle foundations](/learn/device/2/) establish those meanings before they are encoded in a particular systems language.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```rust run:reference
fn sum_to(n: i32) -> i32 {
    let mut total: i32 = 0;
    for i in 1..=n {
        total += i;
    }
    total
}
fn main() {
    let answer: i32 = sum_to(5);
    println!("sum={}", answer);
}
```

Expected result: Console: `sum=15`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
