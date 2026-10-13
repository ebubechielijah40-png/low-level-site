## Before configuring the ideal Hadamard model

Read [quantum-state foundations](/learn/device/8/) and [register contracts](/learn/device/1/). You must distinguish an amplitude from a probability, a gate from a measurement, and a logical gate request from a calibrated physical control. Machine code and C alone do not teach those distinctions.

## Derive the exact displayed state

The model starts in `|00>` and uses basis labels `|q1 q0>`. Gate mask bit zero requests a Hadamard on q0. With mask one, the state becomes `( |00> + |01> ) / sqrt(2)`. Each surviving amplitude has squared magnitude one half. Thus the probabilities are 00=0.5, 01=0.5, 10=0, 11=0, summing to one.

A Hadamard is a unitary state transformation, not a random bit generator that immediately chooses an outcome. The probabilities describe a later specified basis measurement. Relative phase matters for later interference, even when a particular immediate probability table cannot reveal it. Our implemented gate set and initial state are narrow enough that the displayed values are real; general quantum amplitudes can be complex.

## Understand every profile field

The target register mask is one, qubits is two, and requested shots is 1024. The simulator always computes its supported two-qubit state and exact probabilities; it does not allocate a larger system from the qubits number or sample the shots. Under ideal probabilities, 1024 shots would have expected counts of 512 for each surviving outcome, but actual sampled counts would fluctuate.

The third field is a shot-count request, not an enable Boolean. A zero request is an incomplete profile. The site labels invalid qubit counts, unsupported masks, and zero shots as invalid profiles rather than presenting them as a configured physical system. The mathematical probability calculation is useful only under its declared contract.

## Try the request beside the documentation

Run the reference and inspect the three MMIO fields and the probability dictionary in **State / component telemetry**. Change shots to 2048; the exact probabilities remain unchanged while the 1024-shot task target fails. Change mask to zero and observe 00=1. Change qubits to three and observe an invalid-profile note, not a claim that three qubits were simulated.

Actual quantum hardware configuration needs its supported physical architecture, gate/pulse calibration, timing, connectivity, measurement/readout characterization, and noise/error data. The conceptual cryogenic geometry illustrates one technology family; it is not a buildable universal QPU layout. The site has no physical device connection, pulse engine, decoherence, or calibration. The second lab adds a controlled operation and derives the resulting joint state.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 1); // gate_mask
    mmio_write(0xF004, 2); // qubits
    mmio_write(0xF008, 1024); // shots
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,1
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
A qubit state uses complex amplitudes. Probabilities are squared amplitude magnitudes, so a superposition is not a classical register containing both zero and one. A Hadamard operation maps a basis-zero qubit to equal amplitudes for zero and one, giving half probability for each outcome when measured in that basis.

## The virtual interface
This lab starts in |00>, applies H to qubit zero when gate-mask bit zero is set, and reports exact basis probabilities. Under the model qubit zero is the rightmost displayed bit, giving P(00)=0.5 and P(01)=0.5. The requested shot count is metadata, not a claim that random hardware measurements occurred. Cryostat geometry is conceptual; no temperatures or physical pulse controls are simulated.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | gate_mask | 1 | Bit zero requests H on qubit zero |
| 0xF004 | qubits | 2 | Two-qubit mathematical model |
| 0xF008 | shots | 1024 | Requested count; probabilities are exact, not sampled |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the qpu component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Clear gate-mask bit zero and predict P(00)=1. Explain why the model describes a mathematical state transformation without configuring superconducting materials, a real QPU, or a refrigeration system.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
