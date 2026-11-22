"""Direct ten-set witnesses and ordinary triangle clauses; no search-sensitive lemmas."""
import argparse
from hashlib import sha256
from itertools import combinations
from pathlib import Path

from kernel_cnf import Cnf
from path_growth import bits


def witness(graph,size):
    order=len(graph);upper=[]
    for first,row in enumerate(graph):upper.append(row if first<4 else row|sum(1<<second for second in range(4,order) if first!=second and not row&graph[second]))
    def pick(room,need):
        if not need:return []
        while room.bit_count()>=need:
            bit=room&-room;room^=bit;point=bit.bit_length()-1;tail=pick(room&~upper[point],need-1)
            if tail is not None:return [point,*tail]
        return None
    return pick((1<<order)-1,size)


def proof(graph,sites):
    order=len(graph);fixed={(a,b):bool(graph[a]>>b&1)for a,b in combinations(range(order),2)if a<4};form=Cnf(order,fixed);edges=[];witnesses=[]
    for a,b in combinations(sites,2):
        edge=form.edge(a,b,False);edges.append(edge)
        if a<4:assert not fixed[a,b];witnesses.append('-')
        else:
            shared=min(bits(graph[a]&graph[b]));assert shared<4 and fixed[shared,a] and fixed[shared,b];witnesses.append(str(shared));form.add(-form.edge(shared,a,False),-form.edge(shared,b,False),-edge)
    form.add(*edges);return form,witnesses


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('dest',type=Path);args=parser.parse_args();dest=args.dest;directory=dest/'four-certs';directory.mkdir(exist_ok=True)
    entries=[];hist={}
    for idx,(text,answer)in enumerate(zip((dest/'four-40.in').read_text().splitlines(),(dest/'four-open.out').read_text().splitlines(),strict=True)):
        graph=list(map(int,text.split()[1:]));sites=witness(graph,10);accepted=answer.split()[1]=='0';assert (sites is not None)==accepted
        if sites is not None:
            form,why=proof(graph,sites);target=directory/f'{idx:03}.cnf';form.write(target);entries.append('\t'.join([str(idx),sha256(text.encode()).hexdigest(),','.join(map(str,sites)),','.join(why),sha256(target.read_bytes()).hexdigest()]));hist[len(form.clauses)]=hist.get(len(form.clauses),0)+1
    assert len(entries)==78;(directory/'witnesses.tsv').write_text('ordinal\troot_sha256_no_LF\tvertices\t45_witnesses\tcnf_sha256\n'+'\n'.join(entries)+'\n');print('PASS 78/78 direct independent ten witnesses, 117 absence of this immediate blocker; clause histogram',hist)
