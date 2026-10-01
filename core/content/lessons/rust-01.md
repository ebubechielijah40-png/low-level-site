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
