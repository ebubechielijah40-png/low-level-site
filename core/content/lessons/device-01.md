## Before you configure a device

You should be able to distinguish an address from its contents, derive a four-byte word address, and set or clear an individual bit. Review [loads and stores](/learn/machine/5/), [integer flags](/learn/c/2/), and [C device access](/learn/c/8/) when any of those is uncertain. This is a knowledge checklist, not an access restriction.

Knowing C lets you express a write. Knowing the device contract tells you whether that write has a useful meaning. The missing information is supplied by the memory map, register description, reset procedure, and operating environment of a specific controller. No programming language contains that information automatically.

## Address spaces are different contracts

A CPU virtual address is translated under an operating system's mapping policy. A physical address selects a location on a platform's address map. A device may use a different DMA address. The same integer can be valid in one space and meaningless in another. A driver must discover and map its assigned resource; it cannot take a desktop application's ordinary pointer and assume the device can use it.

Our site simplifies this to byte-addressed virtual RAM and a separate 32-bit MMIO window, `0xF000` through `0xF0FC`. Each run starts fresh. It has no page tables, privilege modes, PCI discovery, or native host-address access. You can learn the distinction here without claiming these larger mechanisms have been emulated.

For this experiment, the contract is deliberately small:

| Address | Meaning | Width | Reset | Allowed access |
|---|---|---|---|---|
| 0xF000 | capacity in MiB | 32 bits | 0 | read/write |
| 0xF004 | enable, bit 0 | 32 bits | 0 | read/write |
| 0xF008 | parity request, bit 0 | 32 bits | 0 | read/write |

The next register starts four bytes later because the access width is four bytes. Address `0xF001` is inside the numeric window but is not a permitted word address. Range and alignment are separate conditions.

## Try this in the terminal beside the documentation

Load the example, predict its output, then press Run. Open **State** and inspect **mmio**; addresses appear in hexadecimal there.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 512);
    unsigned int control = mmio_read(0xF004);
    control = control | 1U;
    mmio_write(0xF004, control);
    printf("capacity=%u control=%u\n", mmio_read(0xF000), mmio_read(0xF004));
    return 0;
}
```

Expect `capacity=512 control=1`. The first call records 512. The read returns the reset value zero. OR with one sets bit zero while preserving other bits. The final write publishes one to the control register. Nothing in that sequence allocates 512 MiB of your laptop's RAM.

## A register is a protocol endpoint

Read/write storage is only one register type. A read-only status register is maintained by the device. A write-only command register may start work without retaining a readable command value. A write-one-to-clear status register clears whichever bits the written value selects. A read-to-clear register acknowledges an event when read. Reserved bits may require preservation or zero, depending on the manual.

Read-modify-write is appropriate only when those semantics permit it. Suppose a write-one-to-clear status value is `3` and you want to acknowledge only bit zero. Write `1`. Reading `3`, OR-ing with `1`, and writing `3` would also clear bit one. The arithmetic would be correct and the protocol would be wrong. Our plain MMIO storage does not implement these side effects; the event lesson models them explicitly in software.

On a real system, width, byte order, mapping attributes, permissions, and ordering come from the platform API and controller manual. `volatile` does not discover a device or supply a complete synchronization protocol. Native Linux drivers use mapped I/O accessors rather than this site's teaching functions.

## Practice: produce a contract before code

Change the capacity to 256 and predict the read-back. Change only `0xF004` to `0xF005`; expect an alignment error. Explain why an aligned write can still violate a real device's permission or legal-value rules. Write a register description containing units, valid range, reset, access permissions, reserved bits, side effects, and the evidence required to consider the operation complete. Then proceed to the lifecycle lesson.
