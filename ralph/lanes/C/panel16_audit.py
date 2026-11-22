#!/usr/bin/env python3
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product, zip_longest
from pathlib import Path
from time import process_time

from verify_panel17 import bits, graph6


def mask(sites):
    return sum(1 << site for site in sites)


def g6(rows):
    data = ''.join(str(int(left in rows[right])) for right in range(len(rows)) for left in range(right))
    data += '0' * (-len(data) % 6)
    return chr(63 + len(rows)) + ''.join(chr(63 + int(data[index:index+6], 2)) for index in range(0, len(data), 6))


def controls(catalogue, destination):
    out = Path(destination)
    count = 0
    with (out/'control6.g6').open('w') as small, (out/'control7.g6').open('w') as large, \
            (out/'controls.tsv').open('w') as cases, (out/'plants.tsv').open('w') as plants:
        for host, rows in enumerate(graph6(Path(catalogue))):
            rows = [set(bits(row)) for row in rows]
            if {len(row) for row in rows} != {5}:
                continue
            for first in combinations(range(len(rows)), 2):
                for second in combinations(sorted(set.intersection(*(rows[site] for site in first))), 2):
                    if first >= second:
                        continue
                    roots = (first, second)
                    sides = [set.union(*(rows[site] for site in roots[side])) - set(roots[1-side]) for side in (0,1)]
                    ext = set(range(len(rows))) - set(first) - set(second)
                    neutral = ext.difference(*sides)
                    if len(neutral) != 1 or sorted(map(len,sides)) != [5,6]:
                        continue
                    if len(sides[0]) > len(sides[1]):
                        sides.reverse()
                        roots = roots[::-1]
                    assert not (sides[0] & sides[1])
                    [shared] = neutral
                    windows = [sorted(side | neutral) for side in sides]
                    frames = []
                    sorted_roots = []
                    for side, window in enumerate(windows):
                        indices = dict(zip(window, range(len(window))))
                        marks = sorted((mask(indices[site] for site in rows[root] if site in indices), root)
                                       for root in roots[side])
                        sorted_roots.append([root for _, root in marks])
                        frames.extend([count, indices[shared], *(mark for mark, _ in marks)])
                        file = [small, large][side]
                        print(g6([{indices[peer] for peer in rows[site] if peer in indices} for site in window]), file=file)
                    labels = [shared, *(site for window in windows for site in window if site != shared), *sum(sorted_roots, [])]
                    relabel = dict(zip(labels, range(len(labels))))
                    physical = g6([{relabel[peer] for peer in rows[site]} for site in labels])
                    print(count, count, *frames, file=cases)
                    print(count, host, first[0], first[1], second[0], second[1], physical, file=plants)
                    count += 1
    assert count == 153, count
    print('asymmetric marked plants:', count)


@lru_cache(maxsize=4096)
def independent_masks(graph, wanted):
    found = []

    def emit(available, chosen, remaining):
        if remaining == 0:
            found.append(chosen)
            return
        while available.bit_count() >= remaining:
            take = available & -available
            available ^= take
            emit(available & ~graph[take.bit_length()-1], chosen | take, remaining-1)

    emit((1 << len(graph))-1, 0, wanted)
    return tuple(found)


@lru_cache(maxsize=8192)
def hits_columns(graph, wanted):
    columns = [0]*len(graph)
    witnesses = independent_masks(graph, wanted)
    for index, witness in enumerate(witnesses):
        for site in bits(witness):
            columns[site] |= 1 << index
    return tuple(columns), (1 << len(witnesses))-1


@lru_cache(maxsize=200_000)
def hits_all(graph, remove, wanted):
    columns, full = hits_columns(graph, wanted)
    return union(columns[site] for site in bits(remove)) == full


def source_groups(marks):
    incidence = Counter(site for mark in marks for site in bits(mark))
    return [group for mark in marks if (group := tuple(site for site in bits(mark) if incidence[site] == 1))]


def parse_cases(args):
    catalogues = [list(graph6(Path(path))) for path in (args.small, args.large)]
    result = {}
    for line in Path(args.cases).open():
        left, right, *tail = map(int, line.split())
        stride = args.roots + 2
        frames = []
        for side in (0,1):
            host, neutral, *marks = tail[side*stride:(side+1)*stride]
            frames.append((tuple(catalogues[side][host]), neutral, marks))
        assert len(tail) == 2*stride and (left,right) not in result
        result[left,right] = tuple(frames)
    return result


