from pathlib import Path
import subprocess
import sys
from round20_census import load

def prepare():
    rows=sorted(occupied for occupied,doubled,weight in load('../r21/mark.left') if not doubled)
    pilots={1728,4016,35910};assert len(rows)==263 and pilots=={rows[0],rows[len(rows)//2],rows[-1]}
    rest=[f'{occupied}_0' for occupied in rows if occupied not in pilots]
    for index in (0,1):Path(f'plain{index}.rows').write_text(''.join(tag+'\n' for tag in rest[index::2]))
    print('plain marked',len(rows),'pilots',len(pilots),'rest',len(rest),'no exterior roster')

def work(index):
    lane=Path(__file__).parent
    for tag in Path(f'plain{index}.rows').read_text().split():
        if sum(entry.stat().st_size for entry in Path('.').rglob('*') if entry.is_file())>380_000_000:print('reservation stop',flush=True);break
        assert not Path(tag+'.status').exists();terminal=False
        for directory,phase,argv in [('.','bare',[lane/'exception_sign.py',tag]),('.','bindbare',[lane/'exception_bind.py','bare',tag]),('ext','pole',[lane/'exception_extend.py',tag,'1','260']),('ext','bindpole',[lane/'exception_bind.py',tag,'1','pack'])]:
            with (Path(directory)/(tag+'-'+phase+'.log')).open('w') as out:
                run=subprocess.run(['/usr/bin/time','-o',tag+'-'+phase+'.time','-f','%U %S %M %x','timeout','100','prlimit','--cpu=85:90','--',sys.executable,'-B',*argv],cwd=directory,stdout=out,stderr=subprocess.STDOUT)
            if run.returncode:print(tag,'open',phase,run.returncode,flush=True);break
            if phase=='bindbare' and Path(tag+'.status').read_text().split()[1]=='cert':terminal=True;break
            if phase=='bindpole':terminal=True
        if terminal:
            path=Path('ext')/(tag+'-p1.status');print(tag,path.read_text().split()[2] if path.exists() else 'bare_cert',flush=True)

if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else work(int(sys.argv[1]))
