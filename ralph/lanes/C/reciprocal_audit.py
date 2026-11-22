import argparse
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
from random import Random
from time import process_time
import sys


ROOT = Path(__file__).resolve().parents[3]
SOURCE22 = ROOT / 'gluing/val/r3_7_22.g6'
SOURCE21 = ROOT / 'scratch/B/val/r3_7_21.g6'
SCOUT = ROOT / 'scratch/ideas/r009_R'


def decode(line):
    code = [ord(char) - 63 for char in line.strip()]
    adj = [set() for _ in range(code[0])]
    pairs = ((low, high) for high in range(len(adj)) for low in range(high))
    for index, (low, high) in enumerate(pairs):
        if code[1 + index // 6] >> (5 - index % 6) & 1:
            adj[low].add(high)
            adj[high].add(low)
    return adj


def code_window(adj, vertices):
    raw = [int(src in adj[dst]) for high, dst in enumerate(vertices) for src in vertices[:high]]
    raw.extend([0] * (-len(raw) % 6))
    return chr(63 + len(vertices)) + ''.join(chr(63 + sum(raw[ix + bit] << (5 - bit) for bit in range(6)))
                                            for ix in range(0, len(raw), 6))


def vertices(mask):
    return [vertex for vertex in range(mask.bit_length()) if mask >> vertex & 1]


def mask(vertices):
    return sum(1 << vertex for vertex in vertices)


def controls():
    counts = []
    left, right, planted = [], [], []
    for line in SOURCE22.read_text().splitlines():
        adj = decode(line)
        if set(map(len, adj)) != {6}:
            continue
        assert all(not (adj[src] & adj[dst]) for src in range(22) for dst in adj[src])
        assert not any(all(not (adj[src] & group) for src in group)
                       for group in map(set, combinations(range(22), 7)))
        before = len(planted)
        for a0, a1 in combinations(range(22), 2):
            roots_a = {a0, a1}
            roots_b = adj[a0] & adj[a1]
            if len(roots_b) != 2:
                continue
            b0, b1 = sorted(roots_b)
            if len(adj[b0] & adj[b1]) != 3:
                continue
            names1 = sorted(set(range(22)) - roots_a - adj[a0] - adj[a1])
            names2 = sorted(set(range(22)) - roots_b - adj[b0] - adj[b1])
            overlap = set(names1) & set(names2)
            assert (len(names1), len(names2), len(overlap)) == (10, 11, 3)
            left.append(code_window(adj, names1))
            right.append(code_window(adj, names2))
            roots1 = sorted(mask(index for index, vertex in enumerate(names1) if vertex in adj[root]) for root in roots_b)
            roots2 = sorted(mask(index for index, vertex in enumerate(names2) if vertex in adj[root]) for root in roots_a)
            overlap1 = mask(index for index, vertex in enumerate(names1) if vertex in overlap)
            overlap2 = mask(index for index, vertex in enumerate(names2) if vertex in overlap)
            mapping = [names2.index(vertex) for vertex in names1 if vertex in overlap]
            idx = len(planted)
            planted.append((idx, overlap1, *roots1, 0, idx, overlap2, *roots2, 0, *mapping))
        counts.append(len(planted)-before)
    assert len(counts) == 10 and sum(counts) == 395 and min(counts) > 0
    for output, rows in [('cal-10.g6', left), ('cal-11.g6', right), ('cal-planted.tsv', planted)]:
        Path(output).write_text(''.join((' '.join(map(str, row)) if isinstance(row, tuple) else row) + '\n' for row in rows))
    print('independently extracted', counts)


def marks_by_core(adj, core_order, degree, cap, roots, fixed_core=None):
    width = degree - roots
    sites = set(range(len(adj)))
    codes = [[len(first & second) for second in adj] for first in adj]
    result = {}
    cores = combinations(range(len(adj)), core_order) if fixed_core is None else [vertices(fixed_core)]
    for shared in cores:
        private = sites - set(shared)
        if any(not 0 <= degree - len(adj[vertex] & private) <= width for vertex in shared):
            continue
        inds = [set(choice) for choice in combinations(sorted(private), width)]
        inds = [choice for choice in inds if not any(adj[vertex] & choice for vertex in choice)
                and max(len(row & choice) for row in adj) <= cap]
        out = []
        for selected in combinations(inds, roots):
            if set.union(*selected) != private or any(len(aa & bb) > cap-roots for aa, bb in combinations(selected,2)):
                continue
            roles = [{role for role, nodes in enumerate(selected) if vertex in nodes} for vertex in range(len(adj))]
            if any(len(adj[vertex]) + len(roles[vertex]) > degree or
                   len(adj[vertex] & private) + len(roles[vertex]) < roots for vertex in private):
                continue
            if any(codes[src][dst] + len(roles[src] & roles[dst]) > cap
                   for src, dst in combinations(range(len(adj)),2) if roles[src] & roles[dst]):
                continue
            out.append(tuple(sorted(map(mask, selected))) + (0,) * (3-roots))
        if out:
            result[mask(shared)] = out
    return result


def transfers(first, first_core, other, other_core, degree):
    left, right = vertices(first_core), vertices(other_core)
    domains = {src: [dst for dst in right if len(first[src] & set(left)) == len(other[dst] & set(right)) and
                     len(first[src])+len(other[dst]) == degree+len(first[src] & set(left))] for src in left}
    def assignments(pending, placed, used):
        if not pending:
            yield tuple(placed[src] for src in left)
            return
        src, *tail = pending
        for dst in domains[src]:
            if dst in used or any((other_dst in other[dst]) != (other_src in first[src]) for other_src, other_dst in placed.items()):
                continue
            yield from assignments(tail, placed | {src: dst}, used | {dst})
    yield from assignments(sorted(left, key=lambda src: len(domains[src])), {}, set())


def keys(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        *ints, reason, witness = line.split()
        key = tuple(map(int, ints))
        assert key not in result, key
        result[key] = (reason, int(witness))
    return result


def control_check():
    expected = {tuple(map(int, line.split())) for line in Path('cal-planted.tsv').read_text().splitlines()}
    actual = keys('cal-planted-indexed.tsv')
    assert len(expected) == 395 and expected <= actual.keys()
    assert all(actual[key] == ('live', 0) for key in expected)
    direct = keys('cal-small-direct.tsv')
    indexed = keys('cal-small-indexed.tsv')
    assert direct == indexed
    left = [decode(line) for line in Path('cal-small-10.g6').read_text().splitlines()]
    right = [decode(line) for line in Path('cal-small-11.g6').read_text().splitlines()]
    left_cards = [marks_by_core(adj, 3, 6, 6, 2) for adj in left]
    right_cards = [marks_by_core(adj, 3, 6, 6, 2) for adj in right]
    brute = set()
    for left_id, cards_left in enumerate(left_cards):
        for core1, marks1 in cards_left.items():
            srcs = vertices(core1)
            h1 = left[left_id]
            for right_id, cards_right in enumerate(right_cards):
                h2 = right[right_id]
                for core2, marks2 in cards_right.items():
                    for dsts in permutations(vertices(core2)):
                        if any(len(h1[src])+len(h2[dst]) != 6+len(h1[src] & set(srcs)) for src,dst in zip(srcs,dsts)):
                            continue
                        if any((srcs[ii] in h1[srcs[jj]]) != (dsts[ii] in h2[dsts[jj]]) for ii,jj in combinations(range(3),2)):
                            continue
                        brute.update((left_id, core1, *left_mark, right_id, core2, *right_mark, *dsts)
                                     for left_mark in marks1 for right_mark in marks2)
    assert brute and brute == set(indexed)
    print('all 395 planted maps live; direct, indexed, and independent factorial comparator agree on',len(brute),'bounded maps')


def sample():
    old = set(map(int,(SCOUT / 'held21-ids.tsv').read_text().split()))
    assert len(old) == 1024 and not any(row % 4096 == 0 for row in old)
    count = 1118436
    generator = Random(31010521)
    chosen = []
    for quartile in range(4):
        population = [row for row in range(quartile*count//4,(quartile+1)*count//4)
                      if row % 4096 and row not in old]
        chosen += sorted(generator.sample(population,2048))
    selected = set(chosen)
    rows, by_id = [], []
    old_graphs = set((SCOUT / 'held21.g6').read_text().splitlines() + (SCOUT / 'dispersed21.g6').read_text().splitlines())
    with SOURCE21.open() as catalog:
        for row,line in enumerate(catalog):
            if row in selected:
                assert line.strip() not in old_graphs
                by_id.append(row)
                rows.append(line.strip())
        assert row+1 == count
    assert len(set(rows)) == len(rows) == 8192 and by_id == chosen
    Path('pilot-21.g6').write_text('\n'.join(rows) + '\n')
    Path('pilot-ids.tsv').write_text('\n'.join(map(str,chosen)) + '\n')
    print('8192 distinct new hosts, 2048 per source-row quartile; neither scout sample reused')


def host_masks(adj):
    return [mask(neighbors) for neighbors in adj]


def source_check():
    def find_independent(graph, remaining, needed):
        while remaining.bit_count() >= needed:
            if needed == 1:
                return True
            bit = remaining & -remaining
            remaining ^= bit
            if find_independent(graph,remaining & ~graph[bit.bit_length()-1],needed-1):
                return True
        return False
    for path,count,order in [(SOURCE22,191,22),(Path('pilot-21.g6'),8192,21)]:
        lines = path.read_text().splitlines()
        assert len(set(lines)) == len(lines) == count
        for row,line in enumerate(lines):
            graph = host_masks(decode(line))
            assert len(graph) == order
            assert all(not (neighbors & graph[dst]) for neighbors in graph for dst in vertices(neighbors)), row
            assert max(neighbors.bit_count() for neighbors in graph) <= 6
            assert not find_independent(graph,(1 << order)-1,7), row
        print('direct triangle and independent-seven validation',order,count)


def merge(first, second, key, roots):
    lid, core1, lmark0, lmark1, lmark2, rid, core2, rmark0, rmark1, rmark2, *mapping = key
    shared1 = vertices(core1)
    names1 = [vertex for vertex in range(len(first)) if not core1 >> vertex & 1] + shared1
    names2 = [vertex for vertex in range(len(second)) if not core2 >> vertex & 1] + mapping
    width1, width2 = len(names1)-len(shared1), len(names2)-len(mapping)
    end = width1+width2+len(mapping)
    out = [set() for _ in range(end+2*roots)]
    def add(src, dst):
        out[src].add(dst)
        out[dst].add(src)
    for left in range(end, end+roots):
        for right in range(end+roots, end+2*roots):
            add(left,right)
    for graph, order, start, size, masks, group in [(first,names1,0,width1,[lmark0,lmark1,lmark2],end),
                                                   (second,names2,width1,width2,[rmark0,rmark1,rmark2],end+roots)]:
        names = dict(zip(order, list(range(start,start+size)) + list(range(width1+width2,end))))
        for src in order:
            for dst in vertices(graph[src]):
                add(names[src],names[dst])
        for role, chosen in enumerate(masks[:roots]):
            for vertex in vertices(chosen):
                add(names[vertex],group+role)
    return host_masks(out), width1, width2


def witness_check(lower, left, right, degree, cap, reason, witness):
    chosen = vertices(witness)
    if reason == 'cap':
        first, second = chosen
        return (lower[first] & lower[second]).bit_count() > cap
    if reason == 'fixed-undominated':
        first, second = chosen
        return left+right <= first and not (lower[first] & (1 << second)) and not (lower[first] & lower[second])
    if reason == 'upper-IS':
        return len(chosen) == degree+1 and all(not (lower[src] >> dst & 1) and
                   (not (src < left <= dst < left+right) or lower[src] & lower[dst])
                   for src,dst in combinations(chosen,2))
    return None


def audit():
    sys.path.append(str(SCOUT))
    from join import forced_allows, triples
    started = process_time()
    left = [decode(line) for line in SOURCE22.read_text().splitlines()]
    right = [decode(line) for line in Path('pilot-21.g6').read_text().splitlines()]
    sides = []
    decoded = [[host_masks(graph) for graph in side] for side in [left,right]]
    for index, tag in enumerate(('left','right')):
        groups = {}
        for line in Path(f'scout-{tag}-live.tsv').read_text().splitlines():
            code, host, core, multiplicity = map(int,line.split())
            recovered = triples(decoded[index][host],core,5,9)
            assert len(recovered) == multiplicity, (code,host,core,len(recovered),multiplicity)
            marks = [tuple(sorted(mark)) for mark in recovered]
            assert len(set(marks)) == len(marks)
            groups.setdefault(code,[]).append((host,core,marks))
        sides.append(groups)
    print('all matched scout mark multiplicities independently regenerated', round(process_time()-started,3),flush=True)
    actual = keys('pilot.tsv')
    exact = set()
    cardinal = Counter()
    verdicts = Counter()
    assert sides[0].keys() == sides[1].keys()
    for color in sides[0]:
        for lid, lcore, lmarks in sides[0][color]:
            for rid, rcore, rmarks in sides[1][color]:
                cardinal['card pairs'] += 1
                cardinal['marked pairs'] += len(lmarks)*len(rmarks)
                for mapping in transfers(left[lid],lcore,right[rid],rcore,9):
                    cardinal['card maps'] += 1
                    for lmark in lmarks:
                        for rmark in rmarks:
                            key = (lid,lcore,*lmark,rid,rcore,*rmark,*mapping)
                            assert key not in exact and key in actual, key
                            exact.add(key)
                            reason, witness = actual[key]
                            lower, ll, rr = merge(decoded[0][lid],decoded[1][rid],key,3)
                            check = witness_check(lower,ll,rr,9,5,reason,witness)
                            if check is not None:
                                assert check, key
                            else:
                                other = forced_allows(lower,ll,9,5,True,rr)
                                assert other != 'live', (key,reason)
                                verdicts[other] += 1
                            cardinal[reason] += 1
    assert len(exact) == 70229 == len(actual)
    print('all exact keys and all obstructions agree',cardinal,'fallback',verdicts,round(process_time()-started,3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['controls', 'control-check', 'sample', 'audit', 'source-check'])
    options = parser.parse_args()
    {'controls': controls, 'control-check': control_check, 'sample': sample,
     'audit': audit, 'source-check': source_check}[options.mode]()
