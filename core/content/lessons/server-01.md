## Before configuring server workers

Know [capacity and queues](/learn/device/6/), [activation](/learn/device/2/), and [object lifetime](/learn/c/5/). A software worker is not necessarily a CPU core. It can be a thread, process, or other unit of work. Waiting for I/O and performing CPU work have different resource demands, so a sensible worker count needs a workload and measured constraints.

## Calculate more than one budget

The profile targets eight workers, at most sixty-four queued items, and enabled intake. Suppose each worker requires 32 MiB of working memory and each queued item 1024 bytes. The stated budgets are 256 MiB and 65536 bytes before runtime, application, queue metadata, and allocator overhead. Doubling workers doubles this assumed worker memory without automatically doubling throughput.

If each worker serves ten jobs per second under ideal independence, the illustrative capacity is eighty jobs per second. Arrival at ninety jobs per second makes the backlog grow by about ten per second under those fixed assumptions. A queue bound caps admitted waiting work; it does not fix the service-rate deficit. A policy must decide whether to reject, shed, retry, or route excess work.

## Configuration and observation are distinct

Real server tuning needs the service implementation, scheduling model, CPU and memory limits, connection behavior, downstream dependencies, request workload, latency distribution, failure policy, and monitoring. A process can be alive while no useful request succeeds. Mean response time can look acceptable while tail latency or queue wait is poor.

The site's three registers are a virtual profile for teaching. They are not standard server hardware registers or a deployment manager. The lab association with a systems language suggests useful concepts; the selectable implementation languages here are C and RV32I assembly. Rust is not required to write this virtual profile, and its borrow checker does not calculate an appropriate worker limit.

## Try the profile in the terminal beside the guide

Run the reference and inspect workers=8, queue_limit=64, enabled=1 in **State / mmio**. Change queue_limit to zero and reason about the desired meaning: would zero mean no waiting or unbounded waiting in the actual service? A controller contract must choose; this profile merely records zero and fails the stated sixty-four target. Change workers to sixteen and separately predict memory demand, while declining to infer a throughput measurement from that field.

To configure an actual server, validate a candidate under a known request workload and observe utilization, memory, queue depth, error rate, and latency. In this lab, all you have proved on target completion is that the three requested values were recorded correctly.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 8); // workers
    mmio_write(0xF004, 64); // queue_limit
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,8
sw t1,0(t0)
li t1,64
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

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
