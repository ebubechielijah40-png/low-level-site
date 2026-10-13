## Before configuring an interconnect profile

Know [message and buffer boundaries](/learn/device/5/), [parallel resources](/learn/device/6/), and [DMA ownership](/learn/device/4/). A physical lane, a logical path, a queue, and an application message are different objects. The profile's four lanes are illustrative communication paths, not a standardized hardware link-control register.

## Derive latency and transfer cost separately

A simple isolated-message model is `time = fixed_latency + bytes/bandwidth`. If a path supplies 1 byte per nanosecond and has 1000 ns fixed latency, a 256-byte transfer would take 1256 ns under those assumed parameters. Doubling the bytes to 512 yields 1512 ns, not twice the original time, because the fixed term stays unchanged.

Real links add headers, coding, acknowledgements, buffering, arbitration, congestion, and topology effects. Several lanes can improve aggregate bandwidth only if the protocol, routing, and traffic pattern use them. A synchronization barrier may remain dominated by the slowest participant or by latency regardless of nominal aggregate bandwidth.

## Message correctness has a protocol

Sender and receiver need agreed length, byte order, type or operation identifier, ordering, completion, and ownership rules. A buffer must stay valid until the communication mechanism is finished with it. DMA or direct transfer does not remove mapping and visibility obligations. A received byte count is not proof the application interpreted the content correctly.

An actual high-performance fabric configuration needs supported devices and firmware, link capabilities, routing/topology, queues and memory registration where relevant, flow control, error counters, and a benchmark appropriate to the message distribution. The site's profile records lanes=4, message_bytes=256, and enable=1. It does not move messages, route traffic, create a communication runtime, or estimate physical time.

## Try and inspect beside the guide

Run the reference and verify the three final MMIO values. Change message_bytes to 512 and predict only the changed request field and fixed-target failure. Explain the 1512 ns estimate only after explicitly supplying the hypothetical bandwidth and latency above. It must not be presented as returned site telemetry or observed device behavior.

For independent work, compare small messages with a bulk transfer under the same hypothetical path, then describe why a real benchmark needs both latency and sustained throughput measurements. Identify what happens to a buffer's ownership while the message is pending. A complete interconnect configuration consists of those protocol and capability facts, not simply more low-level syntax.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 4); // lanes
    mmio_write(0xF004, 256); // message_bytes
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,4
sw t1,0(t0)
li t1,256
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

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
