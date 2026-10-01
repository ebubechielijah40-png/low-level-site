## Aliasing creates a coordination problem
The C pointer lesson showed two paths reaching the same object. That is useful, but it raises a question: which path is allowed to change the object while another path depends on its value? Rust's reference rules make an access policy part of the language. At a given relevant period, shared references allow reading, while a mutable reference requires exclusive access to the borrowed object.

A shared reference is written `&value`; a mutable reference is `&mut value`. The original binding must permit mutation before creating a mutable reference. Writing through `*reference` uses indirection, just as the C pointer example did, but the permission model differs. Rust's compiler also tracks lifetimes to ensure references do not outlive their referents.

## What this lab checks
The teaching checker detects attempted reassignment of immutable bindings, creation of a mutable borrow from an immutable binding, overlapping mutable/shared borrows, and writes through a shared reference. It conservatively keeps a borrow active until its enclosing lexical block ends. Native Rust often ends a borrow after its last use through non-lexical lifetime analysis. Consequently some valid native programs are rejected by this narrower checker. It is not a replacement for rustc.

The runner is limited to scalar integer reference experiments and does not implement a complete ownership system for heap values, moves, collections, or concurrent code. Calling every accepted program "memory safe Rust" would overstate the evidence. The lesson is about a concrete access rule you can observe.

## Follow the example
The editor declares value mutable. Inside a nested block, it creates one mutable reference and adds 21 through it. Leaving the block ends that borrow in the teaching checker. The program then prints value = 42. The object has one identity throughout, while permitted access paths change over time.

Add a second mutable reference in the same block and run. The checker rejects overlapping exclusive access. Replace the borrow with a shared one and retain the write through it; that is rejected too. Move a direct assignment to value inside the borrowed block; the checker identifies the conflicting owner access. These are deliberate failure tests, not merely alternate examples.

## Exercise
Create two separate integer objects and borrow each mutably inside one block. Explain why that does not alias the same object. Then implement a read-only calculation using a shared reference. State which guarantee the local checker actually verifies and which full Rust properties require the native compiler. Precise scope is a scientific habit as well as an engineering habit.
