"""PG(3,3): 40 points; classical groups as permutation generators (reflections / transvections / random matrices)."""
import itertools, random

P = 3
def norm(v):
    for x in v:
        if x % P:
            inv = 1 if x % P == 1 else 2
            return tuple((inv * y) % P for y in v)
    return None
POINTS = sorted({norm(v) for v in itertools.product(range(P), repeat=4) if any(v)})
assert len(POINTS) == 40
IDX = {p: i for i, p in enumerate(POINTS)}

def mat_perm(M):
    out = []
    for p in POINTS:
        w = tuple(sum(M[i][j] * p[j] for j in range(4)) % P for i in range(4))
        out.append(IDX[norm(w)])
    return out

def lin_perm(f):
    return [IDX[norm(tuple(x % P for x in f(p)))] for p in POINTS]

# quadratic forms: elliptic x0^2+x1^2+x2^2+x3^2 is elliptic over F3? discriminant check: use
# hyperbolic Q+ = x0x1 + x2x3; elliptic Q- = x0x1 + x2^2 + x3^2 (x2^2+x3^2 anisotropic over F3)
def Qplus(v): return (v[0] * v[1] + v[2] * v[3]) % P
def Qminus(v): return (v[0] * v[1] + v[2] ** 2 + v[3] ** 2) % P
def bil(Q):
    return lambda u, v: (Q(tuple(a + b for a, b in zip(u, v))) - Q(u) - Q(v)) % P
def reflections(Q):
    B = bil(Q); gens = []
    for v in POINTS:
        q = Q(v)
        if q == 0: continue
        qi = 1 if q == 1 else 2
        f = (lambda v, qi: (lambda x: tuple(x[i] - B(x, v) * qi * v[i] for i in range(4))))(v, qi)
        gens.append(lin_perm(f))
    return gens
def symp(u, v): return (u[0] * v[1] - u[1] * v[0] + u[2] * v[3] - u[3] * v[2]) % P
def transvections():
    gens = []
    for v in POINTS:
        f = (lambda v: (lambda x: tuple(x[i] + symp(x, v) * v[i] for i in range(4))))(v)
        gens.append(lin_perm(f))
    return gens
def random_gl(rng):
    while True:
        M = [[rng.randrange(P) for _ in range(4)] for _ in range(4)]
        if len({norm(tuple(sum(M[i][j] * p[j] for j in range(4)) % P for i in range(4))) if any(sum(M[i][j] * p[j] for j in range(4)) % P for i in range(4)) else None for p in POINTS}) == 40:
            return mat_perm(M)
