"""Independent CNF deltas and literal physical guards on each h5 receipt."""

import json
import sys
from itertools import combinations, product
from pathlib import Path

from pysat.card import CardEnc, EncType

from round22_control import decode
from round22_fold import masks
from round22_split import cnf_data


def literals(board):
    grid = [(row, col) for row, col in product(range(5), repeat=2) for _ in range(board[row][col])]
    both = []
    for side in range(2):
        both.append([tuple(i for i in range(5) if support >> i & 1) for support in masks(5)] +
                    [(anchor,) for anchor in range(5) for _ in range(4 - sum(g[side] == anchor for g in grid))])
    assert len(grid) == 17 and list(map(len, both)) == [13, 13]
    pat = {idx: ({row + 2}, {col + 7}) for idx, (row, col) in enumerate(grid)}
    select = {}
    for left, right in product(range(13), repeat=2):
        mask, other = both[0][left], both[1][right]
        if ((0 in mask and 0 in other) or (len(mask) == len(other) == 1)):
            continue
        select[left, right] = 27 + len(select)
        pat[left, right] = ({i + 2 for i in mask}, {i + 7 for i in other})
    numbering = []
    lefts = [{row} for row, _ in grid] + list(map(set, both[0]))
    for one, two in combinations(range(30), 2):
        if lefts[one] & lefts[two] or (two < 17 and grid[one][1] == grid[two][1]):
            continue
        numbering.append(((one, two), 27 + len(select) + len(numbering)))
    return numbering, select, pat


def audit(manifest, previous, ident, prefix, mode):
    board = json.loads(manifest.read_text())[ident]['grid']
    stem = 'p285' if ident == 285 else f'b{ident:03}'
    original_nv, original = cnf_data(previous / 'work' / stem / 'grid.cnf')
    new_nv, new = cnf_data(Path('grid.cnf'))
    assert original <= new
    numbering, selectors, supports = literals(board)
    edges = dict(numbering)
    additions = set()

    def row(items):
        additions.add(' '.join(map(str, (*sorted(set(items)), 0))).encode())

    expected_nv = original_nv
    if 'B' in mode:
        for encode in (CardEnc.atmost, CardEnc.atleast):
            cnf = encode(lits=list(edges.values()), bound=86, top_id=expected_nv, encoding=EncType.seqcounter)
            expected_nv = max(expected_nv, cnf.nv)
            for clause in cnf.clauses:
                row(clause)
    for place, value in enumerate(prefix if prefix != '-' else ''):
        assert place < 10 and value in '01'
        row([(place + 1) * (1 if value == '1' else -1)])
    witnesses = 0
    boundary_edges = {(0, 1), (2, 7), *((0, 2 + i) for i in range(5)), *((1, 7 + i) for i in range(5))}
    if 'M' in mode:
        for line in Path('witness.jsonl').read_text().splitlines():
            data = json.loads(line)
            chosen = data['grid'] + list(map(tuple, data['options']))
            boundary = data['boundary']
            numbers = [site if type(site) is int else site[0] + 17 for site in chosen]
            assert len(numbers) == len(set(numbers)) and all(site in supports for site in chosen)
            assert len({site[1] for site in chosen if type(site) is tuple}) == len(data['options'])
            assert set(boundary) <= set(range(12)) and len(set(boundary)) == len(boundary)
            assert len(chosen) + len(boundary) == 10
            assert not any(edge[0] in boundary and edge[1] in boundary for edge in boundary_edges)
            for site in chosen:
                assert not set(boundary) & (supports[site][0] | supports[site][1])
            clause = [-selectors[site] for site in chosen if type(site) is tuple]
            for first, second in combinations(range(len(chosen)), 2):
                one, two = chosen[first], chosen[second]
                if all(not (mask & other) for mask, other in zip(supports[one], supports[two])):
                    clause.append(edges[tuple(sorted((numbers[first], numbers[second])))])
            row(clause)
            witnesses += 1
    assert new_nv == expected_nv and new - original == additions - original
    print(f'physical addresses checked; exact delta {len(new - original)} clauses; {witnesses} literal witnesses')


if __name__ == '__main__':
    manifest, previous, board, prefix, mode = sys.argv[1:]
    audit(Path(manifest), Path(previous), int(board), prefix, mode)
