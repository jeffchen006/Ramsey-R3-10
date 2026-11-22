from itertools import combinations
from pathlib import Path
import gzip,struct,sys,subprocess,resource,json
from pysat.solvers import Minisat22
from exception_fixed import barriers,block,write_cnf,attach,maskbits
from exception_cover import verify_lrat
from cyclic_proof import proof
from orbit_extend import ROOT,parse_graph6,independent_sets,to_graph6

def instance(tag):
    if tag=='plant':
        full=parse_graph6(Path('../sixplant12.g6').read_text().strip());return [(row&63)|1<<(index^1) for index,row in enumerate(full[:6])],5
    if tag=='small':return [6,9,9,6],4
    short=tag.startswith('old32_');key=int(tag.split('_')[-1]);table=[tuple(map(int,line.split())) for line in Path('../columns.tsv').read_text().splitlines()];base=[1<<(index^1) for index in range(34)]
    for left,right,expr in table:
        same=(key&expr).bit_count()%2
        for src in (2*left,2*left+1):
            dst=2*right+((src%2) if same else 1-(src%2));base[src]|=1<<dst;base[dst]|=1<<src
    return ([row% (1<<32) for row in base[:32]] if short else base),10
def masks(tag):
    board,target=instance(tag);n=len(board);stem=Path(tag);clauses=barriers(board,target);deck=[];found=[];cached={};all_old=(1<<n)-1
    with Minisat22(bootstrap_with=clauses) as solver:
        while solver.solve():
            contact=sum(1<<(literal-1) for literal in solver.get_model() if literal>0);holes=contact&(contact>>1)&(all_old//3)
            if holes not in cached:
                core=[row&~(1<<(index^1)) if holes>>(index&~1)&1 else row for index,row in enumerate(board)];cached[holes]=next(independent_sets(core,all_old,target),0)
            witness=cached[holes]
            if witness:
                doubles=witness&(witness>>1)&(all_old//3);assert doubles and not doubles&~holes;clause=[-index-1 for index in maskbits(doubles|doubles<<1)];assert clause not in deck;deck.append(clause)
            else:found.append(contact);clause=block(n,contact)
            solver.add_clause(clause)
    positive=sorted(found);assert len(positive)==len(set(positive));stem.with_suffix('.masks').write_text(''.join(f'{value}\n' for value in positive));stem.with_suffix('.cores').write_text(''.join(f'{witness}\n' for witness in sorted({witness for witness in cached.values() if witness})));write_cnf(stem,n,clauses+deck+[block(n,contact) for contact in positive]);assert proof(stem)=='dual'
    if tag in ('plant','small'):
        literal=[]
        for contact in range(1<<n):
            full=attach(board,[contact]);
            if any(full[left]&full[right] for left,right in combinations(range(n+1),2) if full[left]>>right&1):continue
            if not any(all(not(full[left]>>right&1) for left,right in combinations(group,2)) for group in combinations(range(n+1),target)):literal.append(contact)
        assert positive==literal
    print(tag,'complete mask list',len(positive),'hole obstructions',len(deck),'dual; literal for small controls',flush=True)
def pair_tables(tag):
    graph,target=instance(tag);masks=list(map(int,Path(tag+'.masks').read_text().split()));args=' '.join(map(str,(len(graph),target,len(masks),*graph,*masks)))+'\n'
    with open(tag+'.pairs','wb') as raw:run=subprocess.run(['timeout','150','prlimit','--cpu=130:132','--','./relations'],input=args.encode(),stdout=raw,stderr=subprocess.PIPE,check=True)
    Path(tag+'.relation').write_bytes(run.stderr);path=Path(tag+'.pairs');data=path.read_bytes();packed=gzip.compress(data,compresslevel=5,mtime=0);assert gzip.decompress(packed)==data;path.with_suffix('.pairs.gz').write_bytes(packed);path.unlink()
def bind(tag,maskonly=False):
    board,target=instance(tag);n=len(board);universe=(1<<n)-1;contacts=list(map(int,Path(tag+'.masks').read_text().split()));assert all(0<=value<=universe for value in contacts) and sorted(set(contacts))==contacts;nogo=set(contacts);witnesses=list(map(int,Path(tag+'.cores').read_text().split()));bad=set()
    for witness in witnesses:
        old=maskbits(witness);assert max(old)<n and len(old)==target and all((left^1)==right or not board[left]>>right&1 for left,right in combinations(old,2));doubles={site for site in old if (site^1) in old};assert doubles;bad.add(tuple(sorted(-site-1 for site in doubles)))
    lines=Path(tag+'.cnf').read_text().splitlines();assert lines.pop(0)==f'p cnf {n} {len(lines)}'
    for line in lines:
        *literals,end=map(int,line.split());assert end==0
        if len(literals)==n and set(map(abs,literals))==set(range(1,n+1)) and sum(1<<(-lit-1) for lit in literals if lit<0) in nogo:nogo.remove(sum(1<<(-lit-1) for lit in literals if lit<0));continue
        if all(lit>0 for lit in literals):
            points=[lit-1 for lit in literals];assert len(set(points))==len(points)==target-1 and all(0<=site<n for site in points) and not any(board[src]>>dest&1 for src,dest in combinations(points,2));continue
        if len(literals)==2 and all(lit<0 for lit in literals):
            left,right=sorted(-lit-1 for lit in literals)
            if 0<=left<right<n and (left^1)!=right and board[left]>>right&1:continue
        assert tuple(sorted(literals)) in bad
    assert not nogo;verify_lrat(Path(tag));size=len(contacts)
    if maskonly:print(tag,'rebound mask cover',size,'dual',flush=True);return
    allowed=[set() for _ in range(size)];compiled={};cursor=0;data=gzip.decompress(Path(tag+'.pairs.gz').read_bytes())
    def check(indices):
        nonlocal cursor
        witness=struct.unpack_from('<Q',data,cursor)[0];cursor+=8
        if not witness:return False
        if witness not in compiled:
            old=[vertex for vertex in range(n) if witness>>vertex&1];assert witness.bit_count()==target;doubles=0
            for left,right in combinations(old,2):
                if (left^1)==right:doubles|=1<<left
                else:assert not board[left]>>right&1
            compiled[witness]=(doubles,witness&universe,witness>>n)
        doubles,old,outer=compiled[witness];assert outer<1<<len(indices);forced=0
        for pos,index in enumerate(indices):
            contact=contacts[index];forced|=contact&(contact>>1)&(universe//3);assert not(outer>>pos&1 and old&contact)
        assert not doubles&~forced;return True
    for left in range(size):
        for right in range(left,size):
            if not check((left,right)):allowed[left].add(right)
    candidates=open_count=0;planted=set();
    for left in range(size):
        for right in sorted(allowed[left]):
            for third in sorted(allowed[left]&allowed[right]):
                candidates+=1
                if not check((left,right,third)):
                    open_count+=1
                    if tag=='plant':planted.add(tuple(contacts[index] for index in (left,right,third)))
    assert cursor==len(data)
    if tag=='plant':
        actual=parse_graph6(Path('../sixplant12.g6').read_text().strip());six=actual[n:];assert all((contact&universe) in contacts for contact in six);triples=list(combinations(range(6),3));plants={tuple(sorted(six[vertex]&universe for vertex in group)) for group in triples if not any(six[left]>>(n+right)&1 for left,right in combinations(group,2))};assert plants and plants<=planted
    print(tag,'list',size,'all unordered pairs',size*(size+1)//2,'supergraph edges',sum(map(len,allowed)),'triples tested',candidates,'unrefuted',open_count,'physical witness masks',len(compiled),flush=True)
    if tag not in ('plant','small'):assert not open_count
if __name__=='__main__':
    for action in sys.argv[2:]:{'masks':masks,'pairs':pair_tables,'bind':bind,'maskbind':lambda tag:bind(tag,True)}[action](sys.argv[1])
