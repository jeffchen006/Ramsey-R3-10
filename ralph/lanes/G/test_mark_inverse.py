#!/usr/bin/env python3
"""Compare the C++ inverse scanner to Lane A's literal smaller replay."""

from collections import defaultdict
from itertools import combinations
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'ralph/lanes/A'))
from audit_adjacent_residues import calibrate_graph, induced, inverse_with_alpha, toggle
from residue_bundle import parse_graph6, to_graph6


def run(binary):
    cases = defaultdict(set)
    case_path = ROOT / 'gluing/val/r3_5_12.g6'
    for index, row in enumerate(case_path.read_text().splitlines(), 1):
        adj = parse_graph6(row)
        for first, _, _, legal in calibrate_graph(adj, 4, 4, f'n12-{index}'):
            section = induced(adj, [vertex for vertex in range(12) if vertex != first and not adj[first] >> vertex & 1])
            for added in range(1, len(legal) + 1):
                for part in combinations(legal, added):
                    cases[added, len(legal) - added].add(to_graph6(toggle(section, part)))
    for (added, remaining), strings in sorted(cases.items()):
        expected = set()
        strings = sorted(strings)
        for index, row in enumerate(strings, 1):
            for mark, _, lower, valid in inverse_with_alpha(parse_graph6(row), 3, 1, added, remaining, 3):
                expected.add((index, mark, int(valid), to_graph6(lower)))
        result = subprocess.run([str(binary), '3', '1', str(added), str(remaining), '3'],
                                input='\n'.join(strings) + '\n', text=True, capture_output=True, check=True, timeout=10)
        received = set()
        for out in result.stdout.splitlines():
            index, mark, validity, lower = out.split('\t')
            key = int(index), tuple(map(int, mark.split(','))), int(validity), lower
            assert key not in received
            received.add(key)
        assert received == expected and any(key[2] for key in received)
        print(f'added={added} remaining={remaining}: {len(strings)} rows; {len(received)} exact marks')


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve())
