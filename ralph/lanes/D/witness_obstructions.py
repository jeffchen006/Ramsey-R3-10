"""Certificates for completed witness stars, without using target-global defect quotas."""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import sys
from kernel_cnf import Cnf
from witness_frontier import raw_children


def independent(upper,room,need):
    if not need:return []
    while room.bit_count()>=need:
        bit=room&-room;room^=bit;point=bit.bit_length()-1;tail=independent(upper,room&~upper[point],need-1)
        if tail is not None:return [point,*tail]
    return None


def prove(child,size):
    fixed,*graph=child;order=len(graph);upper=[mask for mask in graph];pins={}
    for left,right in combinations(range(order),2):
        if fixed & ((1<<left)|(1<<right)):pins[left,right]=bool(graph[left]>>right&1)
        elif not graph[left]&graph[right]&fixed:upper[left]|=1<<right;upper[right]|=1<<left
    witness=independent(upper,(1<<order)-1,size)
    if witness is None:return None
    formula=Cnf(order,pins);edges=[];why=[]
    for left,right in combinations(witness,2):
        edge=formula.edge(left,right,False);edges.append(edge)
        if (left,right) in pins:assert not pins[left,right];why.append('-')
        else:
            common=graph[left]&graph[right]&fixed;vertex=(common&-common).bit_length()-1;assert vertex>=0
            formula.add(-formula.edge(left,vertex,False),-formula.edge(right,vertex,False),-edge);why.append(str(vertex))
    formula.add(*edges);return formula,witness,why


def main(dest):
    old=dest.parent/'ind10';roots=(old/'four-40.in').read_text().splitlines();live=(old/'four-open-live.in').read_text().splitlines();directory=dest/'branch-cert';directory.mkdir(exist_ok=True)
    kept=[];group=set()
    for line in (dest/'all3840.out').read_text().splitlines():
        if line.startswith('child '):group.add(tuple(map(int,line.split()[1:])))
        else:kept.append(group);group=set()
    proofs=[];remaining=[]
    for rank,text in enumerate(live):
        fixed,*graph=map(int,text.split());witnesses=sorted({(graph[point]&graph[point+1]).bit_length()-1 for point in (0,2)}-set(range(4)))
        missing=sorted(set(raw_children(graph,fixed,witnesses))-kept[rank]);ordinal=roots.index(text)
        for idx,child in enumerate(missing):
            tag=f'{ordinal:03}-{idx:04}';material=' '.join(map(str,child));result=prove(child,10)
            if not result:remaining.append(tag+' '+material);continue
            form,sites,why=result;path=directory/(tag+'.cnf');form.write(path);proofs.append('\t'.join((tag,sha256(material.encode()).hexdigest(),','.join(map(str,sites)),','.join(why),sha256(path.read_bytes()).hexdigest())))
    (directory/'witnesses.tsv').write_text('\n'.join(proofs)+'\n');(directory/'others.in').write_text('\n'.join(remaining)+'\n');print('raw-minus-retained',len(remaining)+len(proofs),'direct anchored I10',len(proofs),'other',len(remaining))


if __name__=='__main__':main(Path(sys.argv[1]).resolve())
