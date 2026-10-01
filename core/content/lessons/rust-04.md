## A fixed-size array makes a size claim
An array stores a fixed number of elements of one type. In native Rust, `[i32; 4]` is a type describing four signed 32-bit elements. The teaching subset accepts the concrete initializer `[4, 8, 12, 16]` and keeps an explicit bounded virtual array. Its simplified type inference does not cover all native array types or constructors.

Index zero names the first element. With four elements the valid indices are zero through three. A loop over `0..4` visits precisely those indices, while `0..=4` includes an invalid fifth access. These are source-level ways to express the same address calculation you already studied: base plus index times element size.

## A language can help enforce a boundary
Native Rust normally performs a bounds check for indexed array access and panics on an out-of-range index, unless the compiler proves the check unnecessary. Unsafe operations introduce other obligations. The interpreter gives a structured bounds error rather than a native panic because it is a bounded learning environment.

This difference from ordinary unchecked C array indexing matters. It does not eliminate the need to choose the correct logical range: a program can remain inside every bound and still omit an element, repeat one, or compute the wrong aggregate. Type and runtime checks establish some properties; an algorithm contract establishes others.

## Work the sum
The editor creates four values, declares total mutable, and visits indices in `0..4`. The expected result is 40. The source separates stable input from evolving state: the array binding is immutable while the accumulator changes. Inspect Variables to confirm the input array remains unchanged after execution.

Change the range to `1..4` and predict the new sum, 36. Change it to `0..=4` and observe the boundary failure. Then change an input value and calculate the expected sum before pressing Run. Use these experiments to distinguish a valid execution from an execution satisfying the intended requirement.

## Exercise
Compute a weighted checksum in which each element is multiplied by its one-based index. Derive the expected result independently. Add a second loop that counts elements greater than ten. Keep bounds explicit, explain the work as linear in the number of elements, and discuss where signed integer overflow could arise. Once these foundations are clear, the full Rust toolchain can add ownership-aware collections and iterators without replacing your model of the underlying storage.
