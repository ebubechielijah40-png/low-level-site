## Before Rust: separate machine capability from language permission

Review [C object updates](/learn/c/1/) and [pointer identity](/learn/c/5/). A processor can write a register regardless of the source-language declaration that led to it. Rust's mutability and reference rules constrain which source programs are accepted. They are an additional reasoning layer, not a different physical kind of bit.

The reference binds an i32 object initialized to 21 and grants reassignment with `mut`. Its assignment computes 42. The printed result demonstrates an ordinary state update. Removing `mut` changes the program's permission contract, so the teaching checker rejects the assignment before producing a final state. Do not use the fact that a C equivalent executes as an argument that the Rust source must be accepted.

## Try the rejected version beside the explanation

```rust run:immutable-write
fn main() {
    let value: i32 = 21;
    value = 42;
    println!("value={}", value);
}
```

Expect an immutable-binding error. This is evidence about the explicit teaching rule. The runner supports a focused integer Rust-like subset, not rustc's full type, ownership, lifetime, macro, or inference system.

## Types express intent without measuring the target

Native i32 has a signed 32-bit range and u32 an unsigned 32-bit range. Native usize is an unsigned target-sized type for indexing and sizes; a 64-bit target commonly gives it a different width from i32. This interpreter simplifies usize to its integer model, so its display cannot establish a native target's pointer size or ABI.

Native Rust provides checked, wrapping, saturating, and overflowing arithmetic operations, and ordinary overflow checks depend on build settings. Our subset does not implement all those APIs; it uses the documented checked signed model. State which environment produced a result instead of treating one interpreter outcome as all Rust behavior.

## Why this language is relevant to systems work

Stable inputs can stay immutable while accumulators change. Explicit permission reduces accidental state mutation and documents intended data flow. Memory ownership and borrowing extend that policy when aliases appear. Rust is useful for systems implementations, but learning it does not discover a controller map or perform physical calibration. The [device-foundations track](/learn/device/1/) supplies those interface obligations independently of language syntax.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```rust run:reference
fn main() {
    let mut value: i32 = 21;
    value = value * 2;
    println!("value={}", value);
}
```

Expected result: Console: `value=42`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## Why Rust belongs in this progression
Rust is a systems language with abstractions and compile-time rules intended to make many memory and concurrency errors harder to express. It is not lower in abstraction than assembly. It belongs here because it adds another way to control low-level storage and access after you have understood the machine and C model.

A binding associates a name with a value. `let value: i32 = 21;` creates an immutable binding with a signed 32-bit integer type. `let mut value: i32 = 21;` explicitly permits reassignment. Mutability is a permission in the source language, not a property of the underlying register hardware. The machine could write the bits either way; the language restricts which programs are accepted.

## Types carry arithmetic intention
The name i32 means a signed 32-bit integer; u32 means unsigned. usize is the native index-sized unsigned type in full Rust, but the teaching runner simplifies it to the model's int width. This limitation is documented because a real 64-bit Rust target has different pointer and usize sizes. Native Rust's overflow handling also depends on the operation and build configuration; the runner instead uses explicit checked signed arithmetic inherited from its bounded integer model.

`fn main()` is the entry function. `println!` is a macro in native Rust; the exclamation mark distinguishes macro invocation from an ordinary function call. Here the supported macro uses a literal string and positional `{}` integer placeholders. The interpreter parses it deliberately and supplies bounded output.

## Follow the example
The editor makes value mutable, doubles it, and prints 42. Remove mut and run again. The program now attempts to write an immutable binding, and the teaching checker rejects it. This is a source-level rule that you cannot demonstrate merely by inspecting a final register value; the rejection itself is the important evidence.

In real Rust, shadowing with another let can create a new binding with the same name. This focused runner does not promise all shadowing, inference, lifetime, or pattern features. Use the Runner reference when a construct is rejected. A full rustc build remains the authoritative check for complete Rust semantics.

## Exercise
Create one immutable input binding and one mutable accumulator. Calculate the sum from one through the input. Describe why the input should remain immutable and why the accumulator needs mut. Test zero and one as boundary cases. Then explain which property Rust expresses directly that the earlier C declaration left as a programmer convention.
