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
