#!/usr/bin/env python3
"""Convert an smsg --proof-log file to (DIMACS, LRAT, external-clause list).

Usage: lratlog2lrat.py INPUT.cnf PROOF.log OUT_PREFIX
Writes:
  OUT_PREFIX.cnf    all original clauses in the order the solver received them
                    (input clauses + external clauses from SMS propagators)
  OUT_PREFIX.lrat   LRAT proof (ASCII) over OUT_PREFIX.cnf
  OUT_PREFIX.ext    the clauses of OUT_PREFIX.cnf that are NOT input clauses: "ID lit... 0".
                    Each must be justified separately (symmetry-breaking clause with a
                    permutation witness, or a "no independent k-set" clause).
Deletions of weakened clauses are skipped (CaDiCaL may restore them later).
"""
import sys
from collections import Counter


def read_dimacs(path):
    cls = []
    cur = []
    with open(path) as f:
        for line in f:
            if line.startswith(("c", "p")):
                continue
            for t in line.split():
                x = int(t)
                if x == 0:
                    cls.append(tuple(sorted(cur)))
                    cur = []
                else:
                    cur.append(x)
    return cls


def main():
    cnf_in, log, out = sys.argv[1:4]
    inputs = Counter(read_dimacs(cnf_in))

    # pass 1: originals
    newid = {}
    originals = []
    maxvar = 0
    with open(log) as f:
        for line in f:
            if line[0] == "o":
                t = line.split()
                i = int(t[1])
                lits = [int(x) for x in t[2:-1]]
                if i in newid:
                    raise SystemExit(f"original id {i} seen twice")
                originals.append(lits)
                newid[i] = len(originals)
                for l in lits:
                    maxvar = max(maxvar, abs(l))
    N = len(originals)
    ext = []
    with open(out + ".cnf", "w") as g:
        g.write(f"p cnf {maxvar} {N}\n")
        for k, lits in enumerate(originals, 1):
            g.write(" ".join(map(str, lits)) + " 0\n")
            key = tuple(sorted(lits))
            if inputs[key] > 0:
                inputs[key] -= 1
            else:
                ext.append((k, lits))
    with open(out + ".ext", "w") as g:
        for k, lits in ext:
            g.write(f"{k} " + " ".join(map(str, lits)) + " 0\n")

    # pass 2: proof
    weakened = set()
    live = set(newid)
    nxt = N
    last = N
    status = None
    with open(log) as f, open(out + ".lrat", "w") as g:
        for line in f:
            t = line.split()
            c = t[0]
            if c == "o":
                continue
            if c == "a":
                i = int(t[1])
                z = t.index("0", 2)
                lits = t[2:z]
                hints = [str(newid[int(h)]) for h in t[z + 1:-1]]
                nxt += 1
                newid[i] = nxt
                live.add(i)
                last = nxt
                g.write(f"{nxt} {' '.join(lits + ['0'] + hints + ['0'])}\n")
            elif c == "d":
                i = int(t[1])
                if i in weakened:
                    continue
                live.discard(i)
                g.write(f"{last} d {newid[i]} 0\n")
            elif c == "w":
                weakened.add(int(t[1]))
            elif c == "r":
                i = int(t[1])
                if i not in live:
                    raise SystemExit(f"restored clause {i} is not live")
            elif c == "s":
                status = t[1]
    print(f"originals={N} input_unmatched={sum(inputs.values())} external={len(ext)} "
          f"derived={nxt - N} status={status}")


if __name__ == "__main__":
    main()
