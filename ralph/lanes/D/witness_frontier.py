"""Independent labelled-cell check of the witness frontier and matched timing receipts."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import sys


def raw_children(graph, fixed, needed):
    if not needed:
        yield (fixed, *graph)
        return
    pivot,*rest=needed
    sites=defaultdict(list)
    for point,star in enumerate(graph):
        if not fixed>>point&1 and point!=pivot and not (graph[pivot]&star):sites[fixed&star].append(point)
    base=graph[pivot];target=graph[0].bit_count();cells=list(sites.values());suffix=[0]*(len(cells)+1)
    for rank in reversed(range(len(cells))):suffix[rank]=suffix[rank+1]+len(cells[rank])
    def assign(rank,row,need):
        if need>suffix[rank]:return
        if not need:
            for point,star in enumerate(graph):
                if not fixed>>point&1:continue
                common=(row&star).bit_count()
                if (row>>point&1 and common) or (not row>>point&1 and not 1<=common<=3):return
            child=graph.copy();child[pivot]=row
            for point in range(len(graph)):
                if row>>point&1:child[point]|=1<<pivot
            yield from raw_children(child,fixed|(1<<pivot),rest)
        else:
            cell=cells[rank]
            for used in range(min(len(cell),need)+1):
                yield from assign(rank+1,row,need-used)
                if used<len(cell):row|=1<<cell[used]
    yield from assign(0,base,target-base.bit_count())


def summary(dest):
    older=dest.parent/'ind10';allroots=(older/'four-40.in').read_text().splitlines();roots=(older/'four-open-live.in').read_text().splitlines()
    batches=[];batch=[]
    for row in (dest/'all3840.out').read_text().splitlines():
        if row.startswith('child '):batch.append(tuple(map(int,row.split()[1:])))
        else:
            assert int(row.split()[0])==len(batches);batches.append(batch);batch=[]
    assert len(batches)==len(roots)==117 and not batch
    modes=[0,256,768,4864,1280,1792];outputs=[[row.split() for row in (dest/f'all{mode}.out').read_text().splitlines()] for mode in modes]
    table=defaultdict(Counter);lines=['ordinal\troot_sha256\tshape\tw0\tw1\traw\tretained\t'+ '\t'.join('verdict_nodes_cpu_'+str(mode) for mode in modes)]
    for rank,(text,actual) in enumerate(zip(roots,batches,strict=True)):
        _,*graph=map(int,text.split());witnesses=[(graph[idx]&graph[idx+1]).bit_length()-1 for idx in (0,2)]
        expected=set(raw_children(graph,15,sorted(set(witnesses)-set(range(4)))))
        assert len(set(actual))==len(actual) and set(actual)<=expected
        shape=sum(1<<idx for idx,(first,last) in enumerate(((0,2),(0,3),(1,2),(1,3))) if graph[first]>>last&1)
        counts=table[shape];counts.update(roots=1,raw=len(expected),retained=len(actual),shared=int(witnesses[0]==witnesses[1]),internal=sum(point<4 for point in witnesses))
        fields=[]
        for mode,out in zip(modes,outputs):
            ordinal,status,nodes,cpu=out[rank];assert int(ordinal)==rank
            counts[f'cpu{mode}']+=float(cpu);counts[f'exhaust{mode}']+=status=='0';fields.append(','.join([status,nodes,cpu]))
        lines.append('\t'.join(map(str,(allroots.index(text),sha256(text.encode()).hexdigest(),shape,*witnesses,len(expected),len(actual),*fields))))
    (dest/'frontier.tsv').write_text('\n'.join(lines)+'\n')
    for shape,counts in sorted(table.items()):print(shape,dict(counts))
    print('total',dict(sum(table.values(),Counter())))


if __name__=='__main__':summary(Path(sys.argv[1]))
