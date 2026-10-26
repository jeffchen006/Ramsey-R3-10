import sys, itertools
sys.path.insert(0, '.')
import ev
def circ(n, S):
    adj = [0] * n
    for i in range(n):
        for s in S:
            adj[i] |= 1 << ((i + s) % n); adj[i] |= 1 << ((i - s) % n)
    return adj
def search(n, k):
    half = n // 2; best = None; res = []
    # backtracking over distance sets, triangle-free pruning: S sum-free in Z_n (symmetric)
    def ok(S):
        T = set(S) | {n - s for s in S}
        return all((a + b) % n not in T for a in T for b in T)
    def rec(start, S):
        a = ev.alpha(circ(n, S)) if S else n
        if a < k: res.append(list(S))
        for d in range(start, half + 1):
            S2 = S + [d]
            if ok(S2): rec(d + 1, S2)
    rec(1, [])
    return res
if __name__ == '__main__':
    n, k = int(sys.argv[1]), int(sys.argv[2])
    r = search(n, k); print(n, k, len(r), r[:5])
