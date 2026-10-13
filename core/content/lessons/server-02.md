## Before configuring the network profile

Review [byte protocols and MTU](/learn/device/5/), [buffer ownership](/learn/device/4/), and [resource limits](/learn/device/6/). A network interface transmits frames. IP packages datagrams across networks, transport protocols add their own semantics, and applications define messages. A software connection count is not the number of frames a NIC can physically transmit at once.

## Derive a payload budget under explicit assumptions

The target asks for MTU 1500 bytes, capacity for thirty-two connections, and enabled one. For IPv4 without options and TCP without options, subtract twenty bytes for each header from this IP MTU to obtain 1460 bytes. Extra options, encapsulation, a smaller path MTU, or another protocol change the calculation. Link-layer headers are outside that IP-packet MTU calculation.

```c run:network-budget
#include <stdio.h>
int main(void) {
    int mtu = 1500;
    int ip_header = 20;
    int tcp_header = 20;
    int payload = mtu - ip_header - tcp_header;
    int connections = 32;
    int buffer_bytes = 4096;
    printf("payload=%d connection_buffer_bytes=%d\n",
           payload, connections * buffer_bytes);
    return 0;
}
```

Try this in the terminal beside the documentation. Expect `payload=1460 connection_buffer_bytes=131072`. It is a calculation, so it intentionally does not satisfy the lab's MMIO profile checks. The connection-buffer product omits other per-connection state and kernel overhead; it is not a total memory measurement.

## A real interface needs a path and policy

Identify the supported device/driver, link state, addressing, routes, protocol configuration, MTU compatibility, buffers, ownership, offloads, and admission limits. A correct local MTU request does not prove an entire path accepts packets of that size. A connection capacity does not open thirty-two live connections; application and transport state must exist.

The site's reference writes MTU, connection capacity, and enable fields to plain virtual registers. It does not create sockets, send frames, resolve addresses, route packets, or model congestion. Component telemetry reflects this profile, not observed link traffic.

Run the reference and compare the MMIO values 1500, 32, 1. Change MTU to 1400; the generic code still executes, while the fixed target fails and the arithmetic payload budget would be 1360 under the same header assumptions. Change connections to sixty-four and derive the doubled stated buffer requirement. Explain what packet, resource, and workload observations would be required before claiming that either setting improves network performance.

## Try this in the terminal beside the documentation

Read the prerequisite explanation and register table before running. These two complete reference programs produce the same target MMIO values. Use the language switch above the workspace to select C or RV32I assembly, load the matching example, then press Run. Inspect **State / mmio** and the component telemetry.

```c run:reference
#include <stdio.h>
int main(void) {
    mmio_write(0xF000, 1500); // mtu_bytes
    mmio_write(0xF004, 32); // connections
    mmio_write(0xF008, 1); // enabled
    printf("Configuration written. Inspect MMIO and test checks.\n");
    return 0;
}
```

```assembly run:reference
lui t0,15
li t1,1500
sw t1,0(t0)
li t1,32
sw t1,4(t0)
li t1,1
sw t1,8(t0)
li a7,10
ecall
```

Both references should pass all three address targets in the table. The starter intentionally misses one target. Passing records the configured **virtual profile**; use the guided mutations below to distinguish encoding, domain constraints and measured physical behavior. Each run starts with fresh register state.

## What this component does
A network interface moves frames while protocol stacks interpret them and applications handle messages. An MTU is a size boundary for a particular link or interface, not a guarantee that a larger end-to-end message fits in one packet. Connection limits belong to resource policy above the physical wire.

## The virtual interface
Set the virtual interface MTU to 1500, connection capacity to thirty-two, and enabled state. This combines selected policy settings into a documented teaching interface. It does not configure your operating system network adapter or exchange packets. Real changes would require the platform network APIs, privileges, route and link context, and careful feedback.

This lab uses a separate three-register contract for the selected configuration. Each register is a 32-bit word, starts at zero for each run, and accepts aligned word writes. The same address can have a different documented meaning in another lab; every run gets its own device state. These are teaching registers, not a vendor's real memory map.

| Address | Setting | Target | Unit and meaning |
|---|---|---|---|
| 0xF000 | mtu_bytes | 1500 | Illustrative maximum transmission unit |
| 0xF004 | connections | 32 | Virtual connection capacity |
| 0xF008 | enabled | 1 | 1 enables the interface profile |

## Configure and test
The starter has one setting deliberately at zero. Read the target table and fix the configuration. Select the network component in the model, then run C or switch to RV32I assembly. C uses mmio_write; assembly uses SW through a base register. Both should leave exactly the same final register values. The server checks the actual recorded state and only records completion when every target passes.

The component highlight and telemetry follow the run's values. They are visual evidence of this simulation's state, not a test of physical electrical behaviour. A successful write differs from a valid configuration; target checks establish the latter for the stated model. There is no prerequisite lock.

## Failure experiment
Use an MTU of one and explain why a writable integer is not enough to establish a usable real policy. Describe how a connection limit protects bounded resources but can also reject valid demand under load.

Change one value at a time, predict which check will fail, and use MMIO to identify the corresponding address. Also test an unaligned address and explain why it fails before target comparison. A real configuration tool would additionally need permissions, a supported device, documented capabilities, acknowledgement, rollback, and measured feedback. This exercise isolates the interface reasoning so those future layers have a clear foundation.
