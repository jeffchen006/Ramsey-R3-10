"""Re-gluing self test: for a known graph G and each vertex v, take H = G_v (with the vertex
order H, N(v), v), run glue and glue2 with K = alpha(G), d = deg(v), and check that G is among
the outputs (up to isomorphism, via labelg) and that glue and glue2 give the same output set.
usage: python3 selftest.py FILE.g6 K [nvertices_to_test] [extra glue args...]
"""
import sys, subprocess, os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin')
LABELG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'bin', 'labelg')

def g6dec(s):
    n = ord(s[0]) - 63; bits = []
    for ch in s[1:]:
        x = ord(ch) - 63; bits += [(x >> (5 - t)) & 1 for t in range(6)]
    adj = [set() for _ in range(n)]; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: adj[i].add(j); adj[j].add(i)
            k += 1
    return n, adj

def g6enc(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    while len(bits) % 6: bits.append(0)
    return chr(63 + n) + ''.join(chr(63 + int(''.join(map(str, bits[k:k + 6])), 2)) for k in range(0, len(bits), 6))

def canon(lines):
    p = subprocess.run([LABELG, '-q'], input='\n'.join(lines) + '\n', capture_output=True, text=True)
    return set(l for l in p.stdout.split('\n') if l)

g = open(sys.argv[1]).readline().strip()
K = int(sys.argv[2]); ntest = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
extra = sys.argv[4:]
n, adj = g6dec(g)
cg = canon([g])
for v in range(min(n, ntest)):
    Nv = sorted(adj[v]); rest = [x for x in range(n) if x != v and x not in adj[v]]
    idx = {x: i for i, x in enumerate(rest)}
    hadj = [set(idx[y] for y in adj[x] if y in idx) for x in rest]
    h = g6enc(len(rest), hadj)
    res = {}
    for P in ('glue', 'glue2'):
        p = subprocess.run([os.path.join(B, P), '-k', str(K), '-d', str(len(Nv)), '-q'] + extra,
                           input=h + '\n', capture_output=True, text=True)
        res[P] = canon([l for l in p.stdout.split('\n') if l])
    ok = cg <= res['glue'] and cg <= res['glue2']
    print(f'v={v} deg={len(Nv)} |H|={len(rest)} e(H)={sum(map(len, hadj)) // 2}: '
          f'glue {len(res["glue"])} glue2 {len(res["glue2"])} same={res["glue"] == res["glue2"]} contains_G={ok}', flush=True)
