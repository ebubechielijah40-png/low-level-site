## Before configuring parallel compute

Review [worker budgets and parallel limits](/learn/device/6/), [buffers and networks](/learn/device/5/), and [ownership](/learn/device/4/). A node contains resources, a worker executes scheduled work, and a task decomposition defines what can actually run independently. Multiplying node and worker counts calculates a requested allocation, not achieved speedup.

## Derive the allocation and its assumptions

The profile targets sixteen nodes with eight workers on each, giving 128 requested workers. If each required 32 MiB under an assumed workload, their stated working-memory budget would be 4096 MiB across the allocation, before shared data, communication, and system overhead. Placement must respect resources on each node, not just the aggregate total.

Amdahl's ideal bound is `1/(s+(1-s)/N)`, where s is the serial fraction and N the independent workers. With ten percent serial work and 128 workers it is about 9.34, not 128. This model still excludes communication, synchronization, imbalance, and scheduling overhead, which can make observed performance lower.

## Data movement can dominate arithmetic

A task needs its input data on the node where it executes. Moving that data consumes bandwidth and incurs latency. Synchronization can make fast workers wait for slow ones. A useful implementation identifies independent tasks, partitions data, controls communication, and measures scaling under a fixed problem definition. Increasing worker count without that analysis can make a workload slower.

Actual configuration requires a scheduler/runtime, per-node capabilities, memory and device availability, network topology, deployment of executables and data, admission policy, and failure handling. Those are systems concepts. Learning an additional language does not supply them, though C, Rust, or another systems language can implement parts of the software.

## Try the virtual profile beside the documentation

Run the reference and inspect MMIO 16, 8, 1. The derived `requested_workers` telemetry should be 128. Change workers_per_node to four and predict 64, while the fixed target check fails. No measured execution time changes are claimed by that multiplication: the site's runtime executes your configuration source in one bounded teaching engine, not on 128 compute workers.

For independent reasoning, calculate ideal bounds at N=1, 8, and 128 for a ten-percent serial fraction, then identify the additional costs you would measure. Explain the difference between an allocation accepted by a scheduler, workers actually launched, correct results produced, and observed scaling. The profile task establishes only the encoded request.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 16); // nodes
    mmio_write(0xF004, 8); // workers_per_node
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,16
sw t1,0(t0)
li t1,8
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

## What this component does
A compute cluster distributes work across nodes. Parallel speedup depends on how much work can run independently and how much must remain serial or communicate. Sixteen nodes with eight workers each request 128 workers, but that arithmetic is not evidence of a 128-fold speedup.

## The virtual interface
Configure sixteen virtual nodes and eight workers per node. The model highlights compute resources and records the allocation. It does not run an MPI job, schedule tasks across actual machines, or time a benchmark. An actual cluster also needs a job scheduler, software environment, interconnect, data movement, and failure handling.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | nodes | 16 | Virtual compute-node count |
| 0xF004 | workers_per_node | 8 | Workers requested on each node |
| 0xF008 | enabled | 1 | 1 enables the allocation profile |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the cpu component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Double workers_per_node and explain which quantities increase in the profile and which performance claims remain untested. Use Amdahl-style reasoning: if part of the workload remains serial, an arbitrarily large worker count cannot remove that part.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
