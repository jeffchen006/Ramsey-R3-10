#!/usr/bin/env python3
"""Build all groups of order 40 as multiplication tables (no GAP).

Theory: |G| = 40 = 2^3 * 5. n_5 divides 8 and n_5 = 1 mod 5, so n_5 = 1:
the Sylow 5-subgroup Z5 is normal and G = Z5 x| P with |P| = 8 (Schur-Zassenhaus).
So every group of order 40 is Z5 x|_phi P for P in {Z8, Z4xZ2, Z2^3, D4, Q8}
and phi: P -> Aut(Z5) = Z4. We build all such semidirect products (all phi, all P),
then sort them into isomorphism classes with an explicit isomorphism test.
Expected count: 14 (SmallGroups library, order 40).

Element (a, x), a in Z5, x in P, encoded as 8*a + x. Product:
(a,x)(b,y) = (a + 2^phi(x) * b mod 5, x*y).  2 generates Z5^* (order 4).
Identity is element 0.

Output: groups/G<i>.txt with "40" then 40 rows of the multiplication table,
and groups/index.txt with a description and invariants of each class.
"""
import itertools
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def group_of_order8():
    """Return dict name -> multiplication table on 0..7 (identity 0)."""
    gs = {}
    gs["Z8"] = [[(i + j) % 8 for j in range(8)] for i in range(8)]
    # Z4xZ2: x = 2*i + j, i in Z4, j in Z2
    def enc42(i, j): return 2 * (i % 4) + (j % 2)
    gs["Z4xZ2"] = [[enc42(x // 2 + y // 2, x % 2 + y % 2) for y in range(8)] for x in range(8)]
    gs["Z2^3"] = [[x ^ y for y in range(8)] for x in range(8)]
    # D4: r^i s^j -> x = 2*i + j ; s r = r^-1 s
    def d4(x, y):
        i1, j1 = divmod(x, 2)
        i2, j2 = divmod(y, 2)
        if j1 == 0:
            return 2 * ((i1 + i2) % 4) + j2
        return 2 * ((i1 - i2) % 4) + (1 - j2 if j2 else 1)
    gs["D4"] = [[d4(x, y) for y in range(8)] for x in range(8)]
    # Q8: elements +-1, +-i, +-j, +-k ; encode sign*unit: x = 2*u + s, u in {1,i,j,k}=0..3
    unit_mul = {  # (u,v) -> (sign, w)
        (0, 0): (1, 0), (0, 1): (1, 1), (0, 2): (1, 2), (0, 3): (1, 3),
        (1, 0): (1, 1), (1, 1): (-1, 0), (1, 2): (1, 3), (1, 3): (-1, 2),
        (2, 0): (1, 2), (2, 1): (-1, 3), (2, 2): (-1, 0), (2, 3): (1, 1),
        (3, 0): (1, 3), (3, 1): (1, 2), (3, 2): (-1, 1), (3, 3): (-1, 0),
    }
    def q8(x, y):
        u, s1 = divmod(x, 2)
        v, s2 = divmod(y, 2)
        sg, w = unit_mul[(u, v)]
        neg = (s1 + s2 + (sg < 0)) % 2
        return 2 * w + neg
    gs["Q8"] = [[q8(x, y) for y in range(8)] for x in range(8)]
    return gs


def check_group(T):
    n = len(T)
    e = 0
    assert all(T[e][x] == x and T[x][e] == x for x in range(n))
    for x in range(n):
        assert sorted(T[x]) == list(range(n))
        assert any(T[x][y] == e for y in range(n))
    for x, y, z in itertools.product(range(n), repeat=3):
        assert T[T[x][y]][z] == T[x][T[y][z]]


def homs_to_Z4(P):
    out = []
    for f in itertools.product(range(4), repeat=8):
        if f[0] != 0:
            continue
        if all(f[P[x][y]] == (f[x] + f[y]) % 4 for x in range(8) for y in range(8)):
            out.append(f)
    return out


def semidirect(P, phi):
    T = [[0] * 40 for _ in range(40)]
    for g in range(40):
        a, x = divmod(g, 8)
        m = pow(2, phi[x], 5)
        for h in range(40):
            b, y = divmod(h, 8)
            T[g][h] = 8 * ((a + m * b) % 5) + P[x][y]
    return T


def orders(T):
    n = len(T)
    out = []
    for g in range(n):
        k, x = 1, g
        while x != 0:
            x = T[x][g]
            k += 1
        out.append(k)
    return out


def invariants(T):
    n = len(T)
    o = orders(T)
    inv = [next(y for y in range(n) if T[x][y] == 0) for x in range(n)]
    center = sum(all(T[g][h] == T[h][g] for h in range(n)) for g in range(n))
    commuting = sum(T[g][h] == T[h][g] for g in range(n) for h in range(n))
    comms = {T[T[g][h]][T[inv[g]][inv[h]]] for g in range(n) for h in range(n)}
    # derived subgroup = closure of commutators
    D = set(comms) | {0}
    while True:
        new = {T[a][b] for a in D for b in D} | D
        if new == D:
            break
        D = new
    sq = Counter(T[g][g] for g in range(n))
    return (tuple(sorted(Counter(o).items())), center, commuting, len(D),
            tuple(sorted(sq.values())))


def generators(T):
    """Small generating set (greedy)."""
    n = len(T)
    o = orders(T)
    gens, H = [], {0}
    for g in sorted(range(n), key=lambda g: -o[g]):
        if g in H:
            continue
        gens.append(g)
        H = closure(T, gens)
        if len(H) == n:
            break
    return gens


def closure(T, gens):
    H = {0}
    frontier = [0]
    while frontier:
        x = frontier.pop()
        for g in gens:
            y = T[x][g]
            if y not in H:
                H.add(y)
                frontier.append(y)
    return H


def isomorphic(T1, T2):
    """Try all images of a generating set of T1 in T2 with matching element orders."""
    n = len(T1)
    o1, o2 = orders(T1), orders(T2)
    gens = generators(T1)
    # words: express every element of T1 as product of generators (BFS tree)
    word = {0: ()}
    frontier = [0]
    while frontier:
        nf = []
        for x in frontier:
            for i, g in enumerate(gens):
                y = T1[x][g]
                if y not in word:
                    word[y] = word[x] + (i,)
                    nf.append(y)
        frontier = nf
    cands = [[h for h in range(n) if o2[h] == o1[g]] for g in gens]
    for imgs in itertools.product(*cands):
        f = [None] * n
        for x, w in word.items():
            y = 0
            for i in w:
                y = T2[y][imgs[i]]
            f[x] = y
        if len(set(f)) != n:
            continue
        if all(f[T1[a][b]] == T2[f[a]][f[b]] for a in range(n) for b in range(n)):
            return True
    return False


def main():
    P8 = group_of_order8()
    for name, P in P8.items():
        check_group(P)
    built = []
    for name, P in P8.items():
        for phi in homs_to_Z4(P):
            T = semidirect(P, phi)
            built.append((name, phi, T))
    classes = []  # list of (name, phi, T, inv)
    for name, phi, T in built:
        inv = invariants(T)
        found = False
        for c in classes:
            if c[3] == inv and isomorphic(T, c[2]):
                found = True
                break
        if not found:
            check_group(T)
            classes.append((name, phi, T, inv))
    print(f"semidirect products built: {len(built)}; isomorphism classes: {len(classes)}")
    # pairwise non-isomorphism double check
    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            if classes[i][3] == classes[j][3]:
                assert not isomorphic(classes[i][2], classes[j][2])
    os.makedirs(os.path.join(HERE, "groups"), exist_ok=True)
    with open(os.path.join(HERE, "groups", "index.txt"), "w") as idx:
        idx.write("# id  P  phi(image orders)  |Z|  |G'|  abelian  order-profile\n")
        for i, (name, phi, T, inv) in enumerate(classes):
            img = len(set(phi))
            ab = inv[2] == 1600
            line = f"G{i}  P={name}  |phi(P)|={img}  |Z|={inv[1]}  |G'|={inv[3]}  abelian={ab}  orders={dict(inv[0])}"
            print(line)
            idx.write(line + "\n")
            with open(os.path.join(HERE, "groups", f"G{i}.txt"), "w") as f:
                f.write("40\n")
                for row in T:
                    f.write(" ".join(map(str, row)) + "\n")
    assert len(classes) == 14, "expected 14 groups of order 40"


if __name__ == "__main__":
    main()
