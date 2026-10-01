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
