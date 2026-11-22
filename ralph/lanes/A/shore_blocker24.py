"""Independent one-shore I_k clauses and controls; no SAT solver."""

import json
import sys
from collections import Counter
from functools import cache
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

from physical_blocker23 import H5, Layout, alpha, to_graph6, toy, triangle_free, true_clause


def activity(layout, side, slot):
    return 1 + sum(len(shore) for shore in layout.slots[:side]) + slot


def row_key(row):
    return tuple(sorted(row))


def label(layout, sites, side):
    return (tuple(sorted(site for site in sites if isinstance(site, int))),
            tuple(sorted(site[side] for site in sites if isinstance(site, tuple))))


def opposite_mask(layout, boundary, side):
    base = 2 + (1 - side) * layout.width
    return sum(1 << (anchor - base) for anchor in boundary if base <= anchor < base + layout.width)


def mates(layout, side, slot):
    return [(pair[1 - side], gate) for pair, gate in layout.gates.items() if pair[side] == slot]


def projected(layout, side, boundary, coords, order):
    size = len(layout.grid)
    assert side in (0, 1) and len(boundary) + len(coords) == order
    assert boundary == tuple(sorted(set(boundary))) and coords == tuple(sorted(set(coords)))
    assert all(0 <= site < layout.boundary for site in boundary)
    assert all(0 <= coord < size + len(layout.slots[side]) for coord in coords)
    if any(layout.pair(first, second)[0] == 'boundary-edge' for first, second in combinations(boundary, 2)):
        return None
    base = 2 + side * layout.width
    own = sum(1 << (anchor - base) for anchor in boundary if base <= anchor < base + layout.width)
    off = opposite_mask(layout, boundary, side)
    guards = []
    bad = []
    domains = {}
    for coord in coords:
        if coord < size:
            if own & layout.grid[coord][side] or off & layout.grid[coord][1 - side]:
                return None
            continue
        slot = coord - size
        if own & layout.slots[side][slot]:
            return None
        guards.append(-activity(layout, side, slot))
        good = []
        for mate, gate in mates(layout, side, slot):
            if off & layout.slots[1 - side][mate]:
                bad.append(gate)
            else:
                good.append(mate)
        domains[slot] = good
    edges = [layout.edges[side][pair] for pair in combinations(coords, 2) if pair in layout.edges[side]]
    clause = row_key(guards + bad + edges)
    assert len(clause) == len(set(clause))
    return dict(side=side, boundary=boundary, coords=coords, guards=guards, bad=bad, edges=edges,
                clause=clause, domains=domains)


def independent_sets(adj, count):
    def visit(remaining, want, chosen):
        if not want:
            yield chosen
        else:
            while remaining.bit_count() >= want:
                low = remaining & -remaining
                remaining ^= low
                vertex = low.bit_length() - 1
                yield from visit(remaining & ~adj[vertex], want - 1, (*chosen, vertex))
    yield from visit((1 << len(adj)) - 1, count, ())


def with_activity(layout, selected, positive):
    return positive | {activity(layout, side, pair[side]) for pair in selected for side in (0, 1)}


