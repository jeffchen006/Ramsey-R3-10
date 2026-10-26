#!/usr/bin/env python3
"""cert/sat_sanity.py - SAT sanity check of the same pipeline at n-1.
Runs lazy.py (same SB, same cubes) for (3,s,n) where graphs exist; every SAT
answer is written as graph6 and checked by tools/check_graph.py (independent).
Expect: at least one cube SAT. Usage: sat_sanity.py N S [DEPTH]"""
import ast
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def graph6(n, E):
    bits = [1 if (i, j) in E else 0 for j in range(1, n) for i in range(j)]
    bits += [0] * (-len(bits) % 6)
    return chr(63 + n) + "".join(chr(63 + int("".join(map(str, bits[k:k + 6])), 2)) for k in range(0, len(bits), 6))


def main():
    n, s = int(sys.argv[1]), int(sys.argv[2])
    depth = sys.argv[3] if len(sys.argv) > 3 else "1"
    D = os.path.join(HERE, "demo", "sat_r3_%d_%d" % (s, n))
    os.makedirs(D, exist_ok=True)
    found = []
    for d in range(n):
        cube = [-sb.var(0, 1)] if d == 0 else [sb.var(0, n - 1)] if d == n - 1 else [sb.var(0, d), -sb.var(0, d + 1)]
        r = subprocess.run([sys.executable, os.path.join(HERE, "lazy.py"), str(n), str(s), depth,
                            " ".join(map(str, cube)), os.path.join(D, "c%d" % d)], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if line.startswith("SAT graph edges:"):
                E = set(map(tuple, ast.literal_eval(line.split(":", 1)[1].strip())))
                found.append((d, graph6(n, E)))
        print("cube d=%d: %s" % (d, "SAT" if r.returncode == 1 else "UNSAT"))
    with open(os.path.join(D, "found.g6"), "w") as f:
        for d, g in found:
            f.write(g + "\n")
    print("%d SAT cubes" % len(found))
    if found:
        r = subprocess.run([sys.executable, os.path.join(HERE, "..", "tools", "check_graph.py"), "--k", str(s),
                            os.path.join(D, "found.g6")], capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-3:], "exit", r.returncode)


if __name__ == "__main__":
    main()
