#!/usr/bin/env python3
"""Heavy-work window registrar (workflow iteration-1 item #5, rushed live 2026-10-23).

Usage:
  claim <owner> <what>        # acquire heavy-work window (fails if held)
  release <owner>             # release own window
  status                      # print holder or FREE
  wait <owner> <max_s>        # block until FREE then claim (atomic)

File: /tmp/gsim-heavy-window.json ; flock-protected ; stale >6h auto-FREE (warns).
Measurement campaigns keep using measurement.lock; this is for heavy CPU windows
(generation/compile/official-field) so agents never idle-wait on broadcasts.
"""
import json, os, subprocess, sys, time, fcntl

PATH = "/tmp/gsim-heavy-window.json"
LOCK = PATH + ".flock"
STALE_S = 6 * 3600


def _load():
    try:
        return json.load(open(PATH))
    except Exception:
        return {"owner": None, "what": None, "since": 0}


def _save(d):
    json.dump(d, open(PATH, "w"))


def _stale(d):
    return d.get("owner") and (time.time() - d.get("since", 0)) > STALE_S


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    open(LOCK, "a").close()
    with open(LOCK) as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        d = _load()
        if _stale(d):
            print(f"warn: stale window {d['owner']} ({(time.time()-d['since'])/3600:.1f}h) -> FREE", file=sys.stderr)
            d = {"owner": None, "what": None, "since": 0}
        if cmd == "status":
            print(d["owner"] or "FREE")
            return 0
        if cmd == "claim":
            owner, what = sys.argv[2], " ".join(sys.argv[3:])
            if d.get("owner"):
                print(f"BUSY held by {d['owner']}: {d.get('what')}", file=sys.stderr)
                return 1
            _save({"owner": owner, "what": what, "since": time.time()})
            print(f"CLAIMED {owner}")
            return 0
        if cmd == "release":
            owner = sys.argv[2]
            if d.get("owner") not in (None, owner):
                print(f"ERR: held by {d['owner']}, not {owner}", file=sys.stderr)
                return 1
            _save({"owner": None, "what": None, "since": 0})
            print("FREE")
            return 0
        if cmd == "wait":
            owner, max_s = sys.argv[2], int(sys.argv[3])
            what = " ".join(sys.argv[4:]) or owner
            deadline = time.time() + max_s
            while True:
                if not d.get("owner"):
                    _save({"owner": owner, "what": what, "since": time.time()})
                    print(f"CLAIMED {owner} after wait")
                    return 0
                if time.time() > deadline:
                    print(f"TIMEOUT still held by {d['owner']}", file=sys.stderr)
                    return 1
                fcntl.flock(f, fcntl.LOCK_UN)
                time.sleep(30)
                fcntl.flock(f, fcntl.LOCK_EX)
                d = _load()
                if _stale(d):
                    d = {"owner": None, "what": None, "since": 0}
        print(__doc__)
        return 2


if __name__ == "__main__":
    sys.exit(main())
