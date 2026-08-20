# Measurement Protocol Specification

Normative. Owns how candidates of the GSim optimization loop are measured and
attributed. The incidents that produced these rules are in
`rationales/measurement-protocol.md`; this file states only the current
contracts.

## Timing sessions

- Wall-time comparisons are **same-session, alternating-interleaved, and
  pinned**. The reference configuration is the declared parent baseline, not a
  remembered number.
- Runs at 8 or more workers must set the declared CPU affinity mode. Unpinned
  dense runs are void.
- A violated protocol voids the measurement; the row must not be used for any
  decision.

## Instruments

Each instrument has a declared fidelity and a permitted use. An instrument is
never used outside its permitted use, and no instrument output is a promotion
decision (decisions are recorded in `candidates.jsonl` per
`spec-evidence-records.md`).

| Instrument | Fidelity | Permitted use | Forbidden use |
|---|---|---|---|
| Wall time (pinned, same-session A/B) | Decision grade within one session | Adoption decisions | Cross-session comparison; absolute claims |
| `GSIM_MT_DENSE_DUTY` per-lane counters | ~0.6% distortion | Work attribution, budget arithmetic | Cross-session wall claims |
| `GSIM_MT_PROFILE` | Observer-dominated (~19x distortion at T32) | Coarse existence checks only | Budget arithmetic; headroom claims |
| Floor bound (PEG dump + critical recurrence, measured token costs) | Model of the parallel lower bound | Ceiling computation before implementing scheduler changes | Presenting the bound as measured wall |
| Microbenchmarks of extracted kernels | Valid only under production constraints | Mechanism pricing with captured inputs | Any claim without production input capture and `memcmp` verification |
| Offline analysis (partitioning, census, counting) | Estimate only | Route triage; replacing probes when data exists | Standing in for a build-and-run measurement |

- Every reported wall number is reported against the computed floor bound of
  its configuration, not only as a delta.
- Compute the offline ceiling before implementing a scheduler change. When
  the data for the ceiling already exists, offline analysis replaces the
  probe.
- A component's CPU share is not its wall relevance. Any mechanism that can
  absorb slack (scans, speculation, helpers) additionally requires a
  critical-path or calibrated-replay verification before its gain is claimed.
- A microbenchmark must drive the kernel with inputs captured from real
  production cycles, keep production state arrays and memory layout, and
  verify outputs by `memcmp` against same-cycle production state. A benchmark
  measured outside production constraints proves nothing.

## Probe hygiene

- Experimental changes sit behind default-off knobs. Flag-off generation must
  stay identical to the parent.
- A rejected probe is reverted from the tree unless a recorded reason keeps it.
- Every rejection is recorded in `candidates.jsonl` with its measured numbers;
  absence of a record is a protocol violation, not a neutral outcome.
- Knob debt is real: a default-off knob must be re-validated before reuse
  after executor changes (a knob validated in one executor era is not
  evidence in another).
