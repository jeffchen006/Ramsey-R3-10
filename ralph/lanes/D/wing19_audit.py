"""Independent counting by forced short rows and a subset coefficient on edge orbits."""
from collections import Counter
from csv import DictReader
from itertools import combinations, combinations_with_replacement, permutations
from math import comb, factorial
from pathlib import Path
from time import process_time
import json
import sys


class Margins:
    def __init__(self, degree, short_width, long_width):
        self.degree = degree
        self.order = len(degree)
        self.width = short_width
        self.edges = tuple(combinations(range(self.order),2))
        self.universe = (1 << len(self.edges))-1
        self.stars = [sum(1 << index for index, edge in enumerate(self.edges) if pole in edge)
                      for pole in range(self.order)]
        self.longs = []
        for slots in combinations_with_replacement(range(len(self.edges)),long_width):
            seen = twice = 0
            for pos in slots:
                bit = 1 << pos
                if bit & twice:
                    break
                twice |= seen & bit
                seen |= bit
            else:
                if all((seen & star).bit_count()+(twice & star).bit_count() <= 2 for star in self.stars):
                    self.longs.append((seen,twice))

    def base(self, rows):
        values = [sum(left in row and right in row for row in rows) for left,right in self.edges]
        assert max(values) <= 2
        return tuple(sum(1 << pos for pos,val in enumerate(values) if val >= level) for level in [1,2])

    def cycles(self, perm):
        available = set(self.edges)
        result = []
        while available:
            edge = min(available)
            cycle = 0
            while edge in available:
                available.remove(edge)
                cycle |= 1 << self.edges.index(edge)
                edge = tuple(sorted(perm[pole] for pole in edge))
            result.append(cycle)
        return result

    def units(self, need, allowed, room):
        if need == 0:
            return 1
        for star,cap in zip(self.stars,room):
            if cap == 0:
                allowed &= ~star
        width = allowed.bit_count()
        if width < need:
            return 0
        if need == 1:
            return width
        if need == 2:
            return comb(width,2)-sum(comb((allowed & star).bit_count(),2)
                                      for star,cap in zip(self.stars,room) if cap==1)
        result = 0
        while allowed.bit_count() >= need:
            first = allowed & -allowed
            allowed ^= first
            updated = [cap-bool(star & first) for star,cap in zip(self.stars,room)]
            result += self.units(need-1,allowed,updated)
        return result

    def coefficient(self, demand, permitted, singles, multis):
        need = self.width-demand.bit_count()
        if need < 0:
            return 0
        room = [cap-(star & demand).bit_count() for cap,star in zip(self.degree,self.stars)]
        if min(room) < 0:
            return 0
        def extra(rem, budget, start):
            subtotal = self.units(rem,permitted & singles,budget)
            for pos in range(start,len(multis)):
                cycle = multis[pos]
                size = cycle.bit_count()
                if size <= rem and cycle & permitted == cycle:
                    updated = [cap-(star & cycle).bit_count() for star,cap in zip(self.stars,budget)]
                    if min(updated)>=0:
                        subtotal += extra(rem-size,updated,pos+1)
            return subtotal
        return extra(need,room,0)

    def count(self, masks, perm):
        basepos, basehigh = masks
        cycles = self.cycles(perm)
        multis = [cycle for cycle in cycles if cycle.bit_count()>1]
        singles = self.universe ^ sum(multis)
        total = 0
        for seen, twice in self.longs:
            if (seen & basehigh) or (twice & basepos):
                continue
            if any((seen & cycle not in (0,cycle)) or (twice & cycle not in (0,cycle)) for cycle in multis):
                continue
            missing = self.universe ^ (basepos | seen)
            permitted = self.universe ^ (basehigh | twice | (basepos & seen))
            total += self.coefficient(missing,permitted,singles,multis)
        return total


def group(order,rows):
    source = sorted(rows)
    return [perm for perm in permutations(range(order)) if perm[0]==0 and
            sorted(tuple(sorted(perm[pos] for pos in row)) for row in rows)==source]


