from django.core.management.base import BaseCommand
from core.models import HardwareSystem, HardwareChallenge


class Command(BaseCommand):
    help = 'Seed hardware systems and challenges'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding hardware...')

        systems = [
            {
                'name': 'PERSONAL COMPUTER',
                'slug': 'pc',
                'description': 'A CPU, RAM, storage, and an OS running on your desk. The most common computing environment. You will write the software that controls how it boots, manages memory, and runs processes.',
                'category': 'classical',
                'unlock_order': 1,
                'challenges': [
                    {
                        'order': 1,
                        'title': 'Boot Sequence Simulator',
                        'description': 'When a PC powers on, the CPU starts executing code from a fixed memory address. Before the OS loads, the BIOS/UEFI runs a Power-On Self Test (POST), checks hardware, then hands control to the bootloader. Your task is to simulate this sequence in C.',
                        'instructions': '''Write a C program that simulates the PC boot sequence.

Create a separate function for each boot stage:
  power_on()    — prints "POWER ON"
  bios_check()  — prints "BIOS POST: OK"
  memory_test() — prints "MEMORY: 16384 MB OK"
  load_os()     — prints "LOADING OS..."
  boot_complete() — prints "SYSTEM READY"

Call all five functions from main in the correct order.

Each function should simulate a delay by running an empty loop 10000 times before printing.

This models what real firmware does — each stage runs diagnostics before passing control to the next.''',
                        'starter_code_c': '''#include <stdio.h>

void power_on() {
    // simulate POST delay
    for (int i = 0; i < 10000; i++) {}
    printf("POWER ON\\n");
}

void bios_check() {
    for (int i = 0; i < 10000; i++) {}
    printf("BIOS POST: OK\\n");
}

void memory_test() {
    for (int i = 0; i < 10000; i++) {}
    printf("MEMORY: 16384 MB OK\\n");
}

void load_os() {
    for (int i = 0; i < 10000; i++) {}
    printf("LOADING OS...\\n");
}

void boot_complete() {
    printf("SYSTEM READY\\n");
}

int main() {
    power_on();
    bios_check();
    memory_test();
    load_os();
    boot_complete();
    return 0;
}''',
                        'starter_code_asm_x86': '''; Boot sequence in Assembly
section .data
    msg1 db "POWER ON", 10
    len1 equ $ - msg1
    msg2 db "BIOS POST: OK", 10
    len2 equ $ - msg2
    msg3 db "MEMORY: 16384 MB OK", 10
    len3 equ $ - msg3
    msg4 db "LOADING OS...", 10
    len4 equ $ - msg4
    msg5 db "SYSTEM READY", 10
    len5 equ $ - msg5

section .text
    global _start

%macro print 2
    mov rax, 1
    mov rdi, 1
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

_start:
    print msg1, len1
    print msg2, len2
    print msg3, len3
    print msg4, len4
    print msg5, len5

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 boot sequence
.section .data
msg1: .ascii "POWER ON\n"
len1 = . - msg1
msg2: .ascii "BIOS POST: OK\n"
len2 = . - msg2
msg3: .ascii "SYSTEM READY\n"
len3 = . - msg3

.section .text
.global _start

_start:
    mov x8, #64        // write syscall
    mov x0, #1         // stdout
    adr x1, msg1
    mov x2, len1
    svc #0

    mov x8, #64
    mov x0, #1
    adr x1, msg2
    mov x2, len2
    svc #0

    mov x8, #64
    mov x0, #1
    adr x1, msg3
    mov x2, len3
    svc #0

    mov x8, #93        // exit syscall
    mov x0, #0
    svc #0'''
                    },
                    {
                        'order': 2,
                        'title': 'Memory Block Allocator',
                        'description': 'RAM is a flat array of bytes. The OS tracks which blocks are used and which are free. When a program requests memory, the OS finds a free block and marks it as used. When the program frees it, the block becomes available again. You will simulate this memory management system.',
                        'instructions': '''Write a C program that simulates a memory allocator.

Create a global array of 256 chars representing RAM. Initialize all bytes to 0 (free).

Write these functions:
  allocate(int start, int size) — marks bytes from start to start+size-1 as 1 (used). Print "ALLOCATED: [start] to [start+size-1]"
  free_block(int start, int size) — marks bytes back to 0. Print "FREED: [start] to [start+size-1]"
  print_memory() — prints the first 32 bytes as 0s and 1s in 8-byte rows

In main:
  1. print_memory() — show initial state
  2. allocate(0, 64) — allocate first 64 bytes
  3. print_memory()
  4. allocate(100, 50)
  5. free_block(0, 32) — free first 32 bytes
  6. print_memory() — show final state

This is how malloc and free work at the conceptual level.''',
                        'starter_code_c': '''#include <stdio.h>

#define MEM_SIZE 256
unsigned char memory[MEM_SIZE] = {0};

void allocate(int start, int size) {
    for (int i = start; i < start + size; i++) {
        memory[i] = 1;
    }
    printf("ALLOCATED: %d to %d\\n", start, start + size - 1);
}

void free_block(int start, int size) {
    for (int i = start; i < start + size; i++) {
        memory[i] = 0;
    }
    printf("FREED: %d to %d\\n", start, start + size - 1);
}

void print_memory() {
    printf("MEMORY MAP (first 32 bytes):\\n");
    for (int i = 0; i < 32; i++) {
        printf("%d", memory[i]);
        if ((i + 1) % 8 == 0) printf("\\n");
    }
}

int main() {
    print_memory();
    allocate(0, 64);
    print_memory();
    allocate(100, 50);
    free_block(0, 32);
    print_memory();
    return 0;
}''',
                        'starter_code_asm_x86': '''; Memory tracking in Assembly
section .bss
    memory resb 256     ; 256 bytes of simulated RAM

section .data
    msg_alloc db "ALLOCATED BLOCK", 10
    len_alloc equ $ - msg_alloc

section .text
    global _start

_start:
    ; Mark bytes 0-63 as used (value 1)
    mov rdi, memory     ; start address
    mov rcx, 64         ; count
    mov al, 1           ; value to store
    rep stosb           ; store al into [rdi] rcx times, increment rdi

    mov rax, 1
    mov rdi, 1
    mov rsi, msg_alloc
    mov rdx, len_alloc
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 memory simulation
.section .bss
memory: .skip 256

.section .data
msg: .ascii "MEMORY ALLOCATED\n"
len = . - msg

.section .text
.global _start

_start:
    adr x0, memory
    mov x1, #64
    mov w2, #1
fill_loop:
    strb w2, [x0], #1
    subs x1, x1, #1
    bne fill_loop

    mov x8, #64
    mov x0, #1
    adr x1, msg
    mov x2, len
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                    {
                        'order': 3,
                        'title': 'Process Scheduler',
                        'description': 'The OS runs multiple programs simultaneously by rapidly switching between them. This is called scheduling. The simplest algorithm is round-robin — give each process equal time in turn. You will implement a round-robin scheduler.',
                        'instructions': '''Write a C program that simulates a round-robin process scheduler.

Define a struct Process with fields:
  int id
  char name[20]
  int remaining_time  (units of work left)

Create 4 processes:
  {1, "KERNEL",  8}
  {2, "BROWSER", 5}
  {3, "EDITOR",  3}
  {4, "SHELL",   6}

Write a function schedule(Process procs[], int count) that runs one round-robin cycle:
  For each process that has remaining_time > 0, subtract 1 and print:
  "CPU -> [name] | remaining: [time]"

Run schedule() in a loop until all processes have remaining_time == 0.

Print "ALL PROCESSES COMPLETE" when done.

This shows how a real OS scheduler works — each process gets a time slice, then yields to the next.''',
                        'starter_code_c': '''#include <stdio.h>
#include <string.h>

struct Process {
    int id;
    char name[20];
    int remaining_time;
};

int all_done(struct Process procs[], int count) {
    for (int i = 0; i < count; i++) {
        if (procs[i].remaining_time > 0) return 0;
    }
    return 1;
}

void schedule(struct Process procs[], int count) {
    for (int i = 0; i < count; i++) {
        if (procs[i].remaining_time > 0) {
            procs[i].remaining_time--;
            printf("CPU -> %s | remaining: %d\\n",
                   procs[i].name, procs[i].remaining_time);
        }
    }
}

int main() {
    struct Process procs[4] = {
        {1, "KERNEL",  8},
        {2, "BROWSER", 5},
        {3, "EDITOR",  3},
        {4, "SHELL",   6}
    };

    while (!all_done(procs, 4)) {
        schedule(procs, 4);
    }
    printf("ALL PROCESSES COMPLETE\\n");
    return 0;
}''',
                        'starter_code_asm_x86': '''; Round-robin scheduler simulation
section .data
    msg db "SCHEDULER RUNNING", 10
    len equ $ - msg
    done db "ALL PROCESSES COMPLETE", 10
    done_len equ $ - done

section .text
    global _start

_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, msg
    mov rdx, len
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, done
    mov rdx, done_len
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 scheduler
.section .data
msg: .ascii "SCHEDULER COMPLETE\n"
len = . - msg

.section .text
.global _start

_start:
    mov x8, #64
    mov x0, #1
    adr x1, msg
    mov x2, len
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                ]
            },
            {
                'name': 'SERVER',
                'slug': 'server',
                'description': 'A machine that listens. No display, no keyboard. It runs as a process waiting for network connections, processes requests, and sends responses. You will write the software logic that handles those requests.',
                'category': 'classical',
                'unlock_order': 2,
                'challenges': [
                    {
                        'order': 1,
                        'title': 'Request Router',
                        'description': 'A server receives requests and decides what to do with each one. HTTP servers receive GET, POST, PUT, DELETE requests and route them to the appropriate handler. You will build a request routing system.',
                        'instructions': '''Write a C program that simulates an HTTP request router.

Define constants for request types:
  #define GET    0
  #define POST   1
  #define PUT    2
  #define DELETE 3

Write a function handle_request(int method, char *path) that prints:
  GET    /path  -> "200 OK: [path]"
  POST   /path  -> "201 CREATED: [path]"
  PUT    /path  -> "200 UPDATED: [path]"
  DELETE /path  -> "204 DELETED: [path]"
  unknown       -> "405 METHOD NOT ALLOWED"

In main, simulate these 5 requests:
  GET    "/index"
  POST   "/users"
  GET    "/data"
  DELETE "/file"
  PUT    "/config"

Print each result.

This is the core logic inside every web server — route the request to the right handler.''',
                        'starter_code_c': '''#include <stdio.h>

#define GET    0
#define POST   1
#define PUT    2
#define DELETE 3

void handle_request(int method, char *path) {
    switch (method) {
        case GET:
            printf("200 OK: %s\\n", path);
            break;
        case POST:
            printf("201 CREATED: %s\\n", path);
            break;
        case PUT:
            printf("200 UPDATED: %s\\n", path);
            break;
        case DELETE:
            printf("204 DELETED: %s\\n", path);
            break;
        default:
            printf("405 METHOD NOT ALLOWED\\n");
    }
}

int main() {
    handle_request(GET,    "/index");
    handle_request(POST,   "/users");
    handle_request(GET,    "/data");
    handle_request(DELETE, "/file");
    handle_request(PUT,    "/config");
    return 0;
}''',
                        'starter_code_asm_x86': '''; Request router in Assembly
section .data
    r200 db "200 OK", 10
    len200 equ $ - r200
    r201 db "201 CREATED", 10
    len201 equ $ - r201
    r204 db "204 DELETED", 10
    len204 equ $ - r204

section .text
    global _start

_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, r200
    mov rdx, len200
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, r201
    mov rdx, len201
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, r204
    mov rdx, len204
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 request router
.section .data
r200: .ascii "200 OK\n"
len200 = . - r200
r201: .ascii "201 CREATED\n"
len201 = . - r201

.section .text
.global _start

_start:
    mov x8, #64
    mov x0, #1
    adr x1, r200
    mov x2, len200
    svc #0

    mov x8, #64
    mov x0, #1
    adr x1, r201
    mov x2, len201
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                    {
                        'order': 2,
                        'title': 'Connection Pool Manager',
                        'description': 'A server handles multiple simultaneous connections. To avoid the overhead of creating a new connection for every request, servers maintain a pool of reusable connections. You will build a connection pool with a fixed capacity.',
                        'instructions': '''Write a C program simulating a connection pool.

Define POOL_SIZE as 5.
Create an array int pool[POOL_SIZE] initialized to -1 (empty slot).

Write these functions:
  connect(int client_id) — find the first -1 slot, store client_id there. Print "CONNECTED: client [id] -> slot [slot]". If pool is full, print "REJECTED: pool full".
  disconnect(int client_id) — find the slot with client_id, set it to -1. Print "DISCONNECTED: client [id]".
  print_pool() — print all 5 slots showing slot number and value.

In main:
  print_pool()
  connect(101), connect(102), connect(103)
  print_pool()
  disconnect(102)
  connect(104), connect(105), connect(106)
  print_pool()

This is the logic behind database connection pools, thread pools, and socket pools in real servers.''',
                        'starter_code_c': '''#include <stdio.h>

#define POOL_SIZE 5
int pool[POOL_SIZE];

void init_pool() {
    for (int i = 0; i < POOL_SIZE; i++) pool[i] = -1;
}

void connect(int client_id) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (pool[i] == -1) {
            pool[i] = client_id;
            printf("CONNECTED: client %d -> slot %d\\n", client_id, i);
            return;
        }
    }
    printf("REJECTED: pool full\\n");
}

void disconnect(int client_id) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (pool[i] == client_id) {
            pool[i] = -1;
            printf("DISCONNECTED: client %d\\n", client_id);
            return;
        }
    }
}

void print_pool() {
    printf("POOL STATE:\\n");
    for (int i = 0; i < POOL_SIZE; i++) {
        if (pool[i] == -1)
            printf("  slot %d: [empty]\\n", i);
        else
            printf("  slot %d: client %d\\n", i, pool[i]);
    }
}

int main() {
    init_pool();
    print_pool();
    connect(101); connect(102); connect(103);
    print_pool();
    disconnect(102);
    connect(104); connect(105); connect(106);
    print_pool();
    return 0;
}''',
                        'starter_code_asm_x86': '''; Connection pool in Assembly
section .data
    msg_connected db "CONNECTION ACCEPTED", 10
    len_connected equ $ - msg_connected
    msg_full db "POOL FULL: REJECTED", 10
    len_full equ $ - msg_full

section .bss
    pool resq 5         ; 5 slots of 8 bytes each, initialized to 0

section .text
    global _start

_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, msg_connected
    mov rdx, len_connected
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 connection pool
.section .data
msg: .ascii "POOL MANAGED\n"
len = . - msg

.section .text
.global _start

_start:
    mov x8, #64
    mov x0, #1
    adr x1, msg
    mov x2, len
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                ]
            },
            {
                'name': 'DATA CENTER',
                'slug': 'data-center',
                'description': 'Thousands of servers working together. Redundant power, cooling systems, and network fabric. Your code must distribute work across machines, detect failures, and keep the system running even when hardware dies.',
                'category': 'classical',
                'unlock_order': 3,
                'challenges': [
                    {
                        'order': 1,
                        'title': 'Load Balancer',
                        'description': 'A load balancer sits in front of multiple servers and distributes incoming requests so no single server is overwhelmed. The simplest algorithm is round-robin — send request 1 to server 1, request 2 to server 2, and so on cycling through all servers.',
                        'instructions': '''Write a C program simulating a round-robin load balancer.

Define NUM_SERVERS as 4.

Create a struct Server with fields:
  int id
  char name[20]
  int request_count

Initialize 4 servers: {1,"SERVER-A",0}, {2,"SERVER-B",0}, {3,"SERVER-C",0}, {4,"SERVER-D",0}

Write distribute(Server servers[], int count, int *current, int request_num):
  Send the request to servers[*current]
  Increment that server's request_count
  Print "REQUEST [num] -> [server name]"
  Increment *current, wrap around with modulo

In main, distribute 12 requests using a loop.
After all requests, print each server's total request count.

This is exactly how nginx and HAProxy distribute traffic in real data centers.''',
                        'starter_code_c': '''#include <stdio.h>

#define NUM_SERVERS 4

struct Server {
    int id;
    char name[20];
    int request_count;
};

void distribute(struct Server servers[], int count, int *current, int req_num) {
    servers[*current].request_count++;
    printf("REQUEST %2d -> %s\\n", req_num, servers[*current].name);
    *current = (*current + 1) % count;
}

int main() {
    struct Server servers[NUM_SERVERS] = {
        {1, "SERVER-A", 0},
        {2, "SERVER-B", 0},
        {3, "SERVER-C", 0},
        {4, "SERVER-D", 0}
    };

    int current = 0;
    for (int i = 1; i <= 12; i++) {
        distribute(servers, NUM_SERVERS, &current, i);
    }

    printf("\\nLOAD SUMMARY:\\n");
    for (int i = 0; i < NUM_SERVERS; i++) {
        printf("  %s: %d requests\\n", servers[i].name, servers[i].request_count);
    }
    return 0;
}''',
                        'starter_code_asm_x86': '''; Load balancer simulation
section .data
    sA db "SERVER-A", 10
    lenA equ $ - sA
    sB db "SERVER-B", 10
    lenB equ $ - sB
    sC db "SERVER-C", 10
    lenC equ $ - sC
    sD db "SERVER-D", 10
    lenD equ $ - sD

section .text
    global _start

_start:
    ; Round-robin: print each server name 3 times (12 requests / 4 servers)
    mov rcx, 3

round:
    push rcx

    mov rax, 1
    mov rdi, 1
    mov rsi, sA
    mov rdx, lenA
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, sB
    mov rdx, lenB
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, sC
    mov rdx, lenC
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, sD
    mov rdx, lenD
    syscall

    pop rcx
    dec rcx
    jnz round

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 load balancer
.section .data
sa: .ascii "SERVER-A\n"
lena = . - sa
sb: .ascii "SERVER-B\n"
lenb = . - sb

.section .text
.global _start

_start:
    mov x8, #64
    mov x0, #1
    adr x1, sa
    mov x2, lena
    svc #0

    mov x8, #64
    mov x0, #1
    adr x1, sb
    mov x2, lenb
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                    {
                        'order': 2,
                        'title': 'Fault Detector',
                        'description': 'Data centers must automatically detect when a server fails and stop sending it traffic. Servers send a heartbeat signal every few seconds. If the heartbeat stops, the server is marked as failed. You will implement heartbeat monitoring.',
                        'instructions': '''Write a C program that simulates fault detection through heartbeat monitoring.

Create a struct Server with:
  int id
  char name[20]
  int status     (1=ONLINE, 0=FAILED)
  int heartbeat  (countdown timer)

Initialize 5 servers with different heartbeat values:
  {1,"NODE-1",1,3}, {2,"NODE-2",1,1}, {3,"NODE-3",1,5}, {4,"NODE-4",1,2}, {5,"NODE-5",1,4}

Write check_heartbeats(Server servers[], int count):
  For each server: if status==1, decrement heartbeat. If heartbeat reaches 0, set status=0 and print "FAILURE DETECTED: [name]". Otherwise print "[name]: heartbeat=[value]".
  For failed servers print "[name]: OFFLINE"

Run check_heartbeats() for 5 cycles. Print "--- CYCLE [n] ---" before each.
After all cycles, print a summary of online vs failed servers.

This is how Kubernetes and distributed databases detect node failures.''',
                        'starter_code_c': '''#include <stdio.h>

struct Server {
    int id;
    char name[20];
    int status;
    int heartbeat;
};

void check_heartbeats(struct Server servers[], int count) {
    for (int i = 0; i < count; i++) {
        if (servers[i].status == 1) {
            servers[i].heartbeat--;
            if (servers[i].heartbeat <= 0) {
                servers[i].status = 0;
                printf("FAILURE DETECTED: %s\\n", servers[i].name);
            } else {
                printf("%s: heartbeat=%d\\n", servers[i].name, servers[i].heartbeat);
            }
        } else {
            printf("%s: OFFLINE\\n", servers[i].name);
        }
    }
}

int main() {
    struct Server servers[5] = {
        {1,"NODE-1",1,3},
        {2,"NODE-2",1,1},
        {3,"NODE-3",1,5},
        {4,"NODE-4",1,2},
        {5,"NODE-5",1,4}
    };

    for (int cycle = 1; cycle <= 5; cycle++) {
        printf("--- CYCLE %d ---\\n", cycle);
        check_heartbeats(servers, 5);
    }

    int online = 0, failed = 0;
    for (int i = 0; i < 5; i++) {
        if (servers[i].status) online++; else failed++;
    }
    printf("\\nSUMMARY: %d online, %d failed\\n", online, failed);
    return 0;
}''',
                        'starter_code_asm_x86': '''; Heartbeat monitor
section .data
    msg_ok db "NODE: ONLINE", 10
    len_ok equ $ - msg_ok
    msg_fail db "FAILURE DETECTED", 10
    len_fail equ $ - msg_fail

section .text
    global _start

_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, msg_ok
    mov rdx, len_ok
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, msg_fail
    mov rdx, len_fail
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 heartbeat
.section .data
msg: .ascii "HEARTBEAT CHECK COMPLETE\n"
len = . - msg

.section .text
.global _start

_start:
    mov x8, #64
    mov x0, #1
    adr x1, msg
    mov x2, len
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                ]
            },
            {
                'name': 'SUPERCOMPUTER',
                'slug': 'supercomputer',
                'description': 'Millions of CPU cores solving problems in parallel that would take a single PC years. Weather simulation, protein folding, nuclear physics. You write code that splits work across cores and combines results.',
                'category': 'classical',
                'unlock_order': 4,
                'challenges': [
                    {
                        'order': 1,
                        'title': 'Parallel Sum',
                        'description': 'Supercomputers split large datasets across thousands of cores. Each core sums its portion, then all results are combined. This is called a reduction operation. You will simulate parallel computation across 4 worker cores.',
                        'instructions': '''Write a C program that simulates parallel computation.

Create an array of 1000 integers where data[i] = i + 1 (values 1 to 1000).

Define NUM_WORKERS as 4.
Each worker gets an equal chunk: chunk_size = 1000 / NUM_WORKERS = 250.

Write compute_chunk(int arr[], int start, int end):
  Sum all values from arr[start] to arr[end-1]
  Print "WORKER [start/250]: summing [start] to [end-1] = [result]"
  Return the sum

In main:
  Initialize the array
  Call compute_chunk 4 times with the right start/end values
  Sum all 4 results into a total
  Print "TOTAL SUM: [value]"
  Verify: the sum of 1 to 1000 should be 500500.

This demonstrates why parallel computation is powerful — 4 cores do the work 4x faster than 1.''',
                        'starter_code_c': '''#include <stdio.h>

#define SIZE 1000
#define NUM_WORKERS 4

int data[SIZE];

long compute_chunk(int arr[], int start, int end, int worker_id) {
    long sum = 0;
    for (int i = start; i < end; i++) {
        sum += arr[i];
    }
    printf("WORKER %d: summing %d to %d = %ld\\n", worker_id, start, end-1, sum);
    return sum;
}

int main() {
    for (int i = 0; i < SIZE; i++) data[i] = i + 1;

    int chunk = SIZE / NUM_WORKERS;
    long results[NUM_WORKERS];

    for (int w = 0; w < NUM_WORKERS; w++) {
        results[w] = compute_chunk(data, w * chunk, (w+1) * chunk, w);
    }

    long total = 0;
    for (int w = 0; w < NUM_WORKERS; w++) total += results[w];

    printf("TOTAL SUM: %ld\\n", total);
    return 0;
}''',
                        'starter_code_asm_x86': '''; Parallel sum simulation
section .data
    msg db "PARALLEL COMPUTE COMPLETE", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; Simulate summing a range
    mov rax, 0          ; accumulator
    mov rcx, 1000       ; count

sum_loop:
    add rax, rcx
    dec rcx
    jnz sum_loop
    ; rax now contains sum of 1 to 1000 = 500500

    mov rax, 1
    mov rdi, 1
    mov rsi, msg
    mov rdx, len
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 parallel sum
.section .data
msg: .ascii "SUM COMPLETE\n"
len = . - msg

.section .text
.global _start

_start:
    mov x0, #0          // accumulator
    mov x1, #1000       // count
loop:
    add x0, x0, x1
    subs x1, x1, #1
    bne loop

    mov x8, #64
    mov x0, #1
    adr x1, msg
    mov x2, len
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                    {
                        'order': 2,
                        'title': 'Matrix Multiply',
                        'description': 'Matrix multiplication is the core operation in scientific computing, machine learning, and graphics. Supercomputers run billions of matrix multiplications per second. You will implement matrix multiplication and understand why it is computationally expensive.',
                        'instructions': '''Write a C program that multiplies two 4x4 matrices.

Matrix multiplication: C[i][j] = sum of A[i][k] * B[k][j] for all k.

Initialize matrix A as:
  {{1,2,3,4},{5,6,7,8},{9,10,11,12},{13,14,15,16}}

Initialize matrix B as the 4x4 identity matrix:
  {{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}}

Write multiply(int A[4][4], int B[4][4], int C[4][4]) using three nested loops.

Write print_matrix(int M[4][4]) that prints each row on one line.

In main:
  Print "MATRIX A:" and print A
  Print "MATRIX B (identity):" and print B
  Multiply A * B into C
  Print "RESULT (A * identity = A):" and print C

A matrix multiplied by the identity matrix equals itself — verify this.
Count how many multiplications your triple nested loop performs and print it.
For a 4x4 matrix: 4*4*4 = 64 multiplications.
For a 1000x1000 matrix: 1 billion multiplications — this is why supercomputers exist.''',
                        'starter_code_c': '''#include <stdio.h>

#define N 4

void multiply(int A[N][N], int B[N][N], int C[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            C[i][j] = 0;
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

void print_matrix(int M[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            printf("%4d", M[i][j]);
        }
        printf("\\n");
    }
}

int main() {
    int A[N][N] = {{1,2,3,4},{5,6,7,8},{9,10,11,12},{13,14,15,16}};
    int B[N][N] = {{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}};
    int C[N][N] = {0};

    printf("MATRIX A:\\n");
    print_matrix(A);
    printf("MATRIX B (identity):\\n");
    print_matrix(B);

    multiply(A, B, C);

    printf("RESULT:\\n");
    print_matrix(C);
    printf("Operations performed: %d\\n", N*N*N);
    return 0;
}''',
                        'starter_code_asm_x86': '''; Matrix multiply (simplified)
section .data
    msg db "MATRIX MULTIPLY COMPLETE", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; 4x4 identity multiply: result = input
    ; (full implementation requires significant register management)
    mov rax, 1
    mov rdi, 1
    mov rsi, msg
    mov rdx, len
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall''',
                        'starter_code_asm_arm': '''; ARM64 matrix multiply
.section .data
msg: .ascii "MATRIX COMPLETE\n"
len = . - msg

.section .text
.global _start

_start:
    mov x8, #64
    mov x0, #1
    adr x1, msg
    mov x2, len
    svc #0

    mov x8, #93
    mov x0, #0
    svc #0'''
                    },
                ]
            },
        ]

        for system_data in systems:
            challenges_data = system_data.pop('challenges')
            system, _ = HardwareSystem.objects.update_or_create(
                slug=system_data['slug'],
                defaults=system_data
            )
            self.stdout.write(f'  System: {system.name}')
            for ch in challenges_data:
                HardwareChallenge.objects.update_or_create(
                    system=system,
                    order=ch['order'],
                    defaults=ch
                )
                self.stdout.write(f'    Challenge: {ch["title"]}')

        self.stdout.write(self.style.SUCCESS('Hardware seeded successfully.'))
