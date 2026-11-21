#!/usr/bin/env python3
"""Combine the mixed-window isomorphism filter with replayable graph propagation."""

import argparse
from collections import Counter
import json
from pathlib import Path
from time import process_time

from involution_sat import from_graph6
from m11_prop import Prover, proof_check, targets
from shared74 import MIXED, calibration, surviving_counts


def prove(prover, core, parts):
    lower, upper = targets(core, parts)
    trace = prover.prove(lower, upper, 7, 74)
    if trace[0]:
        proof_check(lower, upper, 7, 74, *trace)
        return trace
    return None


def scan(src, output, prover, match, graph_first):
    stats = Counter()
    started = process_time()
    with src.open(encoding='ascii') as rows, output.open('w', encoding='ascii') as out:
        for index, line in enumerate(rows):
            key, profile, parts, omitted = json.loads(line)
            assert tuple(profile) == MIXED
            core = tuple(from_graph6(key))
            parts = tuple(map(tuple, parts))
            stats['projections'] += 1
            stats['lifts'] += len(omitted)
            trace = prove(prover, core, parts)
            if trace:
                stats['projection graphs'] += 1
                stats['lifts refuted as projection'] += len(omitted)
                print(json.dumps((index, -1, 'graph', 3, trace), separators=(',', ':')), file=out)
                continue
            for serial, option in enumerate(omitted):
                groups = (*parts, tuple(option))
                if match and not graph_first and not any(surviving_counts(core, groups, marked=True)):
                    stats['lift incompatibilities'] += 1
                    print(json.dumps((index, serial, 'incompatible'), separators=(',', ':')), file=out)
                    continue
                for dropped in range(3):
                    trace = prove(prover, core, groups[:dropped]+groups[dropped+1:])
                    if trace:
                        stats['lift graphs'] += 1
                        print(json.dumps((index, serial, 'graph', dropped, trace), separators=(',', ':')), file=out)
                        break
                else:
                    if match and graph_first and not any(surviving_counts(core, groups, marked=True)):
                        stats['lift incompatibilities'] += 1
                        print(json.dumps((index, serial, 'incompatible'), separators=(',', ':')), file=out)
                        continue
                    stats['open lifts'] += 1
                    print(json.dumps((index, serial, 'open'), separators=(',', ':')), file=out)
    print(src.name, 'isomorphism filter', match, 'graph first', graph_first, dict(stats),
          f'cpu={process_time()-started:.3f}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--lib', type=Path, default=Path('../r6_e11/m11_prop.so'))
    parser.add_argument('--unfiltered', action='store_true')
    parser.add_argument('--graph-first', action='store_true')
    args = parser.parse_args()
    calibration()
    scan(args.source, args.output, Prover(args.lib), not args.unfiltered, args.graph_first)


if __name__ == '__main__':
    main()
