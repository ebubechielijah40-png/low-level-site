## A number is an interpretation
A bit has two distinguishable states. We label them 0 and 1; the label is not the physical voltage. Four bits can describe sixteen patterns because each position doubles the number of combinations: 2 × 2 × 2 × 2 = 16. Eight bits make a byte, with 256 possible patterns. The pattern `00101010` represents 42 under an unsigned binary interpretation. It could also represent a character, part of a colour, or an instruction field. Context decides.

To convert binary to decimal, multiply each bit by its place value. From right to left the weights are 1, 2, 4, 8, 16, 32, 64, 128. For `00101010`, only 32, 8, and 2 contribute. Hexadecimal groups four bits into one digit: binary `1010` is hex `A`. Thus the same byte is `0x2A`. Hex does not change the bits; it makes them easier to read.

## What the machine keeps
Our virtual processor follows the RV32I integer instruction format. It has 32 registers containing 32 bits each, a program counter, and byte-addressed memory. A register is small working storage inside the processor model. Memory holds many more bytes. The program counter, abbreviated PC, identifies the next instruction. Normal instructions in this subset occupy four bytes, so sequential execution adds four to PC.

`x0` always reads zero. Writing to it discards the result. Registers do not know whether their bits mean signed integers, pointers, or masks. Instructions impose the interpretation. The runner begins with zeroed registers except `x2`, the stack pointer, which is initialised to a virtual stack address.

## Your first instruction
The word `00500293` means `addi x5, x0, 5`: add the immediate constant 5 to x0 and store the result in x5. Because x0 is zero, x5 becomes 5. The second word is an environment call; service zero stops this teaching machine. The runner accepts one 32-bit word per line. It does not accept arbitrary native binaries or execute anything on the web server's CPU.

Predict x5 before pressing Run. Then inspect Registers and Trace. PC should begin at zero and advance by four per instruction. Replace the leading `005` with `009` and predict the new value. Finally try changing the destination field by using the next lesson's decoding method. A useful experiment changes one cause and measures one consequence.

## Check your understanding
Why can the same byte mean either a number or a character? Why is 0x2A equal to 42 rather than 2 × 10 + 10? Explain why the emulator needs an instruction-set definition before it can interpret an instruction word. Your goal here is a precise model of state changes, rather than memorising hexadecimal strings.
