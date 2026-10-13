## Before you configure storage or networking

Understand [byte order](/learn/machine/3/), [arrays and lengths](/learn/c/4/), and [data contracts](/learn/c/7/). A memory buffer is an object with a length. A block device presents logical blocks. A network interface transfers frames, while IP and transport protocols define other units. Similar words such as packet, frame, message, block, and buffer do not describe interchangeable boundaries.

## Representation crosses an interface

Suppose a protocol defines a two-byte unsigned field in big-endian order. Value 4660 is hexadecimal `0x1234`. Byte zero is `0x12`, byte one is `0x34`, and decoding reconstructs `(first << 8) | second`. The CPU's native byte order does not change that external contract. A raw C structure is unsuitable as a portable wire format because widths, padding, and byte order must all be explicit.

Every received field also needs a length check before access. A two-byte field cannot be decoded from a one-byte buffer merely because the intended value is small. Native C bounds are an obligation of the caller; the teaching runner diagnoses object bounds to make the mistake observable.

## Try this in the terminal beside the documentation

```c run:reference
#include <stdio.h>
int main(void) {
    unsigned int value = 4660U;
    unsigned int high = (value >> 8) & 255U;
    unsigned int low = value & 255U;
    unsigned int decoded = (high << 8) | low;
    int bytes = 1536;
    int block_bytes = 512;
    int blocks = (bytes + block_bytes - 1) / block_bytes;
    int mtu = 1500;
    int ip_header = 20;
    int transport_header = 20;
    printf("high=%u low=%u decoded=%u blocks=%d payload=%d\n",
           high, low, decoded, blocks, mtu - ip_header - transport_header);
    return 0;
}
```

Expect `high=18 low=52 decoded=4660 blocks=3 payload=1460`. These are arithmetic consequences under declared assumptions. The payload budget assumes IPv4 and TCP headers without options and no additional encapsulation in the chosen IP MTU. It is not the Ethernet frame size or a universal maximum application message.

## Block addresses need multiplication and bounds

With 512-byte logical blocks, logical block number 3 starts at byte offset 1536. Block number and byte offset use different units. A 1537-byte payload needs four blocks under the ceiling calculation; padding, allocation policy, and metadata are separate issues. Devices can expose other block sizes. Queue depth counts requests, not bytes or a guaranteed throughput improvement.

A real storage driver must learn capacity, logical/physical block sizes, command format, completion status, transfer buffers, ordering, and flush/durability semantics. A completed write can still be in volatile device cache; durable persistence needs the device's specified operation and failure assumptions. Our profile lab does not write a filesystem or model persistent media.

## A network configuration needs a stack and a path

An interface's MTU is one constraint; the path may have a smaller supported size. Addresses, link state, routing, transport, buffering, and congestion behavior determine communication. A connection limit belongs to a software admission policy, not simply a NIC's raw register. Lowering it can protect resources while refusing more clients.

The site's three-register profile stores an MTU request, connection capacity, and enable flag. It does not send frames, resolve addresses, route packets, create sockets, or measure a physical link. C remains useful for explaining the encoding and validation; the missing knowledge is the protocol and system boundary.

## Practice: test each unit independently

Change bytes to 1537 and expect four blocks. Decode swapped high/low bytes and obtain 13330, a valid integer with the wrong external meaning. Add four bytes of header overhead and derive the revised payload budget. Explain why changing a queue depth cannot prove persistence or packet delivery. Before writing a storage or network setting, list its unit, supported range, owner, and observable completion condition.
