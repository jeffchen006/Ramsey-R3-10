"""Independent census: physical shore profiles, complementary pole sets, reverse join."""
from collections import Counter
from csv import DictReader
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
from time import process_time
import json
import sys


class Audit:
    def __init__(self, margins, short_pairs, long_pairs):
        self.order = len(margins)
        self.poles = tuple(range(self.order))
        self.pairs = tuple((1 << left) | (1 << right) for left, right in combinations(self.poles, 2))
        self.types = tuple(1 << pole for pole in self.poles) + self.pairs
        self.shorts = self.profiles(margins, short_pairs)
        self.longs = self.profiles([2]*self.order, long_pairs)
        self.all_short = (1 << len(self.shorts))-1
        self.columns = []
        for pair in self.pairs:
            bit = 1 << pair
            positive, double = [sum(1 << index for index, profile in enumerate(self.shorts) if profile[level] & bit)
                                for level in (0, 1)]
            self.columns.append((positive, self.all_short ^ double, self.all_short ^ positive, 0, 0))
        self.fixed_cache = {}

    def profiles(self, margins, pairs):
        output = []
        def extend(pole, counts, pairs, present, repeated):
            if pole == self.order:
                if not pairs:
                    output.append((present, repeated))
                return
            for number in range(min(counts[pole], pairs)+1):
                for partners in combinations_with_replacement(range(pole+1, self.order), number):
                    remaining = list(counts)
                    seen, twice = present, repeated
                    for dst in partners:
                        remaining[dst] -= 1
                        bit = 1 << ((1 << pole) | (1 << dst))
                        twice |= bit & seen
                        seen |= bit
                    for _ in range(counts[pole]-number):
                        bit = 1 << (1 << pole)
                        twice |= bit & seen
                        seen |= bit
                    if min(remaining[pole+1:], default=0) >= 0:
                        extend(pole+1, remaining, pairs-number, seen, twice)
        extend(0, list(margins), pairs, 0, 0)
        assert len(set(output)) == len(output)
        return output

    def families(self, rows):
        found = set()
        for selected_poles in range(1 << self.order):
            available = [row for row in rows if not row & selected_poles]
            for sites in combinations(available, self.order-selected_poles.bit_count()):
                if any(not left & right for left, right in combinations(sites, 2)):
                    continue
                compatible = sum(1 << item for item in self.types if not item & selected_poles and all(item & row for row in sites))
                if compatible:
                    found.add(compatible)
        return {family for family in found if not any(family != other and family & other == family for other in found)}

    def moved(self, mask, perm):
        return sum(1 << perm[pole] for pole in self.poles if mask >> pole & 1)

    def stabilized(self, perm):
        if perm not in self.fixed_cache:
            cycles = []
            remaining = set(self.types)
            while remaining:
                start = min(remaining)
                cycle = 0
                item = start
                while item in remaining:
                    remaining.remove(item)
                    cycle |= 1 << item
                    item = self.moved(item, perm)
                assert item == start
                if cycle.bit_count() > 1:
                    cycles.append(cycle)
            def fixed(profile):
                return all(level & cycle in (0, cycle) for cycle in cycles for level in profile)
            self.fixed_cache[perm] = (sum(1 << pos for pos, word in enumerate(self.shorts) if fixed(word)),
                                      bytearray(fixed(word) for word in self.longs))
        return self.fixed_cache[perm]

    def evaluate(self, rows):
        families = self.families(rows)
        def passes(profile):
            seen, twice = profile
            return all(not twice & family and (seen & family).bit_count() <= 1 for family in families)
        eligible = sum(1 << pos for pos, word in enumerate(self.shorts) if passes(word))
        ok_long = [passes(word) for word in self.longs]
        base = [sum(pair & row == pair for row in rows) for pair in self.pairs]
        assert max(base) <= 2
        restrictions = list(sorted(zip(base, self.pairs, self.columns), key=lambda item:-item[0]))
        old = {}
        new = {}
        actions = []
        permutations_of_rows = sorted(rows)
        for tail in permutations(self.poles[1:]):
            perm = (0, *tail)
            if sorted(self.moved(row, perm) for row in rows) != permutations_of_rows:
                continue
            key = ''.join(map(str, perm))
            short_fix, long_fix = self.stabilized(perm)
            new_short = short_fix & eligible
            actions.append((key, short_fix, new_short, long_fix))
            old[key] = new[key] = 0
        for index, (seen, twice) in enumerate(self.longs):
            allowed = self.all_short
            for count, pair, column in restrictions:
                allowed &= column[count+((seen >> pair)&1)+((twice >> pair)&1)]
                if not allowed:
                    break
            if not allowed:
                continue
            for key, short_fix, new_short, long_fix in actions:
                if long_fix[index]:
                    old[key] += (short_fix & allowed).bit_count()
                    if ok_long[index]:
                        new[key] += (new_short & allowed).bit_count()
        forbidden = sum(any(family >> left & family >> right & 1 for family in families)
                        for left, right in combinations_with_replacement(self.types, 2))
        return old, new, forbidden, eligible.bit_count(), sum(ok_long)


