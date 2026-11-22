from itertools import combinations,combinations_with_replacement
from pathlib import Path
import json
import subprocess
import sys
from exception_cover import verify_lrat
from orbit_extend import ROOT,parse_graph6,to_graph6

def known():
    labels=[1,12,2,11,4,9,6,7,3,10];graph=[sum(1<<right for right,dest in enumerate(labels) if (dest-src)%13 in (1,5,8,12)) for src in labels]
    assert not graph[8]>>9&1;size=8;core=[(row&255)|(1<<(vertex^1)) for vertex,row in enumerate(graph[:8])]
    Path('fixedpos.signs').write_text('0 '+to_graph6(core)+'\n');contacts=sorted(row&255 for row in graph[8:]);Path('fixedpos.plant').write_text(' '.join(map(str,contacts))+'\n')
    path=Path('planted10.g6');path.write_text(to_graph6(graph)+'\n');gate=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',path,'10','5'],capture_output=True,text=True,check=True);assert json.loads(gate.stdout)['graphs'][0]['ok'];Path('planted10.gate').write_text(gate.stdout)
    assert any(contacts[0]&(3<<(2*site))==3<<(2*site) for site in range(4));print('known nonadjacent attachments on induced C13',contacts)

def verify(tag,index):
    sign,text=Path(tag+'.signs').read_text().splitlines()[index].split();graph=parse_graph6(text);n=len(graph);target=4 if tag=='plainpos' else 5 if tag=='fixedpos' else 10
    stem=Path(f'{tag}-s{index}');masks=tuple(map(int,stem.with_suffix('.masks').read_text().split()));assert len(set(masks))==len(masks) and all(0<=mask<1<<n for mask in masks)
    blocks=set(masks);lines=stem.with_suffix('.cnf').read_text().splitlines();assert lines.pop(0)==f'p cnf {n} {len(lines)}'
    for line in lines:
        *clause,zero=map(int,line.split());assert not zero and all(0<abs(literal)<=n for literal in clause)
        if len(clause)==n:
            assert set(map(abs,clause))==set(range(1,n+1));excluded=sum(1<<(-literal-1) for literal in clause if literal<0);blocks.remove(excluded)
        elif min(clause)>0:
            sites=[literal-1 for literal in clause];assert len(sites)==len(set(sites))==target-1 and all(not graph[src]>>dst&1 for src,dst in combinations(sites,2))
        else:
            first,second=(-literal-1 for literal in clause);assert 0<=first<second<n and (first^1)!=second and graph[first]>>second&1
    assert not blocks;verify_lrat(stem)
    expected=set(combinations_with_replacement(masks,2));count=len(expected);openpairs=set()
    for line in stem.with_suffix('.pairs').read_text().splitlines():
        first,second,witness=map(int,line.split());expected.remove((first,second));assert 0<=witness<1<<(n+2)
        def edge(left,right):
            if left>=n:return False
            if right>=n:return (first if right==n else second)>>left&1
            if (left^1)!=right:return graph[left]>>right&1
            pair=3<<left
            return all(neighbors&pair!=pair for neighbors in (first,second))
        if witness:
            sites=[vertex for vertex in range(n+2) if witness>>vertex&1];assert len(sites)==target and not any(edge(left,right) for left,right in combinations(sites,2))
        else:openpairs.add((first,second))
    assert not expected
    if tag=='fixedpos':assert tuple(map(int,Path('fixedpos.plant').read_text().split())) in openpairs
    status='open' if openpairs else 'closed';assert stem.with_suffix('.result').read_text().split()==[tag,str(index),sign,status,str(len(masks)),str(count),str(len(openpairs))]
    return len(masks),count,len(openpairs)

if __name__=='__main__':
    if sys.argv[1]=='known':known()
    else:
        tag=sys.argv[1];total=[0,0,0];signs=Path(tag+'.signs').read_text().splitlines()
        for index in range(len(signs)):
            for axis,value in enumerate(verify(tag,index)):total[axis]+=value
        print(tag,'rebound signings/masks/pairs/possibly open',len(signs),*total,flush=True)
