bits 16
org 0x7c00
start:
    xor ax, ax
    mov ds, ax
    mov si, message
    mov ah, 0x0e
print:
    lodsb
    cmp al, 0
    je done
    int 0x10
    jmp print
done:
    hlt
message:
    db "BARE METAL OS", 13, 10, "Booted from your own 512-byte image.", 13, 10, 0
