#!/usr/bin/env python3
"""cert/test_encoding.py - link (a) test: for small n, every graph G satisfies the
CNF from gen.py  <=>  G is triangle-free with alpha < s (checked by brute force,
no shared code). Exhaustive over all 2^C(n,2) labelled graphs."""
import itertools
import subprocess
import sys


def load(n, s):
    out = subprocess.run([sys.executable, "gen.py", "full", str(n), str(s)], capture_output=True, text=True).stdout
    cls, cur = [], []
    for line in out.splitlines():
        if line.startswith(("c", "p")):
            continue
        for t in line.split():
            l = int(t)
            if l == 0:
                cls.append(cur)
                cur = []
            else:
                cur.append(l)
    return cls


def main():
    for n, s in [(3, 3), (4, 3), (5, 3), (6, 3), (5, 4), (6, 4), (7, 4), (7, 3), (7, 5)]:
        pairs = [(i, j) for j in range(n) for i in range(j)]  # colex = var order
        cls = load(n, s)
        good = 0
        for mask in range(1 << len(pairs)):
            E = {pairs[k] for k in range(len(pairs)) if mask >> k & 1}
            sat = all(any((l > 0) == bool(mask >> (abs(l) - 1) & 1) for l in c) for c in cls)
            tri = any((a, b) in E and (a, c) in E and (b, c) in E for a, b, c in itertools.combinations(range(n), 3))
            ind = any(all(p not in E for p in itertools.combinations(S, 2)) for S in itertools.combinations(range(n), s))
            prop = not tri and not ind
            assert sat == prop, (n, s, sorted(E))
            good += prop
        print("n=%d s=%d: %d labelled graphs, %d (3,%d)-graphs; CNF agrees on all" % (n, s, 1 << len(pairs), good, s))


if __name__ == "__main__":
    main()
