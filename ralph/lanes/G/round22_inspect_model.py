"""Decode folded SAT models and test the omitted graph constraints."""

from itertools import combinations, product
import json
from pathlib import Path
import sys

from round22_control import graph6
from round22_fold import deficit, masks


def decode(board, positive):
    width = len(board)
    basic = 2 + 2 * width
    low = (1 << width) - 1
    grid = [(1 << row) | (1 << (width + col)) for row, col in product(range(width), repeat=2)
            for _ in range(board[row][col])]
    shores = [masks(width) + tuple(1 << anchor for anchor, count in enumerate(deficit(board, side))
                                   for _ in range(count)) for side in range(2)]
    literal = sum(map(len, shores))
    selected = []
    for (first, left), (second, right) in product(*[enumerate(shore) for shore in shores]):
        if left & right & 1 or left.bit_count() + right.bit_count() <= 2:
            continue
        literal += 1
        if literal in positive:
            selected.append((first, second, literal))
    assert len({row[0] for row in selected}) == len({row[1] for row in selected}) == len(selected)
    assert len(grid) + len(selected) == 28
    coords = list(range(len(grid))) + [len(grid) + one for one, _, _ in selected]
    indices = {site: idx + basic for idx, site in enumerate(coords)}
    edges = {(0, 1), (2, 2 + width), *((0, 2 + idx) for idx in range(width)),
             *((1, 2 + width + idx) for idx in range(width))}
    supports = grid + [shores[0][one] | shores[1][two] << width for one, two, _ in selected]
    for site, support in enumerate(supports, basic):
        edges.update((2 + idx, site) for idx in range(2 * width) if support >> idx & 1)
    lookup = {}
    layout = [support & low for support in grid] + list(shores[0])
    for first, second in combinations(range(len(layout)), 2):
        overlap = grid[first] & grid[second] if second < len(grid) else layout[first] & layout[second]
        if overlap:
            continue
        literal += 1
        if first in indices and second in indices:
            key = (indices[first], indices[second])
            lookup[key] = literal
            if literal in positive:
                edges.add(key)
        else:
            assert literal not in positive
    gates = {indices[len(grid) + one]: gate for one, _, gate in selected}
    return edges, lookup, gates, basic


def diagnose(board, positive):
    edges, literals, options, basic = decode(board, positive)
    neighbors = [0] * (basic + 28)
    for first, second in edges:
        neighbors[first] |= 1 << second
        neighbors[second] |= 1 << first
    assert all(not neighbors[first] & neighbors[second] for first, second in edges)
    option_mask = sum(1 << site for site in options)

    def find(available, need, permitted, chosen=0):
        if not need:
            return chosen
        if available.bit_count() < need or (available & ~option_mask).bit_count() + permitted < need:
            return None
        while available.bit_count() >= need:
            one = available & -available
            available ^= one
            is_option = int(bool(one & option_mask))
            if is_option <= permitted:
                result = find(available & ~neighbors[one.bit_length() - 1], need - 1, permitted - is_option, chosen | one)
                if result is not None:
                    return result
        return None

    full = (1 << len(neighbors)) - 1
    for least in range(len(options) + 1):
        witness = find(full, 10, least)
        if witness is not None:
            break
    exterior = sum(first >= basic for first, _ in edges)
    holes = sum((first, second) not in edges and not neighbors[first] & neighbors[second]
                for first, second in combinations(range(len(neighbors)), 2))
    info = dict(edge_count=len(edges), exterior_edges=exterior, unsaturated_pairs=holes,
                degree_histogram={degree: sum(mask.bit_count() == degree for mask in neighbors) for degree in range(6, 10)},
                graph=graph6(len(neighbors), edges))
    if witness is not None:
        sites = tuple(idx for idx in range(len(neighbors)) if witness >> idx & 1)
        guards = [-options[site] for site in sites if site in options]
        joins = [literals[first, second] for first, second in combinations(sites, 2) if (first, second) in literals]
        assert not set(joins) & positive and all(-guard in positive for guard in guards)
        info.update(I10=sites, smallest_option_count=least, exact_block=sorted(guards + joins))
    return info


if __name__ == '__main__':
    base = Path(sys.argv[1])
    manifest = json.loads((base / 'manifest.json').read_text())
    for folder in sorted((base / 'work').iterdir()):
        status = folder / 'solve.status'
        if not status.exists() or status.read_text().strip() != '10':
            continue
        data = json.loads((folder / 'binding.json').read_text())
        ident = data['board']
        signed = [int(word) for line in (folder / 'solve.log').read_text().splitlines() if line.startswith('v ')
                  for word in line.split()[1:] if word != '0']
        assert len(signed) == data['variables']
        print(json.dumps(dict(board=ident, receipt=folder.name,
                              **diagnose(manifest[ident]['grid'], set(lit for lit in signed if lit > 0)))), flush=True)
