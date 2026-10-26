import random, itertools, sys
sys.path.insert(0, '.')
import ev
random.seed(1)
for trial in range(30):
    n = random.randint(8, 16); p = random.random() * 0.5
    adj = ev.from_edges(n, [(i, j) for i in range(n) for j in range(i + 1, n) if random.random() < p])
    t = sum(1 for a, b, c in itertools.combinations(range(n), 3) if adj[a] >> b & 1 and adj[a] >> c & 1 and adj[b] >> c & 1)
    assert t == ev.tri(adj)
    for k in (3, 4, 5):
        c = sum(1 for S in itertools.combinations(range(n), k) if all(not adj[a] >> b & 1 for a, b in itertools.combinations(S, 2)))
        assert c == ev.indep(adj, k), (c, ev.indep(adj, k))
        c2, pv = ev.indep_pv(adj, k); assert c2 == c and sum(pv) == k * c
    al = max(k for k in range(n + 1) if ev.indep(adj, k, 1) > 0)
    assert al == ev.alpha(adj)
    assert ev.from_graph6(ev.to_graph6(adj)) == adj
print('all ok')