def controls(path):
    counts = Counter()
    mutations = {}
    for text in path.read_text().splitlines():
        plant = json.loads(text)
        layout, sites, adj, positive = toy(plant)
        assert triangle_free(adj) and alpha(adj) == 6
        positive = with_activity(layout, list(enumerate(plant['mates'])), positive)
        counts['plants'] += 1
        near = set()
        for six in independent_sets(adj, 6):
            bits = sum(1 << item for item in six)
            counts['I6'] += 1
            for vertex, neighbors in enumerate(adj):
                if bits >> vertex & 1 or (bits & neighbors).bit_count() != 1:
                    continue
                near.add(tuple(sorted((*six, vertex))))
        for positions in sorted(near):
            names = [sites[index] for index in positions]
            real_edges = [(first, second) for first, second in combinations(positions, 2) if adj[first] >> second & 1]
            assert len(real_edges) == 1
            for side in (0, 1):
                boundary, coords = label(layout, names, side)
                receipt = projected(layout, side, boundary, coords, 7)
                if receipt is None:
                    counts[f'fixed_{side}'] += 1
                    continue
                counts[f'live_{side}'] += 1
                truths = [literal for literal in receipt['clause'] if true_clause([literal], positive)]
                assert len(truths) == 1 and truths[0] > 0
                omitted = truths[0]
                if omitted in receipt['bad']:
                    counts[f'contact_{side}'] += 1
                    key = f'drop_bad_{side}'
                    if key not in mutations:
                        mutant = [literal for literal in receipt['clause'] if literal != omitted]
                        assert not true_clause(mutant, positive)
                        mutations[key] = dict(plant=plant, positions=positions, unique_edge=real_edges[0],
                                              omitted=omitted, full=receipt, mutant=mutant)
                else:
                    assert omitted in receipt['edges']
                    key = f'drop_activity_{side}'
                    if key in mutations:
                        continue
                    for deleted in real_edges[0]:
                        site = sites[deleted]
                        if not layout.gate(site):
                            continue
                        chosen = [index for index in range(len(adj)) if index != deleted]
                        remaining = [sum(1 << new for new, old in enumerate(chosen) if adj[index] >> old & 1)
                                     for index in chosen]
                        assert triangle_free(remaining) and alpha(remaining) == 6
                        size = len(layout.grid)
                        omitted_activity = -activity(layout, side, site[side] - size)
                        absent_bits = {layout.gate(site), *(activity(layout, axis, site[axis] - size)
                                                           for axis in (0, 1))}
                        absent_bits.update(edge for axis in (0, 1) for pair, edge in layout.edges[axis].items()
                                           if site[axis] in pair)
                        restricted = positive - absent_bits
                        assert layout.decode([sites[index] for index in chosen], restricted) == remaining
                        assert [literal for literal in receipt['clause'] if true_clause([literal], restricted)] == [omitted_activity]
                        mutant = [literal for literal in receipt['clause'] if literal != omitted_activity]
                        assert not true_clause(mutant, restricted)
                        mutations[key] = dict(plant=plant, positions=positions, removed_position=deleted,
                                              induced_plant=to_graph6(remaining), unique_edge=real_edges[0],
                                              omitted=omitted_activity, full=receipt, mutant=mutant)
                        break
    assert counts['plants'] == 1960 and set(mutations) == {
        'drop_bad_0', 'drop_bad_1', 'drop_activity_0', 'drop_activity_1'}
    return dict(counts=dict(counts), mutants=mutations)


def literal_witness(layout, data):
    size = len(layout.grid)
    names = sorted(data['boundary']) + [(coord, coord) for coord in sorted(data['grid'])] + [
        (size + left, size + right) for left, right in sorted(data['options'])]
    assert len(names) == 10
    exact = layout.blocker(names)
    assert exact is not None
    return row_key(exact['compact'])


def match_count(layout, side, selected, domains):
    active = [sorted(pair[axis] for pair in selected) for axis in (0, 1)]
    other = set(active[1 - side])
    available = [sorted(set(domains.get(slot, other)) & other & {mate for mate, _ in mates(layout, side, slot)})
                 for slot in active[side]]

    @cache
    def count(index, used):
        if index == len(available):
            return 1
        return sum(count(index + 1, used | 1 << mate) for mate in available[index] if not used >> mate & 1)

    ways = count(0, 0)
    if not ways:
        count.cache_clear()
        return 0, None
    witness = []
    used = 0
    for index, items in enumerate(available):
        mate = next(item for item in items if not used >> item & 1 and count(index + 1, used | 1 << item))
        pair = (active[side][index], mate)
        witness.append(pair if side == 0 else pair[::-1])
        used |= 1 << mate
    count.cache_clear()
    return ways, sorted(witness)


