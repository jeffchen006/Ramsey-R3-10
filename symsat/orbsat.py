#!/usr/bin/env python3
"""Orbit SAT with CEGAR: search (3,K,n)-graphs invariant under a given permutation group H.

Variables: one per H-orbit on unordered vertex pairs (edge orbit is in or out).
Clauses:
  - triangle: for every vertex triple, not all three pair-orbits present (deduplicated);
  - degree:   every vertex has degree <= K-1 (implied by triangle-free + alpha < K, added
              for propagation) and >= dmin (optional, from a cited bound);
  - independent sets: CEGAR. For a model, find independent K-sets and add the clause
    "some pair of this set is an edge", projected to orbit variables. Each such clause is
    implied by alpha < K, so it is sound.
  - symmetry breaking (optional): lex-leader x <=lex pi(x) for each given permutation pi of
    the vertex set that normalizes H (so it maps pair-orbits to pair-orbits). Sound: the
    full constraint set is invariant under the normalizer, so the lex-least member of the
    orbit of any solution satisfies all lex-leader constraints at once.
Final UNSAT => no (3,K,n)-graph with H <= Aut(G) (under the stated degree bounds).

Library use: build Problem(n, K, gens, breakers, dmin) and call solve().
Writes the final CNF (DIMACS) if asked, so that UNSAT can be re-checked with a DRAT proof.
"""
import ctypes
import itertools
import os
import random
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(HERE, "libindep.so"))
_lib.indep_with.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_int, ctypes.c_int,
                            ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint64)]
_lib.alpha.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_int]


def indep_with(adj, k, must=0, allowed=None, seed=1):
    n = len(adj)
    arr = (ctypes.c_uint64 * n)(*adj)
    out = ctypes.c_uint64(0)
    if allowed is None:
        allowed = (1 << n) - 1
    r = _lib.indep_with(arr, n, k, must, allowed, seed, ctypes.byref(out))
    return out.value if r else None


def alpha(adj):
    n = len(adj)
    return _lib.alpha((ctypes.c_uint64 * n)(*adj), n)


def closure_orbits(n, gens, items, act):
    """Orbits of the group <gens> on `items` (hashable), act(g, item) -> item."""
    rep = {}
    orbits = []
    for it in items:
        if it in rep:
            continue
        orb = [it]
        rep[it] = len(orbits)
        i = 0
        while i < len(orb):
            x = orb[i]; i += 1
            for g in gens:
                y = act(g, x)
                if y not in rep:
                    rep[y] = len(orbits)
                    orb.append(y)
        orbits.append(orb)
    return rep, orbits


def act_pair(g, p):
    a, b = g[p[0]], g[p[1]]
    return (a, b) if a < b else (b, a)


