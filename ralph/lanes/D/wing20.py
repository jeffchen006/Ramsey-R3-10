"""D-047 marginal index and fixed-point census; no target pair is emitted."""
import json
import sys
from collections import Counter
from csv import DictReader, DictWriter
from itertools import combinations, combinations_with_replacement
from pathlib import Path

from triple18_price import shore_words
from wing19 import groups, index_long
from wing19_filterprice import small, tight_types


def site_types(edges, order):
    return [1 << pole for pole in range(order)] + [(1 << first) | (1 << second) for first, second in edges]


class Shore:
    def __init__(self, edges, degrees, width):
        self.words = shore_words(edges, degrees, width)
        self.full = (1 << len(self.words))-1
        self.physical = []
        self.by_pair = Counter()
        self.by_move = {}
        for index, word in enumerate(self.words):
            room = list(degrees)
            sites = []
            for pos, ((first, second), num) in enumerate(zip(edges, word)):
                room[first] -= num
                room[second] -= num
                sites.extend([len(room)+pos]*num)
            sites += [pos for pos, copies in enumerate(room) for _ in range(copies)]
            assert min(room) >= 0 and len(sites) == sum(degrees)-width
            self.physical.append(sites)
            for pair in set(combinations(sorted(sites), 2)):
                self.by_pair[pair] |= 1 << index

    def admitted(self, selectors):
        reject = 0
        for pair in selectors:
            reject |= self.by_pair[pair]
        return self.full ^ reject

    def fixed(self, move):
        if move not in self.by_move:
            changes = [(pos, dst) for pos, dst in enumerate(move) if pos != dst]
            self.by_move[move] = sum(1 << index for index, word in enumerate(self.words)
                                     if all(word[pos] == word[dst] for pos, dst in changes))
        return self.by_move[move]


class Join:
    def __init__(self, degrees, short_width, long_width):
        self.order = len(degrees)
        self.edges = list(combinations(range(self.order), 2))
        self.types = site_types(self.edges, self.order)
        self.short = Shore(self.edges, degrees, short_width)
        self.long = Shore(self.edges, [2]*self.order, long_width)
        self.index = index_long(self.long.words)

    def host(self, triple, word):
        masks = self.types[self.order:]
        rows = [triple]+[mask for mask, copies in zip(masks, word) for _ in range(copies)]
        selectors = tight_types(self.order, rows, self.types)
        short = self.short.admitted(selectors)
        long = self.long.admitted(selectors)
        columns = [table[num+int(mask & triple == mask)] for table, num, mask in zip(self.index, word, masks)]
        values = {}
        for perm, move in groups(self.edges, triple, word):
            action = tuple(map(int, perm)) + tuple(self.order+dst for dst in move)
            assert {tuple(sorted((action[first], action[second]))) for first, second in selectors} == selectors
            possible = short & self.short.fixed(move)
            fixedlong = long & self.long.fixed(move)
            total = 0
            while possible and fixedlong:
                bit = possible & -possible
                possible ^= bit
                allowed = fixedlong
                for digit, column in zip(self.short.words[bit.bit_length()-1], columns):
                    allowed &= column[digit]
                    if not allowed:
                        break
                total += allowed.bit_count()
            values[perm] = total
        return values, len(selectors), short.bit_count(), long.bit_count()


