# Documentation Authority Rationale

## Decision

Workflow knowledge is split into three layers: `spec-*.md` files own the
normative current contracts, `rationales/` owns the reasoning and incidents
behind them, and `scripts/`/`templates/` own the executable realization.
The structure is adopted from [PolyArch/loom](https://github.com/PolyArch/loom)'s
documentation-authority model.

## Why the incident log was retired from the protocol

`agent-flow.md` grew by accretion: every measurement failure appended a new
rule together with the incident that produced it ("the v470 4.6% headroom
claim was retracted because...", "unpinned dense runs have a bistable 2-3x
slow mode from..."). That form was useful while the rules were changing
weekly, but it has the same two failure modes loom describes for its retired
decision ledger:

1. A reader cannot mechanically extract the current contract: the rule, its
   history, and its exception narrative are interleaved, so an agent under
   context pressure re-derives the rule from the story and gets it wrong.
2. Two descriptions of the same rule (prose narrative here, enforcement in an
   ad-hoc check there) drift apart, and the reader must reconcile them.

The split preserves the distinction without the duplication: the spec states
one current contract; this directory retains the motivation, the incident,
and the rejected alternative.

## Why not a chronological decision ledger as authority

The campaign's `candidates.jsonl` is chronological by nature and stays so —
it is an append-only evidence ledger, not the workflow contract. When a
protocol rule changed (for example, duty counters replacing `GSIM_MT_PROFILE`
for attribution), the old rule had to be *replaced* in the contract, with the
invalidating incident recorded here. Keeping both versions live would let a
later agent cite the superseded rule — this happened in practice during the
v470 headroom retraction chain (v468 -> v469 -> v470), where an intermediate
aggregate was briefly treated as authoritative.

## What the layers may not do

- A spec never carries its history; when the rule changes, the old text is
  deleted, not annotated.
- A rationale never restates a contract as implementable text; it points to
  the owning spec.
- Execution state (builds in flight, coordination notes) belongs in neither
  layer; it lives in the task workspace.