def matching_ie(layout, side, selected, domains):
    active = tuple(sorted(pair[side] for pair in selected))
    peers = tuple(sorted(pair[1 - side] for pair in selected))
    choices = {slot: set(mate for mate, _ in mates(layout, side, slot)) for slot in active}
    masks = []
    for slot in active:
        masks.append(sum(1 << j for j, mate in enumerate(peers)
                         if mate in choices[slot] and
                         (slot not in domains or mate in domains[slot])))
    total = 0
    for allowed in range(1 << len(peers)):
        product = (-1) ** (len(peers) - allowed.bit_count())
        for mask in masks:
            product *= (mask & allowed).bit_count()
        total += product
    return total


def read_model(folder, binding):
    assert (folder / 'solve.status').read_text().strip() == '10'
    assert 'OPEN SAT relaxation' in (folder / 'result').read_text()
    signed = [int(word) for line in (folder / 'solve.log').read_text().splitlines() if line.startswith('v ')
              for word in line.split()[1:] if word != '0']
    positive = {literal for literal in signed if literal > 0}
    with (folder / 'grid.cnf').open() as stream:
        assert next(stream).split() == ['p', 'cnf', str(binding['variables']), str(binding['clauses'])]
        assert sorted(map(abs, signed)) == list(range(1, binding['variables'] + 1))
        rows = set()
        checked = 0
        for line in stream:
            row = tuple(map(int, line.split()))
            assert row[-1] == 0 and true_clause(row[:-1], positive)
            rows.add(row_key(row[:-1]))
            checked += 1
        assert checked == binding['clauses']
    return positive, rows


def bind_mates(layout, rows):
    for side in (0, 1):
        for slot in range(len(layout.slots[side])):
            active = activity(layout, side, slot)
            gates = [gate for _, gate in mates(layout, side, slot)]
            assert row_key([-active, *gates]) in rows
            assert all(row_key([-gate, active]) in rows for gate in gates)
            assert all(row_key([-first, -second]) in rows for first, second in combinations(gates, 2))


def bind_channels(layout, receipt, rows):
    side = receipt['side']
    size = len(layout.grid)

    def ends(coord):
        if coord < size:
            return [(coord, 0)]
        allowed = receipt['domains'][coord - size]
        return [(size + mate, gate) for mate, gate in mates(layout, side, coord - size) if mate in allowed]

    seen = set()
    for first, second in combinations(receipt['coords'], 2):
        literal = layout.edges[side].get((first, second), 0)
        for (left, first_gate), (right, second_gate) in product(ends(first), ends(second)):
            if left == right:
                continue
            other = layout.edges[1 - side].get(tuple(sorted((left, right))), 0)
            if other == literal:
                continue
            guards = [-gate for gate in (first_gate, second_gate) if gate]
            for source, destination in ((literal, other), (other, literal)):
                if source:
                    clause = row_key([*guards, -source, *([destination] if destination else [])])
                    assert clause in rows
                    seen.add(clause)
    return len(seen)


