"""Regenerate and certify the diagonal-five P3 e64 residue rows."""

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path

from kernel_projection import decode
from path_three_top import boundary, formula
from p4_factor_proofs import cpu, digest, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--seconds', type=int, default=100)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=1)
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--skip-row', type=int, action='append', default=[])
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    rows = [(index, line, decode(line)) for index, line in enumerate(args.catalogue.read_text().splitlines())]
    rows = [(index, line, core) for index, line, core in rows if sum(map(int.bit_count, core)) == 128]
    assert len(rows) == 59
    args.work.mkdir(exist_ok=True)
    seed = boundary(64)
    totals = Counter()
    cnf_file = args.work / f'tmp-{args.shard}.cnf'
    start = cpu()
    for index, line, core in rows:
        if index % args.shards != args.shard or index in args.skip_row or (args.row and index not in args.row):
            continue
        begin = cpu()
        proof = args.work / f'{index:03d}.lrat'
        if not args.verify and proof.exists():
            raise ValueError(f'refusing to overwrite {proof}')
        if args.verify and not proof.exists():
            totals['missing'] += 1
            continue
        clauses, _ = formula(core, seed, 9, 6)
        clauses.to_file(cnf_file)
        del clauses
        if not args.verify:
            solved = run(args.bin / 'cadical', ['-q', '--lrat', cnf_file, proof], args.seconds)
            if solved.returncode == 124:
                proof.unlink(missing_ok=True)
                totals['wall-cap'] += 1
                print('row', index, 'wall-cap', 'CPU-s', round(cpu() - begin, 4), flush=True)
                continue
            if solved.returncode == 10:
                print('UNVERIFIED RELAXATION MODEL', index, solved.stdout, flush=True)
                raise SystemExit(10)
            if solved.returncode != 20 or 's UNSATISFIABLE' not in solved.stdout.splitlines():
                raise RuntimeError((index, solved.returncode, solved.stdout))
        checked = run(args.bin / 'cake_lpr', [cnf_file, proof], 100)
        if checked.returncode != 0 or 's VERIFIED UNSAT' not in checked.stdout.splitlines():
            raise RuntimeError((index, checked.returncode, checked.stdout))
        totals['checked'] += 1
        print('row', index, 'checked', sha256(line.encode()).hexdigest(), digest(cnf_file), digest(proof),
              proof.stat().st_size, 'CPU-s', round(cpu() - begin, 4), flush=True)
    cnf_file.unlink(missing_ok=True)
    print('TERMINAL', dict(totals), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
