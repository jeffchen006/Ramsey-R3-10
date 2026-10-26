"""D5 / Z5 actions on 40 points with mixed orbit types. Orbit types for D5 = <r,s>:
'R' regular (10 points), 'N' natural action on 5 points (cosets of <s>), 'T' 2 points (cosets of <r>), 'F' fixed.
usage: mkmixed.py SPEC ...   SPEC like D5:R3N2  (3 regular + 2 natural orbits) ; letters with counts."""
import sys, re
sys.path.insert(0, '.')
import groups, orbits

def d5_orbit(t):
    if t == 'R':
        r, s = groups.dihedral(5); return list(r), list(s)
    if t == 'N': return [(i + 1) % 5 for i in range(5)], [(-i) % 5 for i in range(5)]
    if t == 'T': return [0, 1], [1, 0]
    if t == 'F': return [0], [0]

def build(spec):
    parts = re.findall(r'([RNTF])(\d+)', spec.split(':')[1])
    R, S = [], []
    for t, c in parts:
        for _ in range(int(c)):
            r, s = d5_orbit(t); off = len(R)
            R += [off + x for x in r]; S += [off + x for x in s]
    assert len(R) == 40, (spec, len(R))
    return [R, S]

for spec in sys.argv[1:]:
    gens = build(spec)
    if spec.startswith('Z5'): gens = gens[:1]  # rotation only
    orbs = orbits.pair_orbits(40, gens)
    fn = f"orb/m40_{spec.replace(':', '_')}.txt"
    orbits.write(40, 10, orbs, fn); print(fn, len(orbs))
