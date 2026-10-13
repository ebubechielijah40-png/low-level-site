## Before you configure the quantum demonstration

Understand [bit masks](/learn/c/2/) and the difference between [requested state and verified behavior](/learn/device/2/). Quantum configuration additionally needs a mathematical state model. Learning machine code does not establish amplitude, measurement, entanglement, noise, or physical calibration knowledge. This page supplies the mathematics needed for the site's two ideal gate experiments, not a complete QPU engineering course.

## A state contains amplitudes, not classical probability switches

For one qubit, a pure state is `alpha|0> + beta|1>`, with complex amplitudes satisfying `|alpha|^2 + |beta|^2 = 1`. A basis measurement gives probabilities equal to these squared magnitudes. A relative phase can affect later interference even when the immediate measurement probabilities are unchanged, so a probability list alone is not the full quantum state.

For two qubits, our basis order is `|q1 q0>`: `00`, `01`, `10`, `11`. Initially only the amplitude of `00` is one. A Hadamard on q0 gives `( |00> + |01> ) / sqrt(2)`. Controlled-X with q0 as control and q1 as target then maps `01` to `11`, producing `( |00> + |11> ) / sqrt(2)`. The probability is one half for each listed surviving outcome.

The Bell state cannot be written as a product of independent single-qubit states. Both individual measurements are balanced, but the joint outcomes are correlated in this basis. Classical correlated data can also produce matching measurement counts, so this one displayed probability table alone is not an experimental certification of quantum entanglement.

## Try this in the terminal beside the documentation

This integer experiment calculates expected counts for the stated probability model. It neither stores amplitudes nor samples a quantum state.

```c run:reference
#include <stdio.h>
int main(void) {
    unsigned int gate_mask = 3U;
    int shots = 1024;
    int hadamard = (gate_mask & 1U) != 0U;
    int controlled_x = (gate_mask & 2U) != 0U;
    int expected_00 = shots;
    int expected_01 = 0;
    int expected_11 = 0;
    if (hadamard) {
        expected_00 = shots / 2;
        if (controlled_x) {
            expected_11 = shots / 2;
        } else {
            expected_01 = shots / 2;
        }
    }
    printf("expected_00=%d expected_01=%d expected_11=%d\n",
           expected_00, expected_01, expected_11);
    return 0;
}
```

Expect `expected_00=512 expected_01=0 expected_11=512`. These are expectations for 1024 ideal shots under mask three, not an observed count. A sampled experiment would fluctuate. For an odd shot count this integer calculation truncates; real mathematical expectations need not be integers. The actual hardware-page probability model uses amplitudes and reports probabilities without sampling shots.

## Logical gates and physical controls are different layers

A gate request describes an ideal transformation. A physical QPU needs a supported architecture, calibrated control parameters, measurement readout, and error characterization. Pulse schedules and physical conditions are platform specific. Some implementations use cryogenic superconducting circuits; others use different physical systems. The conceptual model view is not a blueprint or a device controller.

The site accepts a two-qubit teaching profile, masks 0 through 3, and a requested shot count. Its amplitude calculation applies H first and controlled-X second when selected. Changing shots does not change the returned exact probabilities. Changing the qubit-count field does not grow the simulator into a larger Hilbert space. Invalid profiles are labeled explicitly rather than presented as a configured physical QPU.

## Practice: make the gate order meaningful

Run mask one and expect `expected_01=512` instead of `expected_11=512`. Run mask zero and expect 1024 for `00`. Explain why controlled-X alone leaves the initial `00` unchanged. Derive why applying controlled-X before H would give a different result from the Bell preparation. Then open the quantum hardware guides and compare their returned probabilities with this derivation; distinguish those ideal results from calibration and experimental evidence.
