from collections import Counter
from datetime import datetime
from pathlib import Path
import json

def main():
    directory=Path.cwd();assert directory.name=='front';attempted=0;counts=Counter();cpu=0;remaining=0
    for tag in ('pilot','wave0','wave1','wave2','wave3'):
        keys=list(map(int,Path(tag+'.keys').read_text().split()));path=Path(tag+'.jsonl');done=0
        for item in (map(json.loads,path.read_text().splitlines()) if path.exists() else ()):
            assert item['start']==done and item['keys']==keys[done:done+len(item['keys'])];done+=len(item['keys']);cpu+=item['cpu']
            if item['status']!='complete':counts['stage_open']+=len(item['keys']);continue
            assert [int(row[0]) for row in item['rows']]==item['keys']
            for row in item['rows']:
                status='bare' if 'bare' in row else 'maskcap' if 'maskcap' in row else 'cap' if 'cap' in row else 'model' if 'model' in row else 'physical';counts[status]+=1
        attempted+=done;remaining+=len(keys)-done
    assert sum(counts.values())==attempted and attempted+remaining==193658
    print(datetime.now().astimezone().isoformat(timespec='seconds'),'including 162 pilot words: attempted',attempted,'statuses',dict(counts),'assigned but unattempted',remaining,'unassigned',580486,'completed child CPU-s',round(cpu,2))
if __name__=='__main__':main()
