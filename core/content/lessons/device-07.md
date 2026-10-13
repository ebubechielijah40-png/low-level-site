## Before you describe a clocked controller

Know [Boolean gates](/learn/verilog/1/) and [multiplexer selection](/learn/verilog/3/) when you take the hardware-design branch. You can do the following software state experiment after [C branches](/learn/c/3/). A digital controller needs both combinational decisions and stored state. The site's Verilog runner handles only the first; a C transition table lets us study the second without falsely labeling it sequential HDL simulation.

## Output depends on state as well as input

A combinational circuit's output is a function of current inputs. A sequential system also contains memory: current state and current inputs determine the next state. Storage elements retain information between clock edges. A finite-state machine gives names to relevant states and specifies allowed transitions.

Consider a controller with states idle = 0, busy = 1, done = 2. A start event in idle leads to busy. A completion event in busy leads to done. An acknowledgement in done leads to idle. A completion event in idle should not masquerade as a completed new operation. That transition rule is the actual protocol; the three names alone are only vocabulary.

## Try this in the terminal beside the documentation

```c run:reference
#include <stdio.h>
int next_state(int state, int start, int complete, int ack) {
    if (state == 0 && start) {
        return 1;
    }
    if (state == 1 && complete) {
        return 2;
    }
    if (state == 2 && ack) {
        return 0;
    }
    return state;
}
int main(void) {
    int state = 0;
    state = next_state(state, 1, 0, 0);
    printf("start=%d ", state);
    state = next_state(state, 0, 1, 0);
    printf("complete=%d ", state);
    state = next_state(state, 0, 0, 1);
    printf("ack=%d\n", state);
    return 0;
}
```

Expect `start=1 complete=2 ack=0`. Each function call computes one modeled transition. There is no measured clock frequency or elapsed cycle duration here. `state` is an ordinary C object; assigning the returned value represents the update that a clocked state register would perform under a chosen hardware design.

## Hardware requires a sampling discipline

A real clocked HDL implementation separates current-state storage from next-state combinational logic. Nonblocking assignment is commonly used for clocked register updates so statements describe simultaneous edge-triggered behavior under the HDL's scheduling rules. Blocking and nonblocking assignments are not interchangeable punctuation. Reset behavior, clock enable, and illegal-state recovery must be designed explicitly.

An external event can arrive between clock edges. Clock-domain crossing needs a design appropriate to the information being transferred. A single stable control bit can use a synchronizer; a multi-bit payload often needs a handshake or asynchronous FIFO so independently sampled bits are not combined into an invalid word. Simulation without timing violations does not prove physical metastability behavior.

The site's combinational truth tables do not model clocks, flip-flops, reset edges, nonblocking assignment scheduling, propagation delay, or synthesis. Do not paste an `always` block into that runner and expect it to teach these mechanisms. This lesson states the next necessary knowledge for building a controller while keeping the runnable experiment inside the supported environment.

## Practice: derive transitions before implementing them

Call `next_state(0, 0, 1, 0)` and predict zero: a stray completion is ignored in idle. Test simultaneous start and completion in idle and explain why the current rule selects busy. Add an error state and a timeout event, then specify which events can recover from it. Draw a transition table with current state, inputs, next state, and emitted action. Explain which part would be a register, which part combinational logic, and what additional tool evidence is needed for a clocked HDL implementation.
