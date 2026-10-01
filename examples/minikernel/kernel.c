/* A freestanding stage-one demonstration. No hosted library or process runtime. */
void kernel_main(void) {
    volatile unsigned short *screen = (volatile unsigned short *)0xB8000;
    const char *message = "BARE METAL: freestanding C kernel entered.";
    for (unsigned int i = 0; i < 80 * 25; i++) screen[i] = 0x0220;
    for (unsigned int i = 0; message[i] != '\0'; i++) {
        screen[i] = (unsigned short)(0x0A00 | (unsigned char)message[i]);
    }
}
