# Evidence Records Rationale

The contracts live in `spec-evidence-records.md`. This file records why the
schemas, vocabulary, and identity rules exist.

## Why a controlled outcome vocabulary

A census of the real campaign ledger found 250+ distinct `status` strings
across 337 records (`reject-runtime-regression`,
`promote-lookahead-n128-validated`, `within-tolerance-retain (causal T16
delta = neutral +0.68%)`, `confirmed-neutral-8806ms`, ...). Each entry was
honest, but the set was unqueryable: no tool could answer "which routes were
closed on correctness grounds?" or "which promotes are load-bearing?" without
human rereading. The vocabulary makes the outcome token machine-checkable
while leaving the detail free-form, mirroring loom's separation of a
controlled registry from free detail. History is grandfathered; enforcement
starts at the adoption date.

## Why single owners per fact

The campaign state leaked into multiple places: a decision appeared in
`candidates.jsonl`, again in `benchmark.csv`'s status column, and again in a
report's Decision section. When they disagreed (they did, after corrections),
there was no rule for which won — the reader reconciled by hand. The spec
names one owner per fact and forbids tie-breaking; `benchmark.csv`'s status
column was re-scoped to row classification to remove the duplicate decision
authority.

## Why an executable checker

The same census found the failure modes the checker now catches:

- 9 of 216 `benchmark.csv` rows had the wrong field count (one had 30 fields
  vs the 16-column header) — unquoted commas in notes made those rows
  unparseable by any CSV consumer.
- A record dated `20208-16` (typo) — accepted silently by every reader.
- Dangling `parent` references after name edits.

Existence checks (the old `check-evidence.py`) catch none of these. The
checker is the executable form of the spec, in loom's anchor-test sense: it
protects canonical identity (dates, names), cross-artifact coupling (parent,
report, candidate references), and failure classification (vocabulary,
transient states) — and it fails when a future edit reintroduces any of them.

## Why identity tuples

The delivery verification (fresh clone, byte-identical model, fingerprint
match, -0.07% reproduced performance) was only possible because champions
carried commit + fingerprint + recipe env. Wall numbers without identity are
anecdotes; with identity they are replayable evidence. Hence: `promote`
requires the tuple, and replay is performed against it.

## Why estimates are labeled

Campaign estimates occasionally leaked into summaries as if measured (an
early "25-30%" estimate was later corrected by a measured number). The
`analysis` token and the missing-evidence-is-not-pass rule make the estimate
boundary machine-visible instead of a convention.

## Clean-clone build is a distinct gate class

The delivery branch passed every in-worktree gate (byte-identity, canon,
NEMU) while being unbuildable from a clean clone for ~2 days: a committed
emitter referenced a helper whose definition lived only in an uncommitted
worktree hunk. Every local build linked because the hunk was always present;
every agent correctly noted "pre-existing WIP, left untouched". The
fresh-clone re-verification caught it in one step. Rule: a push to the
delivery branch is not complete until a clean clone builds — in-worktree
success proves nothing about the pushed tree. This is now the rationale for
making clean-clone link a CI-class gate.
