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
