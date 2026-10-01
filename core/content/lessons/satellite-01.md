## What this component does
A satellite computer collects measurements, timestamps them, packages telemetry, and coordinates communication under power and bandwidth constraints. A sample without units, time, and provenance is difficult to interpret even when its bytes arrive intact.

## The virtual interface
Configure ten samples per second and thirty-two payload bytes per sample. The raw payload rate is 320 bytes per second before headers, coding, framing, or retransmission. This is a calculated request profile, not a radio link budget. The model exposes the onboard-computer component and does not operate any satellite or radio hardware.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | sample_hz | 10 | Requested samples per second |
| 0xF004 | payload_bytes | 32 | Bytes per virtual sample |
| 0xF008 | enabled | 1 | 1 enables telemetry policy |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the cpu component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Double sample_hz and calculate the new raw payload rate. Identify the additional factors needed to estimate power use, actual airtime, or reliable downlink capacity. Keep arithmetic consequences separate from unsupported physical conclusions.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
