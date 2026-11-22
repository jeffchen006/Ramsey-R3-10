from pathlib import Path
from datetime import datetime
import os,subprocess,sys,time

def usage(pid):
    path=Path(f'/proc/{pid}');raw=(path/'stat').read_text().rsplit(') ',1)[1].split();count=sum(int(raw[pos]) for pos in (11,12,13,14));rss=int(raw[21]);
    for child in (path/f'task/{pid}/children').read_text().split():
        try:amount,resident=usage(int(child));count+=amount;rss+=resident
        except FileNotFoundError:pass
    return count,rss
def run(pids):
    high=[0]*len(pids);maximum=[0]*len(pids);clock=os.sysconf('SC_CLK_TCK');last=0;size=0
    with open('external_meter.tsv','x',buffering=1) as output:
        while True:
            live=0;now=time.monotonic()
            if now-last>120:
                result=subprocess.run(['du','-sb','..'],capture_output=True);size=int(result.stdout.split()[0]);last=now
            for slot,pid in enumerate(pids):
                try:
                    cmd=Path(f'/proc/{pid}/cmdline').read_bytes()
                    if b'eight_split.py' not in cmd:continue
                    elapsed,rss=usage(pid);live+=1;high[slot]=max(high[slot],elapsed);maximum[slot]=max(maximum[slot],rss)
                except (ProcessLookupError,FileNotFoundError):pass
            rows=[len(path.read_text().splitlines()) if path.exists() else 0 for path in (Path(f'slot{slot}.rows') for slot in range(len(pids)))];print(datetime.now().astimezone().isoformat(timespec='seconds'),live,size,','.join(map(str,rows)),','.join(str(round(value/clock,2)) for value in high),','.join(map(str,maximum)),file=output)
            if not live:break
            time.sleep(3)
    print('sampled CPU lower bound (sum per-worker maxima), seconds',sum(high)/clock,'peak per slot single-tree RSS pages',maximum,flush=True)
if __name__=='__main__':run(list(map(int,sys.argv[1:])))
