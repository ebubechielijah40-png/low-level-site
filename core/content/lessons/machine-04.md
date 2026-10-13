## Before the ALU: identify what is read and written

Review [register dependencies](/learn/machine/3/). An ALU operation takes input bit patterns and an operation selector, then produces a result. The architectural rule specifies where the result is stored. A possible physical implementation uses adders, gates, and multiplexers; the instruction contract specifies behavior without prescribing a particular transistor arrangement or pipeline.

For an R-type instruction, opcode is `0x33`, rd occupies bits 11-7, rs1 bits 19-15, and rs2 bits 24-20. ADD uses funct3=0 and funct7=0. SUB uses the same funct3 with funct7=32. Therefore the difference between `006283b3` and `40628433` includes both the operation selector and destination register. Decode each changed field instead of assuming all differences identify only subtraction.

## Derive the final state without running

The two initial immediate instructions make x5=20 and x6=7. ADD writes x7=27. SUB reads the same original inputs and writes x8=13. Neither modifies x5 or x6. Write four rows in your prediction table: x5=20, x6=7, x7=27, x8=13. Checking only x7 leaves operand preservation and subtraction untested.

The arithmetic is modulo 2^32 for these RV32I register operations. If an intermediate mathematical sum exceeds that range, the stored pattern keeps its low bits. A signed or unsigned comparison later interprets that same pattern according to its own instruction. RV32I ADD does not raise a global signed-overflow flag or update an x86-style shared condition-code register.

## Try a boundary that has an independent answer

Load this complete program into the terminal beside the explanation. The mathematical intermediate is 2^32, whose low 32 bits are zero.

```machine run:alu-wrap
fff00293
00100313
006283b3
00000073
```

Expect x5=4294967295, x6=1, x7=0. That result is evidence about the instruction's fixed-width rule. It is not permission to rely on signed overflow in C. The C track separates language rules from machine operations explicitly.

For the original example, derive `sub x8,x6,x5` as `40530433`: expect x8=4294967283 in the unsigned view, which corresponds to signed -13. A low-four-bit mask of the sum is `27 & 15 = 11`. State why the mask preserves selected bit positions and why subtracting a number is not equivalent to clearing its corresponding bits.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```machine run:reference
01400293
00700313
006283b3
40628433
00000073
```

Expected result: State / registers: `x7 = 27`, `x8 = 13`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## State transitions, not hidden intention
An arithmetic logic unit, or ALU, performs operations on fixed-width bit patterns. The ADD instruction reads two source registers and writes one destination. It does not erase either source. For `add x7, x5, x6`, x7 receives the sum of the old x5 and x6 values. The instruction works even if a source and destination are the same register because sources are read before the result is written.

SUB reverses one part of that operation: `sub x8, x5, x6` computes x5 minus x6. Operand order matters. Logical operations AND, OR, and XOR combine corresponding bits. AND gives one only when both input bits are one; OR gives one when either input is one; XOR gives one when the bits differ. A mask is simply a value whose one-bits select positions of interest.

## Fixed width imposes arithmetic rules
A 32-bit register cannot hold every integer. RV32I ADD and SUB keep the low 32 bits, so addition wraps modulo 2^32. Adding one to `ffffffff` produces zero. This hardware behaviour is not a promise that every programming language defines signed overflow in the same way. C signed overflow, for example, is undefined; unsigned C arithmetic has a defined modular rule. We will return to that distinction in the C track.

RV32I has no global condition-code register for these instructions. Branch instructions compare registers directly. An x86 explanation that says every ADD updates shared flags cannot simply be applied to this processor. Always identify the architecture before transferring an intuition.

## Follow the worked example
The program loads 20 and 7, computes a sum of 27 into x7, and a difference of 13 into x8. Registers x5 and x6 still contain their original inputs. Check all four values. A successful output message alone would not establish that the program preserves its sources; the state inspection does.

Now change the subtraction to reverse its source operands. Predict the resulting 32-bit pattern for -13 and compare with the unsigned register display. Add an AND with the mask 15 to keep only the lowest four bits of x7. That result is 11 because 27 is binary 11011 and the mask is 01111.

## Independent practice
Write a word sequence that loads a number, doubles it with ADD, then clears only its lowest bit with AND. Derive the words from the field layouts and inspect the trace. Write down which instruction created each observed register value. This turns debugging into causal reconstruction rather than trial and error.
