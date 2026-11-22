from pathlib import Path
import subprocess
import sys
from round20_census import load

def prep():
    rows=sorted(row for row in load('../../r21/mark.left') if row[1]);assert len(rows)==405
    outcomes={}
    for first,second,weight in rows:
        tag=f'{first}_{second}';fields=Path('../'+tag+'.status').read_text().split();assert fields[0]==tag and fields[1] in ('cert','card');outcomes[tag]=fields[1]
    survivors=[tag for tag in outcomes if outcomes[tag]=='card'];assert len(survivors)==131
    pilot={'4064_1088','10088_256'};assert pilot<=set(survivors)
    other=[tag for tag in survivors if tag not in pilot]
    for index in (0,1):Path(f'extra{index}.rows').write_text(''.join(tag+'\n' for tag in other[index::2]))
    print(len(rows),len(survivors),len(pilot),len(other))

def one(tag):
    lane=Path(__file__).parent;stem=Path(tag+'-p1');assert not stem.with_suffix('.status').exists()
    for step,argv in [('discovery',[lane/'exception_extend.py',tag,'1','200']),('bind',[lane/'exception_bind.py',tag,'1','pack'])]:
        with open(tag+'-'+step+'.log','w') as out:
            run=subprocess.run(['/usr/bin/time','-o',tag+'-'+step+'.time','-f','%U %S %M %x','timeout','90','prlimit','--cpu=75:80','--',sys.executable,'-B',*argv],stdout=out,stderr=subprocess.STDOUT)
        if run.returncode:print(tag,step,'open_exit',run.returncode,flush=True);return
    print(tag,stem.with_suffix('.status').read_text().strip(),'bound',flush=True)

def worker(index):
    for tag in Path(f'extra{index}.rows').read_text().split():
        if sum(entry.stat().st_size for entry in Path('..').rglob('*') if entry.is_file())>385_000_000:print('stage cap; pending IDs open',flush=True);break
        one(tag)

if __name__=='__main__':prep() if sys.argv[1]=='prepare' else worker(int(sys.argv[1]))
