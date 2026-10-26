"""Validation: build ALL (3,k;n)-graphs for small k by repeated gluing with bin/glue.

G in R(3,k+1;n) with minimum degree d and v of degree d  =>  G_v in R(3,k;n-d-1).
So R(3,k+1;n) = iso-union over d of glue(R(3,k;n-d-1), d, DMIN=d).
Isomorphism rejection: networkx (WL hash buckets + exact check), or nauty shortg if given.

usage: python build_all.py KMAX OUTDIR [shortg-path]
writes OUTDIR/r3_{k}_{n}.g6 and prints counts.
"""
import sys, os, subprocess
import networkx as nx

KMAX = int(sys.argv[1]); OUT = sys.argv[2]
SHORTG = sys.argv[3] if len(sys.argv) > 3 else None
GLUE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'glue')
os.makedirs(OUT, exist_ok=True)

def dedupe(lines):
    if not lines:
        return []
    if SHORTG:
        p = subprocess.run([SHORTG, '-q'], input='\n'.join(lines) + '\n', capture_output=True, text=True)
        return [l for l in p.stdout.split('\n') if l]
    buckets = {}
    out = []
    for s in lines:
        g = nx.from_graph6_bytes(s.encode())
        key = (tuple(sorted(d for _, d in g.degree())), nx.weisfeiler_lehman_graph_hash(g, iterations=4))
        lst = buckets.setdefault(key, [])
        if any(nx.is_isomorphic(g, h) for h in lst):
            continue
        lst.append(g)
        out.append(s)
    return out

def add_isolated(s):
    g = nx.from_graph6_bytes(s.encode()) if s != '?' else nx.empty_graph(0)
    g.add_node(g.number_of_nodes())
    return nx.to_graph6_bytes(g, header=False).decode().strip()

R = {}  # R[(k,n)] = list of graph6
R[(2, 0)] = ['?']; R[(2, 1)] = ['@']; R[(2, 2)] = ['A_']
RAM = {2: 3}
for k in range(2, KMAX):
    # build R(3,k+1;n) for n = 0.. until empty
    n = 0
    while True:
        cand = []
        for d in range(0, k + 1):
            m = n - d - 1
            if m < 0:
                continue
            Hs = R.get((k, m), [])
            if not Hs:
                continue
            if d == 0:
                cand += [add_isolated(s) for s in Hs]
                continue
            p = subprocess.run([GLUE, '-k', str(k), '-d', str(d), '-q'], input='\n'.join(Hs) + '\n',
                               capture_output=True, text=True)
            cand += [l for l in p.stdout.split('\n') if l]
        if n == 0:
            res = ['?']
        else:
            res = dedupe(cand)
        if n > 0 and not res:
            RAM[k + 1] = n
            break
        R[(k + 1, n)] = res
        with open(os.path.join(OUT, f'r3_{k+1}_{n}.g6'), 'w') as f:
            f.write('\n'.join(res) + '\n')
        print(f'R(3,{k+1};{n}) = {len(res)}  (raw {len(cand)})', flush=True)
        n += 1
    print(f'=> R(3,{k+1}) = {RAM[k+1]}', flush=True)
