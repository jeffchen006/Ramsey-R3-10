"""Level-set graphs: vertices V (40 points), adjacency u~v iff f(u,v) in S. Classes = level sets of f.
Writes class files for otabu (free bits) and runs exhaustive orbex when feasible.
usage: levelset.py            (builds all families into orb/ls_*.txt and prints class counts)"""
import sys, itertools
sys.path.insert(0, './algebra')
import orbits

def classes(V, f):
    lab = {}
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            lab.setdefault(f(V[i], V[j]), []).append((i, j))
    return list(lab.values())

p = 41
F41s = list(range(1, 41))
FAMS = {
    'f41_sum': (F41s, lambda x, y: (x + y) % p),
    'f41_sq': (F41s, lambda x, y: (x * x + y * y) % p),
    'f41_cub': (F41s, lambda x, y: (x ** 3 + y ** 3) % p),
    'f41_sumprod1': (F41s, lambda x, y: (x + y + x * y) % p),
    'f41_sumprod3': (F41s, lambda x, y: (x + y + 3 * x * y) % p),
    'f41_x2y': (F41s, lambda x, y: (x * x * y + x * y * y) % p),
    'f41_sq_plus_prod': (F41s, lambda x, y: (x * x + y * y + 5 * x * y) % p),
    'f41_sum_and_prodQR': (F41s, lambda x, y: ((x + y) % p, pow(x * y % p, 20, p))),
    'f41_diff_and_sumQR': (F41s, lambda x, y: (min((x - y) % p, (y - x) % p), pow((x + y) % p, 20, p) if (x + y) % p else 0)),
    'z40_sum': (list(range(40)), lambda x, y: (x + y) % 40),
    'z40_sq': (list(range(40)), lambda x, y: (x * x + y * y) % 40),
    'z5z8_sum': ([(a, b) for a in range(5) for b in range(8)], lambda u, v: ((u[0] + v[0]) % 5, (u[1] + v[1]) % 8)),
    'z5z8_mix': ([(a, b) for a in range(5) for b in range(8)], lambda u, v: ((u[0] + v[0]) % 5, min((u[1] - v[1]) % 8, (v[1] - u[1]) % 8))),
    'z5z8_mix2': ([(a, b) for a in range(5) for b in range(8)], lambda u, v: (min((u[0] - v[0]) % 5, (v[0] - u[0]) % 5), (u[1] + v[1]) % 8)),
    'z2z20_mix': ([(a, b) for a in range(2) for b in range(20)], lambda u, v: ((u[0] + v[0]) % 2, (u[1] + v[1]) % 20)),
    'f5f8_sumsq': ([(a, b) for a in range(5) for b in range(8)], lambda u, v: ((u[0] ** 2 + v[0] ** 2) % 5, u[1] ^ v[1])),
}

if __name__ == '__main__':
    for name, (V, f) in FAMS.items():
        cl = classes(V, f)
        orbits.write(40, 10, cl, f'orb/ls_{name}.txt')
        print(name, len(cl))