def target(roster, previous, dest):
    join = Join([1]+[2]*6, 5, 6)
    assert (len(join.short.words), len(join.long.words)) == (4062, 6202)
    totals = {mask: Counter() for mask in (7, 14)}
    with previous.open() as oldfile, dest.open('x') as output:
        oldrows = iter(DictReader(oldfile, delimiter='\t'))
        fields = 'row triple word group forbidden short long identity delta_identity orbits delta_orbits fixed delta_fixed'.split()
        writer = DictWriter(output, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for lineno, line in enumerate(roster.read_text().splitlines(), 1):
            row = json.loads(line)
            if row['status'] != 'pass':
                continue
            old = next(oldrows)
            triple = row['triple']
            assert (lineno, triple, row['word']) == (int(old['row']), int(old['triple']), old['word'])
            fixes, forbidden, short, long = join.host(triple, bytes(map(int, row['word'])))
            oldfixed = dict(item.split(':') for item in old['fixed_by_permutation'].split(','))
            assert fixes.keys() == oldfixed.keys() and len(fixes) == int(old['group']) == row['aut']
            diffs = {perm:int(oldfixed[perm])-new for perm, new in fixes.items()}
            assert min(diffs.values()) >= 0
            def coded(mapping):
                return ','.join(f'{perm}:{value}' for perm, value in mapping.items())
            ident = fixes['0123456']
            del_id = diffs['0123456']
            orbits, rem = divmod(sum(fixes.values()), len(fixes))
            del_orb = int(old['orbits'])-orbits
            assert rem == 0 and del_orb*len(fixes) == sum(diffs.values())
            writer.writerow(dict(row=lineno, triple=triple, word=row['word'], group=len(fixes), forbidden=forbidden,
                                 short=short, long=long, identity=ident, delta_identity=del_id, orbits=orbits,
                                 delta_orbits=del_orb, fixed=coded(fixes), delta_fixed=coded(diffs)))
            totals[triple].update(dict(hosts=1, actions=len(fixes), zero=int(ident == 0), identity=ident,
                                       delta_identity=del_id, orbits=orbits, delta_orbits=del_orb,
                                       nonidentity=sum(fixes.values())-ident, delta_nonidentity=sum(diffs.values())-del_id))
        assert next(oldrows, None) is None
    total = totals[7]+totals[14]
    assert (total['hosts'], total['actions'], total['identity']+total['delta_identity'], total['orbits']+total['delta_orbits']) == (162, 267, 4817781, 3128474)
    for mask in (7, 14):
        print('triple', mask, dict(totals[mask]))
    print('total', dict(total))


def literal(order, rows, types):
    """Build the allowed-edge graph, then test both shore sites + the opposite tip."""
    background = list(range(order+len(rows)))
    def edge(left, right):
        if right < order:
            return False
        if left < order:
            return bool(rows[right-order] & (1 << left))
        return not (rows[left-order] & rows[right-order])
    def independent(vertices):
        return not any(edge(left, right) for left, right in combinations(vertices, 2))
    if any(independent(picks) for picks in combinations(background, order+1)):
        return None
    result = set()
    for rest in combinations(background, order):
        if not independent(rest):
            continue
        compatible = [pos for pos, mask in enumerate(types) if all(
            not (mask & (1 << vertex)) if vertex < order else (mask & rows[vertex-order]) for vertex in rest)]
        result.update(combinations_with_replacement(compatible, 2))
    return result


def controls():
    order = 3
    types = site_types(list(combinations(range(order), 2)), order)
    margins = denied = witnesses = 0
    for size in range(6):
        for rows in combinations_with_replacement([3, 5, 6, 7], size):
            expected = literal(order, rows, types)
            if expected is None:
                denied += 1
                continue
            assert tight_types(order, rows, types) == expected
            margins += 1
            witnesses += len(expected)
    repeat = literal(3, [3, 3], types)
    def violated(sites):
        return any(pair in repeat for pair in combinations(sorted(sites), 2))
    assert violated([0, 0]) and not violated([0]) and violated([0, 1]) and not violated([0, 2])
    print('generic literal margins / pre-Hall rejected / type-pair comparisons / positives', margins, denied, margins*21, witnesses)
    toy = Join([1, 2, 2, 2], 1, 2)
    for triple, ordinary in [(7, [9,9,6]), (14, [3,5,9])]:
        word = bytes(ordinary.count(mask) for mask in toy.types[4:])
        values, _, _, _ = toy.host(triple, word)
        forbidden = literal(4, [triple]+ordinary, toy.types)
        assert forbidden is not None
        def keep(sites):
            return all(pair not in forbidden for pair in combinations(sorted(sites), 2))
        for perm, move in groups(toy.edges, triple, word):
            def physical_words(shore):
                return [profile for profile, sites in zip(shore.words, shore.physical) if keep(sites)
                        and tuple(profile[dst] for dst in move) == tuple(profile)]
            expected = sum(all(1 <= left+right+base+int(mask & triple == mask) <= 2
                               for left, right, base, mask in zip(short, long, word, toy.types[4:]))
                           for short in physical_words(toy.short) for long in physical_words(toy.long))
            assert values[perm] == expected
        print('toy', triple, values)
    small()


if __name__ == '__main__':
    if sys.argv[1:] == ['controls']:
        controls()
    else:
        target(*map(Path, sys.argv[1:]))
