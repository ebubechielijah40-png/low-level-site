#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
as --32 examples/minikernel/entry.s -o build/entry.o
gcc -m32 -std=c11 -ffreestanding -fno-pie -fno-stack-protector -mno-sse -mno-mmx -msoft-float -Wall -Wextra -Werror -c examples/minikernel/kernel.c -o build/kernel.o
ld -m elf_i386 -T examples/minikernel/linker.ld -o build/kernel.elf build/entry.o build/kernel.o
printf 'Built build/kernel.elf (32-bit Multiboot ELF). Use a compatible loader to boot it.\n'
