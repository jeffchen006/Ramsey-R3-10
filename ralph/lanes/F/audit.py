#!/usr/bin/env python3
"""Independently count bad sets in annealer checkpoints, or gate and publish candidates."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
from orbit_extend import ROOT, image, independent, independent_sets, parse_graph6, perm_for


def audit(checkpoint, k):
    [line] = checkpoint.read_text().strip().splitlines()
    neighbors = parse_graph6(line)
    degrees = [mask.bit_count() for mask in neighbors]
    if any(not independent(mask, neighbors) for mask in neighbors):
        raise ValueError(f'{checkpoint}: not triangle-free')
    prefix = checkpoint.name.removesuffix('.best.g6')
    log = checkpoint.with_name(f'{prefix}.log')
    match = re.search(r'^sym .*cycles=([0-9,]+)$', log.read_text(), re.M) if log.exists() else None
    cycles = []
    if match:
        cycles = list(map(int, match[1].split(',')))
        permutation = perm_for(cycles)
        if len(permutation) != len(neighbors) or any(
                image(mask, permutation) != neighbors[permutation[index]] for index, mask in enumerate(neighbors)):
            raise ValueError(f'{checkpoint}: symmetry check failed')
    count = sum(1 for _ in independent_sets(neighbors, (1 << len(neighbors)) - 1, k))
    return {'tag': prefix, 'n': len(neighbors), 'k': k, 'I_k': count, 'cycles': cycles,
            'edges': sum(degrees) // 2, 'degree_range': [min(degrees), max(degrees)],
            'degree_excess': sum(max(0, degree - k + 1) for degree in degrees), 'evidence': str(checkpoint)}


def publish(path):
    result = subprocess.run([sys.executable, '-I', str(ROOT / '.hmz/flows/r310_ralph/gate.py'),
                             str(ROOT), 'check', str(path)], capture_output=True, text=True, check=True)
    checks = json.loads(result.stdout.splitlines()[-1])['graphs']
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    if len(checks) != len(lines):
        raise ValueError(f'{path}: gate did not check every candidate')
    for line, check in zip(lines, checks):
        if not check.get('ok'):
            raise ValueError(f'{path}: gate rejected candidate: {check}')
        digest = sha256(line.strip().encode('ascii')).hexdigest()[:20]
        destination = ROOT / f'ralph/found/F_{digest}.g6'
        temporary = path.with_name(f'{path.name}.{digest}.publish.tmp')
        temporary.write_text(line.strip() + '\n')
        temporary.replace(destination)
        print(f'Gate accepted {path}; staged {destination}', flush=True)


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--k', type=int, default=10)
    arg.add_argument('--publish', action='store_true')
    arg.add_argument('paths', type=Path, nargs='+')
    args = arg.parse_args()
    for path in args.paths:
        if args.publish:
            publish(path)
        else:
            print(json.dumps(audit(path, args.k)), flush=True)


if __name__ == '__main__':
    main()
