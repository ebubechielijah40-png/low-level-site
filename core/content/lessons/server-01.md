## What this component does
A server accepts work under finite CPU, memory, and I/O capacity. A queue absorbs brief bursts but does not create processing throughput. A bounded worker pool limits active concurrency, while a bounded queue makes overload an explicit condition rather than unlimited memory growth.

## The virtual interface
Request eight workers, a queue limit of sixty-four, and enabled intake. In a real service, worker count must be related to workload, CPU availability, blocking behaviour, latency, and memory per request. The visual server exposes the chosen profile but does not execute network requests or measure a throughput benchmark.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | workers | 8 | Maximum active workers in the teaching profile |
| 0xF004 | queue_limit | 64 | Maximum queued work items |
| 0xF008 | enabled | 1 | 1 enables intake |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the cpu component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Raise queue_limit without changing workers and explain why that can increase waiting time without increasing service rate. Disable intake and predict which target check fails while all writes still remain valid.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
