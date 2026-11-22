"""Bind mixed-centre placements, C6 profiles and pentagon proof semantics."""
from collections import Counter
from itertools import combinations,permutations
from pathlib import Path
import sys
from kernel_cnf import ROOT,decode
from path_growth import fixed_graph,read_profiles
from punct_path import profile_key
from defect_triangle import canonical


def check_placements(folder):
    expected=(folder/'trans/hub.tsv').read_text().splitlines();labels=(folder/'trans/hub.ids').read_text().splitlines();found=set()
    for idx,record in enumerate(read_profiles(folder.parent/'punct8/path.tsv')):
        graph=fixed_graph(record);pins=(4,0,1,7,2,5,3,6);masks=[sum(1<<pos for pos,site in enumerate(pins) if row>>site&1) for row in graph];hist=Counter(masks[8:])
        key=' '.join(f'{mask}:{size}' for mask,size in sorted(hist.items()));flags=[]
        for first,second in combinations(pins,2):
            common=graph[first]&graph[second]
            if common.bit_count()==1:flags.append({first,second,common.bit_length()-1})
        for site in range(len(graph)):
            if any(site not in flag for flag in flags):continue
            pos=pins.index(site) if site in pins else 8+sum(count for mask,count in hist.items() if mask<masks[site]);found.add((f'{idx} {pos}',f'{1<<pos} {key}'))
    assert len(found)==len(expected)==28447 and found==set(zip(labels,expected,strict=True));print('PASS original graph order, all 2434*40 physical hit-all marks, equal 28447 exact bound source rows')


def check_pendant(folder):
    fixed=[set() for point in range(6)]
    for first in range(3):
        for second in range(3):
            if first!=second:fixed[first].add(3+second);fixed[3+second].add(first)
    pairs=list(combinations(range(6),2));defect={(0,1),(0,2),(1,2),(0,3)}
    low={pair:(1 if pair in defect else 2)-len(fixed[pair[0]]&fixed[pair[1]]) for pair in pairs if pair[1] not in fixed[pair[0]]};up={pair:(1 if pair in defect else 3)-len(fixed[pair[0]]&fixed[pair[1]]) for pair in low};deg=[7]*6
    blocks=[tuple(sub) for count in (6,5,4,3,2) for sub in combinations(range(6),count) if all(up.get(pair,0)>0 for pair in combinations(sub,2))];keys=set();rows=Counter();labelled=0
    def visit(idx,slots):
        nonlocal labelled
        if idx==len(blocks):
            if sum(deg)>slots or max(low.values())>0:return
            full=rows.copy();full[0]=slots-sum(deg)
            for site,count in enumerate(deg):full[1<<site]=count
            labelled+=1;keys.add(canonical(profile_key(+full)));return
        sub=blocks[idx];uses=list(combinations(sub,2));mask=sum(1<<point for point in sub)
        for num in range(min([slots,*[deg[v] for v in sub],*[up[p] for p in uses]])+1):
            rows[mask]=num
            for point in sub:deg[point]-=num
            for pair in uses:low[pair]-=num;up[pair]-=num
            visit(idx+1,slots-num)
            for point in sub:deg[point]+=num
            for pair in uses:low[pair]+=num;up[pair]+=num
        del rows[mask]
    visit(0,34);actual=set()
    for line in (folder/'pendant/c40.in').read_text().splitlines():
        values=list(map(int,line.split()));assert values[0]==63;graph=values[1:41];weak=values[41:];assert all(((graph[first]&graph[second]).bit_count()==1)==bool(weak[first]>>second&1) for first,second in pairs)
        actual.add(canonical(profile_key(Counter(graph[6:]))))
    assert keys==actual and len(actual)==42;print('PASS C6 direct unrestricted mask recursion, designated opposite, labelled',labelled,'same 42 keys')


if __name__=='__main__':
    folder=Path(sys.argv[1]);check_placements(folder);check_pendant(folder)
