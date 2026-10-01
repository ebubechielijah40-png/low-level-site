# Freestanding C kernel milestone

This example is separate from the site's 512-byte BIOS boot emulator. It builds a 32-bit x86 ELF file with a Multiboot v1 header. It is **not** a complete operating system, and the browser workspace does not execute this ELF format.

The header has magic `0x1BADB002`, flags `0x00000003`, and a checksum making their 32-bit sum zero. The assembly entry disables interrupts, selects a 16 KiB stack, clears EBP, calls `kernel_main`, then waits in a halt loop. The C code writes VGA character/attribute pairs at physical address `0xB8000` under the assumptions of a compatible Multiboot loader. Interrupts stay disabled because no IDT or handlers have been installed.

## Build

From the project root on Linux with GNU binutils and GCC:

```bash
bash tools/build_kernel.sh
file build/kernel.elf
readelf -h build/kernel.elf
```

The expected file is an ELF32 executable for Intel 80386. The authoring environment successfully compiled and linked it with warnings treated as errors.

## Boot locally with additional tools

A compatible GRUB installation, `grub-mkrescue`, `xorriso`, and QEMU are needed for this route. These were unavailable in the authoring environment; **no actual native-kernel boot is claimed**.

```bash
mkdir -p build/iso/boot/grub
cp build/kernel.elf build/iso/boot/kernel.elf
cat > build/iso/boot/grub/grub.cfg <<'CFG'
set timeout=0
set default=0
menuentry "Bare Metal kernel" {
    multiboot /boot/kernel.elf
    boot
}
CFG
grub-mkrescue -o build/kernel.iso build/iso
qemu-system-i386 -cdrom build/kernel.iso
```

A successful boot should display `BARE METAL: freestanding C kernel entered.`. Capture that outcome before describing the kernel as boot-tested. The terminal's bounded C interpreter does not support this native pointer-to-VGA program; that is an intentional execution boundary.

Next concrete work is exception handling, a timer, an allocator, and a scheduler. Each needs its own invariant and failure test. The current header, entry, linker, and screen output are a starting milestone rather than those implemented subsystems.
