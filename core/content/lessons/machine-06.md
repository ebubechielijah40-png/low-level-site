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
