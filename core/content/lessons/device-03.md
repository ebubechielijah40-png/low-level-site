## Before you choose timing parameters

Be comfortable with [integer arithmetic](/learn/c/2/) and the [controller lifecycle](/learn/device/2/). Know the units: hertz is cycles per second, a nanosecond is one billionth of a second, watts measure energy transfer per second, and bytes measure storage. A numeric field is meaningless until its unit and interpretation are specified.

## Digital state rests on a physical system

The Boolean model treats a wire as zero or one. Physical circuits use voltage ranges, transition times, and noise margins. Signals need time to propagate and settle. A clocked storage element samples under setup and hold requirements around a clock edge. Sampling a changing asynchronous signal can produce metastability; changing a register value in C cannot remove that physical constraint.

A controller also depends on power rails, reset sequencing, reference clocks, and supported operating points. A requested frequency must be supported by the clock tree and device. Faster switching can change power and timing margins. A profile containing `2400` therefore records a request; it does not establish that a CPU will operate correctly at 2400 MHz.

## Derive a timing budget before choosing cycles

For a simplified 200 MHz controller clock, one cycle lasts 5 ns because one second divided by 200 million is five billionths of a second. If a hypothetical device contract requires at least 13 ns between two events, two cycles give only 10 ns and are insufficient. Three cycles give 15 ns and satisfy this one constraint. The required count is the ceiling of required time divided by cycle time.

Use integer ceiling division `(required + cycle - 1) / cycle` for these small positive inputs. The numerator must not overflow; production code should bound the values or use a suitably wide calculation. Actual memory-controller encodings can use offsets or multiples, so a computed count must still be translated using the register manual.

## Try this in the terminal beside the documentation

```c run:reference
#include <stdio.h>
int main(void) {
    int cycle_ns = 5;
    int required_ns = 13;
    int cycles = (required_ns + cycle_ns - 1) / cycle_ns;
    int supplied_ns = cycles * cycle_ns;
    int load_watts = 6000;
    int cooling_watts = 8000;
    printf("cycles=%d supplied_ns=%d headroom_watts=%d\n",
           cycles, supplied_ns, cooling_watts - load_watts);
    return 0;
}
```

Expect `cycles=3 supplied_ns=15 headroom_watts=2000`. The clock calculation and the heat-removal calculation describe different constraints. A positive heat-removal difference does not establish a safe junction temperature; thermal resistance, airflow distribution, inlet conditions, transients, and sensor placement also matter.

## RAM adds retention and training requirements

DRAM stores charge that must be refreshed. The controller schedules commands according to part-specific timing and refresh requirements. Initialization and training establish conditions for reliable signaling. Capacity comes from installed devices and address organization; it is not created by writing a capacity field. Different memory technologies have different procedures, and controller/firmware support matters as much as source syntax.

Our RAM lab represents a capacity request and flags. It has no voltage, refresh events, command timing, training, or error-injection model. The useful result is learning how a documented profile is encoded and checked. To configure actual RAM you additionally need the controller manual, compatible module information, firmware-supported settings, and measured training/stability/error feedback.

## Practice: make the constraint fail deliberately

Change `cycles` to `required_ns / cycle_ns`; predict 2 and 10 ns. Explain why truncation violated the minimum. Test required times 10, 11, and 15 ns with the original ceiling formula; expect counts 2, 3, and 3. Lower cooling capacity to 5000 W and obtain -1000 W of headroom. Describe the observations needed before claiming a real system is thermally stable. Every example here is budget arithmetic, not a simulated oscilloscope or a prescribed hardware setting.
