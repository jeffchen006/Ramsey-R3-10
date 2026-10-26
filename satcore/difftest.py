#!/usr/bin/env python3
"""Differential test: satcore (up, up --no-props, cegar) vs eager full CNF on cadical.
Random small (3,k,n) instances with random extra unit/binary edge clauses."""
import itertools, random, subprocess, sys, os
R = '.'
BIN = R + '/satcore/bin/satcore'
CAD = R + '/tools/bin/cadical'
TMP = R + '/runs/satcore/tmp'
ev = lambda i, j: j*(j-1)//2 + i + 1 if i < j else i*(i-1)//2 + j + 1
rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
trials = int(sys.argv[2]) if len(sys.argv) > 2 else 100

def sat(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    if 's SATISFIABLE' in out: return 'SAT'
    if 's UNSATISFIABLE' in out: return 'UNSAT'
    return 'UNK:' + out[-300:]

bad = 0; cnt = {}
for t in range(trials):
    n = rnd.randint(7, 13); k = rnd.randint(3, 5)
    nv = n*(n-1)//2
    extra = []
    for _ in range(rnd.randint(0, 2*n)):
        i, j = rnd.sample(range(n), 2)
        if rnd.random() < 0.7: extra.append([rnd.choice([1, -1]) * ev(i, j)])
        else:
            a, b = rnd.sample(range(n), 2)
            if a != b: extra.append([rnd.choice([1, -1]) * ev(i, j), rnd.choice([1, -1]) * ev(a, b)])
    xf = '%s/dx.cnf' % TMP
    with open(xf, 'w') as f:
        for c in extra: f.write(' '.join(map(str, c)) + ' 0\n')
    opts = ['--extra', xf, '--lex'] + (['--mtf'] if rnd.random() < 0.3 else [])
    base = '%s/db.cnf' % TMP
    subprocess.run([BIN, '-n', str(n), '-k', str(k), '--write-cnf', base] + opts, check=True)
    lines = [l for l in open(base) if not l.startswith('c') and not l.startswith('p')]
    hdr = [l for l in open(base) if l.startswith('p')][0].split()
    mv = int(hdr[2])
    isc = [' '.join(str(ev(a, b)) for a, b in itertools.combinations(S, 2)) + ' 0\n'
           for S in itertools.combinations(range(n), k)]
    full = '%s/df.cnf' % TMP
    with open(full, 'w') as f:
        f.write('p cnf %d %d\n' % (mv, len(lines) + len(isc)))
        f.writelines(lines); f.writelines(isc)
    out = subprocess.run([CAD, '-q', full], capture_output=True, text=True).stdout
    ref = 'SAT' if 's SATISFIABLE' in out else 'UNSAT' if 's UNSATISFIABLE' in out else 'UNK'
    res = {}
    for name, extra_opts in [('up', []), ('noprops', ['--no-props']), ('cegar', ['--mode', 'cegar']),
                             ('keep', ['--keep-lazy'])]:
        res[name] = sat([BIN, '-q', '-n', str(n), '-k', str(k)] + opts + extra_opts)
    ok = all(v == ref for v in res.values()); cnt[ref] = cnt.get(ref, 0) + 1
    if not ok:
        bad += 1
        print('MISMATCH n=%d k=%d opts=%s ref=%s %s' % (n, k, opts, ref, res)); os.system('cp %s %s/mismatch_%d.cnf' % (xf, TMP, t))
print('difftest: %d trials, %d mismatches, ref counts %s' % (trials, bad, cnt))
sys.exit(1 if bad else 0)
