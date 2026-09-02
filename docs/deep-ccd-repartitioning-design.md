# Deep CCD Repartitioning — Project Design (pre-authorization draft)

Status: awaiting user authorization. Everything below is grounded in the
2026-09-01 evidence chain (ledger entries `t16-memstall-attribution` …
`strict-kl-loadspread-caveat`); nothing is speculative beyond the marked
open questions.

## Why (measured, not assumed)

- Backend-stall = 23.2% of cycles; 79.9% of it in mtask bodies as compulsory
  streaming + dataflow over the 81.2MB shared RTL state vs 2×32MB L3
  (CCD0 = cores 0-7, CCD1 = 8-15; lscpu-verified).
- Four-point CCD triangulation: greedy affinity **-4.76%** (registered v3),
  SBO layout -1.28%, loose KL +3.5%, strict-KL cut→41.1% **tie**.
- Conclusion the design MUST honor: **static edge cut is decoupled from
  wall time**. The greedy win is *temporal co-scheduling* (producer finishes
  → consumer ready on the same CCD immediately). A static-partitioning
  objective alone will reproduce the KL tie.

## Objective function (the core difference from all prior attempts)

Minimize an estimate of *dynamic coherence traffic*:

    J(assign) = Σ_{edges (p→c)} w(p) · [ ccd(p) ≠ ccd(c) ] · temporal_hotness(p→c)

where `temporal_hotness` is the measured (or lvlSum-modeled) probability the
consumer becomes ready within the producer's L3 residency window — i.e. only
edges whose tokens actually fire close in time count. This is learnable from
the existing tail-stats counters (18% of executions run out-of-order via tail
rescue; those are exactly the "temporal" edges).

## Architecture (three work packages)

WP1 — Instrumentation (2-3 days): per-edge token-fire timestamps sampled
      into the existing tail-stats framework; per-worker load spread
      (max/min) logged in every scheduling fprintf (the caveat entry makes
      this mandatory). Output: the temporal_hotness vector on the real
      workload.

WP2 — Temporal-aware assignment (3-5 days): extend mtBuildDenseScheduleOrder
      with the J-based penalty (generalizes CCD_AFFINITY's flat γ·cost into
      edge-weighted γ_e); plus accumulation-bounded swap refinement using J.
      Default-off knob; FIR gate + model-hash discipline on every commit.

WP3 — State ownership migration (5-10 days, optional but where the ~13%
      ceiling lives): emit per-CCD state arenas for exclusively-owned state
      (SBO groups by decl order; this splits *storage*), with cross-CCD
      shared state left in a common arena accessed through the existing
      owner-ready protocol. Requires emission partitioning + a migration
      pass; correctness contract unchanged (bit-exact gates).

## Validation protocol (per commit)

FIR gate 22/22 (default-off byte-identity) · model-hash change check for
every knob-on generation · 5-pair interleaved A/B (warmup discard, mask
0-15, serialized) · coremark difftest HIT GOOD TRAP bit-identical ·
registration only ≥3% with disjoint ranges · ledger-append + evidence check.

## Budget estimate

WP1+WP2: ~1 week to first A/B. WP3: +1-2 weeks. Success probability for
closing the remaining 5.6% (6.93 → 6.54s): moderate — WP2 alone likely
1-3% (extends the validated greedy); WP3 is where the attribution's 18.5%
ceiling could be realized, with genuine model risk.

## Priority update (2026-09-01, dispatch-machinery-synthesis)

The ledger correction recovered from `t16-tailscan-memo-fail-probe` changes
priority: Verilator executes 310.5G instructions vs gsim 372.2G on the same
workload — the 61.7G excess is dispatch/scan machinery, not bodies, and
instruction parity at gsim's IPC projects ~6.0s (< the 6.30s bar). So:

