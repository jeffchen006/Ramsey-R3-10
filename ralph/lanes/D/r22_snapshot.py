import collections
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'scratch/D/m14r22'


def clock_tree(pid):
    try:
        stat=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split();children=Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
    except (OSError,ValueError):return 0
    return sum(map(int,stat[11:15]))+sum(clock_tree(child) for child in children)


def snapshot():
    pids=[row.split()[1] for row in (BASE/'pids.tsv').read_text().splitlines()];ticks=os.sysconf('SC_CLK_TCK');first=[clock_tree(pid) for pid in pids];time.sleep(1.25);second=[clock_tree(pid) for pid in pids]
    entries={};stats=collections.Counter();unique=set();cpu=0
    for path in sorted(BASE.glob('w*.log')):
        for line in path.read_text().splitlines():
            if not line.startswith('['):continue
            host,head,status,stages=json.loads(line);assert not head and host not in unique;unique.add(host);entries[host]=status;cpu+=sum(stage['cpu'] for stage in stages)
    for host in ['D_864','S_21983','O_6879']:
        record=json.loads((BASE/host/'progress.json').read_text());assert host not in unique;entries[host]=record['status'];cpu+=sum(stage['cpu'] for stage in record['log'])
    whole=entries.copy();leafcost=0;prefix={}
    for profile in (BASE/'prefix').glob('*.json'):
        spec=json.loads(profile.read_text());key=spec['key'];done=[]
        for head in spec['heads']:
            file=BASE/'prefix'/f'{key}-{head}'/'result.json'
            if file.exists():
                record=json.loads(file.read_text());leafcost+=sum(stage['cpu'] for stage in record['checks']);assert record['key']==key and record['head']==head
                if record['status']=='dual_checked':done.append(head)
        prefix[key]=[len(done),len(spec['heads'])]
        if len(done)==len(spec['heads']):entries[key]='prefix_complete'
    for key,status in entries.items():stats[key[0]+':'+status]+=1
    timepoint=datetime.now().astimezone();stamp=timepoint.isoformat(timespec='seconds');states=[]
    for pid in pids:
        try:states.append(Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[0])
        except OSError:states.append('-')
    report=dict(time=stamp,busy_main=sum(right-left>=0.12*ticks for left,right in zip(first,second)),live_coordinators=sum(state!='-' for state in states),temporarily_lent=states.count('T'),cpu_ticks_per_second=round(sum(max(0,right-left) for left,right in zip(first,second))/(1.25*ticks),2),main_completed_cpu_h=round(cpu/3600,6),prefix_completed_cpu_h=round(leafcost/3600,6),main_jobs=len(whole),stats=dict(stats),prefix_counts=prefix,accounted_bytes=int((BASE/'accounted.bytes').read_text()))
    print(json.dumps(report,sort_keys=True),flush=True)
    if len(sys.argv)>1:
        dst=BASE/sys.argv[1];dst.mkdir(exist_ok=True);(dst/'summary.json').write_text(json.dumps(report,sort_keys=True)+'\n');scope=[line.split()[1] for line in (BASE/'manifest.tsv').read_text().splitlines()];assert set(entries)<=set(scope);(dst/'status.tsv').write_text('key\tdirect\teffective\n'+''.join(f'{key}\t{whole.get(key,"undispatched_or_running")}\t{entries.get(key,"undispatched_or_running")}\n' for key in scope))


if __name__=='__main__':
    if sys.argv[1:]==['--watch']:
        sys.argv.pop()
        while True:
            time.sleep(300-time.time()%300);snapshot()
            if not any(Path('/proc') .joinpath(row.split()[1]).exists() for row in (BASE/'pids.tsv').read_text().splitlines()):break
    else:snapshot()
