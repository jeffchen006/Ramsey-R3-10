"""Permutation-group generators for actions on 40 points (products of projective-line actions etc.)."""
import itertools, random

class GF:
    """GF(p^k) with elements 0..q-1 (integer = coeff vector base p); log/exp tables."""
    def __init__(self, p, k):
        self.p, self.k, self.q = p, k, p ** k
        q = self.q
        for poly in itertools.product(range(p), repeat=k):  # monic x^k + poly
            # try to find primitive element x
            def mulx(a):  # a * x mod (x^k + sum poly_i x^i)
                c = [(a // p ** i) % p for i in range(k)]
                top = c[-1]; c = [0] + c[:-1]
                c = [(c[i] - top * poly[i]) % p for i in range(k)]
                return sum(c[i] * p ** i for i in range(k))
            if k == 1:
                # find primitive root
                for g in range(2, p) if p > 2 else [1]:
                    if len({pow(g, e, p) for e in range(p - 1)}) == p - 1: break
                exp = [pow(g, e, p) for e in range(p - 1)]
            else:
                exp = [1]
                for _ in range(q - 2): exp.append(mulx(exp[-1]))
            if len(set(exp)) == q - 1 and 0 not in exp:
                self.exp = exp; self.log = {v: i for i, v in enumerate(exp)}; break
    def add(self, a, b):
        p = self.p; return sum((((a // p ** i) + (b // p ** i)) % p) * p ** i for i in range(self.k))
    def neg(self, a):
        p = self.p; return sum(((-(a // p ** i)) % p) * p ** i for i in range(self.k))
    def mul(self, a, b):
        if a == 0 or b == 0: return 0
        return self.exp[(self.log[a] + self.log[b]) % (self.q - 1)]
    def inv(self, a): return self.exp[(-self.log[a]) % (self.q - 1)]
    def frob(self, a): return self.mul(a, self.mul(a, a)) if self.p == 3 and False else self._pow(a, self.p)
    def _pow(self, a, e):
        if a == 0: return 0
        return self.exp[(self.log[a] * e) % (self.q - 1)]

def pgl2(q_p, q_k, semilinear=True):
    """Generators of PGL(2,q) (or PGammaL) on q+1 points: 0..q-1 field elements, q = infinity."""
    F = GF(q_p, q_k); q = F.q; INF = q
    def moebius(a, b, c, d):  # x -> (a x + b)/(c x + d)
        out = []
        for x in range(q + 1):
            if x == INF:
                out.append(INF if c == 0 else F.mul(a, F.inv(c)))
            else:
                num = F.add(F.mul(a, x), b); den = F.add(F.mul(c, x), d)
                out.append(INF if den == 0 else F.mul(num, F.inv(den)))
        return out
    alpha = F.exp[1]
    gens = [moebius(1, 1, 0, 1), moebius(alpha, 0, 0, 1), moebius(0, 1, 1, 0)]
    for i in range(1, q_k): gens.append(moebius(1, F.exp[i], 0, 1))
    if semilinear and q_k > 1:
        gens.append([INF if x == INF else F._pow(x, q_p) for x in range(q + 1)])
    return gens

def sym(m): return [[(i + 1) % m for i in range(m)], [1, 0] + list(range(2, m))]
def cyc(m): return [[(i + 1) % m for i in range(m)]]
def dih(m): return [[(i + 1) % m for i in range(m)], [(-i) % m for i in range(m)]]
def agl1(p): return [[(i + 1) % p for i in range(p)], [(i * next(g for g in range(2, p) if len({pow(g, e, p) for e in range(p - 1)}) == p - 1)) % p for i in range(p)]] if p > 2 else cyc(2)

def words(gens, rng, length=30):
    n = len(gens[0]); w = list(range(n))
    for _ in range(length):
        g = rng.choice(gens); w = [g[x] for x in w]
    return w

def product_perm(ga, gb, nb):
    return [ga[i // nb] * nb + gb[i % nb] for i in range(len(ga) * nb)]

# factor structures: (name, size, generators)
FACTORS = {
    'PGL2_19': lambda: pgl2(19, 1), 'PGL2_9': lambda: pgl2(3, 2), 'PGL2_7': lambda: pgl2(7, 1),
    'PGL2_4': lambda: pgl2(2, 2), 'PGL2_3': lambda: pgl2(3, 1), 'PGL2_8': lambda: pgl2(2, 3),
    'PGL2_5': lambda: pgl2(5, 1),
    'S2': lambda: cyc(2), 'Z4': lambda: cyc(4), 'S4': lambda: sym(4), 'D4': lambda: dih(4),
    'Z5': lambda: cyc(5), 'D5': lambda: dih(5), 'AGL1_5': lambda: agl1(5), 'S5': lambda: sym(5),
    'Z8': lambda: cyc(8), 'D8': lambda: dih(8), 'Z10': lambda: cyc(10), 'D10': lambda: dih(10),
}
SIZES = {'PGL2_19': 20, 'PGL2_9': 10, 'PGL2_7': 8, 'PGL2_4': 5, 'PGL2_3': 4, 'PGL2_8': 9, 'PGL2_5': 6,
         'S2': 2, 'Z4': 4, 'S4': 4, 'D4': 4, 'Z5': 5, 'D5': 5, 'AGL1_5': 5, 'S5': 5, 'Z8': 8, 'D8': 8, 'Z10': 10, 'D10': 10}
PAIRS = [(a, b) for a in SIZES for b in SIZES if SIZES[a] * SIZES[b] == 40 and a.startswith('PGL2')]
