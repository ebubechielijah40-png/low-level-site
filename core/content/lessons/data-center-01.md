## Before configuring replication

Review [failure domains and resource limits](/learn/device/6/) and [acknowledgement semantics](/learn/device/2/). A node count, replica count, existing durable copies, and required acknowledgement quorum answer different questions. A configuration number must not be presented as evidence that data has actually been copied or can survive a particular failure.

## Derive what six nodes and three replicas permit

The target requests six nodes and three copies per object. Numerically, three distinct-node placements are possible because `0<3<=6`. That condition says nothing about which nodes are chosen, whether copies agree, or whether they share one power supply or rack. Independent failure domains matter when an event can remove multiple nodes together.

If three independent durable copies already exist, losing two can still leave one. A majority quorum of a three-member replica group requires two members, so availability of that quorum after losing two is a different outcome. A six-node pool is not automatically one six-voter consensus group. Define which group, operations, and failure model you mean before calculating tolerance.

## Replication requires a protocol and recovery

A write can be received, cached, persisted, replicated, or committed under a stated protocol. Acknowledgement at one layer does not prove the next. Recovery must handle partial writes, stale copies, rejoining nodes, ownership of repair work, and data verification. Networking, durable storage, ordering, and failure detection are additional necessary systems knowledge beyond C syntax.

This site records requested node and replica counts and computes whether distinct-node placement is numerically possible. It does not create a distributed system, transfer objects, select racks, run consensus, fail nodes, or model durable storage. The visualization illustrates the components relevant to the request rather than a live data centre.

## Try and challenge the profile beside the guide

Run the reference and inspect MMIO 6, 3, 1 and telemetry `distinct_node_placement_possible=true`. Change replicas to seven while nodes remain six. Expect that telemetry to become false as well as the three-replica target failing. A successful register write with impossible placement is a useful counterexample to “valid code means valid configuration.”

Set replicas to one and explain what redundancy remains. Put three imagined copies in one rack and describe the correlated-failure risk without changing the numeric count. Finally define an actual placement and acknowledgement contract. Completing the lab establishes the virtual profile; real durability and availability require the additional observations and implementation just described.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 6); // nodes
    mmio_write(0xF004, 3); // replicas
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,6
sw t1,0(t0)
li t1,3
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

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
