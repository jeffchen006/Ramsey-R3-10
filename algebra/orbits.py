"""Write pair-orbit files for otabu.
usage: orbits.py n k spec out
spec: 'none'                 every pair its own orbit
      'cyc:g'                Z_g acting freely with n/g orbits (i -> i+n/g... block layout: v = (orbit, element))
      'perm:p1;p2'           generators as comma lists of images
"""
import sys

def pair_orbits(n, gens):
    seen = set(); orbs = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in seen: continue
            orb = {(i, j)}; stack = [(i, j)]
            while stack:
                a, b = stack.pop()
                for g in gens:
                    c, d = g[a], g[b]
                    e = (min(c, d), max(c, d))
                    if e not in orb: orb.add(e); stack.append(e)
            seen |= orb
            if any(a == b for a, b in orb): continue
            orbs.append(sorted(orb))
    return orbs

def cyc_gen(n, g):
    m = n // g  # vertex (o, e) = o*g + e
    return [[(v // g) * g + ((v % g) + 1) % g for v in range(n)]]

def write(n, k, orbs, out, groups=None):
    with open(out, 'w') as f:
        f.write(f"{n} {k} {len(orbs)}\n")
        for idx, o in enumerate(orbs):
            g = -1 if groups is None else groups[idx]
            f.write(f"{g} {len(o)} " + " ".join(f"{a} {b}" for a, b in o) + "\n")

if __name__ == '__main__':
    n, k, spec, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
    if spec == 'none': gens = []
    elif spec.startswith('cyc:'): gens = cyc_gen(n, int(spec[4:]))
    elif spec.startswith('perm:'): gens = [list(map(int, p.split(','))) for p in spec[5:].split(';')]
    orbs = pair_orbits(n, gens)
    write(n, k, orbs, out)
    print(len(orbs), 'orbits')
