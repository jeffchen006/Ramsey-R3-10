import fcntl
import json
import os
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from closure22 import ROOT,digest,stage
from patch23 import STORE,physical

OUT=STORE/'wing'


def replay(token,shard):
    source=OUT/token;path=source/'result.json'
    if not path.is_file():print(token,'missing',flush=True);return
    row=json.loads(path.read_text());assert row['token']==token
    if row['status']!='dual_checked':print(token,'open',row['status'],flush=True);return
    files=row['files'];req=files['input.cnf'][1]+files['proof.lrat'][1]+6000000;reserve=OUT/f'reserve.replay{shard}'
    while True:
        with (OUT/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);charged=int((OUT/'charged').read_text());pending=sum(int(path.read_text()) for path in OUT.glob('reserve.*'));budget=4800000000 if (OUT/'go_large').is_file() else 740000000
            if charged+pending+req<budget:reserve.write_text(str(req));break
            if charged+req>=budget:print(token,'replay_space_guard',flush=True);return
        time.sleep(2)
    try:
        with TemporaryDirectory(dir=OUT/'verify') as directory:
            os.chdir(directory)
            if token.startswith('e18_'):
                from hex18 import formula18
                form=formula18(token)
            else:form=physical(token)
            form.write(Path('input.cnf'));assert digest('input.cnf')==files['input.cnf'][0] and digest(source/'proof.zst')==files['proof.zst'][0]
            cpu=0
            for name,cmd,marker in [('extract',['zstd','-dq',source/'proof.zst','-o','proof.lrat'],None),('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],'s VERIFIED UNSAT')]:
                step=stage(name,cmd,140,52000000,0,marker);assert step['ok'],(token,name);cpu+=step['cpu']
            assert digest('proof.lrat')==files['proof.lrat'][0];os.chdir(OUT);print(token,'dual_replayed',round(cpu,2),flush=True)
    finally:
        with (OUT/'lock').open('a') as lock:fcntl.flock(lock,fcntl.LOCK_EX);reserve.unlink()


if __name__=='__main__':
    shard=int(sys.argv[1]);
    if len(sys.argv)>2:tokens=sys.argv[2:]
    else:tokens=[line.split()[1] for line in (OUT/'manifest.tsv').read_text().splitlines() if int(line.split()[0])==shard]
    for token in tokens:replay(token,shard)
