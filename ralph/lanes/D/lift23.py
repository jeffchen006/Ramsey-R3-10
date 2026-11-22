import json
import os
import sys
from pathlib import Path

from closure22 import ROOT,digest,stage
from twins23 import HARD,data,join,sides,build


def shift(source,dest,old,delta):
    def move(value):return (1 if value>=0 else -1)*(abs(value)+delta) if abs(value)>old else value
    with source.open() as inp,dest.open('w') as out:
        for line in inp:
            fields=line.split();ident=int(fields[0]);assert ident>=old
            if fields[1]=='d':preamble=[ident+delta,'d'];hints=fields[2:]
            else:
                border=fields.index('0',1)+1;preamble=[ident+delta,*fields[1:border]];hints=fields[border:]
            print(*preamble,*(move(int(value)) for value in hints),file=out)


def checks():return [('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],0,'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],0,'s VERIFIED UNSAT')]


def control():
    Path('old').write_text('4 1 0 1 2 0\n4 d 1 2 0\n5 0 4 3 0\n');shift(Path('old'),Path('proof.lrat'),3,1)
    Path('input.cnf').write_text('p cnf 3 4\n1 2 0\n1 -2 0\n-1 0\n3 0\n');assert all(stage(name,cmd,45,8000000,rc,marker)['ok'] for name,cmd,rc,marker in checks())
    Path('input.cnf').write_text('p cnf 3 4\n1 2 0\n1 -2 0\n1 0\n3 0\n');bad=[stage('bad'+name,cmd,45,8000000,rc,marker)['ok'] for name,cmd,rc,marker in checks()];assert not bad[1] and not all(bad);print('lifted learnt reference/deletion passed; changed parent dual-rejected; individual checker accepts:',bad)


def bind(token,cards):
    key,head=token.split('-');raw=list(map(int,cards.read_text().splitlines()));right=[-mask for mask in raw if mask<0];left=[mask for mask in raw if mask>0];params=sides(key,[int(head)]);rows,_,_=data(key)
    base,_=build(key,[],'reverse',[-mask for mask in right]);bound,_=join(rows,[params[1],params[0]],14,9,[right,left]);length=len(base.clauses);assert bound.clauses[:length]==base.clauses
    return base,bound,length,len(bound.clauses)-length


def run(token):
    key,head=token.split('-');source=HARD/f'{key}-reverse';previous=json.loads((source/'progress.json').read_text());assert previous['status']=='dual_checked';folder=HARD/'lift'/token;folder.mkdir(parents=True);os.chdir(folder)
    raw=(source/'cards').read_text().splitlines();assert all(int(mask)<0 for mask in raw);raw.extend(mask for mask in (HARD/token/'cards').read_text().splitlines() if int(mask)>0);Path('cards').write_text('\n'.join(raw)+'\n');base,bound,length,delta=bind(token,Path('cards'));base.to_file('base.cnf');assert digest('base.cnf')==previous['files']['input.cnf']['sha256'];bound.to_file('input.cnf');log=[]
    for name,cmd,rc,marker in [('extract',['zstd','-dq',source/'proof.zst','-o','base.lrat'],0,None),('lift',[sys.executable,'-B',Path(__file__).resolve(),'shift',length,delta],0,None),*checks(),('compress',['zstd','--single-thread','-4','-q','proof.lrat','-o','proof.zst'],0,None),('roundtrip',['zstd','-tq','proof.zst'],0,None)]:
        step=stage(name,cmd,120,138000000,rc,marker);log.append(step);assert step['ok'],step
        if name=='extract':assert digest('base.lrat')==previous['files']['proof.lrat']['sha256']
    files={name:{'size':Path(name).stat().st_size,'sha256':digest(name)} for name in ('cards','input.cnf','proof.lrat','proof.zst')};(folder/'progress.json').write_text(json.dumps(dict(host=token,head=[],status='dual_checked',parent=previous['files']['proof.lrat']['sha256'],extra_inputs=delta,log=log,files=files),sort_keys=True)+'\n');
    for name in ('base.cnf','base.lrat','input.cnf','proof.lrat'):Path(name).unlink()
    print(token,'lift dual success',length,delta,files['proof.zst'])


if __name__=='__main__':
    if sys.argv[1]=='control':control()
    elif sys.argv[1]=='shift':shift(Path('base.lrat'),Path('proof.lrat'),*map(int,sys.argv[2:]))
    else:run(sys.argv[1])
