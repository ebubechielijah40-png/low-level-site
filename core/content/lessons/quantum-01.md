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
