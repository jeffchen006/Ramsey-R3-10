"""Direct graph-class comparison for four individualized stars, including tail nodes."""
from collections import defaultdict
from pathlib import Path
import sys

from defect_four import CROSS,PERMS,census,graph_key
from induced_pilot import ROOT
from path_growth import bits
from punct_path import decode,neighbors,pairs
from punctured import certificate


def main(dest,full=(),maximal=False):
    classes,_=census(22,6);indices={(shape,key):idx for idx,(shape,key)in enumerate((shape,key)for shape in sorted(classes)for key in sorted(classes[shape]))}
    expect=defaultdict(set)
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(text))
        if {len(row)for row in graph}!={6}or max(len(first&second)for first,second in pairs(graph))>3:continue
        low=[pair for pair in pairs(range(22))if len(graph[pair[0]]&graph[pair[1]])==1]
        scores=[sum(v in graph[u] for u in left for v in right) for left,right in pairs(low) if not (set(left)&set(right))]
        for left,right in pairs(low):
            if set(left)&set(right):continue
            if maximal and sum(v in graph[u] for u in left for v in right)!=max(scores):continue
            mark=left+right
            for perm in PERMS:
                core=tuple(mark[pos]for pos in perm);shape=sum(1<<idx for idx,(a,b)in enumerate(CROSS)if core[b]in graph[core[a]])
                index=indices.get((shape,graph_key(graph,core)))
                if index is not None:expect[index].add(certificate(graph,[[p] for p in core]+[sorted(set(range(22))-set(core))]))
    def audit(name,source):
        actual=defaultdict(set);capped=[];i=0;cpu=0
        for text in (dest/name).read_text().splitlines():
            words=text.split();index=source[i]
            if words[0]=='model':actual[index].add(certificate([set(bits(int(field)))for field in words[1:]],[[p] for p in range(4)]+[list(range(4,22))]))
            else:
                assert int(words[0])==i and int(words[1])in(-1,0);cpu+=float(words[3]);i+=1
                if words[1]=='-1':assert actual[index]<=expect[index];capped.append(index)
                else: assert actual[index]==expect[index],(index,len(actual[index]),len(expect[index]))
        assert i==len(source);print(name,i,'capped',len(capped),'CPU',round(cpu,3));return capped
    if full:
        for name in full:assert not audit(name,list(range(len(indices))))
    else:
        remaining=audit('four-cal.out',list(range(len(indices))));assert not audit('four-cal-tail.out',remaining)
    print('PASS complete four-star census across',len(indices),'profiles:',sum(bool(classes)for classes in expect.values()),'occupied,',sum(map(len,expect.values())),'individualized classes')


if __name__=='__main__':main(Path(sys.argv[1]),[name for name in sys.argv[2:] if name!='--maximal'],'--maximal' in sys.argv)
