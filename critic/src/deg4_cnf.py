"""critic: CNF for "a (3,10,40)-graph G has a vertex v of degree 4".
Then G - N[v] = H = C35(1,7,11,16), the unique (3,9,35)-graph ([GR] Thm 3), and G is fixed by
the sets S_c = N(a_c) & V(H), c = 0..3, N(v) = {a_0..a_3}.
Var x(u,c) <=> u in S_c. Constraints:
 - each u in H has deg_H(u) = 8 <= 9 - 1, so u is in at most one S_c;
 - S_c independent in H (else triangle a_c u w);
   (|S_c| <= 8, i.e. deg(a_c) <= 9, follows from alpha(H) = 8);
 - alpha(G) <= 9. Independent sets of G: {v} + J (|J| <= 8, fine) or K + J, K subset of N(v),
   J independent in H, no edge K-J. Need |J| + |K| <= 9 for all such: for |J| = 6, 7, 8 at
   least 1, 2, 3 of the 4 sets S_c meet J. "At least 4-t+1 of 4 meet J" <=> every t-set T of
   colours has a member meeting J: clause OR_{c in T, u in J} x(u,c), t = 4, 3, 2.
SAT <=> such a G exists (given uniqueness of the (3,9,35)-graph)."""
import itertools, sys
K = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # alpha(G) <= K-1; K=11 is a calibration run
n = 35; D = {1, 7, 11, 16, 34, 28, 24, 19}
adj = [[(j - i) % n in D for j in range(n)] for i in range(n)]
assert all(sum(r) == 8 for r in adj) and not any(adj[i][i] for i in range(n))
x = lambda u, c: 4 * u + c + 1
cl = []
for u in range(n):  # u in at most K-1-8 sets
    for C in itertools.combinations(range(4), K - 8): cl.append([-x(u, c) for c in C])
for u in range(n):
    for w in range(u + 1, n):
        if adj[u][w]:
            for c in range(4): cl.append([-x(u, c), -x(w, c)])
cnt = {}
def ind(cur, start):
    k = len(cur)
    if k >= K - 4:  # need |J| + |K'| <= K-1, i.e. >= k+5-K of 4 sets meet J; t = K-k
        cnt[k] = cnt.get(k, 0) + 1
        t = K - k
        for T in itertools.combinations(range(4), t):
            cl.append([x(u, c) for c in T for u in cur])
    for w in range(start, n):
        if not any(adj[w][u] for u in cur): ind(cur + [w], w + 1)
ind([], 0)
assert 9 not in cnt
print("indep sets of size 6,7,8:", cnt, file=sys.stderr)
print("p cnf %d %d" % (4 * n, len(cl)))
for c in cl: print(" ".join(map(str, c)), 0)
