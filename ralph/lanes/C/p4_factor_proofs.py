"""Produce/check binary LRAT for the static P4-side relaxation."""

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import resource
import subprocess
import time

from kernel_projection import decode
from path_four_factor import Factor
from path_four_forced import Conflict
from path_four_mixed import cross_patterns


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def run(binary, arguments, timeout):
    return subprocess.run(['timeout', str(timeout), str(binary), *map(str, arguments)],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def cpu():
    timer = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time() + timer.ru_utime + timer.ru_stime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--min-e', type=int, default=0)
    parser.add_argument('--max-e', type=int, default=999)
    parser.add_argument('--seconds', type=int, default=12)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=1)
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--join', action='store_true')
    parser.add_argument('--pins', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    params = (6, 6, 2, 4) if args.control else (9, 9, 3, 6)
    args.work.mkdir(exist_ok=True)
    cnf_path = args.work / ('temp-%d.cnf' % args.shard)
    counts = Counter()
    start = cpu()
    for index, line in enumerate(args.catalogue.read_text().splitlines()):
        if index % args.shards != args.shard or (args.row and index not in args.row):
            continue
        seed = decode(line)
        n_edges = sum(map(int.bit_count, seed)) // 2
        if not args.min_e <= n_edges <= args.max_e:
            continue
        begin = cpu()
        try:
            factor = Factor(seed, *params)
        except Conflict as exc:
            counts['propagation'] += 1
            print('row', index, 'e', n_edges, 'propagation', str(exc), flush=True)
            continue
        statuses = []
        side_list = [(0,), (1,), (0, 1)] if args.join else [(0,), (1,)]
        if args.pins:
            cnf, literals, _ = factor.formula((0, 1))
            base_length = len(cnf.clauses)
            keys = [(f'p{pat:03d}', pat) for pat in cross_patterns(factor.block, factor.cross_target)]
            assert keys
        else:
            keys = [(''.join(map(str, sides)), sides) for sides in side_list]
        for key, entry in keys:
            proof = args.work / f'{index:04d}-{key}.lrat'
            if args.verify and not proof.exists():
                statuses.append((key, 'missing'))
                continue
            if args.pins:
                del cnf.clauses[base_length:]
                for offset, (left, right) in enumerate(factor.cross):
                    literal = literals[left][right]
                    cnf.append([literal if entry >> offset & 1 else -literal])
            else:
                cnf, _, _ = factor.formula(entry)
            cnf.to_file(cnf_path)
            if not args.verify:
                if proof.exists():
                    raise ValueError(f'refusing to overwrite {proof}')
                result = run(args.bin / 'cadical', ['-q', '--lrat', cnf_path, proof], args.seconds)
                status = {10: 'feasible', 20: 'unsat', 124: 'wall-cap'}.get(result.returncode)
                if status is None:
                    raise RuntimeError((index, result.returncode, result.stdout))
                if status != 'unsat':
                    statuses.append((key, status))
                    proof.unlink(missing_ok=True)
                    continue
                if 's UNSATISFIABLE' not in result.stdout.splitlines():
                    raise RuntimeError((index, 'missing solver verdict', result.stdout))
            result = run(args.bin / 'cake_lpr', [cnf_path, proof], 60)
            if result.returncode != 0 or 's VERIFIED UNSAT' not in result.stdout.splitlines():
                raise RuntimeError((index, 'proof failed', result.returncode, result.stdout))
            statuses.append((key, 'checked'))
            print('row', index, 'e', n_edges, 'checked', key, sha256(line.encode()).hexdigest(),
                  digest(cnf_path), digest(proof), proof.stat().st_size,
                  'CPU-s', round(cpu() - begin, 4), flush=True)
            if not args.pins:
                break
        accepted = (len(statuses) == len(keys) and all(status == 'checked' for _, status in statuses)
                    if args.pins else any(status == 'checked' for _, status in statuses))
        if accepted:
            counts['checked'] += 1
            if args.pins:
                print('row', index, 'e', n_edges, 'all-pins-checked', len(statuses),
                      'CPU-s', round(cpu() - begin, 4), flush=True)
        else:
            counts['unresolved'] += 1
            print('row', index, 'e', n_edges, 'unresolved', statuses, 'CPU-s', round(cpu() - begin, 4), flush=True)
    cnf_path.unlink(missing_ok=True)
    print('TERMINAL', dict(counts), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
