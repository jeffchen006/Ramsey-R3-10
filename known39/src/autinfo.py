"""For each graph6 line: |Aut|, orbit sizes, and for each prime p dividing |Aut| the cycle
type (fixed points, number of p-cycles) of one element of order p. Group closure from
pynauty generators (only for |Aut| <= 200000)."""
import sys
sys.path.insert(0, './tools')
from check_graph import parse_graph6
import pynauty

def primes(m):
    out, p = [], 2
    while p * p <= m:
        if m % p == 0:
            out.append(p)
            while m % p == 0: m //= p
        p += 1
    if m > 1: out.append(m)
    return out

def compose(a, b): return tuple(a[i] for i in b)  # a after b

def order(a):
    idn = tuple(range(len(a))); x, k = a, 1
    while x != idn: x = compose(a, x); k += 1
    return k

def power(a, k):
    r = tuple(range(len(a)))
    for _ in range(k): r = compose(a, r)
    return r

def cycle_type(a):
    n, seen, cyc = len(a), set(), {}
    for i in range(n):
        if i in seen: continue
        j, l = i, 0
        while j not in seen: seen.add(j); j = a[j]; l += 1
        cyc[l] = cyc.get(l, 0) + 1
    return dict(sorted(cyc.items()))

for line in open(sys.argv[1]):
    g6 = line.split()[-1].strip()
    if not g6 or g6[0] == '#': continue
    adj = parse_graph6(g6); n = len(adj)
    G = pynauty.Graph(n, adjacency_dict={u: [v for v in range(n) if adj[u] >> v & 1] for u in range(n)})
    gens, g1, g2, orbits, norb = pynauty.autgrp(G)
    size = round(g1 * 10 ** g2)
    orbsz = sorted([orbits.count(o) for o in set(orbits)], reverse=True)
    res = {}
    if 1 < size <= 200000:
        idn = tuple(range(n)); elems = {idn}; frontier = [idn]; gens = [tuple(x) for x in gens]
        while frontier:
            nf = []
            for x in frontier:
                for s in gens:
                    y = compose(s, x)
                    if y not in elems: elems.add(y); nf.append(y)
            frontier = nf
        assert len(elems) == size, (len(elems), size)
        for p in primes(size):
            types = set()
            for x in elems:
                o = order(x)
                if o % p == 0:
                    y = power(x, o // p); ct = cycle_type(y)
                    types.add((ct.get(1, 0), ct.get(p, 0)))
            res[p] = sorted(types)
    print(f"n={n} e={sum(bin(a).count('1') for a in adj)//2} aut={size} orbits={orbsz} "
          + " ".join(f"p{p}:(fix,{p}-cycles)={v}" for p, v in res.items()) + f" {g6}")