def toy():
    problem = Margins([1,2,2,2],1,2)
    for rows,expected in [([(0,1,2),(0,3),(0,3),(1,2)], [10,0]),
                          ([(1,2,3),(0,1),(0,2),(0,3)], [60,4,4,0,0,4])]:
        actions = group(4,rows)
        base = problem.base(rows)
        values = [problem.count(base,perm) for perm in actions]
        assert values==expected
        legal = set()
        for short in problem.edges:
            for left,right in combinations_with_replacement(problem.edges,2):
                if all(1 <= sum(all(pole in item for pole in edge) for item in rows+[short,left,right]) <= 2
                       for edge in problem.edges):
                    legal.add((short,(left,right)))
        def act(perm,word):
            return tuple(sorted(perm[pole] for pole in word))
        def image(perm,pair):
            short,longs = pair
            return act(perm,short),tuple(sorted(act(perm,word) for word in longs))
        assert [sum(image(perm,pair)==pair for pair in legal) for perm in actions]==values
        assert len({min(image(perm,pair) for perm in actions) for pair in legal})==sum(values)//len(values)
        print('literal/compressed',values)


def price():
    problem = Margins([1]+[2]*6,5,6)
    assert len(problem.longs)==6202
    identity = tuple(range(7))
    prices = []
    for double in range(6):
        start = process_time()
        probes = [problem.count(((1 << (16-double))-1,(1 << double)-1),identity),
                  problem.count((((1 << (16-double))-1) << (5+double),((1 << double)-1) << (21-double)),identity)]
        prices.append((process_time()-start)/2)
        print('synthetic two same-histogram locations',double,probes,round(prices[-1],4))
    print('identity full-width max-price x 267; group/bookkeeping separate',round(267*max(prices),2),'CPU-s')
    assert 267*max(prices)<60


def audit(roster,receipts):
    problem = Margins([1]+[2]*6,5,6)
    assert len(problem.longs)==6202
    with receipts.open() as f:
        receipt = iter(list(DictReader(f,delimiter='\t')))
    total = Counter()
    for line, text in enumerate(roster.read_text().splitlines(),1):
        row = json.loads(text)
        if row['status']!='pass':
            continue
        rec = next(receipt)
        triple = tuple(pole for pole in range(7) if row['triple'] >> pole & 1)
        rows = [triple]+[edge for edge,num in zip(problem.edges,row['word']) for _ in range(int(num))]
        assert [sum(pole in item for item in rows) for pole in range(7)]==[5]+[4]*6
        actions = group(7,rows)
        masks = problem.base(rows)
        fixed = {''.join(map(str,perm)):problem.count(masks,perm) for perm in actions}
        ident = fixed['0123456']
        order = len(actions)
        marks = factorial(len(triple)-(0 in triple))*factorial(6-len(triple)+(0 in triple))
        orbits,rem = divmod(sum(fixed.values()),order)
        assert (rem,marks%order,factorial(7)%order)==(0,0,0)
        assert (int(rec['row']),int(rec['triple']),rec['word'])==(line,row['triple'],row['word'])
        assert dict(piece.split(':') for piece in rec['fixed_by_permutation'].split(','))=={perm:str(val) for perm,val in fixed.items()}
        assert (int(rec['group']),int(rec['identity']),int(rec['orbits']))==(order,ident,orbits)
        marked,oriented = ident*(marks//order),ident*(factorial(7)//order)
        assert (int(rec['fixed_eT_weight']),int(rec['oriented_weight']))==(marked,oriented)
        assert (row['fixed'],row['oriented'])==(marks//order,factorial(7)//order)
        assert oriented==marked*7*comb(6,2 if 0 in triple else 3)
        total.update({'hosts':1,'actions':order,'identity':ident,'orbits':orbits,'oriented':oriented,'fixed_eT':marked,
                      'nonidentity_fixed':sum(fixed.values())-ident,'nonidentity_nonzero':sum(val>0 for val in fixed.values())-bool(ident)})
    assert next(receipt,None) is None and total['hosts']==162
    print('independent per-permutation and per-host weight checks',dict(total))


if __name__=='__main__':
    if sys.argv[1]=='toy':
        toy()
    elif sys.argv[1]=='price':
        price()
    else:
        audit(*map(Path,sys.argv[1:]))
