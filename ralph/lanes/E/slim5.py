#!/usr/bin/env python3
"""Order-five SAT with fixed attachments pinned; optionally write and check DRAT."""
import argparse
from itertools import combinations
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
from orbit_run import ROOT, pairmap, parse_graph6, report, setup, verify_sc


def build(size, target, fixed, template):
    moved = size - fixed
    spec = setup(5, fixed, size, target, None, False)
    sigma = spec['generators'][0]
    orbit_count = moved // 5

    def keeps_pins(perm):
        return all(perm[index] == index for index in range(moved, size)) and all(
            perm[index] // 5 == index // 5 for index in range(moved)) and all(
            (perm[index+1] - perm[index]) % 5 == 1 for index in range(0, moved, 5))

    breakers = [perm for perm in spec['breakers'] if keeps_pins(perm)]
    identity = list(range(size))
    for first, second in combinations(range(fixed), 2):
        perm = identity.copy()
        for phase in range(5):
            perm[5*first+phase], perm[5*second+phase] = 5*second+phase, 5*first+phase
        perm[moved+first], perm[moved+second] = moved+second, moved+first
        breakers.append(perm)
    if template[0] == template[1]:
        perm = identity.copy()
        for phase in range(5):
            perm[5*fixed+phase], perm[5*(fixed+1)+phase] = 5*(fixed+1)+phase, 5*fixed+phase
        breakers.append(perm)

    mapping, num_vars, image = verify_sc.orbit_vars(size, [sigma])
    clauses, top = verify_sc.lex_clauses(size, mapping, num_vars, image, breakers)
    for index in range(fixed):
        for orbit in range(orbit_count):
            literal = mapping[5*orbit, moved+index]
            clauses.append((literal if index == orbit else -literal,))
    for orbit, kind in enumerate('I' * fixed + template):
        for diff, present in ((1, kind == 'C'), (2, kind == 'D')):
            literal = mapping[5*orbit, 5*orbit+diff]
            clauses.append((literal if present else -literal,))

    return sigma, mapping, clauses, top, num_vars


def need(condition, reason):
    if not condition:
        sys.exit('RESULT: NOT VERIFIED (' + reason + ')')


def check(prefix, size, target, mapping, extra, num_vars):
    checked_mapping = {}
    with open(prefix + '.map') as handle:
        for line in handle:
            first, second, literal = map(int, line.split())
            need((first, second) not in checked_mapping, 'duplicate pair')
            checked_mapping[first, second] = literal
    need(checked_mapping == mapping, 'orbit map differs from reference')
    allowed = set(map(frozenset, extra))
    for first, second, third in combinations(range(size), 3):
        allowed.add(frozenset((-mapping[first, second], -mapping[first, third], -mapping[second, third])))
    with open(prefix + '.base.cnf') as handle:
        base_count = int(next(line for line in handle if line.startswith('p cnf ')).split()[3])
    clause_index = 0
    with open(prefix + '.full.cnf') as handle, open(prefix + '.ext.sets') as hints:
        header, _, top, total = handle.readline().split()
        need(header == 'p' and _ == 'cnf' and int(total) >= base_count, 'bad full CNF header')
        for line in handle:
            literals = list(map(int, line.split()))
            need(bool(literals) and literals[-1] == 0 and all(0 < abs(lit) <= int(top)
                                                             for lit in literals[:-1]), 'bad CNF clause')
            clause_index += 1
            clause = frozenset(literals[:-1])
            if clause_index <= base_count:
                need(clause in allowed, f'unexplained base clause #{clause_index}')
            else:
                witness = sorted(map(int, hints.readline().split()))
                need(len(witness) == len(set(witness)) == target
                     and witness[0] >= 0 and witness[-1] < size, f'bad witness #{clause_index}')
                need(all(0 < literal <= num_vars for literal in clause)
                     and all(mapping[pair] in clause for pair in combinations(witness, 2)),
                     f'witness does not imply clause #{clause_index}')
        need(not hints.read(1) and clause_index == int(total), 'wrong number of clauses/witnesses')
    print(f'case n={size} K={target}; checked {base_count} base and {clause_index - base_count} lazy clauses')
    result = subprocess.run([str(ROOT / 'opt/bin/drat-trim'), prefix + '.full.cnf', prefix + '.drat'],
                            capture_output=True, text=True)
    status = [line.strip() for line in result.stdout.splitlines() if line.startswith('s ')]
    print('drat-trim:', status)
    need(result.returncode == 0 and status == ['s VERIFIED'], 'DRAT failed')
    print('RESULT: VERIFIED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template', choices=['II', 'IC', 'CC', 'CD'])
    parser.add_argument('prefix')
    parser.add_argument('--n', type=int, choices=[22, 40], default=40)
    parser.add_argument('--time', type=int, default=120)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--search-only', action='store_true')
    args = parser.parse_args()
    size = args.n
    target, fixed = (7, 2) if size == 22 else (10, 5)
    prefix = args.prefix
    sigma, mapping, extra, top, num_vars = build(size, target, fixed, args.template)
    print(f'case n={size} K={target} p=5 f={fixed} injective attachments, residual type={args.template}')
    if not args.check:
        independent_map = pairmap(size, 5, sigma)
        Path(prefix + '.map').write_text(''.join(f'{left} {right} {var}\n'
                                                 for (left, right), var in sorted(independent_map.items())))
        with open(prefix + '.pin.cnf', 'w') as handle:
            print('p cnf', top, len(extra), file=handle)
            for clause in extra:
                print(*clause, 0, file=handle)
        outfile = Path(prefix + '.g6')
        outfile.unlink(missing_ok=True)
        command = [str(ROOT / 'scratch/E/bin/satcore'), '-n', str(size), '-k', str(target),
                   '--pairmap', prefix + '.map', '--extra', prefix + '.pin.cnf', '--out', str(outfile),
                   '--report', '30', '--time', str(args.time)]
        if not args.search_only:
            command += ['--proof', prefix]
        result = subprocess.run(command).returncode
        if result == 0:
            sys.exit('UNKNOWN')
        if result == 10:
            graph = outfile.read_text().strip()
            adj = parse_graph6(graph)
            if (len(adj) != size or not report(adj, target)
                    or not all(adj[left] >> right & 1 == adj[sigma[left]] >> sigma[right] & 1
                               for left, right in mapping)):
                sys.exit('INVALID SAT model')
            if size == 40:
                (ROOT / 'ralph/found' / ('E_' + outfile.name)).write_text(graph + '\n')
            return
        if result != 20:
            sys.exit(f'ERROR: solver return code {result}')
        if args.search_only:
            print('RESULT: UNSAT (unchecked)')
            return
    check(prefix, size, target, mapping, extra, num_vars)


if __name__ == '__main__':
    main()
