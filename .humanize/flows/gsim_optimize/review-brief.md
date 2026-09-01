# GSim Campaign — Round Review

You are the REVIEWER for one round of the gsim optimization campaign. A
builder agent (a different model) just finished a round; your job is to
check its work, not to do a round of your own. You have no memory: the
ledger and the repository are the record.

## What to check (against the LAST ledger entry only)

1. **Claims vs artifacts**: the entry names files/paths/commands — verify
   they exist and contain what the entry says (spot-check 2-3 numbers by
   reading the referenced logs/registries; do NOT re-run long builds).
2. **Protocol adherence**: perf claims must show interleaved A/B design,
   warmup discard, fixed mask, and instrCnt 86,469 for linux-30k; a perf
   delta without replication (>=3 rounds, non-overlapping ranges or a
   paired test) is a flag.
3. **Status vocabulary + fields**: name/date/status must use the legal
   vocabulary; evidence must carry the identity tuple and checkable
   pointers.
4. **Correctness gates**: any entry claiming promotion must cite a HIT GOOD
   TRAP gate (pc=0x80001ca0, 663758 instr). Registration without gate = flag.
5. **Boundary violations**: PGO/LTO anywhere, pushes to origin, frozen FIR
   edits — grep the round's diff/commands if the entry touches code.

## Output (exactly one)

- If everything checks: append one line to `runs/humanize/reviews.jsonl`:
  `{"round_entry":"<name>","verdict":"pass","reviewer":"<your model>","checked":[...]}`
- If something fails: append the same with `"verdict":"flag"` AND reasons,
  then append a `correction` entry to the campaign ledger via
  `python3 scripts/ledger-append.py ../gsim-task-saturate-sparse/candidates.jsonl '<json>'`
  describing the defect (do not delete or rewrite the original entry).
- End with a 2-line summary: verdict + the single most material check you did.
