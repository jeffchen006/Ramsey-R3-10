#!/usr/bin/env python3
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import accumulate, combinations
from pathlib import Path

from deletion_cards19 import canonical, induced, load_catalogue, pin_deleted
from one_neutral_control import encode, require


@dataclass(frozen=True)
class Frame:
    ident: int
    host: int
    neutral: int
    masks: tuple
    support: tuple
    triple: int

    @property
    def axes(self):
        return tuple(site for site in range(len(self.support)) if site != self.neutral)

    @property
    def groups(self):
        return tuple(tuple(site for site, support in enumerate(self.support) if support == 1 << slot)
                     for slot in range(4))

    def raw(self):
        return self.host, self.neutral, *self.masks


def ints(path):
    return [tuple(map(int, line.split())) for line in path.read_text().splitlines()]


class Side:
    def __init__(self, root, binary, order, margin):
        self.order, self.margin, self.binary = order, margin, binary
        self.catalogue = root / f'gluing/val/r3_6_{order}.g6'
        self.graphs = load_catalogue(self.catalogue, order, 2576 if order == 16 else 7)
        self.weights = defaultdict(Counter)
        for host, degsum, nd, shape, triple, weight in ints(root / f'scratch/A/r16/count{order}.tsv'):
            if weight:
                require(triple in (0, 1) and (degsum, nd, shape, triple) not in self.weights[host], 'weight row duplicate')
                self.weights[host][degsum, nd, shape, triple] = weight
        self.offsets = tuple(accumulate([0] + [self.weights[host].total() for host in range(len(self.graphs))]))
        require(self.offsets[-1] == {16: 2817701, 17: 59521}[order], f'whole stream length: {self.offsets[-1]}')

    def marked_count(self, host):
        return sum(weight for (degsum, nd, _, triple), weight in self.weights[host].items()
                   if (degsum, nd) == self.margin and triple == 1)

    def marked(self, host):
        graph = self.graphs[host]
        stream = subprocess.check_output([self.binary, 'frames', self.catalogue, str(self.order),
                                          str(len(self.graphs)), '4', '9', '5', '5', str(host), str(host+1)],
                                         text=True).splitlines()
        require(len(stream) == self.offsets[host+1]-self.offsets[host], 'frozen host ordinal boundary mismatch')
        results = []
        for ident, line in enumerate(stream, self.offsets[host]):
            bound_host, neutral, *masks, degsum, nd = map(int, line.split())
            if (degsum, nd) != self.margin:
                continue
            require(bound_host == host and len(masks) == 4 and sorted(set(masks)) == masks, 'physical stream fields')
            require(nd == len(graph[neutral]) and degsum == sum(map(len, graph))-nd, 'literal margin mismatch')
            support = tuple(sum(1 << slot for slot, mask in enumerate(masks) if (mask >> site) & 1)
                            for site in range(self.order))
            require(support.count(0) == 1 and support[neutral] == 0 and max(map(int.bit_count, support)) <= 3,
                    'old exterior support binding')
            require(all(mask.bit_count() == 5 for mask in masks), 'old row size')
            for mask in masks:
                sites = [site for site in range(self.order) if mask >> site & 1]
                require(all(second not in graph[first] for first, second in combinations(sites, 2)), 'old row not independent')
            triples = [site for site, pattern in enumerate(support) if pattern.bit_count() == 3]
            if triples:
                require(len(triples) == 1, 'nonunique triple site on this stream')
                results.append(Frame(ident, host, neutral, tuple(masks), support, triples[0]))
        require(len(results) == self.marked_count(host), 'old marked frame subtotal mismatch')
        return results


def row_text(row):
    return ' '.join(map(str, row)) + '\n'


def literal_flags(oracle, left, right, candidate, right_frames):
    cases = [(candidate.ident, other.ident, *candidate.raw(), *other.raw()) for other in right_frames]
    Path('oracle.in').write_text(''.join(map(row_text, cases)))
    text = subprocess.check_output([oracle, 'pilot', left.catalogue, right.catalogue, 'oracle.in'], text=True)
    flags = [tuple(line.split()) for line in text.splitlines()]
    require(len(flags) == len(cases), 'literal flags cardinality')
    for row, flag in zip(cases, flags):
        require(tuple(map(int, flag[:2])) == row[:2] and len(flag) == 4 and
                all(len(bits) == 4 and not set(bits) - {'0', '1'} for bits in flag[2:]), 'literal flags bind')
    return cases, flags


def live(flag):
    return tuple(flag[2:]) == ('1111', '1111')


