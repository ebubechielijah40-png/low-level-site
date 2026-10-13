## Before control flow: reason from the current PC

You need [instruction fields](/learn/machine/2/) and [register updates](/learn/machine/4/). A branch reads register values and decides the address of the next instruction. It does not implement a high-level loop condition beyond that comparison. The programmer is responsible for making state progress toward a stopping condition.

In this program the ADD is at PC 8, the decrement at PC 12, and BNE at PC 16. The branch targets PC 8. Its signed relative byte offset is therefore `8-16=-8`, measured from the branch's address. Treating it as relative to PC 20 would target the wrong word.

## Decode a scattered branch field

For B-type decoding, immediate bit 12 comes from word bit 31, bit 11 from word bit 7, bits 10-5 from word bits 30-25, and bits 4-1 from word bits 11-8. Bit zero is implicit zero. Reassemble those positions and sign-extend the resulting thirteen-bit value. For `fe029ce3`, rs1 is x5, rs2 is x0, funct3=1 is BNE, and the offset is -8. That derivation explains the return to ADD.

The loop starts with counter 5 and sum 0. After k completed iterations, the counter is `5-k` and the sum contains the k terms from 5 downward. The counter decreases by one each iteration; for the chosen positive input it reaches zero after five. The not-taken final branch leads to the output setup rather than another iteration.

| Completed iteration | Counter | Sum |
|---|---|---|
| 0 | 5 | 0 |
| 1 | 4 | 5 |
| 2 | 3 | 9 |
| 3 | 2 | 12 |
| 4 | 1 | 14 |
| 5 | 0 | 15 |

## Output adds a second contract

The later `mv` equivalent copies the sum into a0/x10, and the program selects a7/x17=1 for integer printing. ECALL invokes the teaching environment, which formats 15. Selecting a7=10 and invoking ECALL again ends the run. These service numbers are not implied by the RV32I encoding and are not Linux's system-call ABI.

Try the reference beside the documentation and find each ADD destination write in **Trace**. Then change the first immediate from five to six and predict 21. For a zero initial counter, this body-first arrangement does not skip the body: decrement produces -1 and the loop continues until a budget error. Zero therefore exposes a missing entry guard. State the valid input domain before declaring a loop correct.

Your proof needs both a maintained relationship and a termination argument. An interpreter limit supplies neither; it only bounds a faulty experiment's resource use. The next track uses labels to relieve encoding work while retaining this exact state-and-next-PC reasoning.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```machine run:reference
00500293
00000313
00530333
fff28293
fe029ce3
00030513
00100893
00000073
00a00893
00000073
```

Expected result: Console: `15`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## A loop does not need a loop keyword
Sequential execution sets PC to the current address plus four. A branch can replace that next address with a target computed from the current PC and a signed offset. A loop is a sequence that sometimes branches back to earlier instructions. The processor has no need to know the word "loop" or the author's intention.

RV32I branch offsets are byte offsets relative to the branch instruction's own address. They are not relative to the next instruction. The immediate bits are scattered across the B-type encoding, and the low offset bit is implicit zero. This subset requires four-byte aligned targets because compressed two-byte instructions are not implemented.

## Build the sum 1 + 2 + 3 + 4 + 5
The program starts a counter at 5 and a sum at zero. Each iteration adds the counter to the sum, subtracts one from the counter, and branches back while the counter is not zero. The sum takes the values 5, 9, 12, 14, and 15. The counter takes 4, 3, 2, 1, and 0 after decrement. Every update has a particular instruction responsible for it.

The expected mathematical result is n(n+1)/2 with n = 5, so 5 × 6 / 2 = 15. Derive it by pairing the first and last terms: every pair has sum n+1. The closed-form expression is useful as an independent check of a loop implementation; it does not rely on the loop's own logic.

## Output needs an environment
An ECALL transfers control to an execution environment. The meaning of the service number is an environment convention, not an instruction-set rule. This teaching runner uses x17, also called a7: service 1 prints the signed integer in x10/a0, service 11 prints a character, service 4 prints a zero-terminated memory string, and service 10 halts. These are not Linux system-call numbers.

Inspect the trace and find the final branch that is not taken. Then find the instructions copying the sum to the output argument and selecting the output service. The program prints 15 and stops. With n = 6, it should print 21; change the initial instruction's immediate field and verify that prediction.

## Exercise and failure experiment
Move the decrement before the addition and predict how the sum changes. Remove the decrement and observe the execution-limit error. Explain why a bound is a property of the teaching environment, not a correction to the faulty program. Your final task is to explain the whole loop using only registers, arithmetic, and next-PC decisions.
