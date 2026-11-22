import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from wing24 import OUT
from high24 import HIGH
from repair24 import shapes
from work24 import LIMIT,SLOT,task
from index24 import replay

def work(key):
    if (OUT/key).is_dir():return
    small=False
    if key.startswith('h'):
        edges,number,idx=map(int,key[1:].split('_'));small=len(shapes(edges)[number]['points'])==6
    slot=60_000_000 if small else SLOT
    while True:
        with (OUT/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);charged=int((OUT/'charged').read_text());reserved=0
            for path in OUT.glob('reserve.*'):
                try:reserved+=int(path.read_text())
                except FileNotFoundError:pass
            if (OUT/key).is_dir():return
            if (OUT/'stop').exists() or charged+slot>LIMIT:print('staging limit',key,flush=True);sys.exit(0)
            if charged+reserved+slot<=LIMIT:(OUT/f'reserve.{key}').write_text(str(slot));(OUT/key).mkdir();acquired=True
            else:acquired=False
        if acquired:task(key,small);return
        time.sleep(2)

def after(slot):
    priorpid=next(line.split()[1] for line in (OUT/'followpids.tsv').read_text().splitlines() if int(line.split()[0])==slot)
    while True:
        try:active=b'/follow24.py' in Path(f'/proc/{priorpid}/cmdline').read_bytes()
        except FileNotFoundError:active=False
        if not active:break
        time.sleep(2)
    queue=OUT/'sweeps';os.chdir(OUT);(queue/'replayed').mkdir(exist_ok=True);items=[line.split()[0] for line in (OUT/'final18/receipts.tsv').read_text().splitlines()];items.sort(key=lambda key:hashlib.sha256(key.encode()).digest());
    for key in items[slot::30]:
        if (queue/'replayed'/key).exists():continue
        start=time.monotonic();replay(key);(queue/'replayed'/key).write_text(str(time.monotonic()-start))
    deadline=time.monotonic()+5*3600
    completed=set()
    while time.monotonic()<deadline:
        for batch in sorted(queue.glob('batch.*')):
            if batch.name in completed:continue
            if batch.name.startswith('batch.00'):
                for key in batch.read_text().splitlines():work(key)
            else:
                for idx,key in enumerate(batch.read_text().splitlines()):
                    if idx%10==0:
                        for high in sorted(queue.glob('batch.00*')):
                            if high.name not in completed:
                                for repair in high.read_text().splitlines():work(repair)
                                completed.add(high.name)
                    work(key)
            completed.add(batch.name)
        if (queue/'no_more').exists() or (OUT/'stop').exists():return
        time.sleep(5)

if __name__=='__main__':after(int(sys.argv[1]))
