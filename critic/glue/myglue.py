"""critic: independent gluing check (no code from gluing/). Given H (triangle-free, alpha<=8) and d,
decide by CEGAR-SAT whether some (3,10)-graph G on |H|+d+1 vertices has a vertex v with
N(v) = {u_0..u_{d-1}} and G - N[v] = H.  Unknowns: S_i = N(u_i) & V(H).
Constraints: S_i independent in H (no triangle u_i y z); deg_G(y) = deg_H(y) + #{i: y in S_i} <= 9;
|S_i| <= 8 (deg u_i <= 9).  N(v) is independent (forced: N(v) of a triangle-free G).
alpha(G) <= 9 lazily: an independent 10-set I has v not in I (else I-v in H, |I-v| = 9 > alpha(H)),
so I = K + J, K in N(v), J in H; clause for EVERY |K|-subset T of the u's: some u_i (i in T) meets J.
Usage: myglue.py FILE.g6 d [first last]  -> one line per graph: SAT/UNSAT + iterations."""
import sys, itertools
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

def parse(s):
    n = ord(s[0]) - 63; bits = [((ord(c) - 63) >> (5 - i)) & 1 for c in s[1:] for i in range(6)]
    A = [0] * n; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: A[i] |= 1 << j; A[j] |= 1 << i
            k += 1
    return n, A

def max_indep(adj, n):
    best = [0, 0]
    def rec(P, size, cur):
        if size > best[0]: best[0], best[1] = size, cur
        if P == 0 or size + bin(P).count('1') <= best[0]: return
        v = P.bit_length() - 1
        rec(P & ~adj[v] & ~(1 << v), size + 1, cur | (1 << v))
        rec(P & ~(1 << v), size, cur)
    rec((1 << n) - 1, 0, 0)
    return best[0], [i for i in range(n) if best[1] >> i & 1]

def find10(adj, n, want=30):
    """Up to `want` independent 10-sets (DFS, highest-degree pivot not needed)."""
    out = []
    def rec(P, cur, size):
        if len(out) >= want: return
        if size == 10: out.append(list(cur)); return
        if size + bin(P).count('1') < 10: return
        while P and len(out) < want:
            v = (P & -P).bit_length() - 1
            P &= ~(1 << v)
            if size + 1 + bin(P & ~adj[v]).count('1') >= 10:
                cur.append(v); rec(P & ~adj[v], cur, size + 1); cur.pop()
            if size + bin(P).count('1') < 10: return
    rec((1 << n) - 1, [], 0)
    return out

def lex_rows(x, d, m, pool):
    """Rows S_0 >= S_1 >= ... in lex order of (x(i,0), ..., x(i,m-1)); sound: the u_i are interchangeable."""
    cls = []
    for i in range(d - 1):
        eq = None
        for y in range(m):
            a, b = x(i, y), x(i + 1, y)
            pre = [] if eq is None else [-eq]
            cls.append(pre + [a, -b])          # equal so far -> a >= b
            e = pool.id(('eq', i, y))
            if eq is not None: cls.append([-e, eq])
            cls += [[-e, -a, b], [-e, a, -b]]
            cls.append(pre + [a, b, e]); cls.append(pre + [-a, -b, e])
            eq = e
    return cls

def glue(m, AH, d):
    assert max_indep(AH, m)[0] <= 8
    pool = IDPool(); x = lambda i, y: pool.id((i, y))
    for i in range(d):
        for y in range(m): x(i, y)
    cls = []
    for i in range(d):
        for y in range(m):
            for z in range(y + 1, m):
                if AH[y] >> z & 1: cls.append([-x(i, y), -x(i, z)])
        cls += CardEnc.atmost([x(i, y) for y in range(m)], bound=8, vpool=pool, encoding=EncType.seqcounter).clauses
    for y in range(m):
        cap = 9 - bin(AH[y]).count('1')
        cls += CardEnc.atmost([x(i, y) for i in range(d)], bound=cap, vpool=pool, encoding=EncType.seqcounter).clauses
    if '--nosb' not in sys.argv: cls += lex_rows(x, d, m, pool)
    S = Cadical153(bootstrap_with=cls); it = 0
    N = m + d + 1; V0 = m + d  # vertices: H = 0..m-1, u_i = m+i, v = m+d
    while True:
        it += 1
        if not S.solve(): return 'UNSAT', it, None
        mod = set(l for l in S.get_model() if l > 0)
        adj = [0] * N
        for y in range(m): adj[y] = AH[y]
        for i in range(d):
            u = m + i; adj[u] |= 1 << V0; adj[V0] |= 1 << u
            for y in range(m):
                if x(i, y) in mod: adj[u] |= 1 << y; adj[y] |= 1 << u
        sets = find10(adj, N)
        if not sets:
            assert max_indep(adj, N)[0] <= 9
            return 'SAT', it, adj
        for I in sets:
            K = [w - m for w in I if m <= w < m + d]; J = [w for w in I if w < m]
            assert V0 not in I and len(K) >= 1
            for T in itertools.combinations(range(d), len(K)):
                S.add_clause([x(i, y) for i in T for y in J])

if __name__ == '__main__':
    lines = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    sys.argv = [a for a in sys.argv if a != '--nosb']
    d = int(sys.argv[2]); a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(lines))
    for k in range(a, min(b, len(lines))):
        m, AH = parse(lines[k]); r, it, adj = glue(m, AH, d)
        print(k, r, it, flush=True)
        if r == 'SAT':
            sys.path.insert(0, './critic/src'); from gen_tests import g6
            n = len(adj); E = [(a, b) for a in range(n) for b in range(a + 1, n) if adj[a] >> b & 1]
            open(sys.argv[1] + '.sat%d.g6' % k, 'w').write(g6(n, E) + '\n')
