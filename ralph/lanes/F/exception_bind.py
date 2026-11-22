"""From site incidences and physical masks, reconstruct proof inputs independently."""
from itertools import combinations
from pathlib import Path
import gzip
import shutil
import subprocess
import sys
from cyclic_check import check,read_base,rank
from orbit_extend import ROOT,parse_graph6

def reference(tag):
    if tag in ('plainpos','plainneg'):
        ordinary=[{1},{0,2},{1}] if tag=='plainpos' else [{1,2},{0,2},{0,1}]
        hits={0,2} if tag=='plainpos' else set()
        return [[int(left==right or (right in ordinary[left] if max(left,right)<3 else min(left,right) in hits)) for right in range(4)] for left in range(4)],4
    if tag.startswith('control'):
        sites=(1,3,4,2);size=4;target=4 if tag=='controlneg' else 5
        return [[sum((a-b)%13 in {1,5,8,12} for b in ((-c,) if a==c else (c,-c))) for c in sites] for a in sites],target
    occupied,full=map(int,tag.split('_'));assert full&~occupied==0
    board=[[0]*18 for _ in range(18)]
    for site in range(17):
        neighbors=([0,1] if full&(1<<site) else [0] if occupied&(1<<site) else [])
        board[-1][site]=board[site][-1]=len(neighbors)
        board[site][site]=int(len(neighbors)<2)
        for nbr in range(site):board[site][nbr]=board[nbr][site]=int(site-12<=nbr<=site-6)
    board[-1][-1]=int(not full)
    assert all(not board[a][b] for a in range(17) for b in range(17) if a!=b and board[a][-1]==2 and board[b][-1])
    return board,10

def cardbind(tag,graph,board,extra=0,optional=False):
    assert len(graph)==2*len(board)+extra
    for site,row in enumerate(board):
        for nbr,value in enumerate(row):
            for bit in (0,1):
                neighbors=(graph[2*site+bit]>>(2*nbr))&3
                if site==nbr and optional:assert neighbors.bit_count()<=value
                else:assert neighbors.bit_count()==value
                assert ((neighbors&1)<<1|(neighbors>>1))==((graph[2*site+(1-bit)]>>(2*nbr))&3)

def unpack(stem, suffix):
    path=stem.with_suffix(suffix); packed=stem.with_suffix(suffix+'.gz')
    if not path.exists():
        with gzip.open(packed,'rb') as stream,path.open('wb') as out:shutil.copyfileobj(stream,out)
    return path

def bind(tag,extra,pack=False):
    board,target=reference(tag);sites=len(board);core=2*sites;order=core+extra;stem=Path(f'{tag}-p{extra}');status=stem.with_suffix('.status').read_text().split()[2]
    if status=='card':
        cardbind(tag,parse_graph6(stem.with_suffix('.g6').read_text().strip()),board,extra,True);return 'card'
    assert status=='dual';ids={};terms={};base=[];boundary=[];seen=set()
    for edge in combinations(range(order),2):
        a,b=edge;left,right=a//2,b//2
        if b>=core:key=('outside',edge)
        elif left==right:key=('vertical',left) if board[left][right] else None
        elif board[left][right]==2:key=True
        elif board[left][right]==0:key=None
        else:key=('matching',left,right)
        if key is None or key is True:terms[edge]=key;continue
        if key not in ids:
            ids[key]=1+len(ids)
            if key[0]=='matching':
                incidence=(1<<left)|(1<<right)
                if rank(boundary+[incidence])>len(boundary):base.append((-ids[key],));boundary.append(incidence)
        terms[edge]=ids[key]*(-1 if key[0]=='matching' and a%2==b%2 else 1)
    def emit(group,triangle):
        points=list(combinations(group,2)); assert len(group)==(3 if triangle else target)
        if any(terms[edge] is (None if triangle else True) for edge in points):return
        clause={(-1 if triangle else 1)*terms[edge] for edge in points if type(terms[edge]) is int}
        if any(-term in clause for term in clause):return
        key=tuple(sorted(clause,key=abs))
        if key not in seen:base.append(key);seen.add(key)
    for triple in combinations(range(order),3):emit(triple,True)
    deck=unpack(stem,'.deck');lrat=unpack(stem,'.lrat')
    for entry in deck.read_text().splitlines():
        mask=int(entry);assert 0<=mask<1<<order
        emit([vertex for vertex in range(order) if mask>>vertex&1],False)
    count=len(ids)
    if () in base:count+=1;base=[row for row in base if row]+[(count,),(-count,)]
    data=(f'p cnf {count} {len(base)}\n'+''.join(' '.join(map(str,(*row,0)))+'\n' for row in base)).encode()
    cnf=stem.with_suffix('.cnf');rebound=stem.with_suffix('.rebuilt');rebound.write_bytes(data)
    if cnf.exists():assert cnf.read_bytes()==data
    for name,flags,expected in [('lrat-check',[],b'c VERIFIED'),('cake_lpr',['--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32'],b's VERIFIED UNSAT')]:
        run=subprocess.run(['timeout','35','prlimit','--cpu=25:27','--',ROOT/'opt/bin'/name,*flags,rebound,lrat],capture_output=True)
        assert run.returncode==0 and expected in run.stdout.splitlines(),(name,run.returncode)
    if pack:
        for path in (deck,lrat):
            packed=path.with_suffix(path.suffix+'.gz')
            if not packed.exists():
                packed.write_bytes(gzip.compress(path.read_bytes(),compresslevel=4,mtime=0))
            assert gzip.decompress(packed.read_bytes())==path.read_bytes();path.unlink()
        cnf.unlink(missing_ok=True)
    rebound.unlink();return 'rebound'

def bare(tag):
    stem=Path(tag);board,target=reference(tag);text=stem.with_suffix('.q').read_text().strip();assert read_base(text)==board
    status=stem.with_suffix('.status').read_text().split()[1]
    if status=='cert':assert check(text,target,stem)>0
    else:assert status=='card';cardbind(tag,parse_graph6(stem.with_suffix('.g6').read_text().strip()),board)
    return status

if __name__=='__main__':
    if sys.argv[1]=='bare':print(bare(sys.argv[2]))
    else:print(bind(sys.argv[1],int(sys.argv[2]),'pack' in sys.argv))
