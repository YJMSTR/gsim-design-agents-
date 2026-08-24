# Evidence Records Specification

Normative. Owns the evidence files of a task workspace: which file owns which
fact, the ledger schemas, the outcome vocabulary, and artifact identity.
Schemas are enforced by `scripts/check-evidence.py`; that script is the
executable form of this specification.

## Single source of truth

Each fact has exactly one owning file. Projections (reports, summaries) derive
from owners and state no new facts.

| Fact | Owner |
|---|---|
| Candidate decisions (promote/reject/retain/close) and their reasons | `candidates.jsonl` |
| Raw measurement rows (one row per measured run) | `benchmark.csv` |
| Raw instrument output (profiler dumps, logs, extracted metrics) | `profile/<run_name>/` |
| Diagnosis narrative and recommendation | `profile/<run_name>/REPORT.md` (projection; cites owners) |
| Release baselines (champion registrations) | `champions/<name>/` |
| Task contract instance | `docs/task-contract.md` |

When two representations disagree, the secondary one is corrected or
regenerated from its owner. A tie-breaking rule is never added. The `status`
column of `benchmark.csv` classifies the measurement row (for example
`route-smoke-pass`, `measurement-valid`); it is not the candidate decision,
which lives only in `candidates.jsonl`.

## `candidates.jsonl` schema

One JSON object per line. Required keys:

- `name`: string, unique, stable identity of the record.
- `date`: `YYYY-MM-DD`, the date the decision or observation was made.
- `status`: `<outcome-token> [free-text detail]`. The first token is the
  outcome and MUST come from the vocabulary below; the remainder is detail.

Optional keys: `parent` (name of an existing record this one builds on),
`threads`, `design`, `sim_time_ms`, `report` (workspace-relative path that
must exist), `notes`, and any structured result fields.

A record referencing `parent` or `report` with a value that does not resolve
is a schema error. A record with a transient state (`building`,
`generations-running`, `pending`, `in-flight`, `running`) must be finalized or
superseded by a later record before the task closes.

## Outcome vocabulary

| Token | Meaning |
|---|---|
| `baseline` | Reference measurement; no decision |
| `promote` | Adopted as new baseline or champion |
| `retain` | Kept without promotion (default-off knob, within-tolerance, recipe confirmation) |
| `reject` | Not adopted, with recorded reason |
| `closed` | Route or axis terminated with evidence (ceiling, structural, correctness) |
| `measured` | Observation recorded; no adoption decision made or implied |
| `analysis` | Offline/theory result only; no build or run of the candidate |
| `correction` | Amends the claim of an earlier record |
| `retracted` | Withdraws an earlier claim |
| `diagnostic` | Profiling or instrumentation finding; no candidate |
| `instrumentation` | Tooling or report-only change added |
| `validated` | Correctness or gate confirmation without a performance decision |

Rules:

- An estimate is always labeled `analysis` (or carries `measured` only after a
  run). Estimates never silently stand in for measurements.
- A correctness failure is `reject` or `closed`, never `measured`.
- Missing evidence is not pass: a record without the measurements its status
  implies is invalid.

## `benchmark.csv` schema

Header is exactly:

```
candidate,date,design,threads,compiler,flags,sim_time_ms,speedup_vs_parent,speedup_vs_1t,verilator_32t_ratio,cpu_util_pct,ipc,cache_miss_rate,sync_overhead_pct,status,notes
```

Every data row has exactly this width; fields containing commas are quoted.
`candidate` should reference a `candidates.jsonl` record; `sim_time_ms` is
numeric when present. Unparseable rows are schema errors, not warnings.

## Artifact identity

A `promote` record must carry, or point to a champion registration that
carries, the identity tuple of what was measured:

- source commit of the implementation,
- model fingerprint when the pipeline produces one,
- recipe environment (generator flags, thread count, build flags).

Wall numbers without their identity tuple are not reproducible evidence.
Replay or fresh-clone verification of a champion is performed against this
tuple.

`scripts/check-evidence.py --workspace <dir>` enforces this specification.
Run it after every ledger update; a non-zero exit blocks the workflow step
that produced the violation.

**Adoption boundary**: records dated before 2026-08-20 are grandfathered for
the outcome-vocabulary rule (they predate this specification). The checker
downgrades their vocabulary findings to warnings under
`--vocab-since 2026-08-20`; without the flag, strict mode applies. All other
rules (dates, references, widths, identity) have no adoption boundary.

## Champion seed artifacts

Champion registrations carry their seed2 file by path in `registry.json`.
The on-disk seed format is versioned: v1 (legacy uncompressed) and v2
(zlib-framed, ~27:1 on XiangShan). The reader auto-detects; both replay to
byte-identical models under the same recipe (9/9 canon gates). Migration of
an existing champion seed is done with the generator's standalone
transcoder (`GSIM_SEED2_TRANSCODE=in[:out]`, no generation) followed by a
replay verification against the registry's reference model, then an
in-place replace with the v1 file retained under `champions/_seed-v1-archive/`.

The harness scripts (`gsim-experiment.py`, `gsim-champion-gate.py`) have an
offline regression suite in the campaign workspace `tests/` (stdlib
unittest, mocked subprocesses); run it after any harness edit. NEMU
endpoint strings are matched with thousands separators stripped — a
comma-aware parse is required in any new gate code (two live defects came
from this).
