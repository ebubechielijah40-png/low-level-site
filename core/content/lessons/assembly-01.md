## Before assembly: keep the machine model

Complete or review [machine control flow](/learn/machine/6/). The learning path keeps RV32I throughout these first two tracks. Assembly changes how you write instructions, not their architectural effects. The same word can be expressed as a mnemonic, hexadecimal, or binary, and the execution model should agree.

The assembler first determines instruction and data locations, then resolves symbolic references and emits words. This matters because a label cannot be resolved by assuming one source line equals four bytes. Blank lines, comments, and labels emit none. A pseudo instruction may emit more than one word. Data directives emit data bytes, and those bytes are not automatically safe instruction targets.

## Work from source to encoding to state

`li t0,21` means load an immediate into x5. For this small constant the emitted instruction is `addi x5,x0,21`, word `01500293`. `add t1,t0,t0` uses x6 as destination and x5 for both inputs; it computes 42 without changing x5. `mv a0,t1` is ADDI with immediate zero. The instruction name MV is an assembler convenience; the processor executes the resulting ADDI.

Register aliases describe a conventional role, not a type. a0 and x10 are the same physical architectural register in this model. Nothing stops you from storing an address there, but a service expecting an integer will interpret its bits as that integer. Interfaces establish the meaning of the register contents at a boundary.

## Try a pseudo instruction that needs two words

```assembly run:large-immediate
li t0,4096
addi t1,t0,1
mv a0,t1
li a7,1
ecall
li a7,10
ecall
```

Try this in the terminal beside the documentation and expect 4097. Open **Encoding** and inspect the expansion of the first source line. A value outside ADDI's twelve-bit signed range needs a wider construction; the returned listing shows the emitted LUI/ADDI sequence. Moving a later label must account for those extra words. Open **Trace** to connect each emitted word to its register write.

An assembler diagnoses spelling, unsupported instruction forms, unknown labels, and encoding bounds. It cannot determine that adding two valid registers implements the algorithm you intended. Compare a successful assembly with an independently predicted final state. This distinction will carry into C, where a parsed program can still express the wrong algorithm.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```assembly run:reference
li t0,21
add t1,t0,t0
mv a0,t1
li a7,1
ecall
li a7,10
ecall
```

Expected result: Console: `42`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

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
