import sys; sys.path.insert(0, '.'); sys.path.insert(0, './critic/src')
from myglue import parse
from gen_tests import g6
n, A = parse(open('./data/graphs/exoo/exoo39.g6').read().split()[0])
deg = [bin(a).count('1') for a in A]; print('degrees', sorted(set(deg)), file=sys.stderr)
for dd in sorted(set(deg)):
    v = deg.index(dd); keep = [w for w in range(n) if w != v and not A[v] >> w & 1]
    idx = {w: i for i, w in enumerate(keep)}
    E = [(idx[a], idx[b]) for a in keep for b in keep if a < b and A[a] >> b & 1]
    print(dd, g6(len(keep), E))
