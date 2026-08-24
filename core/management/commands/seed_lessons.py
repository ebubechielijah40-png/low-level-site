from django.core.management.base import BaseCommand
from core.models import Language, Lesson


class Command(BaseCommand):
    help = 'Seed all lesson content'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding lessons...')

        # ─── C ───────────────────────────────────────────────
        c, _ = Language.objects.get_or_create(
            name='C',
            defaults={'description': 'A low-level compiled language that gives direct control over memory and hardware. The foundation of operating systems, compilers, and embedded systems.'}
        )

        c_lessons = [
            {
                'order': 1,
                'title': 'What is C',
                'content': '''C is a compiled, statically typed language created by Dennis Ritchie at Bell Labs in 1972. It was designed to write the UNIX operating system.

C sits directly above Assembly in abstraction. Unlike Python or JavaScript, C does not hide memory from you. You decide where data lives, how long it lives, and when it is released.

When you write C, your source code is translated by a compiler (GCC) into machine instructions the CPU can execute directly. There is no virtual machine, no interpreter running between your code and the hardware.

This is why operating systems, device drivers, databases, and embedded firmware are written in C. It is as close to the machine as you can get while still writing human-readable code.

Every concept you learn in C maps directly to what the hardware is doing. A variable is a named memory location. A function call moves the instruction pointer. A loop is a conditional jump back to an earlier address.

Understanding C means understanding the machine.''',
                'challenge': 'Write a C program with a main function that prints your name to the screen using printf. Make sure it returns 0 at the end.',
                'starter_code': '''#include <stdio.h>

int main() {
    printf("Hello from C!\\n");
    return 0;
}''',
                'example_output': 'Hello from C!'
            },
            {
                'order': 2,
                'title': 'Your First Program',
                'content': '''Every C program starts from a function called main. The operating system calls main when your program runs.

#include <stdio.h> tells the preprocessor to include the Standard Input Output header file before compilation. This file contains the declaration for printf. Without it, the compiler does not know what printf is.

int main() declares a function named main that returns an integer. The int before main is the return type.

printf is a function that formats and prints text to standard output (your terminal). The \\n inside the string is an escape sequence meaning newline — it moves the cursor to the next line.

return 0 sends the value 0 back to the operating system. By convention, 0 means the program finished successfully. Any other value signals an error.

The curly braces { } define the body of the function — everything between them belongs to main.

Every statement in C ends with a semicolon. The semicolon tells the compiler where one instruction ends and the next begins.''',
                'challenge': 'Modify the program to print two lines: your name on the first line and your city on the second line. Use two separate printf calls.',
                'starter_code': '''#include <stdio.h>

int main() {
    printf("Name: Elijah\\n");
    printf("City: Lagos\\n");
    return 0;
}''',
                'example_output': '''Name: Elijah
City: Lagos'''
            },
            {
                'order': 3,
                'title': 'Variables and Data Types',
                'content': '''A variable is a named location in memory that stores a value. When you declare a variable in C, you are telling the compiler to reserve a specific number of bytes in memory.

int stores whole numbers. On most systems it is 4 bytes, meaning it can hold values from -2,147,483,648 to 2,147,483,647.

char stores a single character. It is 1 byte. Characters are stored as their ASCII numeric value — the letter A is stored as 65.

float stores decimal numbers using 4 bytes. It has limited precision.

double stores decimal numbers using 8 bytes. More precise than float.

When you write int age = 25; you are declaring a variable named age of type int and immediately assigning it the value 25.

printf uses format specifiers to print different types:
%d prints an integer
%c prints a character
%f prints a float
%s prints a string

The & operator gives you the memory address of a variable. printf("%p", &age) would print the actual memory address where age is stored.''',
                'challenge': 'Declare an int, a char, and a float. Assign values to each. Print each variable using the correct format specifier. Then print the memory address of each variable using %p.',
                'starter_code': '''#include <stdio.h>

int main() {
    int age = 20;
    char grade = 'A';
    float score = 95.5;

    printf("Age: %d\\n", age);
    printf("Grade: %c\\n", grade);
    printf("Score: %.1f\\n", score);
    printf("Address of age: %p\\n", (void*)&age);
    return 0;
}''',
                'example_output': '''Age: 20
Grade: A
Score: 95.5
Address of age: 0x7ffee3a1b4ac'''
            },
            {
                'order': 4,
                'title': 'Operators',
                'content': '''Operators tell the CPU what operation to perform on values.

Arithmetic operators: + - * / %
The % operator is modulo — it returns the remainder after division. 10 % 3 = 1.

Comparison operators: == != < > <= >=
These return 1 (true) or 0 (false). In C there is no boolean type — true is any non-zero value and false is zero.

Logical operators: && || !
&& is AND — both conditions must be true
|| is OR — at least one condition must be true
! is NOT — inverts the value

Assignment operators: = += -= *= /=
x += 5 is shorthand for x = x + 5.

Increment and decrement: ++ --
x++ adds 1 to x after using it. ++x adds 1 before using it.

Integer division is important in C. 7 / 2 = 3 not 3.5, because both operands are integers. To get decimal division, at least one operand must be a float: 7.0 / 2 = 3.5.''',
                'challenge': 'Write a program that takes two hardcoded integers (a=17, b=5) and prints the result of every arithmetic operation: addition, subtraction, multiplication, division, and modulo. Also print whether a is greater than b.',
                'starter_code': '''#include <stdio.h>

int main() {
    int a = 17;
    int b = 5;

    printf("a + b = %d\\n", a + b);
    printf("a - b = %d\\n", a - b);
    printf("a * b = %d\\n", a * b);
    printf("a / b = %d\\n", a / b);
    printf("a %% b = %d\\n", a % b);
    printf("a > b: %d\\n", a > b);
    return 0;
}''',
                'example_output': '''a + b = 22
a - b = 12
a * b = 85
a / b = 3
a % b = 2
a > b: 1'''
            },
            {
                'order': 5,
                'title': 'Control Flow',
                'content': '''Control flow determines which instructions the CPU executes and in what order.

By default the CPU executes instructions sequentially — one after another. Control flow statements change this by making the CPU jump to a different location in memory.

if checks a condition. If the condition is non-zero (true), it executes the block. Otherwise it skips it.

if / else gives the CPU two paths — execute one block or the other, never both.

else if chains multiple conditions. The CPU checks each condition in order and executes the first one that is true.

At the machine level, an if statement compiles to a CMP instruction followed by a conditional jump. The CPU compares two values, sets flags in a status register, then jumps or does not jump based on those flags.

This is why understanding C control flow directly teaches you how the CPU makes decisions.''',
                'challenge': 'Write a program that checks a hardcoded integer. Print "POSITIVE" if it is greater than 0, "NEGATIVE" if less than 0, and "ZERO" if it equals 0.',
                'starter_code': '''#include <stdio.h>

int main() {
    int number = -7;

    if (number > 0) {
        printf("POSITIVE\\n");
    } else if (number < 0) {
        printf("NEGATIVE\\n");
    } else {
        printf("ZERO\\n");
    }
    return 0;
}''',
                'example_output': 'NEGATIVE'
            },
            {
                'order': 6,
                'title': 'Loops',
                'content': '''A loop is a repeated jump back to an earlier instruction. At the machine level, loops compile to a conditional branch that keeps jumping back to the start until a condition becomes false.

The for loop has three parts: initialization, condition, and increment.
for (int i = 0; i < 10; i++) means: start with i=0, keep looping while i is less than 10, add 1 to i after each iteration.

The while loop checks the condition before each iteration. If the condition is false from the start, the body never executes.

The do-while loop executes the body at least once, then checks the condition.

break exits the loop immediately regardless of the condition.
continue skips the rest of the current iteration and goes back to the condition check.

Infinite loops are loops whose condition never becomes false. while(1) {} runs forever until break or the program is killed.

Every loop in C compiles to the same basic pattern in Assembly: load counter, compare, conditional jump back.''',
                'challenge': 'Write a for loop that prints the numbers 1 to 10, one per line. Then write a while loop that counts down from 10 to 1.',
                'starter_code': '''#include <stdio.h>

int main() {
    printf("Counting up:\\n");
    for (int i = 1; i <= 10; i++) {
        printf("%d\\n", i);
    }

    printf("Counting down:\\n");
    int j = 10;
    while (j >= 1) {
        printf("%d\\n", j);
        j--;
    }
    return 0;
}''',
                'example_output': '''Counting up:
1
2
3
4
5
6
7
8
9
10
Counting down:
10
9
8
7
6
5
4
3
2
1'''
            },
            {
                'order': 7,
                'title': 'Functions',
                'content': '''A function is a named block of code that can be called from anywhere in your program.

When you call a function, the CPU pushes the return address onto the stack, then jumps to the function's first instruction. When the function finishes, it pops the return address and jumps back to where it was called from.

This is called the call stack. Every function call adds a frame to the stack. Every return removes a frame.

Functions have a return type, a name, and parameters.
int add(int a, int b) declares a function that takes two integers and returns one integer.

void means the function returns nothing.

Parameters are copies of the values you pass. Changing a parameter inside the function does not change the original variable — this is called pass by value.

Declaring a function before main (a function prototype) tells the compiler the function exists before it has seen the full definition. This allows functions to call each other in any order.

Functions are the building blocks of every program. The operating system itself is thousands of functions calling each other.''',
                'challenge': 'Write a function called multiply that takes two integers and returns their product. Write another function called is_even that takes an integer and returns 1 if it is even, 0 if odd. Call both from main and print the results.',
                'starter_code': '''#include <stdio.h>

int multiply(int a, int b) {
    return a * b;
}

int is_even(int n) {
    return n % 2 == 0;
}

int main() {
    printf("6 * 7 = %d\\n", multiply(6, 7));
    printf("9 is even: %d\\n", is_even(9));
    printf("8 is even: %d\\n", is_even(8));
    return 0;
}''',
                'example_output': '''6 * 7 = 42
9 is even: 0
8 is even: 1'''
            },
            {
                'order': 8,
                'title': 'Pointers',
                'content': '''A pointer is a variable that stores a memory address instead of a value.

Every variable in your program lives at a specific address in RAM. The & operator gives you that address. The * operator follows an address to get the value stored there.

int x = 10;
int *ptr = &x;

ptr now holds the address of x. *ptr gives you the value at that address — which is 10.

Changing *ptr changes x directly because they point to the same memory location. This is called dereferencing.

Pointers are why C is so powerful and so dangerous. You can directly manipulate any memory location. If you point to the wrong address and write to it, you corrupt memory. This is the source of most security vulnerabilities in low-level software.

Pointer arithmetic lets you move through memory by adding to the pointer. ptr + 1 moves to the next int in memory (4 bytes forward).

Arrays in C are pointers. The array name is the address of the first element.

Understanding pointers means understanding how the machine actually stores and accesses data.''',
                'challenge': 'Declare an integer x=42. Create a pointer to it. Print the value of x, the address of x, and the value through the pointer. Then change x to 100 through the pointer and print x again to prove it changed.',
                'starter_code': '''#include <stdio.h>

int main() {
    int x = 42;
    int *ptr = &x;

    printf("Value of x: %d\\n", x);
    printf("Address of x: %p\\n", (void*)ptr);
    printf("Value through pointer: %d\\n", *ptr);

    *ptr = 100;
    printf("x after pointer change: %d\\n", x);
    return 0;
}''',
                'example_output': '''Value of x: 42
Address of x: 0x7ffee3a1b4ac
Value through pointer: 42
x after pointer change: 100'''
            },
            {
                'order': 9,
                'title': 'Arrays',
                'content': '''An array is a contiguous block of memory holding multiple values of the same type.

int numbers[5] reserves 5 consecutive integers in memory — 20 bytes total (5 x 4 bytes).

Array indexing starts at 0. numbers[0] is the first element, numbers[4] is the last. Accessing numbers[5] reads beyond the array — this is undefined behaviour and can crash your program or corrupt data.

The array name is a pointer to the first element. numbers and &numbers[0] are the same address.

You can iterate through an array using a loop with the index as the loop variable.

Arrays and pointers are deeply connected. numbers[i] is exactly equivalent to *(numbers + i). The compiler treats them identically.

String in C are arrays of char ending with a null terminator \\0. The \\0 tells functions like printf and strlen where the string ends. Without it, the function keeps reading memory past the string until it finds a zero byte.

Understanding arrays means understanding how data is laid out in memory.''',
                'challenge': 'Declare an array of 5 integers. Assign values to each element. Print every value and its memory address using a for loop. Then compute and print the sum of all elements.',
                'starter_code': '''#include <stdio.h>

int main() {
    int nums[5] = {10, 20, 30, 40, 50};
    int sum = 0;

    for (int i = 0; i < 5; i++) {
        printf("nums[%d] = %d  address: %p\\n", i, nums[i], (void*)&nums[i]);
        sum += nums[i];
    }
    printf("Sum: %d\\n", sum);
    return 0;
}''',
                'example_output': '''nums[0] = 10  address: 0x7ffee3a1b490
nums[1] = 20  address: 0x7ffee3a1b494
nums[2] = 30  address: 0x7ffee3a1b498
nums[3] = 40  address: 0x7ffee3a1b49c
nums[4] = 50  address: 0x7ffee3a1b4a0
Sum: 150'''
            },
            {
                'order': 10,
                'title': 'Structs',
                'content': '''A struct is a custom data type that groups related variables under one name.

struct CPU { char name[50]; int cores; float clock_speed; };

This defines a new type called CPU. Each CPU has a name, a core count, and a clock speed. They are stored together in memory, one after another.

You access struct members using the dot operator: my_cpu.cores.

If you have a pointer to a struct, you use the arrow operator: ptr->cores.

Structs let you model real-world objects in code. Instead of tracking 10 separate variables for 10 CPUs, you create an array of CPU structs.

The compiler may add padding bytes between struct members to align data on memory boundaries. This is why the size of a struct is sometimes larger than the sum of its members.

Structs are the basis for everything in systems programming. File headers, network packets, hardware registers — all of these are structs mapped to specific memory locations.

In C++, structs evolved into classes. In C, structs are the only way to group data.''',
                'challenge': 'Create a struct called Process with fields: id (int), name (char array of 30), and priority (int). Create three Process instances and print all their fields. Then find and print the process with the highest priority.',
                'starter_code': '''#include <stdio.h>
#include <string.h>

struct Process {
    int id;
    char name[30];
    int priority;
};

int main() {
    struct Process p1 = {1, "kernel", 10};
    struct Process p2 = {2, "browser", 5};
    struct Process p3 = {3, "editor", 7};

    struct Process procs[3] = {p1, p2, p3};

    for (int i = 0; i < 3; i++) {
        printf("PID: %d  Name: %s  Priority: %d\\n",
               procs[i].id, procs[i].name, procs[i].priority);
    }

    struct Process highest = procs[0];
    for (int i = 1; i < 3; i++) {
        if (procs[i].priority > highest.priority) {
            highest = procs[i];
        }
    }
    printf("Highest priority: %s\\n", highest.name);
    return 0;
}''',
                'example_output': '''PID: 1  Name: kernel  Priority: 10
PID: 2  Name: browser  Priority: 5
PID: 3  Name: editor  Priority: 7
Highest priority: kernel'''
            },
        ]

        for data in c_lessons:
            Lesson.objects.update_or_create(
                language=c, order=data['order'],
                defaults={k: v for k, v in data.items() if k != 'order'}
            )

        # ─── ASSEMBLY ────────────────────────────────────────
        asm, _ = Language.objects.get_or_create(
            name='Assembly',
            defaults={'description': 'The human-readable form of machine instructions. One step above binary. You write exactly what the CPU executes — no abstraction, no compiler decisions.'}
        )

        asm_lessons = [
            {
                'order': 1,
                'title': 'What is Assembly',
                'content': '''Assembly language is the direct representation of machine instructions in human-readable form.

When you write C, the compiler translates your code into Assembly, then into binary machine code. Assembly is the middle layer — one step away from the raw bytes the CPU executes.

Each Assembly instruction maps to exactly one machine instruction. There is a 1-to-1 relationship between what you write and what the CPU does. No compiler is making decisions for you.

x86-64 is the Assembly dialect for Intel and AMD 64-bit processors — the CPUs in most laptops and desktop computers today.

An Assembly program has sections:
.data — stores initialized data (strings, constants)
.bss — stores uninitialized data (variables)
.text — stores the executable instructions

_start is the entry point — the first instruction the CPU executes when your program runs. This is equivalent to main() in C.

The syscall instruction transfers control from your program to the operating system kernel. When you want to print text or exit, you set up registers with the right values and call syscall.

Assembly forces you to think like the CPU. Every operation, every memory access, every function call — you control it all.''',
                'challenge': 'Write an Assembly program that exits cleanly with exit code 0. Use the exit syscall (syscall number 60). Add comments to every line explaining what it does.',
                'starter_code': '''; Clean exit program
; Syscall 60 = exit on Linux x86-64

section .text
    global _start

_start:
    mov rax, 60     ; syscall number: exit
    xor rdi, rdi    ; exit code: 0 (xor reg,reg = fastest way to zero a register)
    syscall         ; call the kernel''',
                'example_output': '(program exits silently with code 0)'
            },
            {
                'order': 2,
                'title': 'Registers',
                'content': '''Registers are the CPU\'s internal storage — the fastest memory that exists. Accessing a register takes 1 clock cycle. Accessing RAM takes hundreds.

x86-64 has 16 general-purpose 64-bit registers:
rax — accumulator. Used for arithmetic and return values from functions.
rbx — base register. General purpose, preserved across function calls.
rcx — counter. Used for loop counts and string operations.
rdx — data register. Used for I/O and as the high part of division results.
rsi — source index. Points to source data in memory operations.
rdi — destination index. Points to destination data. Also holds the first function argument.
rsp — stack pointer. Always points to the top of the stack. Never use it for other purposes.
rbp — base pointer. Points to the base of the current stack frame.
r8 through r15 — additional general purpose registers.

For syscalls, Linux uses this convention:
rax — syscall number
rdi — first argument
rsi — second argument
rdx — third argument

The same physical register has different names depending on how much of it you access:
rax is the full 64 bits
eax is the lower 32 bits
ax is the lower 16 bits
al is the lower 8 bits

Understanding registers is understanding where the CPU keeps its working data.''',
                'challenge': 'Write a program that loads different values into rax, rbx, rcx, and rdx. Add a comment on each line stating what that register is typically used for. The program should exit cleanly.',
                'starter_code': '''; Register demonstration
section .text
    global _start

_start:
    mov rax, 1      ; rax: accumulator / syscall number
    mov rbx, 2      ; rbx: base register / general purpose
    mov rcx, 3      ; rcx: counter register
    mov rdx, 4      ; rdx: data register / third syscall arg

    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '(program exits silently — register values are internal to the CPU)'
            },
            {
                'order': 3,
                'title': 'MOV Instruction',
                'content': '''MOV is the most fundamental Assembly instruction. It copies data from one location to another.

MOV destination, source

The destination is always written to. The source is always read from. The source is never changed.

mov rax, 42         — load the immediate value 42 into rax
mov rbx, rax        — copy the value in rax into rbx
mov rax, [rbx]      — load the value at the memory address stored in rbx into rax
mov [rbx], rax      — store the value in rax at the memory address in rbx

The square brackets [ ] mean "the memory at this address". Without brackets you work with the register value. With brackets you work with the memory the register points to.

You cannot move memory to memory directly. You must go through a register:
mov rax, [addr1]    — load from memory into register
mov [addr2], rax    — store from register into memory

MOV does not affect CPU flags. The CPU status register is not changed by MOV.

The size of the operation matters. Moving into rax operates on 64 bits. Moving into eax operates on 32 bits and zeros the upper 32 bits of rax. Moving into ax operates on 16 bits and does not change the rest.''',
                'challenge': 'Move the value 100 into rax. Copy rax into rbx. Move the value 200 into rcx. Copy rcx into rdx. Exit cleanly. Add comments explaining each MOV.',
                'starter_code': '''; MOV instruction demonstration
section .text
    global _start

_start:
    mov rax, 100    ; load immediate value 100 into rax
    mov rbx, rax    ; copy rax into rbx — rbx is now 100
    mov rcx, 200    ; load immediate value 200 into rcx
    mov rdx, rcx    ; copy rcx into rdx — rdx is now 200

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '(program exits silently — values moved between registers)'
            },
            {
                'order': 4,
                'title': 'Arithmetic Instructions',
                'content': '''Assembly arithmetic instructions operate on registers and memory.

ADD destination, source — adds source to destination and stores result in destination
SUB destination, source — subtracts source from destination
IMUL destination, source — signed integer multiply
IDIV source — divides rdx:rax by source. Quotient goes in rax, remainder in rdx.

Before dividing, you must sign-extend rax into rdx using cqo. This clears rdx properly.

INC register — adds 1 to register (faster than ADD reg, 1)
DEC register — subtracts 1 from register

NEG register — negates the value (two\'s complement negation)

All arithmetic instructions set CPU flags:
ZF (zero flag) — set if result is zero
SF (sign flag) — set if result is negative
CF (carry flag) — set if unsigned overflow occurred
OF (overflow flag) — set if signed overflow occurred

These flags are what conditional jumps check. Every if statement in C compiles to an arithmetic/compare instruction followed by a jump that reads these flags.

To print a number in Assembly you must convert it to ASCII characters yourself — there is no printf. The write syscall only outputs raw bytes.''',
                'challenge': 'Load 20 into rax and 7 into rbx. Add them and store result in rcx. Subtract rbx from rax and store in rdx. Then exit. Comment every line.',
                'starter_code': '''; Arithmetic demonstration
section .text
    global _start

_start:
    mov rax, 20     ; rax = 20
    mov rbx, 7      ; rbx = 7

    mov rcx, rax    ; rcx = rax (20)
    add rcx, rbx    ; rcx = 20 + 7 = 27

    mov rdx, rax    ; rdx = rax (20)
    sub rdx, rbx    ; rdx = 20 - 7 = 13

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '(program exits silently — arithmetic results stored in registers)'
            },
            {
                'order': 5,
                'title': 'Logical Operators',
                'content': '''Logical (bitwise) instructions operate on individual bits of a value.

AND destination, source — each bit in result is 1 only if both corresponding bits are 1
OR destination, source — each bit is 1 if either corresponding bit is 1
XOR destination, source — each bit is 1 if the bits are different
NOT destination — flips every bit (one\'s complement)

Real applications:
AND is used for masking — isolating specific bits. AND rax, 0x0F isolates the lower 4 bits.
OR is used for setting bits. OR rax, 0x80 sets bit 7 without touching other bits.
XOR is used for toggling bits and clearing registers. XOR rax, rax is the fastest way to zero rax.
NOT is used for one\'s complement negation.

Example: 0xFF AND 0x0F
11111111
00001111
--------
00001111  = 0x0F

XOR rax, rax is so common it has its own encoding in machine code that is 1 byte shorter than MOV rax, 0.

These operations map directly to hardware logic gates — AND, OR, XOR gates in the CPU\'s ALU (Arithmetic Logic Unit). When you write these instructions you are directly controlling gate-level logic.''',
                'challenge': 'Load 0xFF into rax and 0x0F into rbx. Perform AND, OR, and XOR between them storing each result in rcx, rdx, and r8 respectively. Exit cleanly.',
                'starter_code': '''; Bitwise operations
section .text
    global _start

_start:
    mov rax, 0xFF   ; rax = 11111111 in binary
    mov rbx, 0x0F   ; rbx = 00001111 in binary

    mov rcx, rax
    and rcx, rbx    ; rcx = 0xFF AND 0x0F = 0x0F

    mov rdx, rax
    or  rdx, rbx    ; rdx = 0xFF OR 0x0F = 0xFF

    mov r8, rax
    xor r8, rbx     ; r8  = 0xFF XOR 0x0F = 0xF0

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '(program exits silently — bitwise results stored in registers)'
            },
            {
                'order': 6,
                'title': 'Comparisons',
                'content': '''CMP compares two values by subtracting them without storing the result. Only the CPU flags are updated.

CMP destination, source — subtracts source from destination, sets flags, discards result.

After CMP, you read the flags using conditional jumps:
JE  — jump if equal (ZF=1)
JNE — jump if not equal (ZF=0)
JG  — jump if greater (signed)
JL  — jump if less (signed)
JGE — jump if greater or equal
JLE — jump if less or equal

This is exactly how if statements work at the machine level.

The C code:
if (a > b) { ... }

Compiles to:
cmp rax, rbx
jle skip
; body of if
skip:

TEST is similar to CMP but uses AND instead of subtraction. TEST rax, rax is the fastest way to check if rax is zero — if rax AND rax is zero, ZF is set.

The flags register (RFLAGS) is a 64-bit register where each bit is a flag. CF is bit 0, PF is bit 2, ZF is bit 6, SF is bit 7, OF is bit 11.

Every decision your CPU makes goes through these flags.''',
                'challenge': 'Load 10 into rax and 20 into rbx. Use CMP to compare them. Use a conditional jump to print different output based on whether rax is less than rbx. Use the write syscall to print "rax is less" or "rax is greater".',
                'starter_code': '''; Comparison demonstration
section .data
    msg_less db "rax is less", 10
    len_less equ $ - msg_less
    msg_greater db "rax is greater", 10
    len_greater equ $ - msg_greater

section .text
    global _start

_start:
    mov rax, 10
    mov rbx, 20
    cmp rax, rbx
    jl  rax_less

    ; rax >= rbx
    mov rax, 1
    mov rdi, 1
    mov rsi, msg_greater
    mov rdx, len_greater
    syscall
    jmp done

rax_less:
    mov rax, 1
    mov rdi, 1
    mov rsi, msg_less
    mov rdx, len_less
    syscall

done:
    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': 'rax is less'
            },
            {
                'order': 7,
                'title': 'Jumps and Labels',
                'content': '''A label is a named location in your code. It compiles to a memory address.

A jump instruction tells the CPU to move execution to a different address.

JMP label — unconditional jump. Always jumps. Equivalent to goto in C.

Conditional jumps check the flags set by CMP or TEST and jump only if the condition is true.

Labels and jumps are how loops are implemented in Assembly:

loop_start:
    dec rcx
    jnz loop_start   ; jump back if rcx is not zero

This is exactly how a C for loop compiles. The counter is decremented, the zero flag is checked, and the CPU jumps back if it is not zero.

CALL label — pushes the return address onto the stack then jumps to label. Used for function calls.
RET — pops the return address from the stack and jumps to it. Returns from a function.

JMP is direct — the address is encoded in the instruction.
Indirect jump: JMP [rax] — jumps to the address stored in rax. Used for function pointers and switch statements.

Labels have no overhead — they compile to nothing. They are just markers for the assembler to calculate addresses.

Every loop you have ever written in any language compiles down to these primitives: compare, conditional jump, label.''',
                'challenge': 'Write a loop using a label and JNZ that prints "LOOP" 5 times using the write syscall. Use rcx as your counter starting at 5.',
                'starter_code': '''; Loop using labels and jumps
section .data
    msg db "LOOP", 10
    len equ $ - msg

section .text
    global _start

_start:
    mov rcx, 5      ; loop counter

loop_start:
    push rcx        ; save counter (syscall modifies rcx)

    mov rax, 1      ; syscall: write
    mov rdi, 1      ; fd: stdout
    mov rsi, msg    ; message address
    mov rdx, len    ; message length
    syscall

    pop rcx         ; restore counter
    dec rcx         ; decrement counter
    jnz loop_start  ; jump back if not zero

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '''LOOP
LOOP
LOOP
LOOP
LOOP'''
            },
            {
                'order': 8,
                'title': 'The Stack',
                'content': '''The stack is a region of memory that grows downward. rsp (stack pointer) always points to the current top of the stack.

PUSH value — decrements rsp by 8, then stores value at [rsp]
POP destination — loads value from [rsp] into destination, then increments rsp by 8

The stack follows LIFO order — Last In, First Out. The last value you pushed is the first value you pop.

The stack is used for:
1. Saving and restoring registers across function calls
2. Storing local variables
3. Passing arguments to functions (beyond the first 6)
4. Storing return addresses (CALL pushes, RET pops)

When you call a function, CALL pushes the address of the next instruction onto the stack. When the function hits RET, it pops that address and jumps back to it.

If you push without popping, the stack grows. If you push more than the stack space allows, you get a stack overflow.

If you corrupt rsp, your program crashes because RET will jump to a garbage address.

Maintaining stack alignment is critical. The x86-64 ABI requires rsp to be 16-byte aligned before a CALL. If it is not aligned, certain CPU instructions will crash.

The stack is one of the most important concepts in systems programming. Buffer overflow attacks work by writing past a local variable on the stack to overwrite the saved return address.''',
                'challenge': 'Push the values 1, 2, 3 onto the stack. Pop them off into rax, rbx, rcx. Print the value of each register to stdout as ASCII characters. Notice the order they come off — explain it in a comment.',
                'starter_code': '''; Stack demonstration
section .data
    newline db 10
    one     db "popped: 1", 10
    two     db "popped: 2", 10
    three   db "popped: 3", 10

section .text
    global _start

_start:
    push 1          ; push 1 first
    push 2          ; push 2 second
    push 3          ; push 3 third — this is now at the top

    pop rax         ; rax = 3 (last in, first out)
    pop rbx         ; rbx = 2
    pop rcx         ; rcx = 1

    ; Print confirmation
    mov rax, 1
    mov rdi, 1
    mov rsi, three
    mov rdx, 10
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': 'popped: 3'
            },
            {
                'order': 9,
                'title': 'Functions in Assembly',
                'content': '''In Assembly, functions are implemented manually using CALL, RET, and the stack.

CALL label:
1. Pushes the return address (address of instruction after CALL) onto the stack
2. Jumps to label

RET:
1. Pops the return address from the stack
2. Jumps to that address

The x86-64 System V ABI (the calling convention on Linux) defines how arguments are passed:
First 6 arguments: rdi, rsi, rdx, rcx, r8, r9
Return value: rax
Caller-saved registers (caller must save if needed): rax, rcx, rdx, rsi, rdi, r8, r9, r10, r11
Callee-saved registers (function must preserve): rbx, rbp, r12-r15

A function prologue saves the base pointer and sets up a new stack frame:
push rbp
mov rbp, rsp

A function epilogue restores everything:
pop rbp
ret

This creates a chain of stack frames — each function knows where the previous frame was. This chain is what debuggers read when they show you a stack trace.

Writing functions in Assembly forces you to understand exactly what happens every time your C code calls a function.''',
                'challenge': 'Write an Assembly function called print_hello that prints "HELLO" to stdout using the write syscall. Call it from _start. The function must use proper prologue and epilogue.',
                'starter_code': '''; Function call demonstration
section .data
    msg db "HELLO", 10
    len equ $ - msg

section .text
    global _start

print_hello:
    push rbp            ; save caller base pointer
    mov rbp, rsp        ; set up new stack frame

    mov rax, 1          ; syscall: write
    mov rdi, 1          ; fd: stdout
    mov rsi, msg        ; message
    mov rdx, len        ; length
    syscall

    pop rbp             ; restore base pointer
    ret                 ; return to caller

_start:
    call print_hello    ; call our function

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': 'HELLO'
            },
            {
                'order': 10,
                'title': 'Interrupts and Syscalls',
                'content': '''A syscall is how your program asks the operating system to do something on its behalf.

Printing to the terminal, reading files, allocating memory, creating processes — your program cannot do any of these directly. It must ask the kernel.

On x86-64 Linux, the syscall instruction transfers control from your program (user space) to the kernel (kernel space). The CPU switches to a privileged mode, executes the kernel code, then returns.

The syscall number goes in rax. This tells the kernel which operation you want.
Common Linux syscalls:
1  — write (rdi=fd, rsi=buffer, rdx=length)
0  — read  (rdi=fd, rsi=buffer, rdx=max_length)
60 — exit  (rdi=exit code)
12 — brk   (memory allocation)

File descriptors:
0 = stdin (keyboard)
1 = stdout (terminal)
2 = stderr (error output)

Before the syscall instruction was introduced, programs used INT 0x80 (software interrupt). This is the older 32-bit method. You may see it in old code.

The difference between a syscall and a function call: a function call stays in user space. A syscall crosses the privilege boundary into the kernel. The kernel validates every syscall to prevent programs from corrupting the system.

Every printf in C eventually becomes a write syscall at the lowest level.''',
                'challenge': 'Write a program that uses the write syscall to print "SYSTEM CALL COMPLETE" to stdout, then exits with code 0 using the exit syscall.',
                'starter_code': '''; Syscall demonstration
section .data
    msg db "SYSTEM CALL COMPLETE", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; write syscall
    mov rax, 1          ; syscall number: write
    mov rdi, 1          ; file descriptor: stdout
    mov rsi, msg        ; pointer to message
    mov rdx, len        ; number of bytes to write
    syscall

    ; exit syscall
    mov rax, 60         ; syscall number: exit
    xor rdi, rdi        ; exit code: 0
    syscall''',
                'example_output': 'SYSTEM CALL COMPLETE'
            },
            {
                'order': 11,
                'title': 'Memory Addressing',
                'content': '''x86-64 supports multiple ways to specify a memory address in an instruction.

Immediate: mov rax, 42 — value 42 is encoded directly in the instruction

Register: mov rax, rbx — value comes from register rbx

Direct memory: mov rax, [label] — value comes from the memory address of label

Register indirect: mov rax, [rbx] — rbx holds the address, load value at that address

Base + offset: mov rax, [rbx + 8] — load from address rbx+8

Base + index: mov rax, [rbx + rcx] — add two registers for the address

Base + index + scale: mov rax, [rbx + rcx*8] — scale index by element size

Base + index + scale + displacement: mov rax, [rbx + rcx*8 + 16]

The scale can be 1, 2, 4, or 8 — matching byte sizes of common types.

LEA (Load Effective Address) calculates an address without accessing memory:
lea rax, [rbx + rcx*8] — puts the address into rax, does not load from it

LEA is often used for fast arithmetic because it can compute base+index*scale+displacement in one instruction.

These addressing modes exist because C arrays, structs, and pointers all compile to different combinations of these patterns.''',
                'challenge': 'Define a data label containing 5 integers (dq 10, 20, 30, 40, 50). Use a loop with a base+index*scale addressing mode to load each value and print whether it is above 25. Use LEA to calculate the address.',
                'starter_code': '''; Memory addressing demonstration
section .data
    values dq 10, 20, 30, 40, 50
    msg_above db "above 25", 10
    len_above equ $ - msg_above
    msg_below db "25 or below", 10
    len_below equ $ - msg_below

section .text
    global _start

_start:
    lea rbx, [values]   ; rbx = address of first element
    mov rcx, 0          ; index counter

loop:
    mov rax, [rbx + rcx*8]  ; load values[rcx]
    cmp rax, 25
    jg  is_above

    ; print "25 or below"
    push rcx
    mov rax, 1
    mov rdi, 1
    mov rsi, msg_below
    mov rdx, len_below
    syscall
    pop rcx
    jmp next

is_above:
    push rcx
    mov rax, 1
    mov rdi, 1
    mov rsi, msg_above
    mov rdx, len_above
    syscall
    pop rcx

next:
    inc rcx
    cmp rcx, 5
    jl  loop

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '''25 or below
25 or below
above 25
above 25
above 25'''
            },
            {
                'order': 12,
                'title': 'Your First Complete Assembly Program',
                'content': '''You now have enough to write a complete, functional Assembly program.

A complete program has:
1. A .data section with all string and constant data
2. A .text section with all executable code
3. A _start label as the entry point
4. At least one write syscall for output
5. An exit syscall at the end

The write syscall signature:
rax = 1 (syscall number)
rdi = 1 (stdout file descriptor)
rsi = address of string in memory
rdx = length of string in bytes

String length calculation:
msg db "Hello", 10    ; 10 is the newline byte
len equ $ - msg       ; $ is current address, minus start of msg = length

equ is an assembler directive that calculates a constant at assembly time.

Multiple strings means multiple write syscalls — one per string.

This program writes directly to the Linux kernel. No C standard library. No printf. No runtime. Just your code and the kernel.

This is what runs underneath every program on your computer.''',
                'challenge': 'Write a complete Assembly program that prints three lines: "COMPUTER LANGUAGES", your name, and "ASSEMBLY COMPLETE". Use three separate write syscalls. Exit cleanly.',
                'starter_code': '''; Complete Assembly program
section .data
    line1 db "COMPUTER LANGUAGES", 10
    len1  equ $ - line1
    line2 db "Elijah", 10
    len2  equ $ - line2
    line3 db "ASSEMBLY COMPLETE", 10
    len3  equ $ - line3

section .text
    global _start

_start:
    ; Print line 1
    mov rax, 1
    mov rdi, 1
    mov rsi, line1
    mov rdx, len1
    syscall

    ; Print line 2
    mov rax, 1
    mov rdi, 1
    mov rsi, line2
    mov rdx, len2
    syscall

    ; Print line 3
    mov rax, 1
    mov rdi, 1
    mov rsi, line3
    mov rdx, len3
    syscall

    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '''COMPUTER LANGUAGES
Elijah
ASSEMBLY COMPLETE'''
            },
        ]

        for data in asm_lessons:
            Lesson.objects.update_or_create(
                language=asm, order=data['order'],
                defaults={k: v for k, v in data.items() if k != 'order'}
            )

        # ─── MACHINE LANGUAGE ────────────────────────────────
        ml, _ = Language.objects.get_or_create(
            name='Machine Language',
            defaults={'description': 'The binary instructions the CPU actually executes. No assembler, no compiler — raw bytes that the processor decodes and runs directly.'}
        )

        ml_lessons = [
            {
                'order': 1,
                'title': 'What is Machine Language',
                'content': '''Machine language is the actual binary data that the CPU reads and executes. It is the lowest level of software.

Every instruction you write in C or Assembly eventually becomes a sequence of bytes in machine language. The CPU fetches these bytes from memory, decodes them, and executes them.

A machine instruction consists of:
- Opcode: the operation to perform (1-3 bytes)
- ModRM byte: specifies operand types and registers
- SIB byte: scale/index/base for memory addressing
- Displacement: memory offset (0, 1, 2, or 4 bytes)
- Immediate: constant value encoded in the instruction

Example: MOV EAX, 1 in x86-64
In Assembly:  mov eax, 1
In hex:       B8 01 00 00 00
In binary:    10111000 00000001 00000000 00000000 00000000

B8 is the opcode for "MOV EAX, immediate 32-bit value"
01 00 00 00 is the value 1 in little-endian format (least significant byte first)

Little-endian means the smallest byte value comes first in memory. Intel processors are little-endian.

Machine language is not human-friendly. It has no labels, no variable names, no comments. Just bytes. The CPU does not care what your variable was named — it only cares about addresses.

Reading machine language is called disassembly. Tools like objdump convert binary back to Assembly so humans can read it.''',
                'challenge': 'In the comments below, manually decode the bytes B8 05 00 00 00. What instruction is this? What value does it move? What register does it target? Use the example in the lesson to guide you.',
                'starter_code': '''; Machine Language Decoding Exercise
; You are looking at raw bytes from a compiled program.
;
; Bytes: B8 05 00 00 00
;
; Decode manually in the comments below:
; B8      = opcode for: ?
; 05 00 00 00 = value in little-endian: ?
; Full instruction in Assembly: ?
;
; Now decode these bytes:
; Bytes: 48 B8 01 00 00 00 00 00 00 00
; 48    = REX.W prefix meaning: ?
; B8    = opcode for: ?
; value = ?
; Full instruction: ?''',
                'example_output': 'B8 05 00 00 00 = MOV EAX, 5\n48 B8 01 00 00 00 00 00 00 00 = MOV RAX, 1'
            },
            {
                'order': 2,
                'title': 'How Assembly Becomes Machine Code',
                'content': '''The assembler is the tool that translates Assembly language into machine code.

When you run nasm -f elf64 main.asm -o main.o, NASM reads your Assembly text and produces an object file containing binary machine code.

The linker then combines object files and resolves addresses into a final executable.

This process:
Source (.asm) → Assembler (nasm) → Object (.o) → Linker (ld/gcc) → Executable

The object file contains:
- Machine code bytes for each instruction
- A symbol table mapping label names to addresses
- Relocation entries where addresses need to be filled in

When the assembler sees: mov rax, 60
It knows rax = register 0 in the encoding
It knows 60 = 0x3C
It produces: 48 C7 C0 3C 00 00 00

48 = REX.W prefix (use 64-bit operand size)
C7 = opcode for MOV r/m64, imm32
C0 = ModRM byte encoding rax as destination
3C 00 00 00 = value 60 in little-endian

When the assembler sees a label like loop_start:, it records the current byte offset. When it sees jnz loop_start, it calculates the relative offset between the jump and the target and encodes it in the instruction.

This is why changing code before a label changes the jump encoding — the offset changes.''',
                'challenge': 'Write the Assembly for MOV RAX, 1 followed by MOV RDI, 1 followed by SYSCALL. In comments below each instruction, write what you expect the hex bytes to be based on what you learned. Then explain why the REX.W prefix (0x48) is needed.',
                'starter_code': '''; Assembly to Machine Code
; Write each instruction and predict its hex encoding in the comment

section .text
    global _start

_start:
    mov rax, 1      ; predicted hex: ?
    mov rdi, 1      ; predicted hex: ?
    syscall         ; hex encoding: 0F 05 (always)

    ; Why is the REX.W prefix (0x48) needed before mov rax and mov rdi?
    ; Answer in comment: ?

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': 'SYSTEM CALL COMPLETE\n(examine the binary with: objdump -d main)'
            },
            {
                'order': 3,
                'title': 'Instruction Encoding',
                'content': '''x86-64 instruction encoding follows a precise format. Understanding it lets you read raw binary programs.

Prefixes (optional, 0-4 bytes):
REX prefix: 0100WRXB
  W=1: 64-bit operand size
  R: extends the ModRM reg field
  X: extends the SIB index field
  B: extends the ModRM rm field or SIB base

Opcode (1-3 bytes): identifies the operation

ModRM byte (1 byte, optional):
Bits 7-6: Mod field (00=memory, 01=memory+disp8, 10=memory+disp32, 11=register)
Bits 5-3: Reg field (register or opcode extension)
Bits 2-0: R/M field (register or memory base)

SIB byte (1 byte, optional): Scale/Index/Base for complex addressing

Displacement (0,1,2,4 bytes): memory offset

Immediate (0,1,2,4,8 bytes): constant value

Example: ADD RAX, RBX
48 01 D8
48 = REX.W (64-bit)
01 = ADD r/m64, r64 opcode
D8 = ModRM: mod=11 (register), reg=011 (rbx), rm=000 (rax)

Decoding ModRM D8 in binary:
11 011 000
^^ ^^^ ^^^
|  |   rm = 000 = rax
|  reg = 011 = rbx
mod = 11 = register (not memory)''',
                'challenge': 'Decode the following hex bytes manually in the comments. Identify each byte\'s role (REX prefix, opcode, ModRM, immediate) and what the full instruction is.\nBytes to decode: 48 83 C0 05',
                'starter_code': '''; Instruction Encoding Decoder Exercise
;
; Decode: 48 83 C0 05
;
; 48      = binary 01001000
;           REX prefix: W=1 (64-bit), R=0, X=0, B=0
;           Meaning: ?
;
; 83      = opcode for: ADD/OR/AND/SUB/CMP r/m64, imm8
;           (which operation depends on ModRM reg field)
;
; C0      = ModRM byte: binary 11 000 000
;           mod = 11 meaning: ?
;           reg = 000 meaning: (opcode extension) operation = ADD
;           rm  = 000 meaning: register ?
;
; 05      = immediate value: decimal ?
;
; Full instruction in Assembly: ?
;
; Now assemble and disassemble to verify:
section .text
    global _start
_start:
    db 0x48, 0x83, 0xC0, 0x05  ; raw bytes
    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '48 83 C0 05 = ADD RAX, 5'
            },
            {
                'order': 4,
                'title': 'Reading a Hex Dump',
                'content': '''A hex dump shows the raw bytes of a file or memory region in hexadecimal, with the ASCII representation alongside.

When you run: objdump -d main
You see the disassembly — hex bytes on the left, Assembly instructions on the right.

A hex dump line looks like:
  401000:  b8 3c 00 00 00          mov    eax,0x3c

401000 is the memory address where these bytes live.
b8 3c 00 00 00 are the raw bytes.
mov eax,0x3c is what those bytes mean.

To examine your compiled binary:
objdump -d main          — shows disassembly
xxd main | head -20      — shows raw hex dump
readelf -a main          — shows all ELF metadata

Every program you have ever run is a sequence of bytes like these. The operating system loads them into memory and the CPU starts executing at the entry point.

A hex dump of a simple exit program:
b8 3c 00 00 00    mov eax,0x3c    ; syscall 60 = exit
bf 00 00 00 00    mov edi,0x0     ; exit code 0
0f 05             syscall         ; call kernel

These 12 bytes are a complete program. The CPU needs nothing else.

Understanding hex dumps means you can read any compiled program — including programs you did not write and have no source code for.''',
                'challenge': 'Write the minimal exit program (mov rax 60, xor rdi rdi, syscall). Compile it. Run objdump -d on it. Paste the hex bytes from objdump into comments in your code and label each byte.',
                'starter_code': '''; Minimal program for hex dump analysis
; After compiling, run:
;   nasm -f elf64 main.asm -o main.o
;   ld main.o -o main
;   objdump -d main
;
; Paste the objdump output here as comments and label each byte:
;
; Example output you should see:
; 0000000000401000 <_start>:
;   401000:  48 c7 c0 3c 00 00 00    mov    rax,0x3c
;   401007:  48 31 ff                xor    rdi,rdi
;   40100a:  0f 05                   syscall
;
; Label each byte of: 48 c7 c0 3c 00 00 00
; 48 = ?
; c7 = ?
; c0 = ?
; 3c 00 00 00 = value ? in little-endian

section .text
    global _start

_start:
    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '(program exits — run objdump -d to see the hex dump)'
            },
            {
                'order': 5,
                'title': 'Opcodes and CPU Decoding',
                'content': '''An opcode is the part of a machine instruction that tells the CPU which operation to perform.

The CPU\'s instruction decoder reads the first byte (or bytes) of each instruction to determine the operation. Then it reads the remaining bytes for operands.

Common x86-64 opcodes:
B8-BF    MOV r64, imm64 (B8=rax, B9=rcx, BA=rdx, BB=rbx, BC=rsp, BD=rbp, BE=rsi, BF=rdi)
89       MOV r/m64, r64
8B       MOV r64, r/m64
01       ADD r/m64, r64
29       SUB r/m64, r64
0F 05    SYSCALL
C3       RET
E8       CALL rel32
EB       JMP rel8
74       JE rel8
75       JNE rel8

The opcode table has 256 single-byte opcodes (0x00 to 0xFF) plus escape sequences for multi-byte opcodes (0x0F xx).

When you press a key on your keyboard, the CPU executes thousands of these opcodes per millisecond — fetching bytes, decoding them, executing them, fetching the next.

The instruction decoder is one of the most complex parts of a modern CPU. It must handle variable-length instructions (1 to 15 bytes), prefixes, and multiple encoding formats.

CISC (Complex Instruction Set Computing) — x86 has variable-length instructions
RISC (Reduced Instruction Set Computing) — ARM has fixed 4-byte instructions

x86\'s variable-length encoding makes it efficient for code density but complex to decode.''',
                'challenge': 'Given opcode 0F 05, identify the instruction. Given opcode C3, identify it. Given B8, identify the register being targeted and what type of value follows. Write your answers as comments.',
                'starter_code': '''; Opcode identification exercise
;
; Opcode: 0F 05
; Instruction: ?
; Used when: ?
; In Assembly written as: ?
;
; Opcode: C3
; Instruction: ?
; Used when: ?
; In Assembly written as: ?
;
; Opcode: B8
; Instruction: ?
; Target register: ?
; What follows: ?
; In Assembly written as: ?
;
; Opcode: 48 31 FF
; 48 = ?
; 31 = ?
; FF = ModRM for rdi XOR rdi
; Full instruction: ?

section .text
    global _start

_start:
    ; These instructions produce the opcodes above
    syscall         ; 0F 05
    ; ret           ; C3 (commented out — would crash here)
    mov rax, 0      ; B8 00 00 00 00 00 00 00 00
    xor rdi, rdi    ; 48 31 FF

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': '(examine with objdump -d to verify your opcode answers)'
            },
            {
                'order': 6,
                'title': 'Fetch-Decode-Execute Cycle',
                'content': '''The fetch-decode-execute cycle is the fundamental loop the CPU runs billions of times per second.

FETCH:
The CPU reads the next instruction bytes from memory at the address in RIP (instruction pointer).
RIP always points to the next instruction to execute.
After fetching, RIP is automatically incremented by the instruction length.

DECODE:
The instruction decoder examines the opcode bytes.
It identifies the operation, operand types, sizes, and addressing modes.
It routes the instruction to the appropriate execution unit.

EXECUTE:
The ALU (Arithmetic Logic Unit) performs arithmetic/logic operations.
The AGU (Address Generation Unit) calculates memory addresses.
The FPU (Floating Point Unit) handles floating point operations.
Results are written back to registers or memory.

For MOV RAX, 60:
FETCH: read bytes 48 C7 C0 3C 00 00 00 from [RIP]. RIP += 7.
DECODE: REX.W prefix detected. Opcode C7 = MOV r/m64, imm32. ModRM C0 = register rax.
EXECUTE: write the value 0x3C (60) into the rax register.

Modern CPUs do not execute one instruction at a time. They use:
Pipelining: fetch/decode/execute multiple instructions simultaneously
Out-of-order execution: execute instructions in whatever order is most efficient
Branch prediction: guess where jumps will go and start executing there
Superscalar: multiple execution units running in parallel

But the logical model is always: fetch, decode, execute, repeat.''',
                'challenge': 'Trace through the fetch-decode-execute cycle for each instruction in the program below. For each instruction write: what bytes are fetched, what the decoder identifies, what the execute stage does.',
                'starter_code': '''; Fetch-Decode-Execute trace exercise
;
; Trace each instruction:
;
; Instruction 1: mov rax, 1
;   FETCH:   bytes = 48 C7 C0 01 00 00 00, RIP += 7
;   DECODE:  REX.W + opcode C7 = MOV r/m64 imm32, ModRM C0 = rax
;   EXECUTE: rax = 1
;
; Instruction 2: mov rdi, 1
;   FETCH:   bytes = ?
;   DECODE:  ?
;   EXECUTE: ?
;
; Instruction 3: mov rsi, msg
;   FETCH:   bytes = ?
;   DECODE:  ?
;   EXECUTE: ?
;
; Instruction 4: mov rdx, len
;   FETCH:   bytes = ?
;   DECODE:  ?
;   EXECUTE: ?
;
; Instruction 5: syscall
;   FETCH:   bytes = 0F 05, RIP += 2
;   DECODE:  two-byte opcode 0F 05 = SYSCALL
;   EXECUTE: CPU switches to kernel mode, kernel executes write()

section .data
    msg db "FETCH DECODE EXECUTE", 10
    len equ $ - msg

section .text
    global _start

_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, msg
    mov rdx, len
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                'example_output': 'FETCH DECODE EXECUTE'
            },
        ]

        for data in ml_lessons:
            Lesson.objects.update_or_create(
                language=ml, order=data['order'],
                defaults={k: v for k, v in data.items() if k != 'order'}
            )

        self.stdout.write(self.style.SUCCESS('All lessons seeded successfully.'))
