import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from square23 import ROOT,WORK,formula
from closure22 import digest,stage


def audit():
    records=[];cpu=0
    for token in (WORK/'tokens').read_text().splitlines():
        folder=WORK/token;row=json.loads((folder/'progress.json').read_text());assert row['status']=='dual_checked';files=row['files'];assert digest(folder/'proof.zst')==files['proof.zst']['sha256'];cpu+=sum(step['cpu'] for step in row['log'])
        with TemporaryDirectory(dir=WORK) as directory:
            os.chdir(directory);formula(token).write(Path('input.cnf'));assert digest('input.cnf')==files['input.cnf']['sha256']
            for name,cmd,marker in [('extract',['zstd','-dq',folder/'proof.zst','-o','proof.lrat'],None),('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],'s VERIFIED UNSAT')]:assert stage(name,cmd,120,90000000,0,marker)['ok'],(token,name)
            assert digest('proof.lrat')==files['proof.lrat']['sha256'];os.chdir(WORK)
        records.append([token,*[files[name]['sha256'] for name in ('input.cnf','proof.lrat','proof.zst')]]);print(token,'dual_replayed',flush=True)
    assert len(records)==len(set(row[0] for row in records))==24;(WORK/'receipt-index.tsv').write_text('key\tcnf\tlrat\tzst\n'+''.join('\t'.join(row)+'\n' for row in records));print('retained production stage seconds',round(cpu,3),flush=True)


if __name__=='__main__':audit()
