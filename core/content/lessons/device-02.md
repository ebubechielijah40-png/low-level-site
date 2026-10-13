## Before you start a controller

Know the [register contract](/learn/device/1/) and [bounded loops](/learn/c/3/). You must be able to explain the difference between a requested configuration, a readable stored value, and a completed device operation. The last two can differ even when the source compiles and the bus write succeeds.

## Configuration has a lifecycle

A useful controller lifecycle is reset, validate capabilities, quiesce existing work, write parameters, request activation, wait for acknowledgement, then verify useful work. A reset establishes a defined state. Quiescing stops new requests and waits for outstanding ones to settle. Validation checks both individual ranges and relationships: a queue can fit its numeric field while exceeding the available buffer memory.

The order is a property of the device protocol. Some controllers latch parameters only when an enable transition occurs. Others require a separate commit command. Some registers can be changed live; others require reset. The site's hardware labs record final values and compare targets. They do not enforce all these intermediate transitions. This lesson provides an explicit software mock so you can inspect a lifecycle without pretending that plain MMIO storage contains an asynchronous controller.

## Try this in the terminal beside the documentation

The `poll_device` function is an authored mock: your program changes the status after three polls. It is not a hardware clock or a real device interrupt. Predict how many calls occur before running.

```c run:reference
#include <stdio.h>
void poll_device(int polls) {
    if (polls == 3) {
        mmio_write(0xF00C, 1);
    }
}
int main(void) {
    int capacity = 512;
    int polls = 0;
    unsigned int ready = 0U;
    if (capacity < 256 || capacity > 1024) {
        puts("invalid capacity");
        return 0;
    }
    mmio_write(0xF004, 0);
    mmio_write(0xF000, capacity);
    mmio_write(0xF008, 1);
    mmio_write(0xF004, 1);
    while (polls < 4 && ready == 0U) {
        polls = polls + 1;
        poll_device(polls);
        ready = mmio_read(0xF00C) & 1U;
    }
    printf("ready=%u polls=%d\n", ready, polls);
    return 0;
}
```

Expect `ready=1 polls=3`. Before the loop, the request registers contain capacity 512, parity 1, and enable 1. Status is still zero. Polls one and two observe zero; poll three makes the mock set bit zero in `0xF00C`, and the next read observes one. The loop exits because the acknowledgement has arrived, not because the capacity write printed a success message.

## Timeouts belong to the protocol

A poll-count bound is useful for a deterministic experiment. It is not a duration: four iterations can take very different wall-clock times on different machines. Real driver timeouts need a documented time source, a deadline, appropriate waiting, and a recovery policy. A busy loop can consume CPU while accomplishing nothing; an interrupt or blocking wait may be more suitable.

Change the mock threshold from three to five. Expect `ready=0 polls=4`. The loop ends with a timeout indication. The request registers remain written, so your recovery decision must not assume the device is safely stopped merely because your caller stopped waiting. A real implementation might disable intake, drain or cancel requests, collect status, reset, and report the fault. Which actions are legal depends on the manual.

Reading back a command register proves neither completion nor stability. Even a real bus acknowledgement can precede the completion of the requested internal action. Some buses post writes, so a documented accessor or safe read-back is needed when completion ordering matters. That is a platform-specific requirement; the teaching calls execute synchronously as virtual storage operations.

## Practice: distinguish the four outcomes

Run with capacities 255, 256, 512, and 1025. The outside values print `invalid capacity` before any device writes. Then test successful acknowledgement and timeout by changing the mock threshold. Explain the difference between rejected parameters, successful register writes, acknowledged activation, and useful work passing a separate test. Design a recovery path and state what information it needs before choosing reset or retry.
