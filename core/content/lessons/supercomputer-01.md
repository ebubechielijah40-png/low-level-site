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