def vertex_labels(frames):
    offset = 1
    labels = []
    for graph, neutral, _ in frames:
        current = {}
        for site in range(len(graph)):
            current[site] = 0 if neutral == site else offset
            offset += site != neutral
        labels.append(current)
    return labels, offset


def group_spec(frames):
    groups = [source_groups(frame[2]) for frame in frames]
    return [(side, sites) for pair in zip_longest(*groups) for side, sites in enumerate(pair) if sites is not None]


def packages(args, frames, spec):
    side, sites = spec
    source, zsource, _ = frames[side]
    target, ztarget, _ = frames[1-side]
    bound = args.alpha - args.roots + 1
    options = []
    for site in sites:
        known = list(bits(source[site]))
        share = zsource in known
        size = args.degree - 1 - len(known) + share
        options.append(tuple(row for row in independent_masks(target,size)
                             if bool(row & (1<<ztarget)) == share and hits_all(target,row,bound)))
    domain = []

    def extend(prefix):
        if len(prefix) == len(sites):
            domain.append(prefix)
            return
        for candidate in options[len(prefix)]:
            if all(hits_all(target, candidate | union(pick), bound-count)
                   for count in range(1, len(prefix)+1) for pick in combinations(prefix,count)):
                extend(prefix+(candidate,))

    extend(())
    return domain


def union(rows):
    result = 0
    for row in rows:
        result |= row
    return result


def bindings(frames, specs, flat):
    known = {}
    offset = 0
    for side, sites in specs:
        for site in sites:
            row = flat[offset]
            target, ztarget, _ = frames[1-side]
            for peer in range(len(target)):
                if peer == ztarget:
                    continue
                edge = (site,peer) if side == 0 else (peer,site)
                present = bool(row & (1<<peer))
                if edge in known and known[edge] != present:
                    return None
                known[edge] = present
            offset += 1
    assert offset == len(flat)
    return known


def literal_index(frames, specs, domains):
    if not all(domains):
        return set(), 0
    masks = []
    other_sizes = [len(frame[0]) for frame in frames]
    for (side, sites), domain in zip(specs, domains):
        offset = lambda site, peer: site*other_sizes[1]+peer if side == 0 else peer*other_sizes[1]+site
        cover = mask(offset(site,peer) for site in sites for peer in range(other_sizes[1-side]) if peer != frames[1-side][1])
        choices = []
        for package in domain:
            row = mask(offset(site,peer) for site, neighbourhood in zip(sites,package)
                       for peer in bits(neighbourhood) if peer != frames[1-side][1])
            choices.append((row,package))
        masks.append((cover,choices))
    assignments = [None]*len(specs)
    remaining = set(range(len(specs)))
    covered = 0
    sequence = []
    while remaining:
        index = min(remaining,key=lambda key: (len(masks[key][1]), -(covered & masks[key][0]).bit_count(),key))
        remaining.remove(index)
        cover, choices = masks[index]
        shared = cover & covered
        bucket = defaultdict(list)
        for row, package in choices:
            bucket[row & shared].append((row, package))
        sequence.append((index,shared,bucket))
        covered |= cover
    solutions = set()
    probes = 0

    def extend(depth, present):
        nonlocal probes
        if depth == len(sequence):
            solutions.add(sum(assignments, ()))
            return
        index, overlap, bucket = sequence[depth]
        for row, package in bucket.get(present & overlap, ()):
            probes += 1
            if probes > 2_000_000:
                raise RuntimeError('independent branch cap')
            assignments[index] = package
            extend(depth+1, present | row)

    extend(0,0)
    return solutions,probes


def bounds(frames, labelled, fixed, roots):
    labels, size = labelled
    known, unknown = set(), set()
    for side, (graph, neutral, marks) in enumerate(frames):
        for site, row in enumerate(graph):
            for peer in bits(row):
                known.add(tuple(sorted((labels[side][site], labels[side][peer]))))
        for root, row in enumerate(marks):
            for site in bits(row):
                known.add((labels[side][site], size+side*roots+root))
    known.update(product(range(size,size+roots), range(size+roots,size+2*roots)))
    for (ls, lv), (rs, rv) in product(*[list(label.items()) for label in labels]):
        if lv == 0 or rv == 0:
            continue
        status = fixed.get((ls,rs))
        if status is True:
            known.add((lv,rv))
        elif status is None:
            unknown.add((lv,rv))
    return known, known | unknown


