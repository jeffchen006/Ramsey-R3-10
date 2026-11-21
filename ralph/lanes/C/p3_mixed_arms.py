"""Check the two e63 boundaries with incident cross counts 9 and 8."""

import argparse
from collections import Counter
from pathlib import Path

from kernel_projection import decode
from p3_e63 import control, make_formula
from p3_high_f import NO_HOLE, classify, filter_target, layouts
from p3_round4_index import census
from p4_factor_proofs import cpu, digest, run


def selected_boundary(diagonal):
    selected = (1, NO_HOLE, ((1, 0) if diagonal == 3 else (0, 1)))
    expected = {(1, NO_HOLE, (0, 0)), selected} if diagonal == 3 else {selected}
    passing = {key for _, key in layouts(9, 6, diagonal, 8, 18, 18)
               if (key[1] == NO_HOLE) != (key[2] == NO_HOLE)
               and filter_target(classify(9, 6, diagonal, key)) == 'pass'}
    assert passing == expected
    return classify(9, 6, diagonal, selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('bin', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--diagonal', type=int, choices=(3, 4))
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--seconds', type=int, default=40)
    parser.add_argument('--row', type=int, action='append')
    parser.add_argument('--skip-row', type=int, action='append', default=[])
    parser.add_argument('--shards', type=int, default=1)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.control:
        control()
        return
    rows = census(args.catalogue)
    lines = args.catalogue.read_text().splitlines()
    boundary = selected_boundary(args.diagonal)
    assert 0 <= args.shard < args.shards
    target_rows = [row for row, (edges, _) in rows.items() if edges == 63 and row % args.shards == args.shard
                   and (not args.row or row in args.row) and row not in args.skip_row]
    assert target_rows
    args.work.mkdir(exist_ok=True)
    counts = Counter()
    start = cpu()
    for row in target_rows:
        begin = cpu()
        cnf, _ = make_formula(decode(lines[row]), boundary, 9, 6, 'lite6')
        cnf_path = args.work / f'{args.diagonal}-{row}.cnf'
        proof_path = args.work / f'{args.diagonal}-{row}.lrat'
        cnf.to_file(cnf_path)
        status = 'checked'
        if not args.verify:
            assert not proof_path.exists()
            result = run(args.bin / 'cadical', ['-q', '--lrat', cnf_path, proof_path], args.seconds)
            if result.returncode != 20:
                status = {124: 'wall-cap', 10: 'relaxation-sat'}[result.returncode]
                proof_path.unlink(missing_ok=True)
        if status == 'checked':
            checked = run(args.bin / 'cake_lpr', [cnf_path, proof_path], 150)
            assert checked.returncode == 0 and 's VERIFIED UNSAT' in checked.stdout.splitlines()
            print('bound', row, digest(cnf_path), digest(proof_path), proof_path.stat().st_size, flush=True)
        counts[status] += 1
        print('row', row, status, 'CPU-s', round(cpu() - begin, 4), flush=True)
        cnf_path.unlink()
    print('TERMINAL', args.diagonal, 'lite6', dict(counts), 'CPU-s', round(cpu() - start, 4), flush=True)


if __name__ == '__main__':
    main()
