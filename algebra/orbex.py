"""Exhaustive search over unions of pair-orbits (orbitals): enumerate all MAXIMAL triangle-free unions
(adding edges never increases #independent sets, so only maximal ones matter), score each by
(c10, c9). Node limit -> returns None (too big)."""
import sys
sys.path.insert(0, './algebra')
import ev

def orbex(n, orbs, k=10, node_limit=2_000_000, keep=5):
    M = len(orbs)
    # pre: orbit internally triangle-free?
    masks = []
    for o in orbs:
        m = [0] * n
        for a, b in o: m[a] |= 1 << b; m[b] |= 1 << a
        masks.append(m)
    def tri_free_with(adj, i):
        m = masks[i]
        new = [adj[v] | m[v] for v in range(n)]
        for a, b in orbs[i]:
            if new[a] & new[b]: return None
        return new
    ok = [tri_free_with([0] * n, i) is not None for i in range(M)]
    best = []; nodes = [0]; leaves = [0]
    def rec(i, adj, chosen):
        nodes[0] += 1
        if nodes[0] > node_limit: raise TimeoutError
        if i == M:
            # maximality
            for j in range(M):
                if j not in chosen and ok[j] and tri_free_with(adj, j) is not None: return
            leaves[0] += 1
            c = ev.indep(adj, k)
            best.append((c, sorted(chosen))); best.sort(); del best[keep:]
            return
        if ok[i]:
            new = tri_free_with(adj, i)
            if new is not None: rec(i + 1, new, chosen | {i})
        # exclude i: only valid if it will be blocked eventually; we check maximality at leaf
        rec(i + 1, adj, chosen)
    try:
        rec(0, [0] * n, frozenset())
    except TimeoutError:
        return None, nodes[0], leaves[0]
    return best, nodes[0], leaves[0]

def adj_of(n, orbs, chosen):
    adj = [0] * n
    for i in chosen:
        for a, b in orbs[i]: adj[a] |= 1 << b; adj[b] |= 1 << a
    return adj

if __name__ == '__main__':
    import pg33, orbits
    for name, g in [('O-', pg33.reflections(pg33.Qminus)), ('O+', pg33.reflections(pg33.Qplus))]:
        o = orbits.pair_orbits(40, g)
        print(name, orbex(40, o))