def terminal(lower, upper, order, degree, cap, alpha):
    vertices = range(order)

    def adjacency(edges):
        adj = [set() for _ in vertices]
        for first, last in edges:
            adj[first].add(last)
            adj[last].add(first)
        return adj

    def too_independent(candidates, graph, need):
        if len(candidates) < need:
            return False
        if need == 1:
            return bool(candidates)
        while len(candidates) >= need:
            site = min(candidates, key=lambda present: len(graph[present] & candidates))
            candidates = candidates - {site}
            if too_independent(candidates-graph[site], graph, need-1):
                return True
        return False

    while True:
        lows, highs = adjacency(lower), adjacency(upper)
        if not lower <= upper or any(not len(lo) <= degree <= len(hi) for lo, hi in zip(lows, highs)):
            return 0
        if any(lows[first] & lows[last] for first, last in lower):
            return 1
        if any(len(first & last) > cap for first, last in combinations(lows,2)):
            return 2
        if too_independent(set(vertices), highs, alpha+1):
            return 3
        bans, demands = set(), set()
        for first,last in upper-lower:
            if max(len(lows[first]),len(lows[last])) == degree or lows[first] & lows[last]:
                bans.add((first,last))
            if min(len(highs[first]),len(highs[last])) == degree:
                demands.add((first,last))
        if not bans and not demands:
            return 4
        lower = lower | demands
        upper = upper - bans


def load_plant_line(line):
    identity, host, first, second, third, fourth, text = line.split()
    edges = set()
    encoded = ''.join(f'{ord(char)-63:06b}' for char in text[1:])
    for flag, (low, high) in zip(encoded, ((low,high) for high in range(ord(text[0])-63) for low in range(high))):
        if flag == '1':
            edges.add((low, high))
    return (int(identity), int(identity)), edges


