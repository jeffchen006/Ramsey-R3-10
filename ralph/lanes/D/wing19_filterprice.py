"""Price the next marginal filter. No target Y host is read; no target join."""
from itertools import combinations, combinations_with_replacement
from pathlib import Path
from time import process_time

from triple18_price import shore_words


def tight_types(order, rows, types):
    within = [sum(1 << pos for pos,mask in enumerate(types) if mask & ~cover == 0) for cover in range(1 << order)]
    hitting = [sum(1 << pos for pos,mask in enumerate(types) if mask & row) for row in rows]
    later = [sum(1 << pos for pos in range(index+1,len(rows)) if rows[pos] & row) for index,row in enumerate(rows)]
    unique = set()
    def visit(available, union, hits, size):
        if size and union.bit_count()==size:
            unique.add(hits & within[union])
        while available:
            bit = available & -available
            available -= bit
            index = bit.bit_length()-1
            visit(available & later[index], union | rows[index], hits & hitting[index], size+1)
    visit((1 << len(rows))-1,0,(1 << len(types))-1,0)
    selectors = set()
    for mask in unique:
        selectors.update(combinations_with_replacement([pos for pos in range(len(types)) if mask >> pos & 1],2))
    return selectors


def small():
    import networkx as nx
    types = sorted(range(1,16),key=lambda mask:(mask.bit_count(),mask))
    selectors = tight_types(4,[3,3],types)
    def banned(rows):
        return any(tuple(sorted((types.index(first),types.index(second)))) in selectors for first,second in combinations(rows,2))
    assert banned([1,2]) and banned([1,1]) and not banned([1,4]) and not banned([1])
    regular = hosts = marks = 0
    path = Path(__file__).resolve().parents[3] / 'gluing/val/r3_7_22.g6'
    for line in path.read_bytes().splitlines():
        graph = nx.from_graph6_bytes(line)
        stars = [set(graph[vertex]) for vertex in graph]
        if any(len(star)!=6 for star in stars):
            continue
        regular += 1
        if max(len(left & right) for left,right in combinations(stars,2))>3:
            continue
        hosts += 1
        for left,right in combinations(graph,2):
            middle = stars[left] & stars[right]
            if right in stars[left] or len(middle)!=1:
                continue
            poles = sorted(stars[next(iter(middle))]-{left,right})
            untouched = set(graph)-stars[left]-stars[right]-set(poles)-{left,right}
            def mask(vertex):
                return sum(1 << index for index,pole in enumerate(poles) if pole in stars[vertex])
            selectors = tight_types(4,[mask(site) for site in untouched],types)
            for tip in (left,right):
                rows = [mask(site) for site in stars[tip]-middle]
                assert not banned([row for row in rows if row])
            marks += 1
    assert (regular,hosts,marks)==(10,3,125)
    print('two copies on 01: block singleton 0+1 and 0+0, retain 0+2 and one 0; all 250 C22 planted shores pass')


def marginal_index(degrees,width,edges,types):
    table = {pair:0 for pair in combinations_with_replacement(range(len(types)),2)}
    for index,word in enumerate(shore_words(edges,degrees,width)):
        degrees_left = list(degrees)
        physical = []
        for pos,((first,second),count) in enumerate(zip(edges,word)):
            degrees_left[first] -= count
            degrees_left[second] -= count
            physical.extend([len(degrees)+pos]*count)
        physical.extend(pole for pole,count in enumerate(degrees_left) for _ in range(count))
        assert len(physical)==8
        bit = 1 << index
        for pair in combinations(sorted(physical),2):
            table[pair] |= bit
    return table


def price():
    edges = list(combinations(range(7),2))
    types = [1 << pole for pole in range(7)]+[1 << first | 1 << second for first,second in edges]
    start = process_time()
    tables = [marginal_index(degrees,width,edges,types) for degrees,width in [([1]+[2]*6,5),([2]*7,6)]]
    print('two shore indexes, each 406 bitsets; global build CPU-s',round(process_time()-start,4))
    # A deliberately impossible benchmark: all 14 Y rows share a pole, so all 2^14 subsets are visited.
    synthetic = [3,5,9,17,33,65]*2+[3,7]
    assert all(row & 1 for row in synthetic)
    start = process_time()
    for _ in range(12):
        selectors = tight_types(7,synthetic,types)
        for table in tables:
            mask = 0
            for pair in selectors:
                mask |= table[pair]
            assert mask
    print('synthetic maximal-clique-visit shape only: compiled selectors',len(selectors),
          'x162 projected CPU-s',round((process_time()-start)*162/12,4))


if __name__=='__main__':
    small()
    price()
