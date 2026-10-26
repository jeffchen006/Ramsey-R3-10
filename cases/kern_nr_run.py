"""Near-regular edge-kernel completion runner (codex_strategy_3.md Sec 3). Author: cases, 2026-10-26.
Adapted from duo/kernel_run2.py (same smsg call: -a all completions, timeouts stay pending), without --aut.
Base: sms/gen_ramsey.py -n 40 -k 10 --mtf --codeg-max M --dmin dlo --dmax dhi, plus EXACT degree distribution:
per vertex an equivalence sequential counter (R_j <=> deg >= j), y_{v,d} <=> R_d & -R_{d+1}, exactly one y_{v,d},
and sum_v y_{v,d} = n_d. Kernel: u=0 (deg a), v=1 (deg b), A = 2..a, B = a+1..a+b-1 (kagg/genbg class1 -> A),
u-v, u-A, v-B edges; all other pairs at u, v and inside A x B fixed. Not encoded (sound relaxation): sel gluing
exclusions e(H_v) >= L_d, the L6 per-pair codegree cap, min-e(F) choice of the edge.
Usage: kern_nr_run.py SAMPLEFILE outdir timeout workers   [k]  (k only for positive controls; SAMPLE lines: 'n4..n9 M a b g6', n's comma-separated)"""
import sys, os, time, subprocess
from multiprocessing import Pool
R = '.'; SMSG = R + '/sms/sms-src/build/src/smsg'
sys.path.insert(0, R + '/sms')
from gen_ramsey import Enc
N = 40
KIS = '10'

def g6(s):
    n = ord(s[0]) - 63; bits = []
    for ch in s[1:]:
        x = ord(ch) - 63; bits += [(x >> (5 - t)) & 1 for t in range(6)]
    E = set(); k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: E.add((i, j))
            k += 1
    return n, E

def base_cnf(nd, M, path):
    degs = [d for d in range(4, 4 + len(nd)) if nd[d - 4]]   # len(nd) = 7 (degree 10) only in controls
    if not os.path.exists(path):
        subprocess.run(['python3', R + '/sms/gen_ramsey.py', '-n', '40', '-k', KIS, '--mtf', '--codeg-max', str(M),
                        '--dmin', str(min(degs)), '--dmax', str(max(degs)), '-o', path], check=True)
    hdr, body = open(path).read().split('\n', 1)
    nv, nc = map(int, hdr.split()[2:4])
    E = Enc(N); E.nvars = nv
    y = {}
    for v in range(N):
        lits = [E.e(v, u) for u in range(N) if u != v]
        K = max(degs) + 1
        prev = None
        for i, l in enumerate(lits):        # cur[j] <=> at least j+1 of lits[0..i]
            cur = [E.new() for _ in range(K)]
            for j in range(K):
                a = prev[j] if prev else None
                b = (prev[j - 1] if j else None) if prev else None
                # cur_j <=> a or (l and (j==0 or b))
                if a: E.clauses.append([-a, cur[j]])
                if j == 0: E.clauses.append([-l, cur[j]])
                elif b: E.clauses.append([-l, -b, cur[j]])
                rhs = [-cur[j]] + ([a] if a else [])
                E.clauses.append(rhs + [l])
                if j > 0: E.clauses.append(rhs + ([b] if b else []))
            prev = cur
        Rg = prev   # Rg[j] <=> deg >= j+1
        for d in degs:
            t = E.new(); y[(v, d)] = t
            E.clauses += [[-t, Rg[d - 1]], [-t, -Rg[d]], [t, -Rg[d - 1], Rg[d]]]
        E.clauses.append([y[(v, d)] for d in degs])
        for d1 in degs:
            for d2 in degs:
                if d1 < d2: E.clauses.append([-y[(v, d1)], -y[(v, d2)]])
    for d in degs:
        E.counter([y[(v, d)] for v in range(N)], nd[d - 4], nd[d - 4])
    return nv, nc, body, E, y

def run(arg):
    idx, line, OUT, TO = arg
    f = line.split(); nd = list(map(int, f[0].split(','))); M, a, b = map(int, f[1:4]); s = f[4]
    key = f"{'_'.join(map(str, nd))}_M{M}"
    nv, nc, body, E, y = base_cnf(nd, M, f'{OUT}/base_{key}.cnf')
    n, F = g6(s); assert n == a + b - 2
    A = list(range(2, a + 1)); B = list(range(a + 1, a + b)); X = list(range(a + b, N))
    U = [[E.e(0, 1)]] + [[E.e(0, x)] for x in A] + [[E.e(1, x)] for x in B]
    U += [[-E.e(0, x)] for x in B + X] + [[-E.e(1, x)] for x in A + X]
    for i in range(a - 1):
        for j in range(b - 1):
            U.append([E.e(A[i], B[j])] if (i, a - 1 + j) in F else [-E.e(A[i], B[j])])
    U += [[y[(0, a)]], [y[(1, b)]]]
    cl = E.clauses + U
    cnf = f'{OUT}/k{idx}.cnf'
    with open(cnf, 'w') as fh:
        fh.write(f'p cnf {E.nvars} {nc + len(cl)}\n'); fh.write(body)
        fh.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in cl))
    cells = [str(x) for x in [1] * (a + b) + [N - a - b]]
    t = time.time()
    try:
        p = subprocess.run([SMSG, '-v', '40', '--dimacs', cnf, '--forbid-independent-set', KIS, '--cutoff', '0', '-a',
                            '--initial-partition', *cells], capture_output=True, text=True, timeout=TO)
        sols = [l for l in p.stdout.splitlines() if l.startswith('[(')]; st = f'rc={p.returncode} sols={len(sols)}'
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
        sols = [l for l in out.splitlines() if l.startswith('[(')]; st = f'TIMEOUT sols={len(sols)}'
    os.remove(cnf)
    if sols: open(f'{OUT}/k{idx}.sol', 'w').write('\n'.join(sols) + '\n')
    return idx, line, st, time.time() - t

if __name__ == '__main__':
    KF, OUT, TO, W = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
    if len(sys.argv) > 5: KIS = sys.argv[5]  # positive controls only (e.g. 11)
    os.makedirs(OUT, exist_ok=True)
    L = [l.strip() for l in open(KF) if l.strip() and not l.startswith('#')]
    done = set()
    if os.path.exists(f'{OUT}/res.txt'):
        done = {int(l.split()[0]) for l in open(f'{OUT}/res.txt') if 'TIMEOUT' not in l}
    todo = [(i, l, OUT, TO) for i, l in enumerate(L) if i not in done]
    print('kernels', len(L), 'todo', len(todo), flush=True)
    # build base CNFs serially first (avoid races)
    for k in sorted({' '.join(l.split()[:2]) for _, l, _, _ in todo}):
        nd = list(map(int, k.split()[0].split(','))); M = int(k.split()[1])
        base_cnf(nd, M, f"{OUT}/base_{'_'.join(map(str, nd))}_M{M}.cnf")
    with Pool(W) as P, open(f'{OUT}/res.txt', 'a') as R_:
        for idx, line, st, dt in P.imap_unordered(run, todo):
            R_.write(f'{idx} {line} {st} {dt:.1f}\n'); R_.flush()
    print('done', flush=True)
