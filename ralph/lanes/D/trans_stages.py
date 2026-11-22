"""Bounded, priced, marked-P6 reroot stages; no unpriced exponential escalation."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
from witness_bind import bind


def run(folder,start):
    for stage,cap in [(3,1900),(4,3000),(5,5000),(6,8500),(7,15000),(8,25000),(9,42000)]:
        if stage<start:continue
        source=folder/f'level{stage-1}'/'live.tsv';rows=source.read_text().splitlines()
        if not rows:return
        target=folder/f'level{stage}';target.mkdir(exist_ok=True)
        def solve(part,cpu):
            with part.open() as inp,part.with_suffix('.out').open('w') as out:
                subprocess.run(['nice','-n','5','timeout',str(2*cpu+20),'prlimit',f'--cpu={cpu}:{cpu+1}',folder/'worker','40','9','8','160','9','269',str(cap),source],stdin=inp,stdout=out,check=True)
        sample=rows[::max(1,len(rows)//29)] if len(rows)>32 else rows
        offer=target/'pilot';offer.write_text('\n'.join(sample)+'\n');solve(offer,80)
        stats=offer.with_suffix('.out').read_text().splitlines();assert len(stats)==len(sample)
        done=sum(row.split()[1]=='0' for row in stats);cpu=sum(float(row.split()[3]) for row in stats);estimate=cpu*len(rows)/len(stats)
        print(stage,'inputs',len(rows),'limit',cap,'sample',len(sample),'terminal',done,'CPU-s',cpu,'forecast CPU-s',estimate,flush=True)
        if estimate>650 or (len(rows)>5 and done*4<len(sample)):
            print('STOP for repricing, no production.',flush=True);return
        if len(sample)==len(rows):
            part=target/'p00';part.write_text(offer.read_text());part.with_suffix('.out').write_text(offer.with_suffix('.out').read_text())
        else:
            workers=min(7,len(rows));parts=[]
            for idx in range(workers):
                part=target/f'p{idx:02}';part.write_text('\n'.join(rows[len(rows)*idx//workers:len(rows)*(idx+1)//workers])+'\n');parts.append(part)
            with ThreadPoolExecutor(workers) as executor:list(executor.map(lambda part:solve(part,min(200,max(65,int(2.2*estimate/workers)+35))),parts))
        bind(source,target);sys.stdout.flush()


if __name__=='__main__':run(Path(sys.argv[1]).resolve(),int(sys.argv[2]))