def audit(args):
    cases = parse_cases(args)
    from_cpp = defaultdict(dict)
    for line in Path(args.fills).open():
        left,right,reason,*flat = map(int, line.split())
        assert tuple(flat) not in from_cpp[left,right]
        from_cpp[left,right][tuple(flat)] = reason
    with Path(args.stats).open() as stream:
        header = stream.readline().split()
        stats = {(int(entry['left']),int(entry['right'])): entry for line in stream
                 if (entry := dict(zip(header,line.split())))}
    assert len(stats) == len(cases) and stats.keys() == cases.keys() and from_cpp.keys() <= cases.keys()
    plants = dict(map(load_plant_line,Path(args.plants).open())) if args.plants else {}
    checked, corruptions, left_nonempty, right_nonempty, visited, totals = 0, 0, 0, 0, 0, Counter()
    accepted_mutants = [0,0]
    max_probes = 0
    one_empty_group = 0
    max_cpu = (0, ())
    assert not (args.screen and args.plants)
    for key, frames in cases.items():
        started = process_time()
        specs = group_spec(frames)
        labelled = vertex_labels(frames)
        reported = list(map(int,stats[key]['before'].split(',')))
        assert len(reported) == len(specs) and stats[key]['filtered_cap'] == 'no', key
        if args.screen and 0 in reported:
            zeroes = [index for index,count in enumerate(reported) if not count]
            verifier = min(zeroes,key=lambda index: (len(specs[index][1]),index))
            assert not packages(args,frames,specs[verifier]), (key,verifier)
            assert not from_cpp[key] and not any(int(stats[key][column]) for column in ('degree','triangle','codegree','I','live')), key
            one_empty_group += 1
            visited += 1
            elapsed = process_time() - started
            max_cpu = max(max_cpu,(elapsed,key))
            if args.timing:
                print(*key, 'empty', f'{elapsed:.6f}', verifier, flush=True)
            continue
        domains = [packages(args,frames,spec) for spec in specs]
        assert [len(domain) for domain in domains] == reported, key
        by_side = [all(domain for (side,_),domain in zip(specs,domains) if side == wanted) for wanted in (0,1)]
        left_nonempty += by_side[0]
        right_nonempty += by_side[1]
        reference_fills, probes = literal_index(frames,specs,domains)
        assert reference_fills == from_cpp[key].keys(), (key,len(reference_fills),len(from_cpp[key]))
        max_probes = max(max_probes, probes)
        seen = Counter()
        for flat, reason in from_cpp[key].items():
            cursor = 0
            for (_,sites), domain in zip(specs,domains):
                assert flat[cursor:cursor+len(sites)] in domain, key
                cursor += len(sites)
            fixed = bindings(frames,specs,flat)
            assert fixed is not None, key
            lower, upper = bounds(frames, labelled, fixed, args.roots)
            assert terminal(lower,upper,labelled[1]+2*args.roots,args.degree,args.cap,args.alpha) == reason, (key,flat,reason)
            seen[reason] += 1
        assert [seen[index] for index in range(5)] == [int(stats[key][column]) for column in ('degree','triangle','codegree','I','live')]
        totals.update(seen)
        if key in plants:
            assert all(by_side)
            plant = plants[key]
            assert terminal(plant,plant,labelled[1]+2*args.roots,args.degree,args.cap,args.alpha) == 4
            labels, _ = labelled
            flat = []
            positions = [{},{}]
            for side,sites in specs:
                for site in sites:
                    positions[side][site] = len(flat)
                    vertex = labels[side][site]
                    flat.append(mask(peer for peer,label in labels[1-side].items() if tuple(sorted((vertex,label))) in plant))
            assert from_cpp[key].get(tuple(flat)) == 4, key
            for side in (0,1):
                site = next(iter(positions[side]))
                peer = next(iter(positions[1-side]))
                broken = flat.copy()
                broken[positions[side][site]] ^= 1<<peer
                assert bindings(frames,specs,broken) is None and tuple(broken) not in from_cpp[key], key
                corruptions += 1
            offset = 0
            for (side,sites), domain in zip(specs,domains):
                for package in domain:
                    changed = flat[:offset]+list(package)+flat[offset+len(sites):]
                    if bindings(frames,specs,changed) is None:
                        assert tuple(changed) not in from_cpp[key], key
                        accepted_mutants[side] += 1
                        break
                offset += len(sites)
            fixed = bindings(frames,specs,flat)
            lower, upper = bounds(frames,labelled,fixed,args.roots)
            assert lower <= plant <= upper
            physical_cross = [tuple(sorted((labels[0][ls],labels[1][rs]))) for ls, rs in fixed if fixed[ls,rs]]
            assert physical_cross
            assert terminal(lower,upper-{physical_cross[0]},labelled[1]+2*args.roots,args.degree,args.cap,args.alpha) == 0
            checked += 1
        visited += 1
        elapsed = process_time() - started
        max_cpu = max(max_cpu,(elapsed,key))
        if args.timing:
            print(*key, 'join', f'{elapsed:.6f}', probes, flush=True)
    assert checked == len(plants)
    print(f'{visited} verified IDs: {one_empty_group} exact single-empty-group checks,',
          f'{visited-one_empty_group} full domain reconstructions ({left_nonempty}/{right_nonempty} nonempty left/right directions),',
          f'{sum(totals.values())} terminals', [totals[index] for index in range(5)])
    print(f'max {max_probes} independent-join probes; {checked} physical plants retained, {corruptions} crossing flips rejected,',
          f'{accepted_mutants} locally valid conflicting packages by side, {checked} terminal corruptions rejected')
    print(f'max {max_cpu[0]:.6f} CPU seconds at {max_cpu[1]}')


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command',required=True)
    plant = commands.add_parser('controls')
    plant.add_argument('catalogue')
    plant.add_argument('destination')
    check = commands.add_parser('audit')
    for arg in ('small','large','cases','fills','stats'):
        check.add_argument(arg)
    for arg in ('degree','cap','alpha','roots'):
        check.add_argument(arg,type=int)
    check.add_argument('--plants')
    check.add_argument('--screen',action='store_true')
    check.add_argument('--timing',action='store_true')
    args = parser.parse_args()
    if args.command == 'controls':
        controls(args.catalogue,args.destination)
    else:
        audit(args)


if __name__ == '__main__':
    main()
