"""Necessary-condition prefilter for X in R(6, f*<=5) (notes/cases_local.md Lemma F). Author: cases, 2026-10-25.
Each c in C = {1..6} has N(c) = {0,10} + N_X(c), |N_X(c)| = 7, N_X(c) independent in X (so a maximum
independent set, alpha(X) <= 7); codeg(c,c') <= 6 gives |N_X(c) & N_X(c')| <= 4; and every x in X has
deg_X(x) + #{c : x in N_X(c)} <= 9. Prints per X: e, #7-sets, max compatible family size (capped at 6), verdict.
Run: tools/venv/bin/python cases/r6f_prefilter.py FILE.g6"""
import sys
from itertools import combinations
sys.path.insert(0, 'cases')
from r6f_enc import g6decode

def indep_sets(n, adj, k):
    out = []
    def rec(start, cur, forb):
        if len(cur) == k:
            out.append(frozenset(cur)); return
        for v in range(start, n):
            if not (forb >> v) & 1:
                rec(v + 1, cur + [v], forb | adj[v])
    rec(0, [], 0)
    return out

def check(n, E):
    adj = [0] * n
    deg = [0] * n
    for i, j in E:
        adj[i] |= 1 << j; adj[j] |= 1 << i; deg[i] += 1; deg[j] += 1
    S = [s for s in indep_sets(n, adj, 7) if all(deg[x] <= 8 for x in s)]
    cap = [9 - d for d in deg]
    m = len(S)
    nb = [[j for j in range(m) if j != i and len(S[i] & S[j]) <= 4] for i in range(m)]
    best = [0]
    def rec(cand, chosen, load):
        best[0] = max(best[0], len(chosen))
        if best[0] >= 6:
            return True
        for idx, i in enumerate(cand):
            if all(load[x] < cap[x] for x in S[i]):
                for x in S[i]: load[x] += 1
                nc = [j for j in cand[idx + 1:] if j in nbs[i]]
                if len(chosen) + 1 + len(nc) >= 6 and rec(nc, chosen + [i], load):
                    return True
                best[0] = max(best[0], len(chosen) + 1)
                for x in S[i]: load[x] -= 1
        return False
    nbs = [set(l) for l in nb]
    ok = rec(list(range(m)), [], [0] * n)
    return len(E), m, best[0], ok

if __name__ == "__main__":
  for line in open(sys.argv[1]):
    if line.strip():
        n, E = g6decode(line)
        e, m, b, ok = check(n, E)
        print(e, m, b, 'PASS' if ok else 'KILL', flush=True)
