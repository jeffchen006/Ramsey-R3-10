"""B1 pair estimate (s=2): for H in R(3,9;30,99) samples and each w in H, X = H - N_H[w] is in
R(3,8;20+c, e38(20+c)+t), c = 9 - deg_H(w) (= codegree of u,w in a 9-regular G with H = H_u).
Estimate |class(c,t)| from MCMC curves (runs/gluing/mc38_n*.out) anchored at [GR] T13 counts.
usage: python3 b1pair.py samples.g6 [...]"""
import sys, math, statistics
R = './runs/gluing/'
E38 = {20: 30, 21: 35, 22: 42, 23: 49, 24: 56, 25: 65, 26: 73, 27: 85}
ANCH = {20: (33, 58649), 21: (38, 35797), 22: (45, 2331462), 23: (52, 10326716),
        24: (60, 64233886), 25: (68, 11946369), 26: (77, 1526296)}
R27 = {85: 4, 86: 92, 87: 1374, 88: 11915, 89: 52807, 90: 122419, 91: 151308, 92: 99332, 93: 33145, 94: 4746}
def lncounts(n):
    if n == 27: return {e: math.log(v) for e, v in R27.items()}
    d = {}
    for l in open(R + f'mc38_n{n}.out'):
        if l.startswith('#') or not l.strip(): continue
        e, ns, ma, sa, mr, sr, lw = l.split(); d[int(e)] = (float(ma), float(mr))
    es = sorted(d); lg = {es[0]: 0.0}
    for e in es[:-1]: lg[e + 1] = lg[e] + math.log(d[e][0]) - math.log(d[e + 1][1])
    ae, ac = ANCH[n]
    return {e: lg[e] - lg[ae] + math.log(ac) for e in es}
LN = {n: lncounts(n) for n in E38}
def parse(s):
    n = ord(s[0]) - 63; bits = []
    for ch in s[1:]:
        x = ord(ch) - 63; bits += [(x >> (5 - i)) & 1 for i in range(6)]
    adj = [set() for _ in range(n)]; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: adj[i].add(j); adj[j].add(i)
            k += 1
    return n, adj
mins = []; types = {}
for fn in sys.argv[1:]:
    for line in open(fn):
        line = line.strip()
        if not line: continue
        n, adj = parse(line); deg = [len(a) for a in adj]; eH = sum(deg) // 2
        best = None
        for w in range(n):
            c = 9 - deg[w]; nx = 20 + c
            eX = eH - sum(deg[y] for y in adj[w])
            if nx not in LN: continue
            ln = LN[nx].get(eX)
            if ln is None: ln = float('inf')  # beyond MCMC range (t > 14): huge
            if best is None or ln < best[0]: best = (ln, c, eX - E38[nx])
        mins.append(best[0]); types[(best[1], best[2])] = types.get((best[1], best[2]), 0) + 1
mins.sort(); N = len(mins); L10 = math.log(10)
print(f"samples {N}; min over w of log10 |class(X)|: min {mins[0]/L10:.2f} q10 {mins[N//10]/L10:.2f} "
      f"median {mins[N//2]/L10:.2f} q90 {mins[9*N//10]/L10:.2f} max {mins[-1]/L10:.2f}")
for th in (6, 8, 10, 12, 14):
    print(f"  fraction of H with some X of class <= 1e{th}: {sum(m <= th*L10 for m in mins)/N:.4f}")
print("best (c,t) types:", sorted(types.items(), key=lambda x: -x[1])[:12])
