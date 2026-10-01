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
