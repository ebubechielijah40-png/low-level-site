## What this component does
Parallel nodes must exchange data. An interconnect has latency, throughput, topology, and contention properties. A small message may be dominated by fixed latency, while a large transfer may be dominated by bandwidth. Multiple lanes can help only when the communication pattern and implementation use them.

## The virtual interface
Request four virtual lanes and a 256-byte transfer unit. The model records these fields without timing packets or simulating a complete routing fabric. The purpose is to keep units and configuration intent explicit while relating a software request to a visible network component.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | lanes | 4 | Illustrative communication paths |
| 0xF004 | message_bytes | 256 | Bytes in the model transfer unit |
| 0xF008 | enabled | 1 | 1 enables fabric policy |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the network component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Change message_bytes to 512 and explain the requested difference. Describe which extra evidence would be required to claim improved throughput, reduced latency, or balanced traffic. A saved integer profile supplies none of those measurements alone.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
