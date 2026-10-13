## Before buffers: a legal index is not the entire algorithm

Review [C array layout](/learn/c/4/) and [Rust ranges](/learn/rust/2/). A fixed-size native Rust array has an element type and count in its type. A slice additionally provides a view with a length. This subset supports concrete initialized arrays and bounded indexing; it does not implement the full slice, collection, or iterator APIs.

The reference's stable array contains 4, 8, 12, and 16. The range `0..4` visits indices 0, 1, 2, 3 exactly once. The accumulator produces forty. Using `1..4` stays inside every index bound but misses the first element and produces thirty-six. Bounds protection rules out one category of error; it cannot choose the intended set of elements for you.

## Try a boundary that the checker can diagnose

```rust run:array-boundary
fn main() {
    let values = [4, 8, 12, 16];
    println!("outside={}", values[4]);
}
```

Try this in the terminal beside the documentation and expect a bounds error. In normal native safe Rust, an out-of-range indexed access panics unless an earlier analysis removes the possibility; the teaching environment returns a structured error rather than a native panic. Unsafe access forms have different obligations and are outside this subset.

## Derive a checksum rather than copying a sum

For weights one through four, a weighted sum is `4*1 + 8*2 + 12*3 + 16*4 = 120`. It detects some changes that an ordinary sum cannot distinguish: swapping two different elements preserves the ordinary sum but can change the weighted one. This does not make it a cryptographic integrity function or a general error-correcting code.

Write that weighted calculation using the supported integer range and indexing, then predict the result after swapping the first two values. The new weighted result is 116. A new successful computation may fail the page's forty-sum reference check; use the stated independent target for your experiment.

Device buffers additionally require ownership, valid transferred length, alignment, and mapping. A declared array count does not guarantee that every element has arrived from hardware or that the device has relinquished it. Combine this source-language reasoning with [DMA ownership](/learn/device/4/) and [protocol lengths](/learn/device/5/) before configuring a real transfer path.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```rust run:reference
fn main() {
    let values = [4, 8, 12, 16];
    let mut total: i32 = 0;
    for i in 0..4 {
        total += values[i];
    }
    println!("sum={}", total);
}
```

Expected result: Console: `sum=40`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
