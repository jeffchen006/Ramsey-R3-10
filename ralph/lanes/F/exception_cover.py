"""Independent, proof-producing signing cover from physical singleton supports."""
from itertools import combinations,product
from pathlib import Path
import subprocess
import sys
from cyclic_check import rank
from cyclic_proof import proof
from exception_bind import reference,cardbind
from orbit_extend import ROOT,parse_graph6

def verify_lrat(stem):
    for tool,flags,result in [('lrat-check',[],b'c VERIFIED'),('cake_lpr',['--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32'],b's VERIFIED UNSAT')]:
        run=subprocess.run(['timeout','35','prlimit','--cpu=25:27','--',ROOT/'opt/bin'/tool,*flags,stem.with_suffix('.cnf'),stem.with_suffix('.lrat')],capture_output=True)
        assert run.returncode==0 and result in run.stdout.splitlines(),(stem,tool)

def generate(tag,create):
    base,target=reference(tag);size=len(base);edges=[pair for pair in combinations(range(size),2) if base[pair[0]][pair[1]]==1]
    assert all(base[site][site]==1 and max(base[site])==1 for site in range(size));clauses=[];ids={edge:serial+1 for serial,edge in enumerate(edges)};basis=[]
    for edge,symbol in ids.items():
        boundary=sum(1<<site for site in edge)
        if rank(basis+[boundary])>len(basis):basis.append(boundary);clauses.append([-symbol])
    for triple in combinations(range(size),3):
        pairs=list(combinations(triple,2))
        if all(pair in ids for pair in pairs):
            for bits in product((0,1),repeat=3):
                if sum(bits)%2:clauses.append([ids[pair]*(-1 if bit else 1) for pair,bit in zip(pairs,bits)])
    fields=[line.split() for line in Path(tag+'.trace').read_text().splitlines()];supports=sorted({int(row[2]) for row in fields if row[0]=='cut' and row[1]=='0'})
    assert supports and all(mask.bit_count()==target and mask<1<<size for mask in supports)
    varcount=len(ids);memo={}
    def xor(letters):
        nonlocal varcount
        if len(letters)==1:return letters[0]
        if letters not in memo:
            left=xor(letters[:-1]);right=letters[-1];varcount+=1;symbol=varcount;memo[letters]=symbol
            for first,second in product((False,True),repeat=2):clauses.append([left*(-1 if first else 1),right*(-1 if second else 1),symbol*(1 if first!=second else -1)])
        return memo[letters]
    for mask in supports:
        pivots={};cycles=[]
        for (left,right),symbol in ids.items():
            if not(mask>>left&mask>>right&1):continue
            incidence=(1<<left)|(1<<right);word=1<<(symbol-1)
            while incidence and incidence.bit_length() in pivots:
                pivot,expression=pivots[incidence.bit_length()];incidence^=pivot;word^=expression
            if incidence:pivots[incidence.bit_length()]=(incidence,word)
            else:
                letters=tuple(index for index in ids.values() if word>>(index-1)&1);assert letters;cycles.append(xor(letters))
        assert cycles;clauses.append(cycles)
    signatures=set()
    for line in Path(tag+'.signs').read_text().splitlines():
        raw,text=line.split();graph=parse_graph6(text);cardbind(tag,graph,base);sign=int(raw)
        literal_sign=sum((1<<(symbol-1)) for (left,right),symbol in ids.items() if not graph[2*left]>>(2*right+1)&1)
        # For nonedge parity 1, the edges have equal endpoint bits.
        assert sign==literal_sign and sign not in signatures
        assert all(not(graph[left]&graph[right]) for left,right in combinations(range(len(graph)),2) if graph[left]>>right&1)
        signatures.add(sign);clauses.append([-symbol if sign>>(symbol-1)&1 else symbol for symbol in ids.values()])
    stem=Path(tag+'-cover');data=(f'p cnf {varcount} {len(clauses)}\n'+''.join(' '.join(map(str,(*clause,0)))+'\n' for clause in clauses)).encode()
    if create:stem.with_suffix('.cnf').write_bytes(data);assert proof(stem)=='dual'
    assert stem.with_suffix('.cnf').read_bytes()==data;verify_lrat(stem);print(tag,'cover',len(signatures),len(supports),varcount,len(clauses),flush=True)

if __name__=='__main__':generate(sys.argv[1],sys.argv[2]=='create')
