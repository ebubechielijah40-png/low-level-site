## Before the entanglement experiment

Read [two-qubit states](/learn/device/8/) and [Hadamard preparation](/hardware/quantum/). The basis order is `|q1 q0>` and the model starts in `|00>`. Mask bit zero requests H on q0; bit one requests controlled-X from q0 to q1 after H. The order is part of the contract, not a consequence of the numeric mask alone.

## Derive the joint transformation

H on q0 first creates `( |00> + |01> ) / sqrt(2)`. Controlled-X leaves 00 unchanged because q0=0 and maps 01 to 11 because q0=1 flips q1. The final state is `( |00> + |11> ) / sqrt(2)`, an ideal Bell state. Its probabilities are 00=0.5, 11=0.5, and 01=10=0.

Each individual qubit has a balanced zero/one marginal probability, but the joint basis outcomes match. The state cannot be factored into independent pure single-qubit states. Nevertheless, a classical mixture of correlated 00 and 11 outcomes can share this one basis probability table. The simulator knows the amplitudes it calculated; an experiment would need additional evidence to certify the claimed quantum state or entanglement.

## Gate order changes the experiment

Controlled-X applied alone to the initial 00 does nothing. If it occurs before H, the subsequent state is the first lab's 00/01 superposition rather than the Bell preparation. The fixed implemented sequence applies H then controlled-X, so mask three includes both in that order. A mask is an encoding for a defined protocol; it cannot define all possible circuit schedules.

## Try and compare beside the documentation

Run the matching reference and inspect gate_mask=3, qubits=2, shots=1024 and the probability dictionary. Change gate_mask to one; expect 00 and 01 probabilities one half each. Change it to two; expect 00=1 because controlled-X alone leaves the initial state unchanged. Change it to zero and recover that same initial probability state by a different requested operation sequence.

Changing shots affects the requested experiment count but not exact probabilities. Changing qubits does not extend the state space. A mask outside zero through three is unsupported and marked invalid. The site reports a mathematical model, not measured entanglement, remote QPU execution, gate fidelity, or physical cooling state.

To apply the logical experiment on real hardware you need its control API, supported gates and connectivity, calibrated mappings, timing, readout, and error characterization. Languages implement the request path; the physics and device contract establish what the request actually means. Keep that distinction when writing the project report or showing the conceptual component model.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 3); // gate_mask
    mmio_write(0xF004, 2); // qubits
    mmio_write(0xF008, 1024); // shots
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,3
sw t1,0(t0)
li t1,2
sw t1,4(t0)
li t1,1024
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

## What this component does
A controlled-X gate flips its target when the control basis value is one. Applied after H on qubit zero to the initial state |00>, it creates equal amplitudes for |00> and |11>. Measurement gives correlated equal bits with probabilities one half each. Correlation here is a consequence of a particular joint quantum state, not evidence of controllable faster-than-light communication.

## The virtual interface
Set gate mask to three: bit zero selects H and bit one selects the following controlled-X. The exact state calculation reports P(00)=0.5, P(11)=0.5, and zero for 01 and 10. The model has no noise, decoherence, calibration, or physical timing. Its component view illustrates a possible control assembly rather than specifying a buildable quantum computer.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | gate_mask | 3 | H on q0 followed by controlled-X from q0 to q1 |
| 0xF004 | qubits | 2 | Two-qubit mathematical model |
| 0xF008 | shots | 1024 | Requested count; probabilities are exact, not sampled |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the control component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Use gate mask one and compare the probability table with the previous lab. Use gate mask zero and recover the initial basis state. Explain which outcomes changed because of the controlled-X and which assumptions remain idealised.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
