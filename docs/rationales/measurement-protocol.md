# Measurement Protocol Rationale

The contracts live in `spec-measurement-protocol.md`. This file records why
each exists. Every rule below was paid for.

## Same-session, interleaved, pinned A/Bs

- Machine load drifted absolute wall numbers by 50%+ within a day during the
  campaign; every cross-session "regression" or "gain" compared against a
  remembered number was noise.
- Unpinned dense runs at 8+ workers exhibited a bistable 2-3x slow mode from
  migration churn. A single unpinned number can be off by a factor, silently.
- Interleaving control and candidate removes slow drift within the session;
  pinning removes the bistable mode; requiring the parent baseline as the
  in-session reference removes champion-vs-memory comparisons.

## Instrument fidelity table

- The v470 "4.6% sync headroom" claim was retracted: it was built from
  `GSIM_MT_PROFILE` numbers, whose instrumentation is observer-dominated
  (~19x distortion at T32). A budget claim from a distorting instrument is
  worse than no claim, because it redirects effort. Attribution moved to
  `GSIM_MT_DENSE_DUTY` (~0.6% distortion, per-lane padded counters).
- mcost-derived rates were found thread-count-mixing-unsafe (T16 serial rate
  988 mcost/us vs T32 implied 1,161, a 17.5% skew). Wall-to-floor accounting
  must use aggregate accounting, never rates mixed across thread counts
  (the v468 -> v469 -> v470 correction chain).
- The floor bound (PEG dump + latency-augmented recurrence with measured
  token costs) exists so wall numbers are always reported against a computed
  parallel lower bound rather than only against each other.

## Offline ceiling before probes

A KL partition on the measured traffic matrix bounded the CCD-relabeling
ceiling at ~1.5%; the 1.5h generation+build probe was skipped. The sparse
oracle (activity-level simulation of the champion schedule) bounded the
sparse-hybrid prize at ~6% before any implementation attempt. When the data
for a ceiling exists, the probe adds nothing but cost.

## CPU share is not wall relevance

- The lookahead tail scan was ~40% of CPU but wall-neutral when elided (-17%
  CPU, no wall change) because it runs in stall slack.
- Speculation showed an 82.9% raw hit rate but only +1.2-2.2% wall; tree
  helpers +0.34%. Slack-absorbing mechanisms price themselves by critical-path
  effect, not by share or hit rate. This rule was promoted to the spec's
  verification requirement after those probes.

## Production-constrained microbenchmarks

Kernel timings extracted from the model (register-hoisted hot fields, clean
inputs) measured faster than their in-model cost by wide margins. The
spec's capture/`memcmp`/layout requirements are the direct response: a
mechanism price measured outside production constraints is fiction.

## Probe hygiene and knob debt

- Every rejected probe stayed recorded with its numbers; the campaign's
  negative-results archive (250+ status entries) is what made later route
  triage cheap.
- Knob debt bit concretely: the sparse-gate knob (`GSIM_MT_DENSE_SPARSE_GATE`),
  validated in the pre-lookahead executor era, produced wrong results
  (instrCnt 169/191 vs 528) when reused on the champion recipe — and even
  after that was fixed, a second latent bug (non-atomic activation writes)
  only surfaced at C50000. A default-off knob's validation does not survive
  executor changes for free; reuse requires revalidation.

## Census before emit

The saturate-sparse campaign opened by estimating the unchanged-store
fraction from a T1-vs-T16 instruction ratio — an executor-vs-executor
counterfactual that bounds nothing about value distributions (advisory
catch). The actual site census then measured 96.3-97.25% unchanged stores,
and the site-level number still did NOT predict the grouped outcome: the
cheap extrapolation "97% unchanged => high skip rate per body" ignores the
0.97^k collapse for k-input bodies. Hence: grouped claims need grouped
censuses; site fractions never extrapolate.

The first exec-mode store-skip build also shipped its census counters INTO
the executable form (8.59G atomic RMWs) and hung-as-in-ran-100x-slow; the
counterless form then measured the true (negative) answer. Counting
instruments must be separable from behavior, and single-writer analysis
turns most atomic counters into plain ones.

