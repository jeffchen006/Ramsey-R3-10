"""Guard disjoint certified physical CNFs and lift their LRAT steps with the same guard."""
from pathlib import Path
import subprocess
import sys

from orbit_extend import ROOT


def translate(literal,offset):return (offset+abs(literal))*(1 if literal>0 else -1)


def merge(files,stem):
    variables=len(files);clauses=1;entries=[]
    for index,source in enumerate(files,1):
        with source.with_suffix('.cnf').open() as src:magic,fmt,rawvars,rawclauses=src.readline().split()
        assert magic=='p' and fmt=='cnf';items=int(rawclauses)
        entries.append((index,source,variables,clauses,items));variables+=int(rawvars);clauses+=items
    with stem.with_suffix('.cnf').open('w') as dest:
        print('p cnf',variables,clauses,file=dest);print(*range(1,len(files)+1),0,file=dest)
        for guard,source,offset,_,items in entries:
            with source.with_suffix('.cnf').open() as src:
                src.readline();count=0
                for line in src:
                    *clause,end=map(int,line.split());assert end==0;print(*(translate(literal,offset) for literal in clause),-guard,0,file=dest);count+=1
                assert count==items
    final=clauses;units=[]
    with stem.with_suffix('.lrat').open('w') as dest:
        for guard,source,offset,start,items in entries:
            proofmap={};lastempty=None
            def newid(old):
                if old<0:return -newid(-old)
                assert old>0
                return start+old if old<=items else proofmap[old]
            for line in source.with_suffix('.lrat').read_text().splitlines():
                tokens=line.split();old=int(tokens[0]);assert tokens[-1]=='0'
                if tokens[1]=='d':
                    print(final,'d',*(newid(int(item)) for item in tokens[2:-1]),0,file=dest);continue
                sep=tokens.index('0');clause=list(map(int,tokens[1:sep]));hints=list(map(int,tokens[sep+1:-1]));final+=1
                print(final,*(translate(literal,offset) for literal in clause),-guard,0,*(newid(item) for item in hints),0,file=dest);proofmap[old]=final
                if not clause:assert lastempty is None;lastempty=final
            assert lastempty is not None;units.append(lastempty)
        print(final+1,0,*units,1,0,file=dest)
    print('OR',len(files),'variables',variables,'clauses',clauses,'end',final+1,flush=True)


def checks(stem):
    for name,args,expect in [('lrat-check',[],'c VERIFIED'),('cake_lpr',['--CML_HEAP_SIZE=1024','--CML_STACK_SIZE=64'],'s VERIFIED UNSAT')]:
        result=subprocess.run([ROOT/'opt/bin'/name,*args,stem.with_suffix('.cnf'),stem.with_suffix('.lrat')],capture_output=True,text=True)
        Path(str(stem)+'.'+name+'.log').write_text(result.stdout+result.stderr);assert result.returncode==0 and expect in result.stdout.splitlines(),(name,result.returncode,result.stdout[-300:]);print(name,expect,flush=True)


def main(mode):
    feet=sorted(int(line.split()[0]) for line in Path('feet.request').read_text().splitlines());assert len(feet)==len(set(feet))==1406
    if mode=='strong':feet=sorted(feet+[int(line.split()[0]) for line in Path('eight.request').read_text().splitlines()]);assert len(feet)==len(set(feet))==2623
    if mode=='pilot':feet=feet[::109]
    stem=Path('id8_'+mode);merge([Path('no_blind_pole')]+[Path('bank')/f'f{foot}' for foot in feet],stem);checks(stem)


if __name__=='__main__':main(sys.argv[1])
