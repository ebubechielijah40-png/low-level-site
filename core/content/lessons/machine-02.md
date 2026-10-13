## Before decoding: fields occupy positions

Review [bit patterns and machine state](/learn/machine/1/). A field is a selected group of bit positions. Shifting changes which positions a value occupies; masking discards positions you do not want. The same operations that assemble an instruction also decode it. You do not need to memorize every hex word, but you must be able to derive one and explain each part.

For a word `w`, ADDI decoding uses `opcode = w & 0x7F`, `rd = (w >> 7) & 31`, `funct3 = (w >> 12) & 7`, `rs1 = (w >> 15) & 31`, and `raw_imm = (w >> 20) & 0xFFF`. Mask 31 is five one-bits and isolates a register index. Mask seven isolates three selector bits. Bit numbering starts at zero; the rightmost bit is the least significant.

## Derive both words, then derive their effects

For `00700293`, the fields are immediate 7, rs1 0, funct3 0, rd 5, opcode 0x13. The effect is x5=7. For `00328293`, immediate 3, rs1 5, funct3 0, rd 5, opcode 0x13. Its effect is x5=old x5+3=10. The second instruction depends on the first because its source field now selects x5, not x0. Changing only that source field can create a valid instruction with a wrong answer.

A signed twelve-bit immediate uses bit eleven as its sign. If the raw field is at least 2048, subtract 4096 to obtain the signed value. Thus `0xFFF` gives 4095-4096=-1, while `0x7FF` gives 2047. The field cannot encode +2048 as a positive ADDI immediate. Larger constants need other instructions or an assembler expansion.

## A second complete decoding experiment

Try this in the terminal beside the documentation. Predict x5's stored pattern and x6's value before loading it.

```machine run:signed-immediate
fff00293
00128313
00000073
```

Expect x5=4294967295 in the unsigned register display and x6=0. The first word represents -1; the second adds one to those register bits. Register addition keeps the low 32 bits. The signed immediate rule and the fixed-width arithmetic rule are separate steps in that explanation.

For independent decoding, derive `addi x6,x5,-2` as `ffe28313`. Insert it after the original two arithmetic words and before ECALL. Predict x6=8, then inspect the trace to confirm the source was ten and the immediate was -2. Explain an error by naming a field, an interpretation rule, or a state dependency rather than describing hex as unreadable.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```machine run:reference
00700293
00328293
00000073
```

Expected result: State / registers: `x5 = 10`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## The agreement between software and hardware
An instruction-set architecture, or ISA, defines what instruction bits mean. RV32I is a particular ISA; x86 and ARM have different encodings. Machine code therefore belongs to an architecture, not to computers in general. You cannot send an RV32I instruction to an x86 processor and expect the same result.

RV32I numbers bits starting at zero at the right-hand end. An ADDI instruction uses the I-type layout. Bits 6–0 contain opcode `0010011`, which is hex 13. Bits 11–7 select the destination register. Bits 14–12 contain a function selector, zero for ADDI. Bits 19–15 select the source register. Bits 31–20 contain a signed twelve-bit immediate.

| Field | Width | Value for addi x5, x0, 5 |
|---|---|---|
| immediate | 12 | 5 |
| source rs1 | 5 | 0 |
| function | 3 | 0 |
| destination rd | 5 | 5 |
| opcode | 7 | 19 decimal |

The encoding is `(5 << 20) | (0 << 15) | (0 << 12) | (5 << 7) | 0x13`. A left shift moves a field into its allotted position; bitwise OR combines fields whose one-bits do not overlap. The result is `0x00500293`. This is a derivation you can repeat for any supported ADDI.

## Immediate values have a limit
A twelve-bit signed value ranges from -2048 through 2047. Signed interpretation uses two's complement. The top immediate bit indicates a negative value; decoding sign-extends it to 32 bits. For example the twelve-bit pattern `FFF` represents -1, not 4095, in this field. The ADDI word with source x0, destination x5, and immediate -1 is `fff00293`. The stored register bits become `ffffffff`, which is 4294967295 under an unsigned view and -1 under a signed view.

## Work the example
The editor loads 7 into x5, then adds 3 to x5. The second instruction's source field is no longer zero. Compute its encoding from the layout before checking the source. Run it and inspect x5: the expected value is 10. Read the trace PC values and confirm that data values and instruction addresses are different things.

For the exercise, encode `addi x6, x5, -2`. Derive each field, combine them, and predict x6 = 8 after the existing program. Keep the final halt instruction at the end. If a changed word fails, distinguish a malformed instruction from a valid instruction with an unintended register field. That distinction is central to debugging at this level.
