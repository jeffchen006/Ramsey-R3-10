"""Run G's necessary MTF-root core on the clique complement, one slot at a time."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
from time import monotonic

root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root / 'ralph/lanes/G'))
from root_core import clauses_for, dimacs, graph
from verify_uncovered import verify as verify_clique


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(binary, cnf, proof, marker):
    check = subprocess.run(['timeout', '12s', root / 'opt/bin' / binary, cnf, proof],
                           capture_output=True, text=True)
    assert check.returncode == 0 and marker in check.stdout.splitlines(), (binary, check.returncode, check.stdout)


def make_core(text, clique):
    rows = graph.parse_graph6(text)
    variables, clauses = clauses_for(rows, 7, 9)
    if clique is not None:
        verify_clique(rows, 6, clique)
        for row, mask in enumerate(clique):
            for vertex in range(len(rows)):
                if mask >> vertex & 1:
                    clauses.append((row * len(rows) + vertex + 1,))
    return ''.join(dimacs(variables, clauses))


def run(source, output, count, pin_file, verify_only):
    entries = [line.split('\t') for line in source.read_text().splitlines()]
    assert len(set(index for index, _ in entries)) == len(entries)
    anchors = {}
    if pin_file is not None:
        for line in pin_file.read_text().splitlines():
            local, *masks = line.split()
            assert 1 <= int(local) <= len(entries)
            index = entries[int(local)-1][0]
            assert index not in anchors
            anchors[index] = tuple(int(mask, 16) for mask in masks)
    if count:
        entries = [entries[(len(entries)*index)//count] for index in range(count)]
    output.mkdir(exist_ok=True)
    started = monotonic()
    for index, text in entries:
        assert index.isdigit()
        cnf = output / f'{int(index):06d}.cnf'
        proof = cnf.with_suffix('.lrat')
        log = cnf.with_suffix('.log')
        expected = make_core(text, anchors.get(index))
        if verify_only:
            assert cnf.read_text() == expected
            verify('lrat-check', cnf, proof, 'c VERIFIED')
            verify('cake_lpr', cnf, proof, 's VERIFIED UNSAT')
            print(index, 'cert', sha256(cnf), sha256(proof), flush=True)
            continue
        cnf.write_text(expected)
        with log.open('w') as stream:
            call = subprocess.run(['timeout', '--kill-after=2s', '9s', 'prlimit', '--cpu=6:7', '--',
                                   root / 'opt/bin/cadical', '--lrat', '--no-binary', cnf, proof],
                                  stdout=stream, stderr=subprocess.STDOUT)
        if call.returncode == 20:
            verify('lrat-check', cnf, proof, 'c VERIFIED')
            verify('cake_lpr', cnf, proof, 's VERIFIED UNSAT')
            print(index, 'cert', sha256(cnf), sha256(proof), flush=True)
        else:
            label = 'SAT relaxation' if call.returncode == 10 else f'not verified rc={call.returncode}'
            print(index, label, flush=True)
    print(f'{len(entries)} inputs, {monotonic()-started:.3f} wall s', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--count', type=int, default=0)
    parser.add_argument('--pins', type=Path)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    run(args.source, args.output, args.count, args.pins, args.verify_only)
