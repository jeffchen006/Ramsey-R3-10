"""Produce compact LRATs, then check them against independently regenerated CNFs."""

import argparse
import hashlib
from pathlib import Path
import subprocess

from e107_core_proofs import make_core, root, verify


def run(source, output, pin_file, replay, dual):
    entries = [line.split('\t') for line in source.read_text().splitlines()]
    numeric = [int(index) for index, _ in entries]
    assert all(left < right for left, right in zip([0, *numeric], numeric))
    pins = {}
    for line in pin_file.read_text().splitlines():
        local, *masks = line.split()
        local = int(local)
        assert 1 <= local <= len(entries) and local not in pins
        pins[local] = tuple(int(mask, 16) for mask in masks)

    if not replay:
        output.mkdir()
    counts = {'rup': 0, 'cadical': 0, 'replay': 0}
    temporary = output / ('replay.cnf' if replay else 'produce.cnf')
    for local, (index, graph) in enumerate(entries, 1):
        expected = make_core(graph, pins.get(local)).encode('ascii')
        temporary.write_bytes(expected)
        proof = output / f'{int(index):07d}.lrat'
        if replay:
            method = 'replay'
            verify('cake_lpr', temporary, proof, 's VERIFIED UNSAT')
            if dual:
                verify('lrat-check', temporary, proof, 'c VERIFIED')
        else:
            method = 'rup'
            result = subprocess.run(['timeout', '5s', 'build/unit_lrat', temporary, proof])
            if result.returncode == 10:
                method = 'cadical'
                result = subprocess.run(['timeout', '--kill-after=2s', '9s', 'prlimit', '--cpu=6:7', '--',
                                         root / 'opt/bin/cadical', '--lrat', '--no-binary', temporary, proof],
                                        capture_output=True)
                if result.returncode != 20:
                    (output / f'{int(index):07d}.failure').write_bytes(result.stdout + result.stderr)
            if result.returncode != 20:
                raise RuntimeError(f'{source}:{index}: {method} returncode {result.returncode}')
            verify('lrat-check', temporary, proof, 'c VERIFIED')
        counts[method] += 1
        print(index, hashlib.sha256(expected).hexdigest(), hashlib.sha256(proof.read_bytes()).hexdigest(),
              method, flush=True)
    temporary.unlink(missing_ok=True)
    print('counts', len(entries), counts, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('pins', type=Path)
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--dual', action='store_true')
    args = parser.parse_args()
    if args.dual and not args.replay:
        parser.error('--dual requires --replay')
    run(args.source, args.output, args.pins, args.replay, args.dual)


if __name__ == '__main__':
    main()
