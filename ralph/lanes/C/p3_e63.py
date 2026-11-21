"""Bounded P3/e63 proofs with a fixed boundary, optional root caps and twin sorting."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

from pysat.solvers import Solver

from kernel_projection import bits, decode
from p3_minimal import formula_minimal
from p4_factor_proofs import cpu, digest, run
from path_three_top import formula, plant
from verify_p3_boundary import boundary_graph, boundary_test, matches, orbit_key


def boundary_keys():
    result = set()
    for pattern in range(512):
        rows = [(pattern >> (3 * index)) & 7 for index in range(3)]
        mixed = [(left, right) for left, right in product(range(1, 8), repeat=2)
                 if all(not right & rows[index] for index in bits(left))]
        if any(left.bit_count() + right.bit_count() > 4 for left, right in mixed):
            continue
        for (left_a, right_a), (left_b, right_b) in combinations_with_replacement(mixed, 2):
            used = pattern.bit_count() + sum(mask.bit_count() for mask in (left_a, left_b, right_a, right_b))
            if used < 12:
                continue
            for left, right in product(range(1, 8), repeat=2):
                if used + left.bit_count() + right.bit_count() != 18:
                    continue
                if matches((left, left_a, left_b)) and matches((right, right_a, right_b)):
                    result.add(orbit_key(rows, left, right, ((left_a, right_a), (left_b, right_b))))
    assert len(result) == 13 and all(boundary_test(key) == 'pass' for key in result)
    return sorted(result)


def reflect(key):
    pattern, left, right, middle = key
    transpose = [sum(1 << source for source in range(3) if pattern >> (3 * source + target) & 1)
                 for target in range(3)]
    return orbit_key(transpose, right, left, tuple((right, left) for left, right in middle))


def boundary_masks(key):
    return [sum(1 << vertex for vertex in adjacent) for adjacent in boundary_graph(key)]


def twin_groups(boundary):
    groups = defaultdict(list)
    for index, mask in enumerate(boundary[:-3]):
        groups[mask].append(index)
    return groups.values()


def lex_order(clauses, left, right):
    prefix = None
    for slot, (first, second) in enumerate(zip(left, right)):
        guard = [] if prefix is None else [-prefix]
        clauses.append(guard + [-first, second])
        if slot + 1 == len(left):
            break
        next_prefix = clauses.nv + 1
        clauses.append(guard + [first, second, next_prefix])
        clauses.append(guard + [-first, -second, next_prefix])
        prefix = next_prefix


def make_formula(core, boundary, degree, cap, mode):
    if mode.startswith(('min', 'lite')):
        threshold = int(mode[-1])
        clauses, edges = formula_minimal(core, boundary, degree, cap, min(threshold, degree - 3), mode.startswith('min'))
    else:
        clauses, edges = formula(core, boundary, degree, cap)
    if mode == 'baseline':
        return clauses, edges
    for outer_set in twin_groups(boundary):
        for left, right in zip(outer_set, outer_set[1:]):
            lex_order(clauses, [edges[inner, left] for inner in range(len(core))],
                      [edges[inner, right] for inner in range(len(core))])
    if mode == 'root-twins':
        for root in boundary[-3:]:
            for inner in range(len(core)):
                for excess in combinations(bits(root), cap):
                    clauses.append([-edges[inner, outer] for outer in excess])
    return clauses, edges


def control():
    core, boundary, known = plant()
    permutation = list(range(len(boundary)))
    for group in twin_groups(boundary):
        profiles = sorted(group, key=lambda outer: tuple(known[inner] >> (len(core) + outer) & 1
                                                         for inner in range(len(core))))
        for target, source in zip(group, profiles):
            permutation[target] = source
    for mode in ('baseline', 'root-twins', 'min5', 'min6', 'lite5', 'lite6'):
        clauses, edges = make_formula(core, boundary, 6, 5, mode)
        assignment = [variable if known[inner] >> (len(core) + permutation[outer]) & 1 else -variable
                      for (inner, outer), variable in edges.items()]
        with Solver(name='cadical195', bootstrap_with=clauses.clauses) as solver:
            assert solver.solve(assumptions=assignment)
            assignment[0] *= -1
            assert not solver.solve(assumptions=assignment)
        print('CONTROL C21', mode, 'sorted positive accepted; one-edge negative rejected', flush=True)
    keys = boundary_keys()
    reflection = [keys.index(reflect(key)) for key in keys]
    assert all(reflection[reflection[index]] == index for index in range(len(keys)))
    print('REFLECTION', reflection, 'representatives', [index for index, other in enumerate(reflection) if index <= other])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--mode', choices=['baseline', 'root-twins', 'min5', 'min6', 'lite5', 'lite6'], default='root-twins')
    parser.add_argument('--op', choices=['probe', 'produce', 'verify'], default='probe')
    parser.add_argument('--orbit', type=int, required=False)
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--skip-row', type=int, action='append', default=[])
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=1)
    args = parser.parse_args()
    if args.control:
        control()
        return
    rows = [(index, line, decode(line)) for index, line in enumerate(args.catalogue.read_text().splitlines())]
    rows = [(index, line, core) for index, line, core in rows if sum(map(int.bit_count, core)) == 126]
    assert len(rows) == 60
    keys = boundary_keys()
    assert args.orbit is not None and 0 <= args.orbit < len(keys)
    boundary = boundary_masks(keys[args.orbit])
    args.work.mkdir(parents=True, exist_ok=True)
    cnf_file = args.work / f'{args.orbit:02d}-{args.mode}-{args.shard}-tmp.cnf'
    counts = Counter()
    start = cpu()
    for index, line, core in rows:
        if index % args.shards != args.shard or index in args.skip_row or (args.row and index not in args.row):
            continue
        begin = cpu()
        proof = args.work / f'{args.orbit:02d}-{args.mode}-{index:03d}.lrat'
        if args.op == 'produce' and proof.exists():
            raise FileExistsError(proof)
        if args.op == 'verify' and not proof.exists():
            counts['missing'] += 1
            continue
        clauses, _ = make_formula(core, boundary, 9, 6, args.mode)
        dimensions = (clauses.nv, len(clauses.clauses))
        clauses.to_file(cnf_file)
        del clauses
        if args.op != 'verify':
            proof_args = ['--lrat', cnf_file, proof] if args.op == 'produce' else [cnf_file]
            solved = run(args.bin / 'cadical', ['-q', *proof_args], args.seconds)
            if solved.returncode == 124:
                if args.op == 'produce':
                    proof.unlink(missing_ok=True)
                counts['wall-cap'] += 1
                print('row', index, 'wall-cap', *dimensions, 'CPU-s', round(cpu() - begin, 4), flush=True)
                continue
            if solved.returncode == 10:
                print('UNVERIFIED MODEL', index, solved.stdout, flush=True)
                raise SystemExit(10)
            if solved.returncode != 20 or 's UNSATISFIABLE' not in solved.stdout.splitlines():
                raise RuntimeError((index, solved.returncode, solved.stdout))
        status = 'enum' if args.op == 'probe' else 'checked'
        counts[status] += 1
        if args.op != 'probe':
            checked = run(args.bin / 'cake_lpr', [cnf_file, proof], 160)
            if checked.returncode != 0 or 's VERIFIED UNSAT' not in checked.stdout.splitlines():
                raise RuntimeError((index, checked.returncode, checked.stdout))
        hashes = [sha256(line.encode()).hexdigest(), digest(cnf_file)]
        if args.op != 'probe':
            hashes.extend([digest(proof), proof.stat().st_size])
        print('row', index, status, *dimensions, *hashes, 'CPU-s', round(cpu() - begin, 4), flush=True)
    cnf_file.unlink(missing_ok=True)
    print('TERMINAL', args.orbit, args.mode, args.op, dict(counts), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
