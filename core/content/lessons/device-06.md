## Before you configure a server or compute cluster

Know [bounded algorithms](/learn/c/3/), [configuration validation](/learn/device/2/), and [buffer limits](/learn/device/5/). A configuration combines quantities that constrain one another. Increasing worker count changes memory needs and contention; increasing replicas changes placement, write traffic, and failure behavior. Language syntax alone supplies none of those relationships.

## Capacity is a resource calculation

If eight workers each require 32 MiB, their stated working-memory budget is 256 MiB before the rest of the service. A queue of 64 items with 1024 bytes per item requires another 65536 bytes before metadata and allocator overhead. An active worker count and a waiting queue count are different quantities.

If each worker serves ten jobs per second under a stipulated workload, eight workers suggest at most eighty jobs per second under ideal independence. When arrivals exceed the actual service rate, a queue grows until an admission limit rejects or redirects work. A larger queue does not increase the bottleneck's service rate; it can increase waiting time. Real rates require measurement under a defined workload, rather than multiplication of configuration numbers.

## Try this in the terminal beside the documentation

```c run:reference
#include <stdio.h>
int main(void) {
    int workers = 8;
    int worker_mib = 32;
    int queue_items = 64;
    int item_bytes = 1024;
    int nodes = 6;
    int replicas = 3;
    int placement_possible = replicas > 0 && replicas <= nodes;
    int tolerance = replicas - 1;
    printf("worker_mib=%d queue_bytes=%d placement=%d copy_loss_tolerance=%d\n",
           workers * worker_mib, queue_items * item_bytes,
           placement_possible, tolerance);
    return 0;
}
```

Expect `worker_mib=256 queue_bytes=65536 placement=1 copy_loss_tolerance=2`. The last number means that three existing independent copies can lose two copies and still leave one. It is not a consensus availability claim, a quorum calculation, or a guarantee against correlated failures.

## Placement and consistency answer different questions

Six nodes and three replicas permit choosing three distinct nodes for one object. They do not establish that copies were created, that their data agree, or that the copies are spread across independent racks, power feeds, or sites. A failure domain is a group of resources that can fail together. Three copies on one shared power source have less independence than the node count implies.

Replication also needs a consistency and recovery protocol. An acknowledgement could mean received, stored in cache, persisted, or committed by a specified quorum. If a write reached only one replica before failure, having three configured replicas does not make that particular write durable. The profile lab verifies only the requested counts and reports whether distinct-node placement is numerically possible.

For a parallel compute workload, worker count must be paired with task decomposition, communication cost, and serial work. Amdahl's model gives ideal speedup `1 / (s + (1-s)/N)` for serial fraction `s` and `N` independent workers. With `s=0.1` and `N=128`, the ideal bound is about 9.34, before network and scheduling costs. Writing 128 into a profile does not produce 128-fold speedup.

## Practice: find the invalid relationship

Set replicas to seven while nodes remain six; expect `placement=0`. The arithmetic `replicas-1` can still print six, but it no longer describes a feasible distinct-node placement. Double workers and derive 512 MiB, then include a fixed 128 MiB service overhead in your budget. State an admission policy for an overloaded queue. Explain what must be measured to claim throughput, latency, durability, or availability instead of merely reporting requested fields.
