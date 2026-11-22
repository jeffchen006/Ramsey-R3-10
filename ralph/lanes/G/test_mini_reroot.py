#!/usr/bin/env python3
"""Check joined CNFs against physical rooted projections of known graphs."""

from pathlib import Path
from sys import argv

from mini_reroot import eager_cuts, solve, window_problem
from test_reroot_shell import fixtures, graph, vertices


for line in Path(argv[1]).read_text().splitlines():
    original = graph.parse_graph6(line)
    for fixture in fixtures(original, 3):
        old, alpha, small, large, first, second, common, one, two, slots, floors, rooted = fixture
        if not rooted:
            continue
        args = (old, tuple(vertices(small)), tuple(vertices(large)), (first, second, common),
                (one, two), slots, (floors[0][0], floors[1][0]))
        for unpaired, positive in ((floors[2][1], True), (1000, False)):
            formula = window_problem(*args, unpaired, alpha=alpha + 2, paired_edges=(floors[0][1], floors[1][1]),
                                     sorted_groups=True)
            eager_cuts(formula, old, alpha=alpha + 2)
            result, stats = solve(formula, 3000, alpha=alpha + 2)
            assert result != 'CAP' and (result != 'UNSAT') == positive, (len(original), stats, result, positive)
        print(f'n={len(original)} rooted positive/adverse pair passed', flush=True)
