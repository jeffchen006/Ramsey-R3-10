import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
from random import Random

import pynauty

from reciprocal_audit import SOURCE22, decode, host_masks, merge, vertices
from reciprocal_census import PILOTS
from reciprocal_census_proofs import DOMAIN


def transport(graph, image):
    assert sorted(image) == list(range(len(graph)))
    mapped = [0]*len(graph)
    bits = [1 << target for target in image]
    for idx,row in enumerate(graph):
        mapped[image[idx]] = sum(bits[vertex] for vertex in vertices(row))
    return tuple(mapped)


def normalize(graph, left, right):
    indices = [set(range(0,left)),set(range(left,left+right)),set(range(left+right,len(graph)))]
    nauty_graph = pynauty.Graph(len(graph),adjacency_dict={idx:vertices(row) for idx,row in enumerate(graph)},
                               vertex_coloring=indices)
    orbit_order = pynauty.canon_label(nauty_graph)
    forward = [None]*len(graph)
    for canonical, original in enumerate(orbit_order):
        forward[original] = canonical
    assert all({forward[vertex] for vertex in cell} == cell for cell in indices)
    return transport(graph,forward),tuple(forward)


def check_equiv(classes, graph, left, right, key):
    normalized, forward = normalize(graph,left,right)
    identifier = (left,right,normalized)
    if identifier in classes:
        other, representative, representative_forward = classes[identifier]
        assert other != key
        reverse = {target:vertex for vertex,target in enumerate(representative_forward)}
        image = tuple(reverse[target] for target in forward)
        assert transport(graph,image) == tuple(representative)
        return other,image
    classes[identifier] = key,graph,forward
    return key,tuple(range(len(graph)))


def calibrate():
    generators = Random(310221)
    left, right = ([host_masks(decode(row)) for row in Path(f'cal-{n}.g6').read_text().splitlines()]
                   for n in (10,11))
    variants = 0
    for row in Path('cal-planted.tsv').read_text().splitlines():
        key = tuple(map(int,row.split()))
        graph, ll, rr = merge(left[key[0]],right[key[5]],key,2)
        identity = tuple(range(len(graph)))
        names = list(identity)
        for start,end in [(0,ll),(ll,ll+rr),(ll+rr,len(graph))]:
            segment = names[start:end]
            generators.shuffle(segment)
            names[start:end] = segment
        changed = transport(graph,names)
        classes = {}
        assert check_equiv(classes,graph,ll,rr,key) == (key,identity)
        assert check_equiv(classes,changed,ll,rr,(*key,-1))[0] == key
        variants += 1
    assert variants == 395
    print('395 planted positives retain their exact canonical graph under separate cell permutations')


def ratio():
    left = [host_masks(decode(row)) for row in SOURCE22.read_text().splitlines()]
    classes = {}
    counts = Counter()
    with Path('proof-reuse-stage.tsv').open('w') as receipts:
        for lo,hi in PILOTS:
            folder = Path(f'{lo:07d}-{hi:07d}')
            right = [host_masks(decode(row)) for row in (folder/'hosts.g6').read_text().splitlines()]
            with (folder/'maps.tsv').open() as source:
                for row in source:
                    *fields,reason,_ = row.split()
                    if reason not in DOMAIN:
                        continue
                    key = tuple(map(int,fields))
                    graph,ll,rr = merge(left[key[0]],right[key[5]-lo],key,3)
                    representative,image = check_equiv(classes,graph,ll,rr,key)
                    token = sha256(bytes().join(mask.to_bytes(5,'little') for mask in graph)).hexdigest()
                    print(reason,','.join(map(str,key)),','.join(map(str,representative)),
                          ','.join(map(str,image)),token,sep='\t',file=receipts)
                    counts[reason] += 1
                    if representative == key:
                        counts[f'representative:{reason}'] += 1
    print('domain maps',sum(counts[kind] for kind in DOMAIN),'exact representatives',len(classes),dict(sorted(counts.items())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=['cal','ratio'])
    args = parser.parse_args()
    calibrate() if args.mode == 'cal' else ratio()
