## Before a loop: state the valid input domain

Review [machine branches](/learn/machine/6/). Labels relieve you of splitting branch immediate fields manually; they do not remove the need for a correct control-flow argument. An instruction target is a location, while the value in your counter is an algorithm variable. Do not mix those two roles because both are integers.

The reference visits positive integers from one to five. t0 holds the current term, t1 the exclusive limit six, and t2 the accumulated sum. At the loop's entry, sum equals the sum of positive terms below the counter. ADD includes the current counter; increment advances to the next, preserving that relationship. BLT then checks whether there is another permitted term.

The source uses a body-first structure after initialization. For the stated five-term input it is correct. If you generalize by deriving the limit from an arbitrary n, you need an entry test for n=0, and a bound that prevents overflow. A reference passing one fixed n is not proof of a generalized function.

## Try a zero-safe loop beside the documentation

```assembly run:zero-loop
li t0,0
li t1,0
beq t0,zero,done
again:
add t1,t1,t0
addi t0,t0,-1
bne t0,zero,again
done:
mv a0,t1
li a7,1
ecall
li a7,10
ecall
```

Expect zero. The first branch skips the entire body when n=0. Change t0's initial value to five and expect 15; the new sum visits terms downward. The two algorithms have different intermediate states but the same final answer over the stated nonnegative domain.

## A correctness argument has two parts

An invariant connects current state to the work completed or remaining. A decreasing bound establishes termination. In the countdown, after k iterations the counter is n-k, and the sum contains the k largest positive terms through n. The remaining counter decreases to zero. A negative input violates that argument: repeated decrement moves away from zero under the intended signed reading and eventually hits a model limit or wrapping behavior.

Use **Trace** to inspect the last taken and first not-taken branches. Their PC decisions explain where execution goes. A missing update, a reversed comparison, and a wrong label are distinct causes, even if all produce repeated execution. Predict each mutation before running; the model's step budget bounds the experiment without repairing any of those faults.

## Try this in the terminal beside the documentation

The following is a complete program for this page's engine. Load it into the terminal beside this explanation, predict the result, then press Run. Open **State** for final values, **Trace** for recorded execution, and **Encoding** for emitted bytes when this engine supplies them.

```assembly run:reference
li t0,1
li t1,6
li t2,0
loop:
add t2,t2,t0
addi t0,t0,1
blt t0,t1,loop
mv a0,t2
li a7,1
ecall
li a7,10
ecall
```

Expected result: Console: `15`.

The fixed reference checks describe this program. A deliberate mutation can run correctly while failing those original checks; compare it with your new prediction. **Restore draft** restores the source present before the most recent example load.

## A label marks a location
A label such as `loop:` names the current instruction address. A branch references that name, and the assembler calculates the relative offset. The label occupies no bytes. If an earlier pseudo instruction expands to two words instead of one, the assembler updates the offset accordingly. This is one important source of reliability over hand-encoding control flow.

A branch has a comparison and a target. `bne t0,zero,loop` branches if the two registers differ. It does not decrement t0, update a sum, or decide what the counter means. Those are separate instructions. A branch can therefore be perfectly encoded and still implement the wrong stopping rule.

## State an invariant
The example accumulates integers from 1 through 5 in ascending order. Initially the counter is 1, the limit is 6, and the sum is zero. At the top of each iteration, the sum contains all positive integers smaller than the counter. This is a loop invariant: a statement that holds before and after each iteration when stated at the same point.

The loop adds the counter, then increments it. After the increment, the sum again contains all positive integers smaller than the new counter. The branch continues while the counter is smaller than the limit. When it stops, the counter is 6, so the sum contains 1 through 5. The invariant explains both correctness and the off-by-one choice of limit.

## Termination is a separate claim
An invariant can describe a loop that never ends. To establish termination, identify a quantity that decreases toward a bound. Here limit minus counter decreases by one every iteration and eventually reaches zero. A bound in the runner stops a faulty loop from consuming unlimited resources, but it does not establish that your algorithm terminates normally.

Run the example and find the sequence of ADD writes to t2. Change BLT to BGE and predict whether the loop runs once, repeatedly, or stops. Move the increment before the addition and compute the resulting sum. These controlled changes reveal the ordering assumptions in your original proof.

## Practice
Write a countdown loop that computes the same answer. State its invariant in terms of the remaining counter and the accumulated sum. Test n = 1, n = 5, and n = 0; the last case requires choosing an entry condition carefully. Explain why copying the same loop body without considering zero would be an incomplete test strategy.
