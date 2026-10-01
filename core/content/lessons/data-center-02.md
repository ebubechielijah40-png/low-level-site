## What this component does
Electrical work in computing equipment largely becomes heat. A cooling plan must remove heat under expected load and account for airflow, redundancy, ambient conditions, and equipment limits. A nominal wattage is only one parameter; it cannot establish safe temperatures by itself.

## The virtual interface
Request an illustrative 6000 W load budget and 8000 W heat-removal budget. The numerical headroom is 2000 W, but this simple comparison is not a thermodynamic design or a real sensor reading. The model demonstrates representing related quantities, defining their units, and testing a stated configuration.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | power_watts | 6000 | Illustrative IT load estimate in watts |
| 0xF004 | cooling_watts | 8000 | Illustrative cooling-removal capacity |
| 0xF008 | enabled | 1 | 1 enables the model policy |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the cooling component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Lower cooling capacity below the load and describe the mismatch. Explain why neither an animated fan nor a passing register target proves rack inlet temperature remains safe. Identify the measurements a real control system would need.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