## Instrument builds and the optimizer

Wrapping ~257K sites concentrated into the two heaviest translation units
made -O3 spend 2h47m on 2 TUs (still unfinished when killed). -O1 on the
pathological TUs unblocked the census build; ratios counted by the
instrument are optimizer-independent. Census builds therefore pre-plan
per-file -O overrides instead of abandoning the measurement. The .o path
mismatch (build dir root vs model/) also cost a build cycle: verify the
make target's object path before hand-compiling stragglers.

## Premature closure

After the store-skip rejection the direction was declared "closed" while the
task's own report listed two unmeasured levers — a violation of the
campaign's standing rule (rejected probe => next candidate). Advisory
caught it; the correction record reopened the task and the read-side census
followed immediately, yielding the 97.07% read-side measurement. The spec
now states the rule.

## Same-binary controls

The wake-trim round-1 headline (-2.54%, "5/5 negative") was retracted when
review showed the candidate side carried an ungated owner-map emission and
a changed spawn guard from a different generator build. The matched-control
redo (both sides from one final binary, one-file diff verified by direct
tree diff) reversed the sign to neutral. Runtime-inert machinery is still
generated text; only proven byte identity counts.

## Sub-phase measurement before optimization

The generation-speed campaign hit this rule twice in a row. First, the
"Final is CPU-bound text formatting" premise survived a 4MiB-buffer probe
(neutral) and a full parallel-emission rewrite (byte-identical, but +2.3%)
— phase timers then proved emission is only 1.6% of Final; the real cost
was scheduleBuild (620s) and a hidden duplicate schedule build behind
--dump-mt-schedule-json (~521s). Second, inside scheduleBuild, sub-timers
found 77% of the VCONTRACT mergeLoop in ONE function (pathExists, 3.51M
calls). Both times the optimizing work began only after the cost owner was
measured directly. The pattern is now a standing rule: before optimizing a
phase, add timers fine enough to name the guilty function, and treat a
wrong premise as a measurement result, not a wasted experiment.

## Revert-with-evidence before commit

The scheduleBuild optimization tried a bidirectional pathExists and caught
its own unsoundness during development: the live quotient graph's gP is not
the exact reverse of gS through merged groups (a meet-node-on-src divergence
at frm=9803). The optimization was reverted to one-directional gS-only DFS
BEFORE commit, with the failure documented in the commit message, and a
standalone differential harness (11 seeds, 470k queries, zero mismatches)
backed the kept implementation. An optimization that cannot prove its
invariant does not ship; the attempt's existence belongs in the ledger, not
in the tree.

## Build straggler watchdog

Census/instrumented models wrap hundreds of thousands of sites, and a few
heaviest TUs then explode the -O3 optimizer (2h47m observed on SimTop682/683
before being killed). Each incident was rescued by hand: kill, recompile the
TU at -O1 into the make-expected object path, resume make. Three rescues is
enough to automate: `scripts/build-watchdog.py --build-dir <dir>` polls
/proc, kills any clang compiling a model TU longer than the threshold, and
recompiles it at -O1 in place. Ratios counted by instrumentation are
optimizer-independent, so -O1 objects are valid for census builds; for
performance-candidate builds the watchdog's rescue list tells you which TUs
to revisit at -O3 with more time budget.

## Host contamination attribution before blaming the machine

A week of "machine drift" (+10-17% on T32 absolute walls, T16 unaffected)
turned out to be a single long-lived process pinned to CPU 1 — inside the
T32 gate mask 0-31, outside the T16 mask 16-31. The attribution was found
by mask controls (same binary on 0-31 vs 32-63/64-95/96-127), not by
guessing load averages. Lessons: (1) same-session interleaved A/Bs stay
valid under a constant contaminant, but absolute gates and cross-day
comparisons silently break; (2) when a gate drifts, first vary the mask,
not the theory; (3) a current-machine reference is only useful if the
measurement mask is itself quiet — the reference must record its mask.