class Problem:
    def __init__(self, n, K, gens, breakers=(), dmin=0, dmax=None, solver="cadical195",
                 lex_len=None, log=None, forced_zero=(), seed=0, card=True, pair2=False, cube_nvars=None):
        self.n, self.K = n, K
        self.gens = [list(g) for g in gens]
        for g in self.gens:
            assert sorted(g) == list(range(n))
        self.log = log or (lambda s: print(s, flush=True))
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
        self.prep, self.porbits = closure_orbits(n, self.gens, pairs, act_pair)
        self.nv = len(self.porbits)            # vars 1..nv
        self.var = {p: self.prep[p] + 1 for p in pairs}
        self.vrep, self.vorbits = closure_orbits(n, self.gens, range(n), lambda g, x: g[x])
        self.pool = IDPool(start_from=self.nv + 1)
        self.clauses = []
        self.solver = Solver(name=solver)
        self.rng = random.Random(seed)
        self.n_indep = 0
        self.indep_seen = set()
        self.indep_sets = []   # vertex masks behind each independent-set clause (certificate)
        # triangles
        tri = set()
        for a, b, c in itertools.combinations(range(n), 3):
            cl = frozenset((self.var[(a, b)], self.var[(a, c)], self.var[(b, c)]))
            tri.add(cl)
        for cl in tri:
            self.add([-v for v in cl])
        self.n_tri = len(tri)
        # forced non-edges (e.g. structural assumptions)
        for v in forced_zero:
            self.add([-v])
        # degree bounds, one vertex per vertex-orbit
        dmax = K - 1 if dmax is None else dmax
        for orb in (self.vorbits if card else []):
            v = orb[0]
            lits = [self.var[(min(v, u), max(v, u))] for u in range(n) if u != v]
            # lits may repeat (several incident pairs in one orbit): the sequential
            # counter / totalizer count multiplicity correctly.
            enc = CardEnc.atmost(lits=lits, bound=dmax, vpool=self.pool, encoding=EncType.totalizer)
            for cl in enc.clauses:
                self.add(cl)
            if dmin > 0:
                enc = CardEnc.atleast(lits=lits, bound=dmin, vpool=self.pool, encoding=EncType.totalizer)
                for cl in enc.clauses:
                    self.add(cl)
        # pair constraints: u, w non-adjacent => |N(u) u N(w)| >= n - 2 - (R(3,K-2) - 1)
        # (else u, w plus an independent (K-2)-set outside N[u] u N[w] is an independent K-set).
        self.n_pair2 = 0
        if pair2:
            R3 = {3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36, 10: 40}
            bound = n - 2 - (R3[K - 2] - 1)
            reps = {}
            for p, v in self.var.items():
                reps.setdefault(v, p)
            for v, (u, w) in sorted(reps.items()):
                ys = []
                for t in range(n):
                    if t in (u, w):
                        continue
                    y = self.pool.id(("y", u, w, t))
                    self.add([-y, self.var[(min(u, t), max(u, t))], self.var[(min(w, t), max(w, t))]])
                    ys.append(y)
                enc = CardEnc.atleast(lits=ys, bound=bound, vpool=self.pool, encoding=EncType.seqcounter)
                for cl in enc.clauses:
                    self.add(cl + [v])
                self.n_pair2 += 1
        # cube: exactly cube_nvars orbit variables are true (a partition of the search space by an
        # invariant of the normalizer; all values 0..nv must be run for a complete result)
        if cube_nvars is not None:
            enc = CardEnc.equals(lits=list(range(1, self.nv + 1)), bound=cube_nvars, vpool=self.pool,
                                 encoding=EncType.totalizer)
            for cl in enc.clauses:
                self.add(cl)
        # symmetry breaking (lex-leader on orbit variables 1..nv)
        self.n_sb = 0
        for pi in breakers:
            self.add_lex(pi, lex_len)

    def add(self, cl):
        self.clauses.append(list(cl))
        self.solver.add_clause(cl)

    def var_perm(self, pi):
        """Map orbit var -> orbit var induced by vertex permutation pi (must normalize H)."""
        m = {}
        for p, v in self.var.items():
            w = self.var[act_pair(pi, p)]
            if v in m:
                assert m[v] == w, "breaker does not normalize H"
            m[v] = w
        return [None] + [m[v] for v in range(1, self.nv + 1)]

    n_lexgroups = 0

    def add_lex(self, pi, lex_len=None):
        """x <=lex pi(x) over vars 1..nv (x_i = var i, y_i = var pi(i))."""
        m = self.var_perm(pi)
        self.n_lexgroups += 1
        L = self.nv if lex_len is None else min(lex_len, self.nv)
        idx = [i for i in range(1, L + 1)]
        # e_{i}: x_j == y_j for all j < i (prefix equal). Standard encoding.
        prev = None  # literal meaning "prefix so far equal"; None = true
        for i in idx:
            x, y = i, m[i]
            if x == y:
                continue
            # prefix_equal -> (x <= y)  i.e. not(x and not y)
            cl = [-x, y]
            if prev is not None:
                cl = [-prev] + cl
            self.add(cl)
            # new prefix-equal e = prev and (x == y)
            e = self.pool.id(("lex", self.n_lexgroups, i))
            # e -> prev ; e -> (x==y); prev and x==y -> e (only need e implied by, for propagation)
            base = [] if prev is None else [-prev]
            self.add(base + [x, y, e])    # prev & !x & !y -> e
            self.add(base + [-x, -y, e])  # prev & x & y -> e
            prev = e
            self.n_sb += 1

    def model_graph(self, model):
        true = set(l for l in model if 0 < l <= self.nv)
        adj = [0] * self.n
        for (a, b), v in self.var.items():
            if v in true:
                adj[a] |= 1 << b
                adj[b] |= 1 << a
        return adj

    def indep_clause(self, mask):
        vs = [i for i in range(self.n) if (mask >> i) & 1]
        cl = frozenset(self.var[(a, b)] for a, b in itertools.combinations(vs, 2))
        return cl

    def refine(self, adj, per_round):
        """Add clauses for independent K-sets of the current graph. Returns number added."""
        added = 0
        reps = [orb[0] for orb in self.vorbits]
        tries = 0
        starts = reps * max(1, per_round // max(1, len(reps)))
        for v in starts:
            tries += 1
            # random restriction to diversify
            allowed = (1 << self.n) - 1
            m = indep_with(adj, self.K, must=1 << v, allowed=allowed, seed=self.rng.randrange(1 << 30))
            if m is None:
                continue
            cl = self.indep_clause(m)
            if cl in self.indep_seen:
                # try with one more forced vertex removed at random
                vs = [i for i in range(self.n) if (m >> i) & 1 and i != v]
                drop = self.rng.choice(vs)
                m = indep_with(adj, self.K, must=1 << v, allowed=allowed & ~(1 << drop),
                               seed=self.rng.randrange(1 << 30))
                if m is None:
                    continue
                cl = self.indep_clause(m)
                if cl in self.indep_seen:
                    continue
            self.indep_seen.add(cl)
            self.indep_sets.append(m)
            self.add(sorted(cl))
            added += 1
        return added

    def solve(self, per_round=None, max_iter=10 ** 9, time_limit=None):
        t0 = time.time()
        it = 0
        per_round = per_round or max(4 * len(self.vorbits), 20)
        while it < max_iter:
            it += 1
            if time_limit and time.time() - t0 > time_limit:
                return "TIMEOUT", None, it
            if not self.solver.solve():
                return "UNSAT", None, it
            adj = self.model_graph(self.solver.get_model())
            m = indep_with(adj, self.K)
            if m is None:
                return "SAT", adj, it
            added = self.refine(adj, per_round)
            if added == 0:
                cl = self.indep_clause(m)
                assert cl not in self.indep_seen
                self.indep_seen.add(cl)
                self.indep_sets.append(m)
                self.add(sorted(cl))
                added = 1
            self.n_indep += added
            if it % 200 == 0:
                self.log(f"  iter {it} indep_clauses {self.n_indep} t={time.time()-t0:.1f}s")
        return "LIMIT", None, it

    def write_cnf(self, path):
        nv = max(self.pool.top, self.nv)
        with open(path, "w") as f:
            f.write(f"p cnf {nv} {len(self.clauses)}\n")
            for cl in self.clauses:
                f.write(" ".join(map(str, cl)) + " 0\n")
