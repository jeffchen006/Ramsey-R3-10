"""Make orbit files for n=40 symmetric classes: mkclass.py NAME:FIXED ..."""
import sys
sys.path.insert(0, '.')
import groups, orbits
for spec in sys.argv[1:]:
    name, fixed = spec.split(':'); fixed = int(fixed)
    gens = groups.action(name, 40, fixed)
    orbs = orbits.pair_orbits(40, gens)
    fn = f"orb/n40_{name}_f{fixed}.txt"
    orbits.write(40, 10, orbs, fn)
    print(fn, len(orbs))
