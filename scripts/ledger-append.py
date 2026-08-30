#!/usr/bin/env python3
"""Append a validated JSON entry to a JSONL evidence ledger.

Replaces `cat >> ledger.jsonl << 'EOF'` heredoc appends, which corrupted the
ledger 3+ times in one session (unparseable "Extra data" entries). Each entry
is json.dumps-serialized (single line, ensure_ascii=False) and parsed back to
verify before commit; the ledger stays parseable or the append fails loudly.

Usage:
  ledger-append.py <ledger.jsonl> '<json object>'
  ledger-append.py <ledger.jsonl> --file entry.json
  echo '<json>' | ledger-append.py <ledger.jsonl> -
"""
import json
import sys
import tempfile
import os


def main() -> int:
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    ledger, source = sys.argv[1], sys.argv[2]

    if source == "--file":
        with open(sys.argv[3], encoding="utf-8") as f:
            entry = json.load(f)
    elif source == "-":
        entry = json.load(sys.stdin)
    else:
        entry = json.loads(source)

    if not isinstance(entry, dict):
        sys.stderr.write("error: ledger entry must be a JSON object\n")
        return 2
    for field in ("name", "date", "status"):
        if field not in entry:
            sys.stderr.write(f"error: entry missing required field '{field}'\n")
            return 2

    line = json.dumps(entry, ensure_ascii=False)
    json.loads(line)  # self-verify round-trip

    # Atomic-ish append: write to temp in the same dir, then append+fsync.
    d = os.path.dirname(os.path.abspath(ledger)) or "."
    with tempfile.NamedTemporaryFile("w", dir=d, delete=False, encoding="utf-8") as t:
        t.write(line + "\n")
        tmp = t.name
    try:
        with open(ledger, "a", encoding="utf-8") as f:
            with open(tmp, encoding="utf-8") as src:
                f.write(src.read())
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.unlink(tmp)

    # Post-condition: the whole ledger still parses.
    with open(ledger, encoding="utf-8") as f:
        n = 0
        for i, ln in enumerate(f, 1):
            if not ln.strip():
                continue
            try:
                json.loads(ln)
            except json.JSONDecodeError as e:
                sys.stderr.write(f"error: ledger broke at line {i}: {e}\n")
                return 1
            n += 1
    print(f"appended '{entry['name']}' ({n} entries, ledger verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
