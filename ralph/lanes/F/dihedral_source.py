"""Complete regular-dihedral unsigned sources, with explicit quotient-isomorphism maps."""

import argparse
from collections import Counter, defaultdict
from itertools import product, combinations, repeat
from math import gcd
from pathlib import Path

import pynauty

from relift_audit import decode, encode, explicit_lift, pairs, quotient, walk_score
from orbit_extend import independent, to_graph6


def base_matrix(vert, inner, cross):
    length = len(inner)
    return [[vert if left == right else inner[(right-left) % length] if left//length == right//length
             else cross[(right-left if left < right else left-right) % length] for right in range(2*length)]
            for left in range(2*length)]


def source(length, degrees):
    crosses = defaultdict(list)
    for cross in product(range(3), repeat=length):
        if sum(cross) <= max(degrees) and all(cross <= cross[shift:]+cross[:shift] for shift in range(1, length)):
            crosses[sum(cross)].append(cross)
    units = [step for step in range(1, length) if gcd(step, length) == 1]
    for half in product(range(3), repeat=length//2):
        inner = tuple((0, *half)[min(step, length-step)] for step in range(length))
        for vert in range(2):
            for degree in degrees:
                for cross in crosses[degree-vert-sum(inner)]:
                    if vert and (2 in cross or 2 in inner):
                        continue
                    if any((inner, cross) > (tuple(inner[(unit*step) % length] for step in range(length)),
                                              tuple(cross[(unit*step+shift) % length] for step in range(length)))
                           for unit in units for shift in range(length)):
                        continue
                    base = base_matrix(vert, inner, cross)
                    if any(base[0][right] == 2 and any(base[0][other] and base[right][other]
                           for other in range(2*length)) for right in range(1, 2*length)):
                        continue
                    yield base


def canon(base):
    size = len(base)
    adjacency = {left: [size+left] + [right for right in range(size) if left != right and base[left][right]]
                 for left in range(size)}
    adjacency.update({size+left: [left]+[size+right for right in range(size) if base[left][right] == 2]
                      for left in range(size)})
    perm = pynauty.canon_label(pynauty.Graph(2*size, adjacency_dict=adjacency,
               vertex_coloring=[set(range(size)), set(range(size, 2*size))]))[:size]
    assert sorted(perm) == list(range(size))
    return encode([[base[left][right] for right in perm] for left in perm]), perm


def generate(tag, length, degrees, old=()):
    existing, representatives, counts = {}, [], Counter()
    for index, text in enumerate(old):
        key, perm = canon(decode(text))
        existing[key] = ('old', index, perm)
    with open(tag+'.maps', 'w') as receipts:
        for base in source(length, degrees):
            key, perm = canon(base)
            text = encode(base)
            if key not in existing:
                existing[key] = ('new', len(representatives), perm)
                representatives.append(text)
            origin, index, dest = existing[key]
            image = [dest[perm.index(left)] for left in range(len(base))]
            print(text, origin, index, ','.join(map(str, image)), file=receipts)
            counts[origin] += 1
    Path(tag+'.q').write_text(''.join(text+'\n' for text in representatives))
    print(tag, 'affine rows', dict(counts), 'distinct new', len(representatives))
    return representatives


def calibrate():
    small = generate('small', 2, range(8))
    scores = {}
    positions = [(left,right,side) for left,right in pairs(4) for side in range(1 if left==right else 2)]
    for encoded in range(1 << len(positions)):
        graph = [0]*8
        for ident,(left,right,side) in enumerate(positions):
            if encoded & (1 << ident):
                for layer in range(2):
                    other = right*2+(layer^(side if left!=right else 1))
                    graph[2*left+layer] |= 1 << other
                    graph[other] |= 1 << (2*left+layer)
        if not all(independent(adj,graph) for adj in graph):
            continue
        base = quotient(graph)
        if any(base[left][right] != base[0][left^right] for left,right in pairs(4)):
            continue
        key, _ = canon(base)
        score = walk_score(graph,4)
        scores[key] = min(scores.get(key,score),score)
    assert {canon(decode(text))[0] for text in small} == scores.keys()
    Path('small.scores').write_text(''.join(str(scores[canon(decode(text))[0]])+'\n' for text in small))
    control = generate('ctl',4,[5]); planted = encode(base_matrix(0,(0,1,1,1),(2,0,0,0)))
    matches = [text for text in control if canon(decode(text))[0]==canon(decode(planted))[0]]
    assert len(matches)==1
    Path('planted.q').write_text(matches[0]+'\n')
    print('PASS 65536 graphs; Clebsch-type noncyclic quotient located at row', control.index(matches[0]))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('mode', choices=['ctl','target'])
    if parser.parse_args().mode=='ctl': calibrate()
    else: generate('target',10,[9], Path('../r8/target.q').read_text().splitlines())
