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

## Kill criteria

If WP2's J-aware assignment does not beat the greedy γ250 by ≥1% in a
5-pair, WP3's premise (locality beats protocol) is weakened — re-audit
before continuing.
