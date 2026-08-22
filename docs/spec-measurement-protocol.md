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
- **Census before emit.** A value-distribution claim (e.g. "most stores write
  unchanged values") is measured at the exact sites in a census-only
  instrumented build before any behavior-affecting emission is written.
  Counterfactual quantities (instruction ratios between executors, request
  counts) never bound value-change distributions, and a site-level fraction
  never extrapolates to a grouped fraction (0.97^k collapse): grouped claims
  need grouped censuses.
- **Counting instruments must not carry their own cost explosion.** Census
  counters go on the affected sites only, use single-writer plain increments
  where static ownership proves it (atomic fallback otherwise), and are built
  with per-file optimization overrides ready: heavily-wrapped translation
  units can explode the -O3 optimizer (observed 2h47m on 2 TUs); -O1 for the
  pathological TUs is acceptable for census builds because the counted ratios
  are optimizer-independent.

## A/B isolation

- A candidate A/B is single-variable: the model diff between sides must be
  fully explained by the feature under test (verified by direct diff of the
  generated trees), and both sides must come from the same generator binary.
  Runtime-inert machinery is still a confound: any emitted text difference
  requires the knob treatment.
- Flag-off identity is proven, not assumed: unset-knob generation is compared
  byte-for-byte against the pre-knob generator before any performance claim.
- Premature closure is a protocol violation: a rejected probe requires
  continuing to the next candidate on the route (or an explicit structural
  closure argument), never "direction closed" from one implementation's
  failure.
- Knob debt is real: a default-off knob must be re-validated before reuse
  after executor changes (a knob validated in one executor era is not
  evidence in another).
