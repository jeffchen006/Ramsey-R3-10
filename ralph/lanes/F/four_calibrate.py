"""Literal physical calibration of unsigned one-pole footprints and mirror cut."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import json
import subprocess
import sys

from cyclic_base import matrix,profiles
from four_slot import put
from orbit_extend import ROOT,independent,independent_sets,parse_graph6,to_graph6
from relift_audit import decode,encode,explicit_lift


def footprint(mask,size):
    full=0;single=0
    for site in range(size):
        num=((mask>>(2*site))&3).bit_count()
        if num==2:full|=1<<site
        if num==1:single|=1<<site
    return full,single


def odd_control():
    graph=[0]*12
    for left,right in ((0,4),(4,5),(5,1),(1,8),(8,0),(2,6),(6,7),(7,3),(3,9),(9,2),(10,11)):
        graph[left]|=1<<right;graph[right]|=1<<left
    base=[[((graph[2*left]>>(2*right))&3).bit_count() for right in range(4)] for left in range(4)]
    assert all(base[left][right]==int((left-right)%4==2) for left,right in combinations(range(4),2))
    assert [base[site][site] for site in range(4)]==[0,0,1,1]
    for tag in ('yes','no'):
        if tag=='no':graph[0]^=1<<8;graph[8]^=1
        put(f'odd.{tag}.g6',[to_graph6(graph)])
        response=subprocess.check_output([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',f'odd.{tag}.g6','12','6'],text=True)
        assert json.loads(response)['graphs'][0]['ok']==(tag=='yes');Path(f'odd.{tag}.gate').write_text(response)
    print('explicit C5+C5+K2 control: old P4+P4, antipodal crossing degree one, vertical bits 0011; deletion of contact 0--8 introduces I6')


def main():
    orig=Path('small.q').read_text().strip();sources=[orig];count=Counter()
    for profile,_ in profiles(4,0,5):
        if profile[0]:continue
        for vertical in (0,1,5,15):
            if max(profile)==2 and vertical:continue
            base=matrix(4,profile)
            for site in range(4):base[site][site]=vertical>>site&1
            sources.append(encode(base))
    for number,text in enumerate(dict.fromkeys(sources)):
        base=decode(text);singles=sum(base[left][right]==1 for left,right in combinations(range(4),2))
        put('tmp.q',[text]);subprocess.run(['./columns','tmp.q','5','0','0','tmp.columns'],check=True,stdout=subprocess.DEVNULL)
        stages={(full,single):stage for full,single,_,stage in (map(int,line.split()) for line in Path('tmp.columns').read_text().splitlines())}
        count['inputs']+=1;count.update({f'stage{idx}':amount for idx,amount in Counter(stages.values()).items()})
        for flags in range(1<<singles):
            graph=explicit_lift(base,iter((flags>>pos)&1 for pos in range(singles)))
            if not all(independent(row,graph) for row in graph):continue
            count['signings']+=1
            for mask in range(256):
                if not independent(mask,graph) or mask.bit_count()>=5:continue
                key=footprint(mask,4);degree=mask.bit_count();assert key in stages
                strict=next(independent_sets(graph,255^mask,4),None) is None
                if strict:
                    assert stages[key]==3;count['positive placements']+=1
                    if degree==4:assert key[0];count['size-four mirror positives']+=1
                else:count['adverse placements']+=1
        if text==orig:
            physical=parse_graph6(Path('small.yes.g6').read_text().strip());assert all(stages[footprint(row&255,4)]==3 for row in physical[8:])
    assert all(count[key] for key in ('stage1','stage2','stage3','positive placements','adverse placements','size-four mirror positives'))
    print(sorted(count.items()))


if __name__=='__main__':main();odd_control()
