#!/usr/bin/env python3
"""Small physical two-defect oracle, without importing an encoder."""
import argparse
import itertools as it
import json
from collections import Counter, defaultdict
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BOUND = ((0, 1), (2, 5), *((0, anchor) for anchor in range(2, 5)),
         *((1, anchor) for anchor in range(5, 8)))
DOUBLES = (3, 5, 6)


def encode(neighbors):
    bits = [bool(neighbors[high] & (1 << low))
            for high in range(len(neighbors)) for low in range(high)]
    bits.extend([False] * (-len(bits) % 6))
    return chr(63 + len(neighbors)) + ''.join(
        chr(63 + sum(bit << (5 - index) for index, bit in enumerate(bits[pos:pos + 6])))
        for pos in range(0, len(bits), 6))


def decode(line, order):
    assert ord(line[0]) - 63 == order
    bits = [(ord(char) - 63) >> shift & 1 for char in line[1:] for shift in range(5, -1, -1)]
    assert len(bits) == (order * (order - 1) // 2 + 5) // 6 * 6
    neighbors = [0] * order
    cursor = 0
    for high in range(order):
        for low in range(high):
            if bits[cursor]:
                neighbors[high] |= 1 << low
                neighbors[low] |= 1 << high
            cursor += 1
    assert not any(bits[cursor:]) and encode(neighbors) == line
    return neighbors


def independent(neighbors, remaining, need):
    while remaining.bit_count() >= need:
        bit = remaining & -remaining
        remaining ^= bit
        if need == 1 or independent(neighbors, remaining & ~neighbors[bit.bit_length() - 1], need - 1):
            return True
    return False


def good(neighbors, limit=5):
    return all(not (neighbors[one] & neighbors[two])
               for one, mask in enumerate(neighbors) for two in range(one) if mask >> two & 1
               ) and not independent(neighbors, (1 << len(neighbors)) - 1, limit + 1)


def canonical(lines):
    lines = sorted(set(lines))
    if not lines:
        return {}
    reply = subprocess.run([ROOT / 'opt/bin/labelg', '-q'], check=True, text=True,
                           input='\n'.join(lines) + '\n', stdout=subprocess.PIPE).stdout.splitlines()
    assert len(reply) == len(lines)
    return dict(zip(lines, reply, strict=True))


def groups_sorted(values, *, doubles_first=False):
    def order(item):
        return (-item[0].bit_count(), item) if doubles_first else item
    return [tuple(group) for _, group in it.groupby(sorted(values, key=order), key=lambda item: item[0])]


def own_orders(groups):
    for order in it.product(*(tuple(it.permutations(group)) for group in groups)):
        yield tuple(it.chain.from_iterable(order))


def remap(neighbors, vertices):
    return [sum(1 << index for index, other in enumerate(vertices) if mask >> other & 1)
            for mask in (neighbors[vertex] for vertex in vertices)]


def from_catalogue(order, defect, limit=5, lines=None):
    if lines is None:
        source = ROOT / ('scratch/B/val/r3_6_15.g6' if order == 15 else f'gluing/val/r3_6_{order}.g6')
        lines = source.read_text().splitlines()
        labels = canonical(lines)
        assert len(lines) == {15: 64732, 16: 2576, 17: 7}[order] == len(labels) == len(set(labels.values()))
    placements = set()
    marks = 0
    for line in lines:
        neighbors = decode(line, order)
        assert good(neighbors, limit)
        roots = [index for index, mask in enumerate(neighbors) if mask.bit_count() == 4]
        for one, two in it.combinations(roots, 2):
            if not neighbors[one] >> two & 1:
                continue
            shores = ([pos for pos in range(order) if pos != two and neighbors[one] >> pos & 1],
                      [pos for pos in range(order) if pos != one and neighbors[two] >> pos & 1])
            crossing = [(left, right) for left, right in it.product(*shores) if neighbors[left] >> right & 1]
            if len(crossing) != 1:
                continue
            exterior = sorted(set(range(order)).difference((one, two), *shores))
            supports = [{site: set(anchors).intersection(pos for pos in range(order) if neighbors[site] >> pos & 1)
                         for site in exterior} for anchors in shores]
            if any(any(len(contact) not in (1, 2) for contact in side.values()) or
                   any(sum(contact == {anchor} for contact in side.values()) != 2 for anchor in anchors) or
                   len({frozenset(contact) for contact in side.values() if len(contact) == 2}) != order - 14
                   for anchors, side in zip(shores, supports, strict=True)):
                continue
            grid = [site for site in exterior if all(len(side[site]) == 1 for side in supports)]
            if len(grid) != 6 - defect:
                continue
            marks += 1
            outside = sorted(set(exterior).difference(grid))
            for exchange in (False, True):
                root_order = (two, one) if exchange else (one, two)
                allowed = []
                for anchors, crossed in zip(shores, crossing[0], strict=True):
                    allowed.append([(crossed, *tail) for tail in it.permutations(sorted(set(anchors) - {crossed}))])
                for left, right in it.product(*allowed[::(-1 if exchange else 1)]):
                    left_masks = {site: sum(1 << index for index, anchor in enumerate(left) if neighbors[site] >> anchor & 1)
                                  for site in exterior}
                    right_masks = {site: sum(1 << index for index, anchor in enumerate(right) if neighbors[site] >> anchor & 1)
                                   for site in exterior}
                    cell = {site: 3 * (left_masks[site].bit_length() - 1) + right_masks[site].bit_length() - 1
                            for site in grid}
                    board = ''.join(str(sum(index == value for value in cell.values())) for index in range(9))
                    grid_groups = groups_sorted((cell[site], site) for site in grid)
                    left_groups = groups_sorted(((left_masks[site], site) for site in outside), doubles_first=True)
                    right_groups = groups_sorted(((right_masks[site], site) for site in outside), doubles_first=True)
                    for grid_order, left_order, right_order in it.product(own_orders(grid_groups), own_orders(left_groups),
                                                                           own_orders(right_groups)):
                        left_slots = tuple(mask for mask, _ in left_order)
                        right_slots = tuple(mask for mask, _ in right_order)
                        right_number = {site: slot for slot, (_, site) in enumerate(right_order)}
                        mates = tuple(right_number[site] for _, site in left_order)
                        vertices = (*root_order, *left, *right, *(site for _, site in grid_order + left_order))
                        placements.add((board, left_slots, right_slots, mates, encode(remap(neighbors, vertices))))
    return placements, marks


def boards(defect):
    for cells in it.product(range(3), repeat=9):
        if cells[0] or sum(cells) != 6 - defect:
            continue
        left = tuple(2 - sum(cells[index:index + 3]) for index in (0, 3, 6))
        right = tuple(2 - sum(cells[index::3]) for index in range(3))
        if min(*left, *right) < 0:
            continue
        yield ''.join(map(str, cells)), left, right


def tails(contacts, limit):
    neighbors = [0] * (8 + len(contacts))
    for one, two in (*BOUND, *((8 + site, 2 + anchor) for site, support in enumerate(contacts)
                              for anchor in range(6) if support >> anchor & 1)):
        neighbors[one] |= 1 << two
        neighbors[two] |= 1 << one
    allowed = [(8 + low, 8 + high) for high, mask in enumerate(contacts)
               for low in range(high) if not mask & contacts[low]]

    def search(index):
        if index == len(allowed):
            if not independent(neighbors, (1 << len(neighbors)) - 1, limit + 1):
                yield encode(neighbors)
            return
        one, two = allowed[index]
        yield from search(index + 1)
        if not neighbors[one] & neighbors[two]:
            neighbors[one] ^= 1 << two
            neighbors[two] ^= 1 << one
            yield from search(index + 1)
            neighbors[one] ^= 1 << two
            neighbors[two] ^= 1 << one

    yield from search(0)


def literal(order, defect, limit=5, only=None):
    placements = set()
    layouts = 0
    for board, left, right in boards(defect):
        if only is not None and board not in only:
            continue
        grid = [(1 << row) | (1 << (col + 3)) for row, col in it.product(range(3), repeat=2)
                for _ in range(int(board[3 * row + col]))]
        for left_doubles, right_doubles in it.product(it.combinations(DOUBLES, order - 14), repeat=2):
            left_slots = (*left_doubles, *(1 << row for row, count in enumerate(left) for _ in range(count)))
            right_slots = (*right_doubles, *(1 << col for col, count in enumerate(right) for _ in range(count)))
            for mates in it.permutations(range(len(right_slots))):
                pairs = tuple((mask, right_slots[mate]) for mask, mate in zip(left_slots, mates, strict=True))
                if any((left_mask & right_mask & 1) or left_mask.bit_count() + right_mask.bit_count() < 3
                       for left_mask, right_mask in pairs):
                    continue
                layouts += 1
                contacts = grid + [left_mask | (right_mask << 3) for left_mask, right_mask in pairs]
                for graph in tails(contacts, limit):
                    placements.add((board, left_slots, right_slots, mates, graph))
    return placements, layouts


def export(out, order, defect, placements, limit=5, only=None, expect_mutations=False):
    labels = canonical(place[-1] for place in placements)
    by_board = defaultdict(set)
    by_type = defaultdict(set)
    alias = 0
    raw_shapes = Counter()
    short = None
    alias_witness = None
    alias_edge_witness = None
    option_edge_witness = None
    placement_counts = Counter()
    classes = [(place, labels[place[-1]]) for place in sorted(placements)]
    with (out / f'n{order}.d{defect}.placements.jsonl').open('w') as stream:
        for (board, left, right, mates, graph), label in classes:
            left_repeat = len(set(left)) < len(left)
            right_repeat = len(set(right)) < len(right)
            raw_shapes[(left_repeat, right_repeat)] += 1
            fate = ('R' if left_repeat else 'S') + ('R' if right_repeat else 'S')
            by_board[board].add(label)
            placement_counts[board] += 1
            by_type[fate].add((board, label))
            row = dict(board=board, left=left, right=right, mates=mates, graph=graph, canonical=label)
            print(json.dumps(row, separators=(',', ':')), file=stream)
            if not left_repeat and not right_repeat:
                alias += 1
            elif alias_witness is None and left_repeat:
                slots = [index for index, mask in enumerate(left) if left.count(mask) > 1]
                assert len(slots) == 2 and mates[slots[0]] != mates[slots[1]]
                alias_witness = dict(**row, identical_left_masks_at_distinct_sites=[8 + sum(map(int, board)) + slot for slot in slots])
            if defect == 2 and (option_edge_witness is None or (left_repeat and alias_edge_witness is None)):
                neighbors = decode(graph, order)
                start_options = 8 + sum(map(int, board))
                if option_edge_witness is None:
                    for one, two in it.combinations(range(start_options, order), 2):
                        if neighbors[one] >> two & 1:
                            option_edge_witness = dict(**row, true_edge=[one, two])
                            break
                if left_repeat and alias_edge_witness is None:
                    same = [start_options + slot for slot, mask in enumerate(left) if left.count(mask) > 1]
                    one, two = same
                    assert not neighbors[one] >> two & 1
                    for grid_site in range(8, start_options):
                        if neighbors[one] & neighbors[grid_site] & 28:
                            continue
                        one_edge = neighbors[grid_site] >> one & 1
                        two_edge = neighbors[grid_site] >> two & 1
                        if one_edge != two_edge:
                            alias_edge_witness = dict(**row, identical_left_masks_at_distinct_sites=same,
                                                      grid=grid_site, edge_values=[one_edge, two_edge],
                                                      right_mask_overlap=[bool(neighbors[site] & neighbors[grid_site] & 224)
                                                                          for site in same])
                            break
            if short is None and defect == 2:
                neighbors = decode(graph, order)
                for sites in it.combinations(range(8, order), 3):
                    if any(neighbors[one] >> two & 1 for one, two in it.combinations(sites, 2)):
                        continue
                    remaining = 255
                    for site in sites:
                        remaining &= ~neighbors[site]
                    if not independent(neighbors, remaining, limit + 1 - len(sites)):
                        short = dict(**row, independent_exterior=sites, available_boundary=remaining, required_padding=limit + 1 - len(sites))
                        break
    with (out / f'n{order}.d{defect}.classes.tsv').open('w') as stream:
        print('board\tcanonical_g6', file=stream)
        for board, labels_on_board in sorted(by_board.items()):
            for label in sorted(labels_on_board):
                print(board, label, sep='\t', file=stream)
    if defect == 2:
        with (out / f'n{order}.d{defect}.summary.tsv').open('w') as stream:
            print('board\tleft_deficit\tright_deficit\tclasses\tplacements', file=stream)
            for board, left_deficit, right_deficit in boards(defect):
                if only is None or board in only:
                    print(board, ''.join(map(str, left_deficit)), ''.join(map(str, right_deficit)),
                          len(by_board[board]), placement_counts[board], sep='\t', file=stream)
        alias_classes = {label for (_, left, right, _, _), label in classes
                         if len(set(left)) == len(left) and len(set(right)) == len(right)}
        full_classes = {label for _, label in classes}
        if expect_mutations:
            assert alias_witness and alias_edge_witness and option_edge_witness and short and 0 < alias < len(placements), (
                bool(alias_witness), bool(alias_edge_witness), bool(option_edge_witness), bool(short), alias)
        mutation = dict(alias=alias_witness, short_witness=short,
                        alias_edge=alias_edge_witness, option_edge=option_edge_witness,
                        lost_canonical=sorted(full_classes - alias_classes))
        (out / f'n{order}.mutations.json').write_text(json.dumps(mutation, indent=2) + '\n')
    print('order', order, 'defect', defect, 'placements', len(placements), 'classes', len(set(labels.values())),
          'nonempty boards', sum(bool(classes) for classes in by_board.values()), 'board-classes by type', {key: len(value) for key, value in sorted(by_type.items())},
          'labelled types (R=1,S=0)', sorted(raw_shapes.items()), 'alias survivors', alias, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('scan', 'full', 'positive'))
    parser.add_argument('out', type=Path)
    parser.add_argument('--historical', action='store_true')
    parser.add_argument('--only', nargs='+')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.phase == 'positive':
        assert args.only is None or set(args.only) <= {board for board, _, _ in boards(2)}
        placements, layouts = literal(16, 2, 6, args.only)
        labels = canonical(place[-1] for place in placements)
        scanned, marked = from_catalogue(16, 2, 6, sorted(set(labels.values())))
        if args.only is not None:
            scanned = {place for place in scanned if place[0] in args.only}
        print('positive n16 layouts', layouts, 'placements', len(placements), 'rescanned marks', marked,
              'missing/extra', len(scanned - placements), len(placements - scanned), flush=True)
        assert placements == scanned and (args.only is not None or placements)
        export(args.out, 16, 2, placements, limit=6, only=args.only, expect_mutations=args.only is None)
        return
    assert args.only is None
    if args.historical:
        for order, marks_expected in ((15, 174), (16, 11)):
            placements, marks = from_catalogue(order, 1)
            ref = set((ROOT / f'scratch/ideas/r018_N/ref.{order}.set').read_text().splitlines())
            assert marks == marks_expected and set(canonical(place[-1] for place in placements).values()) == ref
            print('historical calibration', order, 'marked pairs', marks, 'classes', len(ref), flush=True)
    for order in (16, 17):
        scanned, marks = from_catalogue(order, 2)
        print('physical scan', order, 'marked pairs', marks, flush=True)
        if args.phase == 'full':
            rebuilt, layouts = literal(order, 2)
            print('literal', order, 'layouts', layouts, 'placements', len(rebuilt),
                  'missing/extra', len(scanned - rebuilt), len(rebuilt - scanned), flush=True)
            assert scanned == rebuilt
        export(args.out, order, 2, scanned)


if __name__ == '__main__':
    main()
