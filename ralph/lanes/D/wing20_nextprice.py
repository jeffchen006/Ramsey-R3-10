"""One-shore arbitrary-size independent-set threshold. Synthetic pricing only."""
from itertools import combinations, combinations_with_replacement
from time import process_time

from wing20 import Shore, site_types


def limits(order, rows, types, width):
    contained = [sum(1 << index for index, site in enumerate(types) if not site & ~union)
                 for union in range(1 << order)]
    hits = [sum(1 << index for index, site in enumerate(types) if site & row) for row in rows]
    later = [sum(1 << dst for dst in range(src+1,len(rows)) if rows[dst] & row) for src,row in enumerate(rows)]
    capacity = {}
    universe = (1 << order)-1
    def visit(selection, occupied, eligible, count):
        extra = universe ^ occupied
        while True:
            union = occupied | extra
            bound = union.bit_count()+1-count
            if bound < width:
                key = eligible & contained[union]
                if bound < capacity.get(key,width):
                    capacity[key] = bound
            if not extra:
                break
            extra = (extra-1) & ~occupied & universe
        while selection:
            bit = selection & -selection
            selection ^= bit
            pos = bit.bit_length()-1
            visit(selection & later[pos], occupied | rows[pos], eligible & hits[pos], count+1)
    visit((1 << len(rows))-1,0,(1 << len(types))-1,0)
    return capacity


class Threshold:
    def __init__(self, profiles, types):
        self.width = len(profiles[0])
        self.full = (1 << len(profiles))-1
        self.presence = [[sum(1 << index for index, sites in enumerate(profiles) if sites.count(pos) >= level)
                          for level in (1,2)] for pos in range(len(types))]
        assert all(max(map(sites.count,sites)) <= 2 and len(sites)==self.width for sites in profiles)

    def allowed(self, capacity):
        reject = 0
        for key,bound in capacity.items():
            if bound < 0:
                return 0
            levels = [0]*self.width.bit_length()
            while key:
                bit = key & -key
                key ^= bit
                for carry in self.presence[bit.bit_length()-1]:
                    for shift in range(len(levels)):
                        if not carry:
                            break
                        levels[shift], carry = levels[shift] ^ carry, levels[shift] & carry
                    assert not carry
            excess = 0
            for shift, level in enumerate(levels):
                excess = excess & level if bound >> shift & 1 else excess | level
            reject |= excess
        return self.full ^ reject


def literal(order, rows, wing):
    poles = list(range(order))
    sites = list(rows)+list(wing)
    def edge(left,right):
        if right < order:
            return False
        if left < order:
            return bool(1 << left & sites[right-order])
        if left-order >= len(rows):
            return False
        return not sites[left-order] & sites[right-order]
    return not any(all(not edge(left,right) for left,right in combinations(chosen,2))
                   for chosen in combinations(poles+list(range(order,order+len(sites))),order+2))


def controls():
    order = 3
    edges = list(combinations(range(order),2))
    types = site_types(edges,order)
    shores = Shore(edges,[2,2,1],1).physical
    checker = Threshold(shores, types)
    trials = veto = 0
    for size in range(5):
        for rows in combinations_with_replacement([3,5,6,7],size):
            mask = checker.allowed(limits(order,rows,types,4))
            for index,sites in enumerate(shores):
                expected = literal(order,rows,[types[pos] for pos in sites])
                assert expected == ((mask >> index)&1)
                trials += 1
                veto += not expected
    assert not literal(3,[3],[1,2,3,4]) and literal(3,[3],[1,3,4])
    print('future arbitrary-size test: literal toy profiles / excluded',trials,veto,'; strict three-site witness and deletion control')


def price():
    start = process_time()
    edges = list(combinations(range(7),2))
    types = site_types(edges,7)
    tables = [Threshold(Shore(edges,degree,width).physical,types) for degree,width in [([1]+[2]*6,5),([2]*7,6)]]
    setup = process_time()-start
    for name,rows in [('stress-star',[3,5,9,17,33,65]*2+[3,7]),
                      ('sparse',[7,9,10,12,17,18,20,33,34,36,65,66,68,24])]:
        start = process_time()
        bounds = limits(7,rows,types,8)
        passed = [table.allowed(bounds).bit_count() for table in tables]
        print('synthetic', name, 'constraints',len(bounds),'margins',passed,
              'setup + 159 host filters CPU-s',round(setup+159*(process_time()-start),2))


if __name__=='__main__':
    controls()
    price()
