import hashlib
import json
import sys
import time
from pathlib import Path
from wing24 import OUT
from work24 import worker

def materialize():
    high=OUT/'high';selected=[]
    for density in (23,24):
        rows=json.loads((high/f'spec{density}.json').read_text());records=[(len(row['decks']),row['number'],idx) for row in rows for idx in range(len(row['decks']))];keys=[f'h{density}_{number}_{idx}' for count,number,idx in records];keys.sort(key=lambda key:hashlib.sha256(key.encode()).digest());(high/f'queue{density}').write_text('\n'.join(keys)+'\n')
        if density==23:
            examples=[]
            for count in [3,10,13,42,62,9]:
                index=next((idx for idx,item in enumerate(records) if item[0]==count),None)
                if index is not None:
                    _,number,idx=records[index];examples.append(f'h23_{number}_{count//2}')
            (high/'pilot23').write_text('\n'.join(examples)+'\n')

def follow(slot):
    parent=next(line.split()[1] for line in (OUT/'tailpids.tsv').read_text().splitlines() if int(line.split()[0])==slot)
    while True:
        try:cmd=Path(f'/proc/{parent}/cmdline').read_bytes();active=b'/slot24.sh' in cmd or b'/work24.py' in cmd
        except FileNotFoundError:active=False
        if not active:break
        time.sleep(2)
    high=OUT/'high';worker((high/'pilot23').read_text().splitlines());worker((high/'queue24').read_text().splitlines());
    deadline=time.monotonic()+1200
    while not (high/'go23').exists() and time.monotonic()<deadline:time.sleep(2)
    if (high/'go23').exists():worker((high/'queue23').read_text().splitlines())
    deadline=time.monotonic()+900
    while not (OUT/'nextgo').exists() and time.monotonic()<deadline:time.sleep(2)
    if (OUT/'nextgo').exists():worker((OUT/'nextmanifest').read_text().splitlines())

if __name__=='__main__':
    if sys.argv[1]=='materialize':materialize()
    else:follow(int(sys.argv[1]))
