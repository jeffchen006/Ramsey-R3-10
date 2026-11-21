#!/usr/bin/env python3
"""Combine checked oriented-kernel exclusions with the side-exchange cover."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random

from catalogue_m3 import signature_of, swap
from kernel_cnf import decode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalogue', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('checked_jsonl', nargs='+', type=Path)
    parser.add_argument('--sample-seed', type=int, default=3401)
    parser.add_argument('--sample-per-stratum', type=int, default=2)
    args = parser.parse_args()
    catalogue = args.catalogue.read_text().splitlines()
    records = {record['g6']: record for report in args.checked_jsonl for line in report.read_text().splitlines()
               if line.strip() for record in [json.loads(line)]}
    assert records.keys() <= set(catalogue)

    orbits = defaultdict(list)
    for index, kernel in enumerate(catalogue):
        signature = signature_of(8, kernel)
        orbits[min(signature, swap(signature))].append(index)
    by_edges = defaultdict(list)
    manifest = ['representative\tedges\toriented_indices\tchecked_excluded_by\tkernel']
    for indices in orbits.values():
        index = indices[0]
        kernel = catalogue[index]
        edge_count = len(decode(kernel))
        excluded = [other for other in indices if records.get(catalogue[other], {}).get('status') == 'cert']
        if not excluded:
            by_edges[edge_count].append(index)
        manifest.append(f'{index}\t{edge_count}\t{",".join(map(str, indices))}\t{",".join(map(str, excluded))}\t{kernel}')
    args.output.mkdir(exist_ok=True)
    (args.output / 'orbits.tsv').write_text('\n'.join(manifest) + '\n')
    retained = [index for _, values in sorted(by_edges.items()) for index in values]
    (args.output / 'survivors.g6').write_text(''.join(catalogue[index] + '\n' for index in retained))
    random_generator = random.Random(args.sample_seed)
    sample = [index for _, values in sorted(by_edges.items())
              for index in random_generator.sample(values, min(args.sample_per_stratum, len(values)))]
    (args.output / 'sample.ids').write_text(''.join(f'{index}\n' for index in sample))
    print('Records marked cert:', sum(record['status'] == 'cert' for record in records.values()))
    print('Orbits:', len(orbits), 'remain:', len(retained), 'by edges:', sorted((edge, len(values)) for edge, values in by_edges.items()))
    print('Sample:', *sample)


if __name__ == '__main__':
    main()