def toy():
    audit = Audit([1, 2, 2, 2], 1, 2)
    for rows, old, new in [([7, 9, 9, 6], [10, 0], [0, 0]),
                            ([14, 3, 5, 9], [60, 4, 4, 0, 0, 4], [48, 2, 2, 0, 0, 2])]:
        before, after, *margins = audit.evaluate(rows)
        assert list(before.values()) == old and list(after.values()) == new
        print('reverse toy old/new', old, new, 'margins', margins)


def price():
    start = process_time()
    audit = Audit([1]+[2]*6, 5, 6)
    elapsed = process_time()-start
    assert (len(audit.shorts), len(audit.longs)) == (4062, 6202)
    start = process_time()
    result = audit.evaluate([7, 9, 10, 12, 17, 18, 20, 33, 34, 36, 65, 66, 68, 24])
    projected = elapsed+162*(process_time()-start)
    print('synthetic (not roster) action count', len(result[0]), 'one-time + 162 hosts CPU-s', round(projected, 2))
    assert projected < 60


def audit_target(roster, previous, receipt):
    audit = Audit([1]+[2]*6, 5, 6)
    assert (len(audit.shorts), len(audit.longs)) == (4062, 6202)
    with previous.open() as oldfile, receipt.open() as newfile:
        oldrows = iter(DictReader(oldfile, delimiter='\t'))
        newrows = iter(DictReader(newfile, delimiter='\t'))
        total = Counter()
        removed = []
        for line, txt in enumerate(roster.read_text().splitlines(), 1):
            support = json.loads(txt)
            if support['status'] != 'pass':
                continue
            old, new = next(oldrows), next(newrows)
            masks = [support['triple']]+[pair for num, pair in zip(support['word'], audit.pairs) for _ in range(int(num))]
            assert len(masks) == 14
            for table in [old, new]:
                assert (int(table['row']), int(table['triple']), table['word']) == (line, support['triple'], support['word'])
            before, after, *margins = audit.evaluate(masks)
            assert margins == [int(new[field]) for field in ('forbidden', 'short', 'long')]
            def decode(text):
                fields = text.split(',')
                answer = {key:int(value) for key, value in (field.split(':') for field in fields)}
                assert len(answer) == len(fields)
                return answer
            delta = {perm:value-after[perm] for perm, value in before.items()}
            assert before == decode(old['fixed_by_permutation']) and after == decode(new['fixed']) and delta == decode(new['delta_fixed'])
            group = len(before)
            assert group == int(new['group']) == int(old['group']) == support['aut']
            for values, fields in [(after, ('identity', 'orbits')), (delta, ('delta_identity', 'delta_orbits'))]:
                assert min(values.values()) >= 0
                assert values['0123456'] == int(new[fields[0]]) and sum(values.values()) == group*int(new[fields[1]])
            total.update(dict(hosts=1, actions=group, identity=after['0123456'], orbits=sum(after.values())//group))
            if not after['0123456']:
                removed.append((line, support['word'], before['0123456']))
        assert next(oldrows, None) is next(newrows, None) is None
    assert (total['hosts'],total['actions']) == (162,267)
    print('independent old, new and delta: all fixed counts and both margins agree', dict(total))
    print('zero supports (roster line, ordinary word, old ident)', removed)


if __name__ == '__main__':
    if sys.argv[1:] == ['toy']:
        toy()
    elif sys.argv[1:] == ['price']:
        price()
    else:
        audit_target(*map(Path, sys.argv[1:]))
