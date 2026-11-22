from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time
from wing24 import OUT

def session_totals(sessions):
    totals=Counter()
    for file in Path('/proc').glob('[0-9]*/stat'):
        try:fields=file.read_text().rsplit(')',1)[-1].split();session=int(fields[3]);ticks=sum(int(fields[index]) for index in (11,12,13,14))
        except (OSError,ValueError,IndexError):continue
        if session in sessions:totals[session]+=ticks
    return totals

def report():
    sessions={int(line.split()[2]) for path in OUT.glob('*pids.tsv') for line in path.read_text().splitlines() if len(line.split())==4};hz=os.sysconf('SC_CLK_TCK');last=session_totals(sessions);delta=0;nextpost=0;previouscpu=0;rows={};groups={}
    while True:
        now=time.time()
        active_file=OUT/'activepids.tsv'
        if active_file.exists():sessions.update(int(line.split()[2]) for line in active_file.read_text().splitlines() if len(line.split())==4)
        current=session_totals(sessions);delta+=sum(max(0,ticks-last.get(session,ticks)) for session,ticks in current.items());last=current
        if now>=nextpost:
            for path in OUT.glob('*/result.json'):
                key=path.parent.name
                if key not in rows:rows[key]=json.loads(path.read_text())
            statuses=Counter(row['status'] for row in rows.values());success={key for key,row in rows.items() if row['status']=='dual_checked'};completed=sum(step['cpu'] for row in rows.values() for step in row['log']);phase={}
            for edge in range(19,25):
                directory=OUT/'high';path=directory/f'plan{edge}'
                if not path.exists():path=directory/f'keys{edge}'
                if not path.exists():continue
                keys=groups.setdefault(str(edge),set(path.read_text().splitlines()));phase[edge]=dict(total=len(keys),checked=len(keys&success),missing=len(keys-rows.keys()),nondual=len((keys&rows.keys())-success))
            pending=0;live=0;active=0
            for path in OUT.glob('reserve.*'):
                try:pending+=int(path.read_text());active+=1
                except (FileNotFoundError,ValueError):pass
                for field in ('input.cnf','base.bin','proof.lrat','proof.zst'):
                    try:live+=(OUT/path.name[8:]/field).stat().st_size
                    except FileNotFoundError:pass
            print(json.dumps(dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),booked_session_cpu_delta_floor_s=round(delta/hz,2),completed_stage_cpu_s=round(completed,2),completed_stage_delta_s=round(completed-previouscpu,2),raw_status=statuses,distinct_primary=phase,charged=int((OUT/'charged').read_text()),reserved=pending,live_temp=live,active=active),sort_keys=True),flush=True);delta=0;previouscpu=completed;nextpost=300*(int(time.time())//300+1)
        time.sleep(12)

if __name__=='__main__':report()
