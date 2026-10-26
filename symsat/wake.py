#!/usr/bin/env python3
"""Exit 0 (and print why) if a wake condition holds: a SAT at n=40, a FAILED certificate,
a positive control that is not SAT, a calibration mismatch, or the subcase queue is finished."""
import json, os, subprocess, sys
R = "./runs/symsat/"
def rows(f):
    try:
        return [json.loads(l) for l in open(R + f) if l.strip()]
    except FileNotFoundError:
        return []
why = []
for f in ("sub_search.jsonl", "p50_search.jsonl", "rerun1.jsonl"):
    for d in rows(f):
        if d.get("result") == "SAT":
            why.append(f"SAT n=40 in {f}: {d.get('p')},{d.get('f')},a={d.get('amax')}")
if os.path.exists(R + "certs.log"):
    for l in open(R + "certs.log"):
        if " FAILED " in l:
            why.append("FAILED certificate: " + l[:80])
for d in rows("bench39b.jsonl"):
    if d.get("result") == "UNSAT" and d.get("amax") == 1 and d.get("f") == 1:
        why.append(f"positive control (39) not SAT: {d}"[:200])
out = subprocess.run([sys.executable, "./symsat/calib_amax_check.py", R + "calib_amax.jsonl"],
                     capture_output=True, text=True).stdout
if "MISMATCHES []" not in out:
    why.append("calibration mismatch: " + out[:200])
if len(rows(sys.argv[2] if len(sys.argv) > 2 else "sub_search.jsonl")) >= int(sys.argv[1]):
    why.append("queue finished")
if why:
    print("\n".join(why)); sys.exit(0)
sys.exit(1)
