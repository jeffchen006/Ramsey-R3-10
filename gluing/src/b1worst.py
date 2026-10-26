"""Guaranteed (worst-case G) bound for B1 pair gluing in the 9-regular case: per vertex u,
sum over its 30 non-neighbours w of (t_w + c_w^2 + e38(20+c_w)) = 1836 and sum c_w = 72.
Adversary makes every pair class >= 10^L; find the largest L it can afford (DP over c-multisets)."""
import math, sys
sys.argv = ['x']; exec(open('src/b1pair.py').read().split('mins = []')[0])
INF = 10**9
def tmin(c, L):
    n = 20 + c; ln = LN[n]
    for e in sorted(ln):
        if ln[e] >= L * math.log(10): return e - E38[n]
    return INF
best = None
for L10 in [x / 4 for x in range(20, 64)]:
    cost = {c: tmin(c, L10) + c * c + E38[20 + c] for c in range(0, 8)}
    # DP: 30 slots, sum c = 72, minimize sum cost
    dp = {0: 0}
    for _ in range(30):
        nd = {}
        for s, v in dp.items():
            for c in range(8):
                if s + c <= 72 and cost[c] < INF:
                    if v + cost[c] < nd.get(s + c, INF): nd[s + c] = v + cost[c]
        dp = nd
    ok = dp.get(72, INF) <= 1836
    print(f"L=1e{L10}: min sum {dp.get(72, INF)} {'adversary CAN' if ok else 'cannot'}")
    if ok: best = L10
print("guaranteed: some pair has X-class <= 1e%s only for L above this; worst G has all pair classes >= 1e%s" % (best, best))
