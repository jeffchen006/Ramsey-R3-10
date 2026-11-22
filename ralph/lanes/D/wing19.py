"""Count ordered wings at fixed supports; never emit a target pair."""
import json
import sys
from collections import Counter
from itertools import combinations, permutations
from math import factorial
from pathlib import Path

from triple18_price import shore_words


def groups(sites, triple, word):
    order = 1 + max(max(site) for site in sites)
    for tail in permutations(range(1, order)):
        perm = (0, *tail)
        if sum(1 << perm[pole] for pole in range(order) if triple >> pole & 1) != triple:
            continue
        move = tuple(sites.index(tuple(sorted((perm[left], perm[right])))) for left, right in sites)
        if bytes(word[pos] for pos in move) == word:
            yield ''.join(map(str,perm)), move


def index_long(rights, lower=1):
    bits = [[sum(1 << pos for pos, word in enumerate(rights) if word[site] == value)
             for value in range(3)] for site in range(len(rights[0]))]
    return [[[sum(mask for value, mask in enumerate(by_value) if lower <= count+left+value <= 2)
              for left in range(3)] for count in range(3)] for by_value in bits]


def count(lefts, rights, table, move):
    if move == tuple(range(len(move))):
        fixed = (1 << len(rights))-1
        short = lefts
    else:
        def stable(word):
            return all(word[pos] == word[dst] for pos, dst in enumerate(move) if pos != dst)
        fixed = sum(1 << pos for pos, word in enumerate(rights) if stable(word))
        short = filter(stable, lefts)
    total = 0
    for word in short:
        allowed = fixed
        for value, choices in zip(word, table):
            allowed &= choices[value]
            if not allowed:
                break
        total += allowed.bit_count()
    return total


def one(sites, triple, word, lefts, rights, table):
    counts = [val + ((1 << first | 1 << second) & triple == (1 << first | 1 << second))
              for (first, second), val in zip(sites, word)]
    local = [choices[num] for choices, num in zip(table, counts)]
    return [(perm, count(lefts, rights, local, move)) for perm, move in groups(sites, triple, word)]


def controls():
    from triple18_price import compare_toy
    sites = list(combinations(range(4), 2))
    lefts = shore_words(sites, [1,2,2,2], 1)
    rights = shore_words(sites, [2]*4, 2)
    for triple, ordinary, expected in [(7, [(0,3),(0,3),(1,2)], [10,0]),
                                       (14, [(0,1),(0,2),(0,3)], [60,4,4,0,0,4])]:
        pole_set = {pole for pole in range(4) if triple >> pole & 1}
        literal = compare_toy(pole_set, ordinary)
        fixes = one(sites, triple, bytes(ordinary.count(site) for site in sites), lefts, rights, index_long(rights))
        assert [val for perm, val in fixes] == literal == expected
    for perm in permutations(range(4)):
        assert tuple([2]*4)[::-1] != tuple([1,2,2,2][pos] for pos in perm)
    assert all(sum(short)==1 for short in lefts) and all(sum(long)==2 for long in rights)
    print('rejected shore exchange: neither the contact degrees nor pair totals can be exchanged')
    planted()


def planted():
    import networkx as nx
    path = Path(__file__).resolve().parents[3] / 'gluing/val/r3_7_22.g6'
    regular = hosts = marks = admissible = 0
    for line in path.read_bytes().splitlines():
        graph = nx.from_graph6_bytes(line)
        stars = [set(graph[vertex]) for vertex in graph]
        if any(len(star) != 6 for star in stars):
            continue
        regular += 1
        if max(len(first & second) for first, second in combinations(stars,2)) > 3:
            continue
        hosts += 1
        for first, second in combinations(graph,2):
            middle = stars[first] & stars[second]
            if second in stars[first] or len(middle) != 1:
                continue
            poles = sorted(stars[next(iter(middle))] - {first,second})
            short, long = stars[first]-middle, stars[second]-middle
            outside = set(graph)-short-long-middle-set(poles)-{first, second}
            sites = list(combinations(poles,2))
            def observations(region):
                return bytes(len(region & stars[left] & stars[right]) for left, right in sites)
            base, little, large = map(observations, (outside, short, long))
            images = set()
            for perm in permutations(poles):
                renamed = dict(zip(poles,perm))
                images.add(bytes(large[sites.index(tuple(sorted((renamed[left],renamed[right]))))]
                                 for left,right in sites))
            literal = sum(all(base[pos]+little[pos]+big[pos] <= 2 for pos in range(6)) for big in images)
            assert all(base[pos]+little[pos]+large[pos]+1 == len(stars[left]&stars[right]) <= 3
                       for pos,(left,right) in enumerate(sites))
            choices = [basis[num] for basis,num in zip(index_long(sorted(images),lower=0), base)]
            assert count([little], sorted(images), choices, tuple(range(6))) == literal >= 1
            marks += 1
            admissible += literal
    assert (regular,hosts,marks)==(10,3,125)
    print('C22 191 catalogue, regular/cap-three hosts/marks',regular,hosts,marks,'legal distinct long images',admissible)


def target(roster, dest):
    sites = list(combinations(range(7),2))
    lefts = shore_words(sites,[1]+[2]*6,5)
    rights = shore_words(sites,[2]*7,6)
    assert (len(lefts),len(rights))==(4062,6202)
    table = index_long(rights)
    totals = Counter()
    with dest.open('x') as receipt:
        print('row\ttriple\tword\tgroup\tidentity\torbits\tfixed_eT_weight\toriented_weight\tfixed_by_permutation',file=receipt)
        for rownum,line in enumerate(roster.read_text().splitlines(),1):
            row = json.loads(line)
            if row['status'] != 'pass':
                continue
            fixes = one(sites,row['triple'],bytes(map(int,row['word'])),lefts,rights,table)
            ident = fixes[0][1]
            aut = len(fixes)
            assert fixes[0][0]=='0123456' and aut==row['aut'] and max(val for _,val in fixes)==ident
            orbits, remainder = divmod(sum(val for _,val in fixes),aut)
            assert not remainder and row['oriented']*aut == factorial(7)
            weighted = ident*row['fixed'],ident*row['oriented']
            print(rownum,row['triple'],row['word'],aut,ident,orbits,*weighted,
                  ','.join(f'{perm}:{val}' for perm,val in fixes),sep='\t',file=receipt)
            for key,val in [('hosts',1),('nonempty',bool(ident)),('actions',aut),('identity',ident),
                            ('orbits',orbits),('fixed_eT',weighted[0]),('oriented',weighted[1])]:
                totals[row['triple'],key] += val
    for triple in [7,14]:
        print('T mask',triple,{key:val for (mask,key),val in totals.items() if mask==triple})
    assert sum(totals[mask,'hosts'] for mask in [7,14])==162


if __name__=='__main__':
    if sys.argv[1:] == ['controls']:
        controls()
    else:
        target(*map(Path,sys.argv[1:]))
