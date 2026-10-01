# Exact execution contracts

The site's Run button executes a documented model. It never launches a submitted program as a host process, invokes a shell, or sends source to an external service. These contracts define the supported subset; they do not imply complete language-standard compliance.

## Shared bounds

- Source: 24,000 UTF-8 bytes; parser nesting: 60 bracket levels.
- Execution: 12,000 interpreter steps and a 1.5-second cooperative time budget.
- Console output: 16,000 characters; trace: first 200 records.
- C arrays: 1–1024 elements; total virtual-object allocation budget: 8192; call depth: 40.
- These are workload limits, not a hardened operating-system sandbox or cycle measurements. Parser work precedes cooperative checks. A public service additionally needs request concurrency limits, hard worker time/memory limits, and independent security review.
- Authenticated execution is limited to 60 requests per user with a process-local cache. The simple sliding expiry is not a distributed rate limiter; shared caching and atomic updates are necessary for multi-worker deployment.

## C

Source is parsed by pycparser. Supported statements include declarations, assignments, compounds, if/else, for, while, do/while, break, continue, and return. Supported expressions include integer constants, strings/characters for output, unary and binary integer operators, short-circuit logical operations, ternary expressions, casts in the model's types, function calls, array indexing, structure members, and pointers to virtual objects.

The model uses 32-bit int/unsigned int/pointers, 16-bit short, and 8-bit char. Signed 32-bit arithmetic overflow is reported; unsigned 32-bit arithmetic wraps. Integer division truncates toward zero. Array and pointer bounds are checked. Reads of uninitialised local objects and reads through pointers after the model object's lifetime ends are rejected. Globals are zero-initialised. Lexical local scopes and parameter frames do not expose a caller's unrelated local names.

This is not a complete C compiler/type checker. It excludes floating point, dynamic allocation, native address casts, full ABI layouts/padding, unions, native structure sizeof, function pointers, general preprocessor expansion, switch/goto, and most standard-library functions. Structure field access is modelled; general aggregate-by-value/native layout semantics are outside the contract. Type qualifiers are parsed but do not implement optimisation, atomics, or memory-ordering rules. `sizeof` supports the documented scalar and direct-array cases; it must not be used to infer a real target ABI.

Allowed headers are `stdio.h`, `stdint.h`, `stddef.h`, `stdbool.h`, and `limits.h`; they are recognised locally, never read from host include paths. Simple integer `#define NAME value` constants are supported. Fixed-width typedefs uint32_t, int32_t, uint8_t, size_t, and bool are provided by the model. Complete header APIs are not implied. Use explicit U-suffixed literals for unsigned intent.

Output functions: printf with `%d`, `%i`, `%u`, `%x`, `%X`, `%c`, literal `%s`, and `%%`, optionally simple integer width/zero padding; puts and putchar. There is no scanf or interactive stdin. Main must be callable with no arguments; falling off its end returns zero in this model. Nonzero return codes are reported in the result.

Virtual device API:

```c
mmio_write(0xF000, 512);
unsigned int value = mmio_read(0xF000);
```

Addresses must be four-byte aligned inside 0xF000–0xF0FC. Every execution has fresh virtual state. Each configuration lab separately defines register meanings and target values.

## RV32I assembly and machine code

Implemented integer instructions: ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND; ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI; LUI, AUIPC; LB, LH, LW, LBU, LHU; SB, SH, SW; BEQ, BNE, BLT, BGE, BLTU, BGEU; JAL, JALR; ECALL and EBREAK.

Pseudo instructions: LI, LA, MV, NOP, J, CALL, RET, BEQZ, BNEZ. Labels are resolved in two passes; LI can expand into two real instructions. Directives: .text, .data, .word, .byte, .global/.globl. RISC-V numeric and standard integer register aliases are supported. x0 is fixed zero. Initial sp/x2 is 0xE000. Instructions begin at zero, data at 0x2000, RAM is 64 KiB, and the virtual word-only MMIO window starts at 0xF000. Images have at most 8 KiB of instructions and 4 KiB of initial data.

Memory is little-endian. This model rejects misaligned halfword/word accesses and instruction targets outside the loaded image. It does not implement compressed instructions, multiplication/division extensions, privileged mode, CSRs, interrupt controllers, floating point, or an actual OS.

Machine-code input uses **one 32-bit word** per token, as eight hex digits or 32 binary digits. It does not accept arbitrary byte dumps. Encoding output provides the resulting little-endian byte image.

Teaching ECALL interface (a7/x17 chooses service; a0/x10 supplies argument): 1 prints a signed integer, 4 prints a zero-terminated virtual-memory string, 11 prints one character, 10 stops. Service zero and EBREAK also stop. This is expressly **not the Linux system-call ABI**.

## Rust subset

Supports fn, typed scalar parameters and integer return values, return and trailing expressions, let/let mut, i32/u32/model usize/bool, concrete array initialisers, indexing, if/else, while, integer for ranges, break/continue, scalar references, and a limited println! integer formatter. Mutability and local overlapping-borrow checks run before the bounded AST execution.

The checker conservatively retains a borrow until its lexical block ends. It rejects direct reads/writes of an owner while a mutable borrow is active, writes through shared references, and overlapping mutable/shared reference creation. It does not implement complete ownership/move analysis, non-lexical lifetimes, inference, traits, generics, String/Vec, reference parameters, concurrency, unsafe Rust, or the full native Rust type system. usize is simplified to the model's int width. Use rustc to validate real Rust programs; acceptance here is not a complete Rust safety claim.

## Verilog subset

One ANSI-style module; each input/output width is 1–4 bits; total input width is at most 8 bits. Each output has exactly one continuous assign. The simulator supports bounded combinational integer/bitwise expressions, comparisons, bit selection, and a conditional expression. Every input vector is evaluated. Output values are masked to the declared width. The first declared input occupies the least significant portion of the enumeration vector.

No sequential logic, clocks, always blocks, four-state X/Z values, delay/timing analysis, synthesis, FPGA bitstreams, or physical device programming. Native HDL sizing, signedness, and elaboration rules are broader than this teaching model.

## x86 boot subset

The assembler accepts bits 16, org 0x7c00, labels, db bytes/ASCII strings, MOV register/immediate and zero segment setup, register XOR, INT, LODSB, CMP AL/AX with immediate, JMP/CALL/RET, JE/JNE/JZ/JNZ, LOOP, PUSH/POP, INC/DEC, ADD/SUB AX with immediate, HLT, CLI/STI/CLD, and NOP. It pads to 510 bytes and adds 55 AA. Selected conventional padding/signature source directives are recognised.

The model loads exactly 512 bytes at 0x7C00, begins with zero segments and SP = 0x7C00, bounds its stack below that address, uses forward LODSB, and emulates BIOS INT 10h/AH=0Eh teletype output only. HLT ends a run. It is not a general PC emulator. An image with a valid signature can still contain unsupported instructions and be rejected at boot.

Saved images are private to their user. Imported sectors retain their bytes but have no reconstructed source. The editor displays an example for such imports; saving that source creates a different project. Native ELF/Multiboot kernels are a separate included build milestone and are not executed by the site.
