.set MAGIC, 0x1BADB002
.set FLAGS, 0x00000003
.set CHECKSUM, -(MAGIC + FLAGS)
.section .multiboot
.align 4
.long MAGIC
.long FLAGS
.long CHECKSUM
.section .bss
.align 16
stack_bottom:
.skip 16384
stack_top:
.section .text
.global _start
.type _start, @function
_start:
    cli
    mov $stack_top, %esp
    xor %ebp, %ebp
    call kernel_main
1:
    hlt
    jmp 1b
.size _start, . - _start
.section .note.GNU-stack,"",@progbits
