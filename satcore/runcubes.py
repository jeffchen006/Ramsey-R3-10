#!/usr/bin/env python3
"""Cube-and-conquer driver for satcore.

usage: runcubes.py --cpus 52,53,54 --cubes CUBES --dir OUTDIR [--time SEC] [--proof] -- SATCORE_ARGS...

Each line of CUBES (literals, 0-terminated) becomes an extra unit-clause file; the
satcore run for cube i gets `--extra OUTDIR/cube_i.cnf` and logs to OUTDIR/cube_i.log
(with --proof also `--proof OUTDIR/cube_i --lrat`). One worker per CPU, pinned with
taskset. Results are appended to OUTDIR/results.tsv (cube, status, seconds) as they
finish; finished cubes are skipped on restart. Stops early on the first SAT cube.
Note: the cube disjunction must be a tautology for UNSAT of all cubes to imply UNSAT;
CaDiCaL lookahead cubes (--gen-cubes) are complete splits of the base CNF.
"""
import os, subprocess, sys, threading, time, queue

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'satcore')

def main():
    a = sys.argv[1:]
    sep = a.index('--')
    opts, sargs = a[:sep], a[sep + 1:]
    o = {'--time': '0', '--proof': None}
    i = 0
    while i < len(opts):
        if opts[i] == '--proof': o['--proof'] = True; i += 1
        else: o[opts[i]] = opts[i + 1]; i += 2
    cpus = o['--cpus'].split(',')
    out = o['--dir']
    os.makedirs(out, exist_ok=True)
    cubes = [l.split()[:-1] for l in open(o['--cubes']) if l.strip()]
    done = {}
    res_path = os.path.join(out, 'results.tsv')
    if os.path.exists(res_path):
        for l in open(res_path):
            c, st, t = l.split('\t'); done[int(c)] = st
    q = queue.Queue()
    for ci, cube in enumerate(cubes):
        if ci in done: continue
        with open(os.path.join(out, 'cube_%d.cnf' % ci), 'w') as f:
            for lit in cube: f.write('%s 0\n' % lit)
        q.put(ci)
    lock = threading.Lock()
    found = threading.Event()

    def worker(cpu):
        while not found.is_set():
            try: ci = q.get_nowait()
            except queue.Empty: return
            cmd = ['taskset', '-c', cpu, 'nice', '-n', '5', BIN] + sargs + \
                  ['--extra', os.path.join(out, 'cube_%d.cnf' % ci), '-q']
            if o['--time'] != '0': cmd += ['--time', o['--time']]
            if o['--proof']: cmd += ['--proof', os.path.join(out, 'cube_%d' % ci), '--lrat']
            t0 = time.time()
            with open(os.path.join(out, 'cube_%d.log' % ci), 'w') as lf:
                r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT).returncode
            st = {10: 'SAT', 20: 'UNSAT'}.get(r, 'UNKNOWN(%d)' % r)
            with lock:
                with open(res_path, 'a') as f: f.write('%d\t%s\t%.2f\n' % (ci, st, time.time() - t0))
            if st == 'SAT': found.set()

    th = [threading.Thread(target=worker, args=(c,)) for c in cpus]
    for t in th: t.start()
    for t in th: t.join()
    sts = [l.split('\t')[1] for l in open(res_path)]
    print('cubes=%d finished=%d UNSAT=%d SAT=%d other=%d' % (
        len(cubes), len(sts), sts.count('UNSAT'), sts.count('SAT'),
        len(sts) - sts.count('UNSAT') - sts.count('SAT')))

if __name__ == '__main__':
    main()
