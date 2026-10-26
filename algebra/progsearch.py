"""FunSearch-style program search (programs written by algebra, parameters evolved).
A program maps a parameter vector theta to an edge priority order on 40 vertices; a greedy fill
(first come first served, keep triangle-free) gives a maximal triangle-free graph; score = (#indep 10-sets, #indep 9-sets).
Programs (families) are in PROGRAMS. Evolution: (mu + lambda) with Gaussian mutation of theta and noise-seed resampling.
usage: progsearch.py FAMILY SEED SECONDS OUTPREFIX
"""
import sys, time, random, json, math
import numpy as np
sys.path.insert(0, './algebra')
import ev, orbits, groups

N = 40
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
PU = np.array([p[0] for p in PAIRS]); PV = np.array([p[1] for p in PAIRS])

def classes_from_orbits(orbs):
    cl = np.zeros(len(PAIRS), dtype=int); pidx = {p: t for t, p in enumerate(PAIRS)}
    for c, o in enumerate(orbs):
        for p in o: cl[pidx[p]] = c
    return cl, len(orbs)

def abelian_diff_classes(dims):
    """vertices = Z_d1 x Z_d2 x ..., class = {u-v, v-u}."""
    pts = [tuple(x) for x in np.ndindex(*dims)]; assert len(pts) == N
    idx = {}
    cl = np.zeros(len(PAIRS), dtype=int)
    for t, (i, j) in enumerate(PAIRS):
        d = tuple((a - b) % m for a, b, m in zip(pts[i], pts[j], dims))
        e = tuple((b - a) % m for a, b, m in zip(pts[i], pts[j], dims))
        key = min(d, e)
        cl[t] = idx.setdefault(key, len(idx))
    return cl, len(idx)

def make_family(name):
    if name.startswith('ab:'):
        dims = tuple(int(x) for x in name[3:].split('x')); return abelian_diff_classes(dims)
    if name.startswith('lift:'):  # lift:GROUP:FIXED
        _, g, f = name.split(':'); return classes_from_orbits(orbits.pair_orbits(N, groups.action(g, N, int(f))))
    if name.startswith('pg33:'):
        import pg33
        g = {'O-': pg33.reflections(pg33.Qminus), 'O+': pg33.reflections(pg33.Qplus), 'Sp': pg33.transvections()}[name[5:]]
        return classes_from_orbits(orbits.pair_orbits(N, g))
    if name == 'vertexw':  # priority = w_u + w_v + w_{u}w_{v}... classes = none; theta = vertex weights
        return None, N
    raise ValueError(name)

class Program:
    """theta = (table T over classes, sigma, noise seed). priority = T[class] + sigma * noise."""
    def __init__(self, fam, rng):
        self.cl, self.C = make_family(fam); self.rng = rng; self.fam = fam
    def random_theta(self):
        return {'T': self.rng.normal(size=self.C), 'sigma': 10 ** self.rng.uniform(-2, 0), 'seed': self.rng.integers(1 << 30)}
    def mutate(self, th):
        th = {'T': th['T'].copy(), 'sigma': th['sigma'], 'seed': th['seed']}
        r = self.rng.random()
        if r < 0.4:
            k = self.rng.integers(1, 4)
            for _ in range(k): th['T'][self.rng.integers(self.C)] += self.rng.normal() * 0.7
        elif r < 0.6:
            i, j = self.rng.integers(self.C, size=2); th['T'][i], th['T'][j] = th['T'][j], th['T'][i]
        elif r < 0.85:
            th['seed'] = self.rng.integers(1 << 30)
        else:
            th['sigma'] = float(np.clip(th['sigma'] * math.exp(self.rng.normal() * 0.5), 1e-3, 3))
        return th
    def graph(self, th):
        noise = np.random.default_rng(int(th['seed'])).normal(size=len(PAIRS))
        if self.cl is None:
            pr = th['T'][PU] + th['T'][PV] + th['sigma'] * noise
        else:
            pr = th['T'][self.cl] + th['sigma'] * noise
        order = np.argsort(-pr)
        return ev.greedy(N, [PAIRS[t] for t in order])

def score(adj):
    c10 = ev.indep(adj, 10, 10 ** 7)
    c9 = ev.indep(adj, 9, 10 ** 8) if c10 < 2000 else 10 ** 8
    return (c10, c9)

def run(fam, seed, seconds, out):
    rng = np.random.default_rng(seed); P = Program(fam, rng)
    mu, lam = 20, 40
    pop = []
    for _ in range(mu * 3):
        th = P.random_theta(); g = P.graph(th); pop.append((score(g), th))
    pop.sort(key=lambda x: x[0]); pop = pop[:mu]
    t0 = time.time(); gen = 0; evals = 0; best = pop[0][0]; last = 0
    log = open(out + '.log', 'a')
    log.write(f"# family {fam} seed {seed} classes {P.C}\n")
    while time.time() - t0 < seconds:
        kids = []
        for _ in range(lam):
            par = pop[int(rng.integers(len(pop)) * rng.random())][1]  # bias to good
            th = P.mutate(par); g = P.graph(th); kids.append((score(g), th)); evals += 1
        pop = sorted(pop + kids, key=lambda x: x[0])
        # dedupe by score
        seen = set(); newpop = []
        for s, th in pop:
            if s in seen: continue
            seen.add(s); newpop.append((s, th))
        pop = newpop[:mu]; gen += 1
        if pop[0][0] < best: last = gen
        if gen - last > 300:  # restart: keep the best, re-seed the rest
            pop = pop[:1] + sorted(((score(P.graph(th)), th) for th in (P.random_theta() for _ in range(mu * 2))), key=lambda x: x[0])[:mu - 1]
            last = gen
        if pop[0][0] < best:
            best = pop[0][0]; g = P.graph(pop[0][1])
            log.write(f"gen {gen} evals {evals} t {time.time()-t0:.0f}s best c10={best[0]} c9={best[1]} edges={sum(bin(x).count('1') for x in g)//2} sigma={pop[0][1]['sigma']:.3f}\n"); log.flush()
            open(out + '.best', 'w').write(ev.to_graph6(g) + '\n')
            if best[0] == 0 and ev.tri(g) == 0:
                open(out + '.FOUND', 'a').write(ev.to_graph6(g) + '\n'); log.write('FOUND\n'); log.flush(); return
    log.write(f"done gen {gen} evals {evals} best {best}\n")

if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
