## What this component does
A data centre combines compute, storage, networks, power, and cooling. Replication places multiple copies of data so one failed component need not destroy availability. Its usefulness depends on failure independence and consistency rules; three copies on one physical disk do not provide three independent failure domains.

## The virtual interface
The target has six nodes and three replicas. A real placement algorithm would validate that enough distinct nodes and failure domains exist, select destinations, track versions, and repair lost replicas. This model records a chosen policy and exposes it on the rack view. It does not implement a distributed storage protocol or claim durability from the configuration alone.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | nodes | 6 | Available virtual nodes |
| 0xF004 | replicas | 3 | Requested copies per object |
| 0xF008 | enabled | 1 | 1 enables placement policy |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the racks component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Set replicas above nodes and explain the impossible distinct-node placement. The lab target rejects the mismatch; independently state the general replicas <= nodes invariant before choosing a valid alternative profile.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
