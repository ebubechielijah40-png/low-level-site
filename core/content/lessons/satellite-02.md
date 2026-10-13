## Before choosing a packet check

Review [bit masks](/learn/c/2/), [protocol boundaries](/learn/device/5/), and the [telemetry profile](/hardware/satellite/). An error-detection bit is a defined transformation over a selected group of data bits. It does not validate the measurement's meaning, identify its sender, or encrypt its contents.

## Derive even parity bit by bit

Target payload byte 85 is `0x55`, binary `01010101`, which has four one-bits. An even-parity check bit is therefore zero. XORing all eight bit values produces that check: each pair of ones cancels under XOR. A single-bit change makes the parity one; a two-bit change can leave it zero and go undetected.

```c run:parity-derive
#include <stdio.h>
int main(void) {
    unsigned int data = 85U;
    unsigned int parity = 0U;
    for (int bit = 0; bit < 8; bit++) {
        parity = parity ^ ((data >> bit) & 1U);
    }
    mmio_write(0xF000, data);
    mmio_write(0xF004, parity);
    mmio_write(0xF008, 1);
    printf("data=%u parity=%u\n", data, parity);
    return 0;
}
```

Try this in the terminal beside the documentation. Expect `data=85 parity=0`, all three MMIO targets passing, and telemetry `computed_parity=0`, `parity_matches=true`. The program computes the bit rather than copying a literal answer.

## Detecting corruption is not correcting or authenticating it

Parity can detect odd numbers of changed bits in its group but cannot locate a change. CRCs provide different structured detection properties for transmission error patterns. Error-correcting codes add redundancy capable of correcting specified errors. Cryptographic authentication checks integrity under an adversarial model with keys; parity has no secret and cannot establish origin or resist intentional modification.

The model masks the payload to its low eight bits when deriving parity. That is the stated byte-sized experiment, not validation that any arbitrary larger register value was an allowed packet field. A real protocol needs field widths, framing, byte order, a defined check region, error response, and implementation tests.

## Try mutations that distinguish properties

Change data to 84 in the computed-parity program: it has three one-bits, so parity becomes one and matches the new data, while the original target byte and parity checks fail. Keep data at 85 but write parity one: the telemetry should report a mismatch. Change two payload bits while holding the original parity and derive a case the parity test cannot detect.

The antenna geometry is contextual, and no physical antenna or radio path is configured. Passing this lab establishes the virtual byte/check-bit profile. Link modulation, coding, RF constraints, measurements, and platform command authority are additional prerequisites for any actual communications configuration.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 85); // data_byte
    mmio_write(0xF004, 0); // parity_bit
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,85
sw t1,0(t0)
li t1,0
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

## What this component does
An error-detection code adds redundant information so selected corruptions can be noticed. The byte 0x55 is binary 01010101 and contains four one-bits. Under even parity its added parity bit is zero. A single flipped bit changes the parity count and can be detected; two flips can escape this simple test.

## The virtual interface
Write data value 85, parity zero, and enabled state. The chosen payload makes the target parity independently derivable. This register exercise does not simulate a noisy radio channel or implement a full error-correcting code. The Verilog XOR idea provides the logic bridge: XOR of the payload bits gives the bit needed for even parity.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | data_byte | 85 | Example payload 0x55 |
| 0xF004 | parity_bit | 0 | Even parity for four one-bits |
| 0xF008 | enabled | 1 | 1 enables the demonstration |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the antenna component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Use payload 84, count its one-bits, and derive the required parity before changing the code. Explain why parity detects selected errors but does not tell the receiver which bit to repair. Compare this limit with stronger codes conceptually.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
