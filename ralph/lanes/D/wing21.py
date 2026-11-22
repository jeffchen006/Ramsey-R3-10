"""D-049: count fixed ordered assignments with both one-shore tests."""
import json
import sys
from collections import Counter, defaultdict
from csv import DictReader, DictWriter
from itertools import combinations
from pathlib import Path

from wing19 import groups
from wing20 import Join
from wing20_nextprice import Threshold, controls as small_profiles, limits, literal


def scalar(order, rows, sites):
    types = list(range(1 << order))
    bounds = limits(order, rows, types, len(sites))
    return all(sum((key >> site) & 1 for site in sites) <= bound for key, bound in bounds.items())


def controls():
    import networkx as nx
    small_profiles()
    for rows, sites, expected in [([], [1,1,1], False), ([], [1,1], True),
                                   ([3,3], [5,5,6], False), ([3], [5,5,6], True),
                                   ([3,3], [5,6], True), ([3], [1,2,3,4], False),
                                   ([3], [1,3,4], True)]:
        assert scalar(3, rows, sites) == literal(3, rows, sites) == expected
    print('empty F; nonempty F and strict superset U; repeated row/site; deletion controls PASS')
    regular = hosts = plants = empty_sites = 0
    path = Path(__file__).resolve().parents[3] / 'gluing/val/r3_7_22.g6'
    catalogue = path.read_bytes().splitlines()
    for line in catalogue:
        graph = nx.from_graph6_bytes(line)
        stars = [set(graph[vertex]) for vertex in graph]
        if not all(len(star) == 6 for star in stars):
            continue
        regular += 1
        if any(len(left & right) > 3 for left, right in combinations(stars, 2)):
            continue
        hosts += 1
        for left, right in combinations(graph, 2):
            middle = stars[left] & stars[right]
            if right in stars[left] or len(middle) != 1:
                continue
            poles = sorted(stars[next(iter(middle))]-{left, right})
            untouched = set(graph)-stars[left]-stars[right]-set(poles)-{left, right}
            def mask(vertex):
                return sum(1 << index for index, pole in enumerate(poles) if pole in stars[vertex])
            rows = list(map(mask, untouched))
            for tip in (left, right):
                sites = list(map(mask, stars[tip]-middle))
                assert len(poles) == 4 and len(sites) == len(rows) == 5
                assert scalar(4, rows, sites) and literal(4, rows, sites)
                empty_sites += sites.count(0)
                plants += 1
    assert (len(catalogue), regular, hosts, plants) == (191, 10, 3, 250)
    print('C22 catalogue/regular/cap-three/physical shores',len(catalogue),regular,hosts,plants,
          '; all retained by literal and compiled inequality; zero-mask shore occurrences',empty_sites)


class StrongJoin(Join):
    def __init__(self, degrees, short_pairs, long_pairs):
        super().__init__(degrees, short_pairs, long_pairs)
        self.tables = [Threshold(shore.physical, self.types) for shore in (self.short, self.long)]

    def evaluate(self, triple, word):
        masks = self.types[self.order:]
        rows = [triple]+[mask for mask, copies in zip(masks, word) for _ in range(copies)]
        assert self.tables[0].width == self.tables[1].width
        bounds = limits(self.order, rows, self.types, self.tables[0].width)
        short, long = [table.allowed(bounds) for table in self.tables]
        columns = [table[num+int(mask & triple == mask)] for table, num, mask in zip(self.index, word, masks)]
        fixes = {}
        for perm, move in groups(self.edges, triple, word):
            if move != tuple(range(len(move))):
                images = tuple(map(int, perm))+tuple(self.order+dst for dst in move)
                image_bits = [1 << dst for dst in images]
                for key, bound in bounds.items():
                    assert bounds[sum(bit for index,bit in enumerate(image_bits) if key >> index & 1)] == bound
            possible = short & self.short.fixed(move)
            fixedlong = long & self.long.fixed(move)
            total = 0
            while possible and fixedlong:
                selected = possible & -possible
                possible ^= selected
                allowed = fixedlong
                for digit, column in zip(self.short.words[selected.bit_length()-1], columns):
                    allowed &= column[digit]
                    if not allowed:
                        break
                total += allowed.bit_count()
            fixes[perm] = total
        return fixes, short.bit_count(), long.bit_count()


def target(roster, baseline, dest):
    join = StrongJoin([1]+[2]*6, 5, 6)
    supports = roster.read_text().splitlines()
    totals = defaultdict(Counter)
    zero = defaultdict(list)
    fields = 'row triple word group short long identity delta_identity orbits delta_orbits result fixed delta_fixed'.split()
    with baseline.open() as source, dest.open('x') as output:
        writer = DictWriter(output, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        skipped = []
        for old in DictReader(source, delimiter='\t'):
            line = int(old['row'])
            if not int(old['identity']):
                skipped.append(line)
                continue
            host = json.loads(supports[line-1])
            triple, word = int(old['triple']), old['word']
            assert (host['status'], host['triple'], host['word']) == ('pass', triple, word)
            fixed, short, long = join.evaluate(triple, bytes(map(int, word)))
            oldfixed = {key:int(value) for key, value in (field.split(':') for field in old['fixed'].split(','))}
            assert oldfixed.keys() == fixed.keys() and len(fixed) == int(old['group']) == host['aut']
            assert short <= int(old['short']) and long <= int(old['long'])
            delta = {key:oldfixed[key]-value for key,value in fixed.items()}
            group = len(fixed)
            identity, change = fixed['0123456'], delta['0123456']
            orbits, rem = divmod(sum(fixed.values()), group)
            lost, extra = divmod(sum(delta.values()), group)
            assert not rem and not extra and min(delta.values()) >= 0
            assert identity+change == int(old['identity']) and orbits+lost == int(old['orbits'])
            cause = 'positive' if identity else ('both' if not short and not long else 'short' if not short else 'long' if not long else 'join')
            if not identity:
                zero[cause].append(line)
            def coded(mapping):
                return ','.join(f'{key}:{value}' for key,value in mapping.items())
            writer.writerow(dict(row=line,triple=triple,word=word,group=group,short=short,long=long,
                                 identity=identity,delta_identity=change,orbits=orbits,delta_orbits=lost,
                                 result=cause,fixed=coded(fixed),delta_fixed=coded(delta)))
            totals[triple].update(dict(hosts=1, actions=group, identity=identity, delta_identity=change,
                                       orbits=orbits, delta_orbits=lost, nonidentity=sum(fixed.values())-identity,
                                       delta_nonidentity=sum(delta.values())-change, strict=int(change>0)))
            totals[triple][cause] += 1
    total = totals[7]+totals[14]
    assert skipped == [255,345,350]
    assert (total['hosts'],total['actions'],total['identity']+total['delta_identity'],
            total['orbits']+total['delta_orbits']) == (159,264,2296202,1334977)
    for triple in (7,14):
        print('triple',triple,dict(totals[triple]))
    print('total',dict(total))
    for cause in ('both','short','long','join'):
        print('new zero',cause,zero[cause])


if __name__ == '__main__':
    if sys.argv[1:] == ['controls']:
        controls()
    else:
        target(*map(Path,sys.argv[1:]))