def mark_header(left, right, frame, other, flag):
    graph = left.graphs[frame.host]
    other_graph = right.graphs[other.host]
    root = frame.triple
    require(frame.support[root].bit_count() == 3 and len(graph[root]) == 3, 'invalid chosen fifth pole')
    singleton, core = pin_deleted(graph, root)
    key, order = canonical(induced(graph, core))
    require(len(core) == 12 and set(core) == set(range(16)) - ({root} | graph[root]), 'core physical binding')
    require(frame.neutral in core or frame.neutral in singleton, 'old neutral unbound')
    return {'id': [frame.ident, other.ident], 'old_flags': flag[2:],
            'order16': frame.raw(), 'order17': other.raw(), 'axes': [frame.axes, other.axes],
            'x16': root, 'x17': other.triple, 'x_old16_support': frame.support[root],
            'x_required_private_degree17': 9 - 3 - len(singleton),
            'x_adjacent_neutral': frame.neutral in singleton,
            'core16': core, 'core_graph6': encode(graph, core), 'canonical_core': key,
            'canonical_to_physical16': tuple(core[pos] for pos in order),
            'x_old16_singletons': singleton, 'old17_singletons': other.groups,
            'full17_support': other.support, 'right_neutral_contacts': sorted(other_graph[other.neutral])}


def main():
    mode, root, binary, oracle = sys.argv[1:]
    require(mode in ('sample', 'select'), 'unknown binder mode')
    root, binary, oracle = [Path(path).resolve() for path in (root, binary, oracle)]
    left = Side(root, binary, 16, (66, 4))
    right = Side(root, binary, 17, (75, 5))
    right_frames = [frame for host in range(len(right.graphs)) if right.marked_count(host) for frame in right.marked(host)]
    require(len(right_frames) == len({item.ident for item in right_frames}) == 116, 'right denominator')
    require([item.ident for item in right_frames] == sorted(item.ident for item in right_frames), 'right order')
    old_rows = ints(root / 'scratch/C/r16/bound.cases.tsv')
    old = {row[:2] for row in old_rows}
    require(len(old_rows) == len(old) == 544 and all(len(row) == 14 for row in old_rows), 'frozen old pilot roster')
    eligible = [host for host, graph in enumerate(left.graphs)
                if left.marked_count(host) and any(len(row) == 3 for row in graph)]
    print('upper left marked', sum(left.marked_count(host) for host in eligible), 'right denominator', len(right_frames),
          'eligible host count', len(eligible), 'old IDs', len(old), flush=True)
    examined = 0
    with Path('selection.tsv').open('x') as selection:
        print('frame16\tx16\thost16\told_pilot_pair_count\t00\t10\t01\t11', file=selection)
        for host in eligible:
            for frame in left.marked(host):
                if len(left.graphs[host][frame.triple]) != 3:
                    continue
                overlap = sum((frame.ident, other.ident) in old for other in right_frames)
                if overlap:
                    print(frame.ident, frame.triple, host, overlap, '-', '-', '-', '-', sep='\t', file=selection)
                    continue
                cases, flags = literal_flags(oracle, left, right, frame, right_frames)
                subtotal = Counter((fwd == '1111', rev == '1111') for _, _, fwd, rev in flags)
                four = tuple(subtotal[first, second] for first, second in ((0, 0), (1, 0), (0, 1), (1, 1)))
                print(frame.ident, frame.triple, host, 0, *four, sep='\t', file=selection, flush=True)
                examined += 1
                if mode == 'sample' and examined == 3:
                    print('priced first', examined, 'candidates at', 116*examined, 'literal old-margin flags')
                    return
                if mode != 'select' or not four[-1]:
                    continue
                require(not old & {row[:2] for row in cases}, 'old pilot overlap in delivery')
                with (Path('heldout.cases.tsv').open('x') as raw, Path('heldout.flags.tsv').open('x') as bits,
                      Path('heldout.positive.cases.tsv').open('x') as positive, Path('heldout.marked.jsonl').open('x') as marks):
                    for case, flag, other in zip(cases, flags, right_frames, strict=True):
                        raw.write(row_text(case))
                        print(*flag, sep='\t', file=bits)
                        if live(flag):
                            positive.write(row_text(case))
                        print(json.dumps(mark_header(left, right, frame, other, flag), sort_keys=True, separators=(',', ':')), file=marks)
                print('selected left', frame.ident, 'x', frame.triple, 'host', host, 'neutral', frame.neutral,
                      'old four', four, 'literal candidate bins examined', examined, 'old overlaps', overlap)
                return
    raise ValueError('preregistered rule found no eligible positive held-out bin')


if __name__ == '__main__':
    main()
