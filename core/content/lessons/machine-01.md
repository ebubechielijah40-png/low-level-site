## Start with the state you can actually inspect

No programming prerequisite is required. You need positional notation: decimal `42` means four tens plus two ones; binary uses powers of two instead of ten. A byte contains eight bits and has 256 possible patterns, because each of eight positions has two possibilities. A 32-bit word has 2^32 patterns. Width counts available states; interpretation assigns meanings to them.

A physical machine must distinguish its states reliably. A voltage range can represent a logical level; a latch or other storage structure retains a state. These physical mechanisms have tolerances and timing. The emulator starts above that layer, at the architectural contract: registers, a program counter, instruction bytes, and memory. It lets you inspect the logical consequences of instructions; it cannot establish transistor behavior or electrical timing.

For this page the initial contract is `pc=0`, `x0=0`, `x2=0xE000`, and the other integer registers zero. Program instructions begin at address zero. At the start of each instruction, PC identifies the instruction being fetched. Execution then computes the next PC. The stack pointer's initial value is supplied by this teaching environment; the RV32I instruction set does not require a stack at that address.

## Follow one cause through the whole machine

The instruction word `00500293` contains a request to add the immediate five to the value read from x0 and write the result to x5. Fetch obtains the bits at the current PC. Decode selects ADDI and the register fields. Execute computes `0+5`. Writeback changes x5. The next-PC rule advances by four bytes. x6, RAM, and x0 remain unchanged. An instruction is constrained by its decoded fields, not by what you hoped it would do.

The final word `00000073` is ECALL. With a7 initially zero, this teaching environment treats it as a stop. ECALL itself does not universally mean stop; the environment defines the service convention. Keeping that distinction now prevents confusion when you later encounter a real operating system.

Before running, write a before/after table for PC and x5. After running, use **Trace** to locate the x5 write and **State / registers** to inspect the retained value. Empty console output is expected: changing a register does not automatically print anything. Change the immediate word to `00900293`; predict x5=9 while the original reference check fails. A failed reference check can therefore mean your experiment changed the intended result, rather than that execution is broken.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```machine run:reference
00500293
00000073
```

Expected result: State / registers: `x5 = 5`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## Bits are state before they are meaning
A machine does not begin with numbers, variables, or text. It begins with distinguishable physical states. In real hardware those states may be voltage ranges, charge, magnetic orientation, transistor arrangements, or optical levels. In this teaching machine we collapse that physical mess into one clean abstraction: a bit can be in one of two states, written `0` or `1`.

The labels are already a human convenience. A bit marked `1` is not the idea of one. It is a state we have agreed to interpret as one when a particular rule says so. This matters because the same eight bits can be treated as an unsigned integer, a signed integer, an ASCII character, part of an instruction, a colour channel, a permission mask, or raw uninterpreted data.

The pattern below is not born as the number 42:

```text
00101010
```

It becomes 42 only when you apply the unsigned positional rule:

```text
bit:      0 0 1 0 1 0 1 0
weight: 128 64 32 16 8 4 2 1
value:        32    8   2   = 42
```

Hexadecimal is not another thing the CPU secretly understands. It is a compact notation for humans. Four bits become one hex digit, so `0010 1010` becomes `0x2A`. The bits did not change. Only the way you wrote them changed.

## The first machine model
This project begins with a small RV32I-style integer machine because it gives you the essential pieces without drowning the first lesson in every detail of a commercial processor. The model has:

- thirty-two general registers, `x0` through `x31`;
- each register holds exactly 32 bits;
- byte-addressed memory;
- a program counter, `pc`, that stores the address of the next instruction;
- fixed-width 32-bit instruction words for the subset used here.

The processor state before the first instruction is mostly zero:

```text
pc = 0
x0 = 0
x1 = 0
x2 = virtual stack address
x3..x31 = 0
```

Register `x0` is special. It always reads as zero. If an instruction tries to write into `x0`, the result is discarded. That is not a style rule; it is part of the architecture. Many instruction sequences rely on this fixed zero source.

The program counter is not a line number. It is an address. Because this subset uses 32-bit instruction words, each normal instruction occupies four bytes. If execution simply moves to the next instruction, `pc` changes from `0` to `4`, then to `8`, then to `12`.

## One instruction as a state transformation
The first word in the starter program is:

```text
00500293
```

Under the RV32I decoding rule used by this lesson, that word means:

```text
addi x5, x0, 5
```

Read it as a transformation:

```text
destination = x5
source      = x0
immediate   = 5
operation   = source + immediate
```

Before the instruction:

```text
x0 = 0
x5 = 0
pc = 0
```

After the instruction:

```text
x0 = 0
x5 = 5
pc = 4
```

Nothing mystical happened. The CPU model fetched the 32-bit word at the address in `pc`, decoded fields inside that word, read `x0`, added the immediate value `5`, wrote the result into `x5`, then advanced `pc`.

The second word in the starter is an environment call used by the teaching runner to stop the program. That stop instruction is part of this educational execution contract. It does not mean the web server ran a native binary on its own CPU.

## What this destroys
The first false model to kill is this: “machine code is just unreadable text.”

Machine code is not text. It is encoded control. A 32-bit instruction word is divided into fields. Some bits identify the operation. Some bits identify registers. Some bits carry an immediate value. Assembly is a human notation for the same control pattern. The machine word is what the processor model actually executes.

A second false model: “a number is a number everywhere.”

The same bits can be interpreted differently by different instructions. `11111111` may be 255 under an unsigned rule, -1 under an 8-bit two's-complement signed rule, or part of an instruction field under a decoder rule. If you do not know the rule being applied, you do not yet know what the bits mean.

## Run the experiment
Before pressing Run, predict these three facts:

```text
x5 after first instruction = 5
pc after first instruction = 4
x0 after first instruction = 0
```

Run the program, then inspect **State / registers** and **Trace**. The trace is more important than the success message because it shows the state transition.

Now mutate exactly one cause:

```text
00500293
```

to:

```text
00900293
```

Predict the new `x5`. The destination and operation are unchanged; only the immediate changes from 5 to 9. If your model is right, `x5` becomes 9.

Then test a boundary:

```text
00000013
```

This is a no-op style instruction in RV32I notation: `addi x0, x0, 0`. It tries to write zero into `x0`, but `x0` remains zero because writes to `x0` are discarded. This is a small architectural law, and small laws compound into whole systems.

## Check your understanding
Explain these without using vague words like “the computer understands it”:

- Why does `00101010` become 42 under one rule but not under every rule?
- Why does `0x2A` not change the underlying bits?
- Why does the emulator need an instruction-set rule before it can execute `00500293`?
- Why does `pc` advance by four instead of one?
- Why can an instruction write to `x5` but fail to change `x0`?

If you can answer those precisely, you are not memorising machine code. You are beginning to reason from state, encoding, and transformation.
