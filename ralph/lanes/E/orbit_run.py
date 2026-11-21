#!/usr/bin/env python3
"""Lane E driver; all outputs are relative to the job's scratch directory."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT / name) for name in ('symsat', 'tools')]
from check_graph import parse_graph6, report
import verify_sc


def setup(order, fixed, size, target, amax, full):
    moved = size - fixed
    identity = list(range(size))
    orbits = list(range(0, moved, order))
    sigma = [base + ((position + 1) % order) for base in orbits
             for position in range(order)] + identity[moved:]
    breakers = []
    for base in orbits:
        perm = identity.copy()
        perm[base:base + order] = sigma[base:base + order]
        breakers.append(perm)
    for multiplier in range(2, order):
        if len({pow(multiplier, exp, order) for exp in range(order - 1)}) == order - 1:
            perm = identity.copy()
            for base in orbits:
                perm[base:base + order] = [base + (multiplier * pos) % order for pos in range(order)]
            breakers.append(perm)
            break
    group = list(range(moved, size))
    if amax is None:
        swaps = [(orbits, order), (group, 1)]
    else:
        swaps = [(orbits[1:], order), (group[:amax], 1), (group[amax:], 1)]
    for starts, width in swaps:
        pairs = combinations(starts, 2) if full else zip(starts, starts[1:])
        for left, right in pairs:
            perm = identity.copy()
            perm[left:left + width], perm[right:right + width] = (
                perm[right:right + width], perm[left:left + width])
            breakers.append(perm)
    spec = dict(n=size, K=target, p=order, f=fixed, generators=[sigma], breakers=breakers)
    if amax is not None:
        spec.update(amax=amax, A=group[:amax], B=group[amax:])
    return spec


def pairmap(size, order, sigma):
    mapping = {}
    count = 0
    for pair in combinations(range(size), 2):
        if pair not in mapping:
            count += 1
            left, right = pair
            for _ in range(order):
                mapping[tuple(sorted((left, right)))] = count
                left, right = sigma[left], sigma[right]
    return mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('p', type=int)
    parser.add_argument('f', type=int)
    parser.add_argument('prefix')
    parser.add_argument('--n', type=int, default=40)
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--amax', type=int)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--time', type=int, default=120)
    parser.add_argument('--search-only', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--boost', choices=['degree', 'quotient', 'seeded'])
    parser.add_argument('--dmin', type=int, choices=[4, 5])
    parser.add_argument('--extra', nargs='*', default=[])
    args = parser.parse_args()
    if (not 0 <= args.f < args.n or args.p not in (2, 3, 5, 7)
            or (args.n - args.f) % args.p or (args.amax is not None and not 1 <= args.amax <= args.f)):
        parser.error('bad orbit parameters')
    if args.boost and (args.p != 3 or not args.search_only or args.check_only):
        parser.error('boosted rows currently require order three and --search-only')
    if args.dmin is not None and (not args.boost or (args.n, args.k) != (40, 10)):
        parser.error('--dmin is only supported on boosted (3,10,40) jobs')
    prefix = args.prefix
    specfile, mapfile = prefix + '.spec.json', prefix + '.map'
    verify_sc.DRAT = str(ROOT / 'opt/bin/drat-trim')
    verify_sc_path = str(ROOT / 'symsat/verify_sc.py')
    spec = setup(args.p, args.f, args.n, args.k, args.amax, args.full)
    sigma = spec['generators'][0]
    if not args.check_only:
        Path(specfile).write_text(json.dumps(spec))
        mapping = pairmap(args.n, args.p, sigma)
        Path(mapfile).write_text(''.join(f'{left} {right} {var}\n'
                                      for (left, right), var in sorted(mapping.items())))
        lexfile = prefix + '.lex.cnf'
        subprocess.run([sys.executable, verify_sc_path, 'lex', specfile, lexfile], check=True)
        graphfile = Path(prefix + '.g6')
        graphfile.unlink(missing_ok=True)
        cmd = [str(ROOT / 'scratch/E/bin/satcore'), '-n', str(args.n), '-k', str(args.k),
               '--pairmap', mapfile, '--extra', lexfile, '--out', str(graphfile), '--report', '30',
               '--time', str(args.time)]
        if not args.search_only:
            cmd += ['--proof', prefix]
        if args.boost:
            import orbit_boost
            with open(lexfile) as lex:
                top = int(lex.readline().split()[2])
            rows = orbit_boost.build(spec, mapping, top, args.boost, args.dmin)
            boostfile = prefix + '.boost.cnf'
            rows.write(boostfile)
            cmd += ['--extra', boostfile]
            print(f'boost={args.boost}, extra clauses={len(rows.clauses)}, maxvar={rows.top}')
        result = subprocess.run(cmd + args.extra).returncode
        if result == 10:
            graph = graphfile.read_text().strip()
            adj = parse_graph6(graph)
            if (len(adj) != args.n or not report(adj, args.k)
                    or not all(adj[left] >> right & 1 == adj[sigma[left]] >> sigma[right] & 1
                               for left, right in mapping)):
                sys.exit('INVALID SAT model')
            if args.amax is not None:
                fixed_mask = ((1 << args.f) - 1) << (args.n - args.f)
                if max((row & fixed_mask).bit_count() for row in adj[:args.n-args.f]) != args.amax:
                    sys.exit('SAT model outside subcase')
            if (args.n, args.k) == (40, 10):
                (ROOT / 'ralph/found' / ('E_' + graphfile.name)).write_text(graph + '\n')
            return
        if result != 20:
            sys.exit('UNKNOWN' if result == 0 else f'ERROR: solver return code {result}')
        if args.search_only:
            print('RESULT: UNSAT (unchecked)')
            return
    sys.argv = [verify_sc_path, 'check', specfile, mapfile, prefix,
                *map(str, (args.n, args.k, args.p, args.f))]
    verify_sc.main()


if __name__ == '__main__':
    main()
