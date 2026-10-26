#!/usr/bin/env python3
"""Translate SMS cube files to satcore numbering.

usage: smscube.py N IN.cubes OUT.cubes [--select i,j,...]

SMS edge var (0-based i<j): v = i*n - i*(i+1)/2 + (j-i)   (row-wise; sms/gen_ramsey.py)
satcore edge var:           w = j*(j-1)/2 + i + 1          (colex)
Input lines: "a lit ... 0" (the leading "a" is optional). Literals on vars > C(n,2)
(SMS aux vars) are dropped and counted. Output: one cube per line "lit ... 0",
for satcore/runcubes.py --cubes OUT.cubes. --select keeps only the given cube indices
(0-based, in input order); the output line k then corresponds to the k-th selected index,
and OUT.cubes.idx lists the original indices.
"""
import sys

def main():
    a = sys.argv[1:]
    n, inp, out = int(a[0]), a[1], a[2]
    sel = None
    if '--select' in a:
        sel = [int(x) for x in a[a.index('--select') + 1].split(',')]
    m = n * (n - 1) // 2
    tr = {}
    for i in range(n):
        for j in range(i + 1, n):
            tr[i * n - i * (i + 1) // 2 + (j - i)] = j * (j - 1) // 2 + i + 1
    assert sorted(tr) == list(range(1, m + 1)) and sorted(tr.values()) == list(range(1, m + 1))
    cubes = []
    for line in open(inp):
        t = line.split()
        if not t or t[0] in ('c', 'p'): continue
        if t[0] == 'a': t = t[1:]
        lits = [int(x) for x in t if x != '0']
        cubes.append(lits)
    idx = sel if sel is not None else list(range(len(cubes)))
    dropped = 0
    with open(out, 'w') as f:
        for ci in idx:
            res = []
            for l in cubes[ci]:
                v = abs(l)
                if v > m: dropped += 1; continue
                res.append(tr[v] if l > 0 else -tr[v])
            f.write(' '.join(map(str, res)) + ' 0\n')
    with open(out + '.idx', 'w') as f:
        f.write('\n'.join(map(str, idx)) + '\n')
    print('cubes=%d written=%d dropped_aux_literals=%d' % (len(cubes), len(idx), dropped))

if __name__ == '__main__':
    main()