- **WP2' (new, higher EV): on-path dispatch slimming** — reduce per-mtask
  entry/flag-check/subStep-prologue cost on the critical path (the cursor
  probe cut off-path scan volume; the on-path machinery is the 1.20x).
  First slice DONE (wp2p-first-slice-findings, 2026-09-01): the on-path
  machinery is the $old$ copy wall + activation compares at every mtask
  entry. Two candidate cuts, both correctness-critical emission surgery:
  (a) dead-$old$-elimination — QUANTIFIED (old-copy-liveness-quantified,
  2026-09-01): 1.11M static copies; 53.3% DEAD (592,763 sites, decl never
  used; mechanical cut, lower risk, mostly hygiene: smaller bodies/I-cache),
  47% USED (519,587 sites feeding ESSENT compares — the actual wall lever),
  (b) batched activation over the 519,587 USED compare sites (higher risk).
  SEQUENCED KILL-TEST: **(a) EXECUTED 2026-09-01** (`dead-old-strip-killtest`):
  386,483 dead lines textually stripped, compiler-oracle-verified correct,
  wall **-0.9% (overlapping)** — below the 0.5% bar. VERDICT: the dead half
  was LLVM-DCE'd already; the excess is LIVE compares. (b) batched activation
  over the 725,867 USED sites is the sole remaining emission lever — but the
  attribution revision now required is: WHERE do the 61.7G excess instructions
  actually execute if not in dead loads? Re-run perf attribution on the
  stripped build before investing in (b). **REVISED ANALYTICALLY 2026-09-01**
  (`attribution-revision-analytical`): the excess lives in the 136G tail-scan
  + dispatch pool; (b) is re-scoped as **fused compare-scan** (batch activation
  + scan-loop fusion in one emission change, ceiling ~10% wall — above the
  5.6% gap). Fresh-session work.
  Implement in a FRESH session: FIR gate + model-hash + 5-pair + coremark
  gate discipline mandatory (770bab7 trap).
- WP1/WP2/WP3 as below remain valid; state arenas are now second priority.

## Kill criteria

If WP2's J-aware assignment does not beat the greedy γ250 by ≥1% in a
5-pair, WP3's premise (locality beats protocol) is weakened — re-audit
before continuing.


## Appendix: fused compare-scan implementation sketch (2026-09-01, session-final)

Current emitted scan (per entry, per candidate):
```cpp
for (wait = entry->waitBegin; wait < entry->waitEnd; ++wait)
  ready &= (tokens[waitList[wait]].ready.load(acquire) == target);
```
Cost: 15.1 avg iterations × (double-indirect load + cmp + and) × 46.4M calls.

Fused version (emission change in the lookahead-tail emitter):
1. SORT each task's waitList slice by token index at emission (locality:
   adjacent tokens share cache lines 64-way).
2. BATCH-CHECK: for sorted consecutive indices within a 64-token window,
   load the containing line's 64 bytes as one uint64_t and mask-compare
   against target pattern — one load replaces up to 64 individual loads
   when a task's waits cluster (they do: intra-supernode dependencies).
3. FALLBACK: scattered indices check individually as today.

Expected: 15.1 → ~3-5 effective loads per entry (batched + fallback),
attacking the 136G scan pool directly. Correctness invariant: the batched
check must be equivalent to the conjunction of individual checks — the
mask/match logic must handle the target-parity semantics exactly.

Emission site: cppEmitter's dispatch-table emission (~line 14590, the
kDenseOwnerReadyWaitList writer). Knob: GSIM_EMIT_FUSED_SCAN=1 (default
off). Validation: the standard chain.


## v4 后记（2026-09-02，LA1024 发现）

**v4 已注册**：`newrtl-t16-compact-v4`（LA=1024，-1.98% vs v3 5/5，种子 `2348c8900e5d3ce8`）。LA 曲线未在 512 饱和——早期停止规则"段长 ~530"是 CCD 亲和引入前的测量。全栈 {512,768,1024,2048}={7.050,6.990,**6.910**,6.940}。

**WP2′ 三切片终局**（更新上文优先级）：
- 死拷贝剔除：LLVM 已 DCE（零效果）
- OR 位点批量（bacc[256]，11.5× 静态压缩）：**+1.16% 回归**——OR 管道不是成本
- SIMD 打包 diff：投影上限 ~1-3%（加载主导）
- **结论：61.7G 指令超额 = 事件检测机制的内在代价**（Verilator 静态求值零代价，gsim 付比较换跳工）。突破需层级汇总位——激活协议重设计。

**重扫纪律**（v4 三维验证）：MAXMT（结构层，稳定 2000）、γ（调度层，稳定 250）、LA（调度层，**移动** 512→1024）。规则：栈变更后必须重扫调度层参数。

**supernode 粒度**（未测过的生成旋钮）：{20,30,60}={7.25,7.06,7.68}——30 最优；+60 损失 3.3× 于 -10（跳过粒度敏感性主导）。
