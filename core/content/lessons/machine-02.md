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
