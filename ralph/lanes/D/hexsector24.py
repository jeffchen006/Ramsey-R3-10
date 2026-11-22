from collections import Counter,defaultdict
from itertools import combinations
import json
from high24 import HIGH,graph_masks,sites

def ring_sites(wing):
    cycles=set()
    for first in range(8):
        def extend(path):
            if len(path)==6:
                if wing[path[-1]]>>first&1:cycles.add(tuple(sorted(path)))
                return
            for vertex in sites(wing[path[-1]]):
                if vertex not in path and vertex>=first:extend(path+[vertex])
        extend([first])
    return cycles

def rings(wing):
    cycles=ring_sites(wing);counts=[]
    for cycle in cycles:
        mask=sum(1<<site for site in cycle);assert all((wing[site]&mask).bit_count()==2 for site in cycle);counts.append(sum(wing[site].bit_count()-2 for site in cycle))
    return sorted(counts)

def sector():
    for density in (19,20,21,22):
        spec={row['number']:row for row in json.loads((HIGH/f'spec{density}.json').read_text()) if len(row['points'])==4};keys=(HIGH/f'free{density}').read_text().splitlines();shapes=Counter();catalog=defaultdict(list);assignments={}
        for number,row in spec.items():
            wing=graph_masks(row['g6']);counts=rings(wing);rebound=[]
            for triple in combinations(range(8),3):
                common=[wing[first]&wing[second] for first,second in combinations(triple,2)]
                if all(mask.bit_count()==1 for mask in common) and len(set(common))==3:rebound.append(sum(wing[site].bit_count()-2 for site in [*triple,*[mask.bit_length()-1 for mask in common]]))
            assert counts==sorted(rebound);shapes[(min(counts) if counts else 7,len(counts))]+=1;assignments[number]=counts
        for key in keys:
            counts=assignments[int(key.split('_')[1])];catalog[min(counts) if counts else 7].append(key)
        (HIGH/f'rings{density}.json').write_text(json.dumps(assignments));print(density,'colored shape histogram by minimum exits and ring count',dict(sorted(shapes.items())),'leader keys by min exits',dict(sorted((mark,len(group)) for mark,group in catalog.items())),flush=True)
        for mark,group in catalog.items():(HIGH/f'minexit{density}.{mark}').write_text('\n'.join(group)+'\n')
        rare=[key for key in keys if len(assignments[int(key.split('_')[1])])<=1];(HIGH/f'rare{density}').write_text(''.join(key+'\n' for key in rare));print('at most one ring',density,'leader roots',len(rare),flush=True)
        disjoint=set()
        for number,row in spec.items():
            cycles=ring_sites(graph_masks(row['g6']));multiplicity=Counter(site for cycle in cycles for site in cycle);pairwise=all(not set(first).intersection(second) for first,second in combinations(cycles,2));assert pairwise==(max(multiplicity.values(),default=0)<=1)
            if len(cycles)>=2 and pairwise:disjoint.add(number)
        residual=[key for key in keys if int(key.split('_')[1]) in disjoint];(HIGH/f'disjoint{density}').write_text(''.join(key+'\n' for key in residual));print('two or more rings but no intersecting pair',density,'shapes',len(disjoint),'keys',len(residual),flush=True)

if __name__=='__main__':sector()
