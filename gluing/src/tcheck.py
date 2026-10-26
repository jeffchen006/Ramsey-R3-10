"""Check GR-style increments t_d (GR2013 Sec. 3, 'Neighborhood Gluing Extension Method').

Claim checked: every (3,k;n,e)-graph H with e <= EMAX has a vertex v of degree d with
  e(H_v) <= e(3,k-1,n-d-1) + t_d - 1.
Proof idea: deficiency gamma(v) = e - Z(v) - e(3,k-1,n-d-1) >= 0 and
  sum_v gamma(v) = n e - sum_v (d_v^2 + e(3,k-1,n-d_v-1))   (GR eq. (4)).
If gamma(v) >= t_{d(v)} for all v then n e - sum_d n_d (d^2 + f(d) + t_d) >= 0.
We enumerate ALL integer degree sequences (n_d) with sum n_d = n, sum d n_d = 2e even,
e <= EMAX, degrees in [max(0, n - R(3,k-1)), k-1], and report any that satisfy it
(-> increments insufficient). Degrees d with t_d = 0 need no input.

usage: python3 tcheck.py k n emax t_spec   e.g.  tcheck.py 9 31 96 6:3,7:3
"""
import sys

# e(3,k,m) from [GR] Table 3 (exact), inf if no graph. index: E[k][m]
INF = 10 ** 9
# Fill from GR Table 3 rows (n: e(3,6..9,n)). Only the parts we use are entered.
T3 = {  # n: (k6, k7, k8, k9)
    3: (0, 0, 0, 0), 4: (0, 0, 0, 0), 5: (0, 0, 0, 0), 6: (1, 0, 0, 0),
    7: (2, 1, 0, 0), 8: (3, 2, 1, 0), 9: (4, 3, 2, 1), 10: (5, 4, 3, 2),
    11: (8, 5, 4, 3), 12: (11, 6, 5, 4), 13: (15, 9, 6, 5), 14: (20, 12, 7, 6),
    15: (25, 15, 10, 7), 16: (32, 20, 13, 8), 17: (40, 25, 16, 11), 18: (INF, 30, 20, 14),
    19: (INF, 37, 25, 17), 20: (INF, 44, 30, 20), 21: (INF, 51, 35, 25), 22: (INF, 60, 42, 30),
    23: (INF, INF, 49, 35), 24: (INF, INF, 56, 40), 25: (INF, INF, 65, 46), 26: (INF, INF, 73, 52),
    27: (INF, INF, 85, 61), 28: (INF, INF, INF, 68), 29: (INF, INF, INF, 77), 30: (INF, INF, INF, 86),
    31: (INF, INF, INF, 95), 32: (INF, INF, INF, 104), 33: (INF, INF, INF, 118),
    34: (INF, INF, INF, 129), 35: (INF, INF, INF, 140), 36: (INF, INF, INF, INF),
}
def e3(k, m):
    if m <= 0:
        return 0
    if m < 3:
        return 0 if m < k else INF
    return T3[m][k - 6]

def check(k, n, emax, t):
    km1 = k - 1
    f = {}
    for d in range(0, k):
        m = n - d - 1
        if m < 0:
            continue
        v = e3(km1, m) if m >= 3 else (0 if m < km1 else INF)
        if v >= INF:
            continue
        f[d] = v
    degs = sorted(f)
    bad = []
    # recursive enumeration of n_d
    def rec(i, left, sumd, acc, seq):
        if i == len(degs):
            if left:
                return
            if sumd % 2 or sumd // 2 > emax:
                return
            e = sumd // 2
            if n * e - acc >= 0:
                bad.append((e, dict(seq), n * e - acc))
            return
        d = degs[i]
        w = d * d + f[d] + t.get(d, 0)
        for c in range(left + 1):
            if sumd + c * d > 2 * emax:
                break
            if c:
                seq.append((d, c))
            rec(i + 1, left - c, sumd + c * d, acc + c * w, seq)
            if c:
                seq.pop()
    rec(0, n, 0, 0, [])
    return f, bad

if __name__ == '__main__':
    k, n, emax = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    t = {}
    if len(sys.argv) > 4 and sys.argv[4]:
        for p in sys.argv[4].split(','):
            d, v = p.split(':'); t[int(d)] = int(v)
    f, bad = check(k, n, emax, t)
    print(f'(3,{k};{n},<={emax}) degrees {sorted(f)} f(d)=e(3,{k-1},n-d-1): {f}')
    print('inputs needed: ' + ', '.join(f'd={d}: R(3,{k-1};{n-d-1},<={f[d]+t[d]-1})' for d in sorted(t) if t[d] > 0 and d in f))
    if bad:
        print(f'FAIL: {len(bad)} degree sequences survive, e.g.', bad[:3])
    else:
        print('OK: increments suffice')
