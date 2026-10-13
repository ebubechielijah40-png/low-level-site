## Before configuring telemetry

Review [sampling/timing units](/learn/device/3/), [byte protocols](/learn/device/5/), and [resource limits](/learn/device/6/). Sampling rate measures observations per second; payload size measures bytes per observation. Their product is a payload byte rate. Actual radio capacity, airtime, and power need additional link and platform information.

## Derive the target and include overhead explicitly

The target is ten samples per second, thirty-two payload bytes per sample, and enabled telemetry. Raw payload rate is 320 bytes per second or 2560 bits per second. With an assumed eight-byte header per sample, the pre-coding rate would be 400 bytes or 3200 bits per second. Error-control coding, framing, encryption/authentication overhead, retries, and availability windows can increase the required channel budget.

A sample also needs a meaning: sensor/channel identity, units, timestamp, scale, and validity information. Bytes that arrive intact can still be useless if the receiving software assumes a different unit or cannot determine when the observation occurred. Integrity of representation and correctness of interpretation are distinct requirements.

## A telemetry queue has a time budget

If the link is unavailable for sixty seconds, the raw target generates 19200 payload bytes under a constant sampling policy. With the assumed header it generates 24000 bytes before other storage overhead. Buffer space must account for retained records, and a policy must decide what happens at exhaustion: discard, summarize, lower rate, or stop intake. This calculation does not predict a satellite pass or establish a radio link budget.

Actual onboard configuration needs supported sensors, command/telemetry definitions, timing and storage limits, communications protocol, energy budget, fault response, and the platform's validated control procedures. C or assembly can express those operations, but cannot infer the hardware contract or mission policy.

## Try the virtual profile beside the documentation

Run the reference and inspect MMIO 10, 32, 1 and `payload_bytes_per_second=320` in telemetry. Change sample_hz to twenty and expect 640; the task's fixed sampling target fails even though the arithmetic is consistent with the new request. Change payload_bytes to sixteen and expect 160 at the original rate.

The site models only this profile arithmetic and a conceptual onboard-computer view. It has no sensors, orbital propagation, live radio, timestamps, packet transmission, channel noise, or power model. Use the second satellite lab to study one integrity mechanism, then explain why parity alone cannot establish accurate measurements or a secure communications channel.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 10); // sample_hz
    mmio_write(0xF004, 32); // payload_bytes
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,10
sw t1,0(t0)
li t1,32
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

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
