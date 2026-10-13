## Before borrowing: understand why aliases need a policy

Review [C copies and aliases](/learn/c/5/) and [Rust mutation permission](/learn/rust/1/). The same object can be reached through multiple paths. The question is not only whether those paths point to valid storage, but which path may read or write while another path relies on that object's state.

A shared reference grants reading through a shared access path. A mutable reference grants exclusive access during the relevant borrow. The owner must permit mutation to create that mutable reference. These permissions are language rules enforced by analysis; they do not add a new CPU register type.

## Follow the ownership of access in the reference

Initially value is accessible through its owner binding. Inside the nested block, pointer borrows it mutably. Writing `*pointer` changes the same referent from 21 to 42. While the borrow is active, direct owner access conflicts with this teaching policy. Leaving the block ends the lexical borrow, so the later print through value is allowed.

Native Rust commonly uses non-lexical lifetime analysis: a borrow can stop being needed after its last use rather than lasting until the enclosing brace. This runner deliberately retains it through the block and can reject valid native examples. It also lacks general move analysis, reference parameters, heap collections, traits, concurrency, and unsafe code. Its local checks are a learning experiment, not a full memory-safety certification.

## Try conflicting access beside the documentation

```rust run:borrow-conflict
fn main() {
    let mut value: i32 = 21;
    {
        let first = &mut value;
        let second = &mut value;
        *first = 42;
        *second = 7;
    }
}
```

Expect a borrow error. Both references would grant overlapping exclusive access to the same object. Borrowing two distinct integer objects is a different case: the paths do not alias, so the same conflict need not exist.

## Exclusive software access is not device synchronization

A device or interrupt handler can change state outside an ordinary sequential reference model. Native systems Rust needs abstractions appropriate to MMIO, synchronization, DMA buffer ownership, and platform constraints. Passing a local borrow check does not guarantee a DMA engine has finished using memory or that a write reached a physical controller. [DMA and event foundations](/learn/device/4/) describe those additional ownership transfers. Their requirements exist regardless of whether the driver source is C or Rust.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```rust run:reference
fn main() {
    let mut value: i32 = 21;
    {
        let pointer = &mut value;
        *pointer = *pointer + 21;
    }
    println!("value={}", value);
}
```

Expected result: Console: `value=42`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
