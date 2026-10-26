"""Python mirror of R310/LP/Simple.lean `passSimple` (for cross-checking only)."""
E39 = {4: 140, 5: 129, 6: 118, 7: 104, 8: 95, 9: 86}
DEGS = (4, 5, 6, 7, 8, 9)


def g(n, i):
    return n[i - 4] if 4 <= i <= 9 else 0


def deg2n(n):
    return sum(d * g(n, d) for d in DEGS)


def cum(n, t):
    return sum(g(n, d) for d in DEGS if d <= t)


def nsub(a, b):
    return max(0, a - b)


def zthr(n, d):
    return 4 * d + sum(nsub(d, nsub(cum(n, t), 1 if d <= t else 0)) for t in range(4, 9))


def zmtf(d):
    return nsub(d * d + 78, 11 * d)


def zmin(n, mtf, d):
    return max(zthr(n, d), zmtf(d)) if mtf else zthr(n, d)


def vecs4():
    out = []
    for a in range(5):
        for b in range(5 - a):
            for c in range(5 - a - b):
                for d in range(5 - a - b - c):
                    for e in range(5 - a - b - c - d):
                        out.append([a, b, c, d, e, 4 - a - b - c - d - e])
    return out


VECS4 = vecs4()


def pairOK(k):
    for a in DEGS:
        for b in DEGS:
            if not (a == b or g(k, a) == 0 or g(k, b) == 0 or 12 <= a + b):
                return False
            if not (g(k, a) < 2 or 12 <= 2 * a):
                return False
    return True


def zOfK(k):
    return sum(d * g(k, d) for d in DEGS)


def distOfK(k):
    s1 = nsub(zOfK(k), 4)
    return [1 + g(k, 4), g(k, 5), g(k, 6), g(k, 7), nsub(35, s1) + g(k, 8), s1 + g(k, 9)]


def deg4ok(n, elb):
    return any(pairOK(k) and elb <= 140 + zOfK(k) and list(n) == distOfK(k) for k in VECS4)


def minZok(n, mtf):
    return all(g(n, d) == 0 or zmin(n, mtf, d) + E39[d] <= deg2n(n) // 2 for d in DEGS)


def passSimple(n, elb, mtf):
    a = lambda i: g(n, i)
    return (deg2n(n) % 2 == 0 and elb <= deg2n(n) // 2 and deg2n(n) // 2 <= 180
            and (not mtf or (a(4) == 0 and a(5) == 0))
            and a(4) * 156 + a(5) * 154 + a(6) * 154 + a(7) * 153 + a(8) * 159 + a(9) * 167
            <= 20 * deg2n(n)
            and a(4) + a(5) <= 2
            and (a(4) == 0 or nsub(a(4), 1) + a(5) + a(6) <= 4)
            and (a(4) != 2 or a(6) == 0)
            and (a(4) == 0 or deg4ok(n, elb))
            and minZok(n, mtf))
