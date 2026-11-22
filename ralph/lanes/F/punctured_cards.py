"""Generate and bind degree-eight cyclic unsigned cards; physical addback control."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from math import comb, gcd
from pathlib import Path
import sys

from cyclic_base import profiles, matrix
from cyclic_check import read_base
from relift_audit import encode, quotient
from orbit_extend import independent, independent_sets, parse_graph6, to_graph6


def rows(path):
    return Path(path).read_text().splitlines()


def write(path, data):
    Path(path).write_text(''.join(str(row) + '\n' for row in data))


def oracle(size, degree):
    legal = set()
    raw = 0
    for vertical in range(2):
        if (degree - vertical) % 2:
            continue
        for positive in combinations_with_replacement(range(1, size // 2 + 1), (degree - vertical) // 2):
            if any(positive.count(step) > 2 for step in positive):
                continue
            raw += 1
            word = tuple([vertical] + [positive.count(step) + positive.count(size-step) for step in range(1, size)])
            graph = [0] * (2*size)
            for left, right in combinations(range(2*size), 2):
                weight = word[(left//2 - right//2) % size]
                if weight == 2 or (weight == 1 and (left^right)&1):
                    graph[left] |= 1 << right
                    graph[right] |= 1 << left
            assert all(neighbours.bit_count() == degree for neighbours in graph)
            if all(independent(neighbours, graph) for neighbours in graph):
                legal.add(word)
    return raw, legal


def sources(size, degree, tag):
    raw, legal = oracle(size, degree)
    source = []
    total = len(legal)
    for profile, orbit in profiles(size, degree, degree):
        text = encode(matrix(size, profile))
        base = read_base(text)
        assert all(base[left][right] == base[0][(right-left)%size] for left in range(size) for right in range(size))
        images = {tuple(base[0][step*unit%size] for step in range(size)) for unit in range(1,size) if gcd(unit,size)==1}
        assert len(images) == orbit and images <= legal
        legal -= images
        source.append(text)
    assert not legal
    write(tag + '.q', source)
    print('source',size,degree,'raw/legal/unit rows',raw,total,len(source))
    return source


def add(graph, contacts, vertical):
    size = len(graph)
    result = graph[:] + [0,0]
    if vertical:
        result[-2] = 1 << (size+1)
        result[-1] = 1 << size
    for contact in contacts:
        for side in (0,1):
            result[size+side] |= 1 << (contact^side)
            result[contact^side] |= 1 << (size+side)
    return result


def control():
    source = sources(5,2,'small')
    cyclic_order = [2*(index%5) + int(index>=5) for index in range(10)]
    graph = [0]*10
    for position, vertex in enumerate(cyclic_order):
        graph[vertex] = sum(1<<cyclic_order[(position+step)%10] for step in (-1,1))
    physical = quotient(graph)
    assert any(all(physical[left][right] == read_base(source[0])[left*unit%5][right*unit%5]
                   for left in range(5) for right in range(5)) for unit in range(1,5))
    expected = {}
    goods = []
    for contacts in product((-1,0,1), repeat=5):
        selected = tuple(2*index+side for index,side in enumerate(contacts) if side>=0)
        for vertical in (0,1):
            result = add(graph,selected,vertical)
            if not all(independent(row,result) for row in result):continue
            assert [row&1023 for row in result[:10]] == graph
            score = sum(1 for _ in independent_sets(result,4095,6))
            expected[(tuple(selected),vertical)] = score
            if not score:goods.append(to_graph6(result))
    verified = {}
    for mask in range(1024):
        if any((mask>>(2*index))&3 == 3 for index in range(5)) or not independent(mask,graph):continue
        partner = ((mask & 341)<<1) | ((mask & 682)>>1)
        def count(remaining, amount):
            return sum(1 for subset in combinations(range(10),amount) if (bits:=sum(1<<vertex for vertex in subset)) & ~remaining == 0 and independent(bits,graph))
        for vertical in (0,1):
            score = count(1023,6)+count(1023^mask,5)+count(1023^partner,5)+(not vertical)*count(1023^(mask|partner),4)
            verified[tuple(vertex for vertex in range(10) if mask&(1<<vertex)),vertical] = score
    assert verified==expected
    good = add(graph,[cyclic_order[0],cyclic_order[3]],1)
    bad = add(graph,[cyclic_order[0],cyclic_order[2]],1)
    assert expected[(0,6),1]==0 and expected[(0,4),1]>0
    write('positive.g6',[to_graph6(good)]);write('adverse.g6',[to_graph6(bad)])
    print('addbacks',len(expected),'positive',len(goods),'positive/adverse scores',expected[(0,6),1],expected[(0,4),1])


def target():
    source = sources(19,8,'card')
    old = rows('../r8/ctl.q')
    assert set(source) == {text for text in old if all(sum(row)==8 for row in read_base(text))}
    write('r8.bind', [f'{index} {old.index(text)} '+','.join(map(str,range(19))) for index,text in enumerate(source)])
    oldgraphs=rows('../r6/sparse.distinct.g6');assert len(oldgraphs)==33
    report=[]
    for index,line in enumerate(oldgraphs):
        graph=parse_graph6(line)
        degrees=tuple(sorted(map(int.bit_count,graph)))
        assert degrees!=(8,)*38
        report.append(f'{index} degree-invariant '+','.join(map(str,degrees)))
    write('r6.bind',report)
    print('R8 actual identity maps',len(source),'R6 impossible maps by degree',len(report))
    for vertical in (0,1):
        counts = [(contacts,comb(19,contacts)*2**contacts) for contacts in range(20) if 4<=contacts+vertical<=9 and 152+2*contacts+vertical>=161]
        print('vertical',vertical,'contact-count / labelled signed contact choices before triangles',counts,'total',sum(num for _,num in counts))


if __name__=='__main__':
    {'control':control,'target':target}[sys.argv[1]]()
