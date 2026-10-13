## Before configuring the thermal profile

Review [physical timing and budgets](/learn/device/3/) and [configuration feedback](/learn/device/2/). Power is an energy-transfer rate; temperature is a state affected by heat generation, thermal resistance, heat capacity, ambient conditions, and the removal path. Subtracting two watt values does not directly compute a processor or rack temperature.

## Calculate the target's limited consequence

The target writes a load estimate of 6000 W and heat-removal capacity of 8000 W. The derived headroom is 2000 W. Relative to the 6000 W load, that is about one third of the load. It is a steady budget comparison under given assumptions, not proof of uniform airflow, sufficient local heat transfer, or safe temperatures during a transient.

For an airflow path, required heat removal can be related to mass flow, specific heat, and air-temperature change. A thermal-resistance model can relate dissipated power to temperature rise under its assumed conditions. Neither is implemented by this three-register profile, and neither supplies accurate parameters automatically. Fans, liquid loops, heat exchangers, and room cooling operate at different points in the overall heat path.

## Try the arithmetic beside the guide

```c run:thermal-budget
#include <stdio.h>
int main(void) {
    int load_watts = 6000;
    int cooling_watts = 8000;
    int headroom = cooling_watts - load_watts;
    int budget_satisfied = headroom >= 0;
    printf("headroom_watts=%d budget_satisfied=%d\n", headroom, budget_satisfied);
    return 0;
}
```

Expect `headroom_watts=2000 budget_satisfied=1`. Change cooling to 5000 and predict -1000 and zero. The program does not write MMIO targets, so the lab's fixed configuration checks remain unsatisfied during this arithmetic experiment.

## A control loop needs measurements and a response

Real thermal configuration needs the system topology, rated operating limits, actual inlet/outlet or device measurements, sensor quality, response delays, fan/pump controls, hysteresis or control policy, and a response to sensor or cooling failure. A delayed or wrong sensor can defeat a superficially reasonable threshold. Workload reduction and emergency shutdown are policy decisions under the real platform contract.

Run the MMIO reference below and inspect telemetry `headroom_watts=2000`. Reducing cooling to 5000 should report -1000. The site computes that difference from the actual writes; it does not simulate air, fluid, thermal mass, temperature, or real sensors. A rendered cooling component does not extend those capabilities. State which budget passed and what still needs measured evidence before calling an actual data-centre configuration adequate.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 6000); // power_watts
    mmio_write(0xF004, 8000); // cooling_watts
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,6000
sw t1,0(t0)
li t1,8000
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

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
