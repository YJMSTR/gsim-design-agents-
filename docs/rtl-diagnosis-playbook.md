# RTL Simulator Performance Diagnosis Playbook

Golden rule: Profile -> Diagnose -> Plan. Never start a simulator rewrite from a hunch.

## Six analysis dimensions

1. **Thread utilization and launch geometry**: active threads, CPU utilization, affinity, oversubscription, runnable vs waiting time.
2. **Load balance and tail effect**: per-thread work time, max/min ratio, long-tail timeline shape, task granularity.
3. **Synchronization and stall breakdown**: barriers, locks, atomics, futex waits, spin time, CPI/IPC.
4. **SIMD and generated-code efficiency**: vectorization reports, hot scalar loops, branch density, instruction count.
5. **Timeline shape**: flat-high, long-tail, sawtooth compute/sync, flat-low, ramp-up effects.
6. **Memory and cache behavior**: L1/LLC misses, false sharing, HITM, NUMA locality, hot/cold layout.

## Pattern -> cause -> fix

| Pattern | Signals | Likely cause | First fix |
|---|---|---|---|
| A. CPU idle | active threads < available cores; low CPU utilization | not enough parallel tasks | increase partitions or over-decompose work |
| B. Tail effect | max thread time / min thread time > 3; long tail timeline | static partition imbalance or activity skew | dynamic scheduling or smaller tasks |
| C. False sharing | `perf c2c` HITM; speedup drops with threads | multiple threads write same cache line | `alignas(64)`, padding, per-thread state |
| D. Atomic contention | hot `lock`/atomic instructions; poor scaling | shared counters or queues serialize | per-thread batching, hierarchical reduction |
| E. Sync overhead | barrier/spin/futex > 20% of time | too frequent global barriers | reduce barrier frequency or redesign phases |
| F. SIMD absent | vectorization ratio near zero on hot loops | scalar generated eval loops | simplify aliasing, SoA layout, explicit vector paths |
| G. Lock contention | mutex hotspots, lock wait events | shared work queue or event queue | shard queues or use low-contention design |
| H. Cache conflicts | high L1 misses with regular strides | layout maps hot data to same sets | padding, swizzle, SoA/hot-cold split |
| I. Barrier wait | wait concentrated at cycle boundaries | slowest worker controls all workers | over-decompose, local queues, sense-reversal barrier |
| J. Low achieved utilization | threads exist but idle/waiting | scheduler overhead or blocking | tune task grain and dequeue batching |
| K. Stack or allocation overhead | page faults, allocator hotspots | per-event allocation or large stack objects | arenas, pools, preallocation |
| L. Type width waste | unnecessary 64-bit/double operations | generated code uses wider types | narrow types and constants where safe |
| M. Pipeline bubbles | sawtooth compute/sync timeline | no overlap between phases | double buffering or phase fusion |
| N. Task divergence | branch miss rate high; irregular paths | mixed work types in same task | classify tasks by cost/path |

## Diagnosis sentence template

`Candidate <name> at <threads> threads reaches <speedup>x. Dimension 1 shows <utilization>. Dimension 2 shows <imbalance>. Dimension 3 shows <sync/stall metric>. Dimension 6 shows <cache/NUMA metric>. Therefore the dominant bottleneck is <pattern>, and the next candidate should <fix>.`
