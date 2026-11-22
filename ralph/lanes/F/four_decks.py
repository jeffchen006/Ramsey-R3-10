"""Bind archived order-36 inputs to paired-card degree and automorphism tests."""
from collections import Counter
from itertools import combinations, islice
from math import comb
from pathlib import Path
import sys
import pynauty

from orbit_extend import independent_sets,parse_graph6
from cyclic_check import read_base


def check_graph(graph,deleted,stats,survivors,record):
    selected=sum(1<<site for site in deleted);degrees=Counter((hood&~selected).bit_count() for site,hood in enumerate(graph) if not selected>>site&1)
    if any(count%2 for count in degrees.values()) or max(degrees)-min(degrees)>1 or not any(set(degrees)<={cross,cross+1} for cross in (6,7,8)):return
    stats['degree']+=1
    sites=[site for site in range(len(graph)) if not selected>>site&1]
    index={site:pos for pos,site in enumerate(sites)}
    nauty=pynauty.Graph(len(sites),adjacency_dict={idx:[index[site] for site in sites if graph[original]>>site&1] for idx,original in enumerate(sites)})
    gens,order,power,_,_=pynauty.autgrp(nauty)
    identity=tuple(range(len(sites)));group={identity};queue=[identity]
    for perm in queue:
        for generator in gens:
            nxt=tuple(generator[image] for image in perm)
            if nxt not in group:group.add(nxt);queue.append(nxt)
        assert len(group)<20000
    assert len(group)==round(order*10**power)
    frees=[perm for perm in group if all(image!=site and perm[image]==site for site,image in enumerate(perm))]
    if not frees:return
    stats['free involution']+=1
    for perm in frees:
        pairs=[(sites[pos],sites[image]) for pos,image in enumerate(perm) if pos<image]
        base=[[((graph[left]>>a)&1)+((graph[left]>>b)&1) if (left,right)!=(a,b) else (graph[left]>>right)&1 for a,b in pairs] for left,right in pairs]
        if len({sum(row)-row[idx] for idx,row in enumerate(base)})!=1:continue
        stats['constant-crossing actions']+=1
        def cert(matrix):
            num=len(matrix); simple=[(left,right) for left,right in combinations(range(num),2) if matrix[left][right]==2]
            adjacency={pos:[] for pos in range(num+len(simple))}
            for left,right in combinations(range(num),2):
                if matrix[left][right]==1:adjacency[left].append(right);adjacency[right].append(left)
            for new,(left,right) in enumerate(simple,num):adjacency[new]=[left,right];adjacency[left].append(new);adjacency[right].append(new)
            colours=[set(range(num)),set(range(num,len(adjacency)))] if simple else []
            return pynauty.certificate(pynauty.Graph(len(adjacency),adjacency_dict=adjacency,vertex_coloring=colours))
        if not hasattr(check_graph,'certs'):check_graph.certs={cert(read_base(text)):idx for idx,text in enumerate(Path('max.q').read_text().splitlines())}
        idx=check_graph.certs.get(cert(base))
        if idx is not None:
            stats['in roster']+=1;survivors.append((record,deleted,idx))


def main(stride):
    lane=Path(__file__).resolve().parent
    for name in ('anchor36','score178','score179'):
        stats=Counter();matches=[]
        if name=='anchor36':
            population=Path('../r4/anchor36.g6').read_text().splitlines();assert len(population)==9490
            for index in range(0,len(population),stride):
                stats['raw']+=1;check_graph(parse_graph6(population[index]),[],stats,matches,index)
        else:
            graph=parse_graph6((lane/('round4_seed40_24'+('_e179' if name=='score179' else '')+'.g6')).read_text().strip());assert sum(hood.bit_count() for hood in graph)==2*int(name[5:])
            tens=list(independent_sets(graph,(1<<40)-1,10));assert len(tens)==24
            for deleted in islice(combinations(range(40),4),0,None,stride):
                stats['raw']+=1
                if all(sum(1<<site for site in deleted)&mask for mask in tens):
                    stats['hits24']+=1;check_graph(graph,deleted,stats,matches,name)
        print(name,stride,sorted(stats.items()),'matched',matches[:10],flush=True)
        Path(f'deck.{name}.{stride}.tsv').write_text(''.join(f'{entry}\n' for entry in matches))
    for idx,text in enumerate(Path('../r11/card.q').read_text().splitlines()):
        base=read_base(text);degrees={sum(row[1:])-row[pos] for pos,row in enumerate(base) if pos}
        assert len(degrees)>1
    print('all 27 R11 parents punctured once have nonconstant crossings IN THE INHERITED PAIRING; their known I10 excludes other strict representations as well.')


if __name__=='__main__':main(int(sys.argv[1]))
