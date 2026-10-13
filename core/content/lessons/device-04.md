## Before you handle events or DMA

Review [object identity and pointers](/learn/c/5/), [register access](/learn/device/1/), and [acknowledgement](/learn/device/2/). An event is a change you must notice and handle. DMA, direct memory access, lets a device transfer data without the CPU performing every byte copy. Neither mechanism is supplied by knowing the C assignment operator.

## Interrupts report events; handlers manage ownership

Polling repeatedly reads state. An interrupt asks the CPU to handle a reported condition through the platform's interrupt mechanism. The handler must identify the source, acknowledge it according to its register semantics, and arrange the remaining work. Level-triggered and edge-triggered sources have different behavior. Acknowledging the wrong condition can lose an event; failing to acknowledge can cause repeated interrupts.

Keep a distinction between the device's event bit, the interrupt controller, and the application work queue. Our RV32I and C engines have no interrupt delivery or privileged interrupt controller. The following C experiment models acknowledgement as an ordinary function so the meaning of a write-one-to-clear mask is visible.

## Try this in the terminal beside the documentation

```c run:reference
#include <stdio.h>
unsigned int acknowledge(unsigned int pending, unsigned int mask) {
    return pending & ~mask;
}
int main(void) {
    unsigned int pending = 3U;
    unsigned int after = acknowledge(pending, 1U);
    int cpu_buffer[2] = {7, 9};
    int device_view[2] = {0, 0};
    device_view[0] = cpu_buffer[0];
    device_view[1] = cpu_buffer[1];
    int descriptor_valid = 1;
    printf("pending=%u after_ack=%u dma_sum=%d valid=%d\n",
           pending, after, device_view[0] + device_view[1], descriptor_valid);
    return 0;
}
```

Expect `pending=3 after_ack=2 dma_sum=16 valid=1`. Binary `11` contained two pending conditions. Mask `01` selects only the first, so the result is `10`. The array copies represent publishing data to a second view; they are a software analogy, not a DMA engine or cache-maintenance operation.

## A DMA descriptor is a handoff protocol

A descriptor commonly describes a buffer location, length, control flags, and ownership or completion state. Before publishing it, the driver checks buffer lifetime, size, device-address mapping, alignment, and access direction. The device must not use a descriptor before its fields are initialized. The CPU must not reuse a buffer while the device still owns it.

Caches and write buffers complicate visibility. Cache coherence and ordering are distinct: coherent memory does not automatically make every publication sequence correct. The platform's DMA mapping and synchronization APIs provide the contract for the target. A CPU pointer, a physical address, and a DMA address can differ, particularly with an IOMMU. A driver must use the returned device address rather than invent one by casting a pointer.

Similarly, `volatile` does not make a multi-field descriptor update atomic and does not replace a release/ownership protocol or hardware barriers. Interrupt completion can notify the CPU that work ended, but the driver still needs the documented synchronization before consuming device-written data. The site does not simulate caches, IOMMUs, races, interrupts, or real DMA; it teaches their obligations explicitly.

## Practice: expose a lost event and an early handoff

Change the acknowledgement mask to 3 and expect `after_ack=0`: you cleared both events. Change it to 0 and expect 3. Remove the second array copy and expect `dma_sum=7` while `valid` still prints 1. Explain why setting a validity flag cannot repair missing data. Describe a descriptor lifecycle with CPU-owned, device-owned, completed, and recycled states. State the measurements and platform APIs required before using that protocol on actual hardware.
