## Assembly adds names, not new hardware
Machine code is the processor's encoding. Assembly is a textual way to describe those encodings. An assembler resolves mnemonics, registers, constants, and labels into bytes. The mnemonic `addi` is easier to edit than `00500293`, but both can describe the same instruction. The processor never reads the mnemonic itself.

Our assembly track uses RV32I, the same architecture as the machine-code track. This avoids silently changing register sizes or instruction rules while you are still constructing a model. Existing x86 examples in the original project used rax and NASM; those names belong to a different architecture. The OS boot lab later introduces its x86 16-bit target explicitly.

## Register names are conventions
`x10` and `a0` name the same register. Aliases make roles visible: a0–a7 conventionally carry arguments, t0–t6 are temporary values, ra holds a return address, and sp holds a stack pointer. Hardware does not enforce these roles. A calling convention is an agreement between separately written pieces of software about how they will cooperate.

The first example loads 21 into t0, adds t0 to itself, and moves 42 into a0. `li` and `mv` are pseudo instructions. The assembler rewrites them using real instructions. For a small constant, `li t0,21` is ADDI from x0. `mv a0,t1` is ADDI with immediate zero. A large constant may require LUI followed by ADDI, so one assembly line need not equal one machine word.

## Read the evidence
Run the example and open Encoding. Compare the machine words with the first track. Each listing row includes the original source line and the byte address of the emitted instruction. Open Registers and find both x10 and the numeric register that t1 names. Trace establishes the order of writes; the register view establishes the final state.

The program selects teaching ECALL service 1 to print an integer, followed by service 10 to halt. These calls are provided by the emulator, not by the browser and not by a Linux kernel. A program ported to Linux would need that environment's system-call ABI and a way to encode text.

## Practice
Rewrite the program using only numeric x-register names and real instructions. Its output should stay 42. Then use a constant larger than 2047 and inspect how many words `li` emits. Explain why labels are preferable to counting offsets manually when pseudo-instruction expansion can change program size. Assembly removes bookkeeping, while preserving the underlying machine behaviour.