def target(base, manifest, name):
    folder = base / 'work' / name
    binding = json.loads((folder / 'binding.json').read_text())
    board = binding['board']
    assert binding['grid'] == manifest[board]['grid']
    assert binding['manifest'] == sha256((H5 / 'manifest.json').read_bytes()).hexdigest()
    assert sha256((folder / 'witness.jsonl').read_bytes()).hexdigest() == binding['witnesses']
    layout = Layout(binding['grid'])
    positive, rows = read_model(folder, binding)
    bind_mates(layout, rows)
    prefix = binding['prefix']
    assert prefix == name.split('_')[-1] and all(((index in positive) == (sign == '1') and
                                                ((index if sign == '1' else -index),) in rows)
                                               for index, sign in enumerate(prefix, 1))
    selected = [pair for pair, gate in layout.gates.items() if gate in positive]
    sites = layout.sites(selected)
    adj = layout.decode(sites, positive)
    assert len(adj) == 40 and len(selected) == 11 and triangle_free(adj)
    assert sum(degree.bit_count() for degree in adj) // 2 == 170
    used = {literal_witness(layout, json.loads(line)) for line in (folder / 'witness.jsonl').read_text().splitlines()}
    assert used <= rows
    old_seeds = {literal_witness(layout, json.loads(line)) for line in
                 (base / 'seeds-follow' / f'{board}.jsonl').read_text().splitlines()}
    best = None
    counts = Counter()

    @cache
    def cached_matches(side, allowed):
        return match_count(layout, side, selected, dict(allowed))[0]

    def matches(side, domains):
        return cached_matches(side, tuple(sorted((slot, tuple(domain)) for slot, domain in domains.items())))

    for positions in independent_sets(adj, 10):
        counts['I10'] += 1
        names = [sites[pos] for pos in positions]
        exact = layout.blocker(names)
        assert not true_clause(exact['compact'], positive)
        assert row_key(exact['compact']) not in rows and row_key(exact['compact']) not in used
        if row_key(exact['compact']) in old_seeds:
            counts['old_seed_exact'] += 1
            continue
        for side in (0, 1):
            boundary, coords = label(layout, names, side)
            receipt = projected(layout, side, boundary, coords, 10)
            assert receipt and not true_clause(receipt['clause'], positive) and receipt['clause'] not in rows
            fixed = {name[side] - len(layout.grid): [name[1 - side] - len(layout.grid)] for name in names
                     if layout.gate(name)}
            if not fixed:
                continue
            width = len(receipt['clause'])
            if best is not None and width > best[0][0]:
                continue
            new = matches(side, receipt['domains'])
            old = matches(side, fixed)
            if new <= old:
                continue
            key = (width, -new, side, positions)
            if best is None or key < best[0]:
                best = (key, dict(positions=positions, sites=names, exact=exact, projected=receipt,
                                  projected_matchings=new, exact_matchings=old), fixed)
    cached_matches.cache_clear()
    assert counts['I10'] and best
    _, witness, fixed = best
    receipt = witness['projected']
    side = receipt['side']
    witness['bound_channel_rows'] = bind_channels(layout, receipt, rows)
    assert witness['projected_matchings'] == matching_ie(layout, side, selected, receipt['domains'])
    assert witness['exact_matchings'] == matching_ie(layout, side, selected, fixed)
    alternatives = []
    for slot, good in receipt['domains'].items():
        without = [mate for mate in good if mate not in fixed[slot]]
        count, alternative = match_count(layout, side, selected, {**receipt['domains'], slot: without})
        if count:
            assert alternative is not None
            alternatives.append(alternative)
    assert alternatives
    alternative = min(alternatives)
    assert all(any(pair[side] == slot and pair[1 - side] in good for pair in alternative)
               for slot, good in receipt['domains'].items())
    alternative_positive = with_activity(layout, alternative, {layout.gates[pair] for pair in alternative})
    size = len(layout.grid)
    alternative_sites = [*receipt['boundary'], *((coord, coord) for coord in receipt['coords'] if coord < size),
                         *((size + pair[0], size + pair[1]) for pair in alternative
                           if size + pair[side] in receipt['coords'])]
    assert label(layout, alternative_sites, side) == (receipt['boundary'], receipt['coords'])
    alternate_exact = layout.blocker(alternative_sites)
    assert alternate_exact is not None
    assert true_clause(witness['exact']['compact'], alternative_positive)
    assert not true_clause(alternate_exact['compact'], alternative_positive)
    assert not true_clause(receipt['clause'], alternative_positive)
    witness['alternative_mates'] = alternative
    witness['alternative_witness_sites'] = alternative_sites
    return dict(board=board, leaf=name, prefix=prefix, checked_cnf_rows=binding['clauses'],
                formula_sha256=sha256((folder / 'grid.cnf').read_bytes()).hexdigest(),
                selected=selected, graph=to_graph6(adj), counts=dict(counts), witness=witness)


def main():
    phase, *names = sys.argv[1:]
    if phase == 'controls':
        assert not names
        result = controls(H5 / 'n17.d3.placements.jsonl')
    else:
        assert phase == 'target' and names
        base = Path.cwd() / 'inputs'
        manifest = json.loads((H5 / 'manifest.json').read_text())
        result = [target(base, manifest, name) for name in names]
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
