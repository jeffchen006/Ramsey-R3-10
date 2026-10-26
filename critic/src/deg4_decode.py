"""critic: drop clauses of one J-size from deg4.cnf, solve, decode model into a 40-vertex graph (g6)."""
import sys, subprocess
sys.path.insert(0, './critic/src')
from gen_tests import g6
drop = int(sys.argv[1])  # clause length to drop: 6*4=24 (|J|=6), 7*3=21 (|J|=7), 8*2=16 (|J|=8)
L = open('deg4.cnf').read().split('\n')
cl = [l for l in L[1:] if l.strip() and len(l.split()) - 1 != drop]
open('relax.cnf', 'w').write('p cnf 140 %d\n' % len(cl) + '\n'.join(cl) + '\n')
out = subprocess.run(['./tools/bin/cadical', '-q', 'relax.cnf'], capture_output=True, text=True).stdout
if 's SATISFIABLE' not in out: print('drop', drop, 'UNSAT'); sys.exit()
lits = [int(t) for l in out.split('\n') if l.startswith('v') for t in l.split()[1:]]
true = {t for t in lits if t > 0}
n = 35; Dd = {1, 7, 11, 16, 34, 28, 24, 19}
E = [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) % n in Dd]
v, A = 35, [36, 37, 38, 39]
E += [(v, a) for a in A] + [(u, A[c]) for u in range(n) for c in range(4) if 4 * u + c + 1 in true]
print(g6(40, E))
