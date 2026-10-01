## What this component does
A network interface moves frames while protocol stacks interpret them and applications handle messages. An MTU is a size boundary for a particular link or interface, not a guarantee that a larger end-to-end message fits in one packet. Connection limits belong to resource policy above the physical wire.

## The virtual interface
Set the virtual interface MTU to 1500, connection capacity to thirty-two, and enabled state. This combines selected policy settings into a documented teaching interface. It does not configure your operating system network adapter or exchange packets. Real changes would require the platform network APIs, privileges, route and link context, and careful feedback.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | mtu_bytes | 1500 | Illustrative maximum transmission unit |
| 0xF004 | connections | 32 | Virtual connection capacity |
| 0xF008 | enabled | 1 | 1 enables the interface profile |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the network component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Use an MTU of one and explain why a writable integer is not enough to establish a usable real policy. Describe how a connection limit protects bounded resources but can also reject valid demand under load.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
