import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
import sys
import pynauty
from wing24 import OUT,graph_masks,sites

def graph(row,words):
    wing=graph_masks(row['g6']);size=len(wing);points=row['points'];outer=size+3
    edges={site:list(sites(mask)) for site,mask in enumerate(wing)};edges.update({size:[],size+1:[],size+2:[]});colors=[set(range(size))-set(points),set(points),{size,size+1},{size+2},set(range(outer,outer+len(words)))];colors=[group for group in colors if group]
    def edge(first,second):edges[first].append(second);edges[second].append(first)
    for site in range(size):edge(site,size+int(site>=size//2))
    edge(size,size+2);edge(size+1,size+2)
    for idx,word in enumerate(words):
        edges[outer+idx]=[]
        for bit in sites(word):edge(points[bit],outer+idx)
    return pynauty.Graph(len(edges),False,edges,colors)

def join(first,second):
    order1=pynauty.canon_label(first);order2=pynauty.canon_label(second);perm={old:new for old,new in zip(order1,order2)}
    assert all({perm[other] for other in first.adjacency_dict[site]}==set(second.adjacency_dict[perm[site]]) for site in perm)
    assert all({perm[site] for site in left}==right for left,right in zip(first.vertex_coloring,second.vertex_coloring));return [perm[idx] for idx in range(len(perm))]

def index():
    roots={};groups=defaultdict(list);shapes=defaultdict(list)
    for row in json.loads((OUT/'spec.json').read_text()):
        shapes[pynauty.certificate(graph({**row,'points':[]},[]))].append(row['number'])
        for idx,words in enumerate(row['decks']):
            key=f'{row["number"]}_{idx}';roots[key]=graph(row,words);groups[pynauty.certificate(roots[key])].append(key)
    records=[]
    for group in groups.values():
        first=group[0];records.append({'keys':group,'perms':{key:join(roots[first],roots[key]) for key in group}})
    (OUT/'orbits.json').write_text(json.dumps(records));(OUT/'shapeorbits.json').write_text(json.dumps(list(shapes.values())));print('360 marked keys, orbit representatives',len(groups),'hist',Counter(map(len,groups.values())),'57 shapes, unmarked orbits',len(shapes),'hist',Counter(map(len,shapes.values())))

if __name__=='__main__':index()
