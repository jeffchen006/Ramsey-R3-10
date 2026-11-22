from collections import Counter
from pathlib import Path
import json,os
from front24 import BASE,REGIONS,outcome

def main():
    root=Path(os.getenv('F_WIDE24_ROOT',BASE/'global'));seen=set();total=Counter();times=Counter();active=[];per_region={}
    for tag,work,manifest in [('pilot',root,root/'pilot.tsv'),*(('prod',work,work/'manifest.tsv') for work in sorted(root.glob('work*')))]:
        journal=work/(tag+'.jsonl');completed=0;summary=Counter();cpu=0;reserve=[]
        for line in journal.open() if journal.exists() else []:
            if not line.endswith('\n'):break
            row=json.loads(line);idx=row['idx'];assert idx==completed;completed+=1;first,last,words,visit,strict=row['counts'];identity=(first,last);reserve.append(identity);assert row['first']==first and row['last']==last and words==(last-first)*2048 and 0<=strict<=visit<=words;assert all(prefix>>7 not in REGIONS and prefix not in seen for prefix in range(first,last));seen.update(range(first,last));assert list(map(int,(work/f'{tag}_{idx}.count').read_text().split()))==row['counts'];states=Counter();keys=set()
            for values in (work/f'{tag}_{idx}.rows').read_text().splitlines():
                fields=values.split();key=int(fields[0]);assert first*2048<=key<last*2048 and key not in keys;keys.add(key);states['stage' if fields[1]=='stage' else outcome(fields)]+=1
            assert states==row['stages'] and len(keys)==strict;summary.update(states);summary['bare']+=words-strict;cpu+=row['cpu'];times['physical']+=row['physical_cpu'];assert first>>13==(last-1)>>13;bucket=per_region.setdefault(first>>13,Counter());bucket.update(states);bucket['bare']+=words-strict
        manifests=[tuple(map(int,line.split())) for line in manifest.read_text().splitlines()];assert manifests[:completed]==reserve;total.update(summary);times['all']+=cpu;active.append([work.name,completed,len(manifests),dict(summary),round(cpu,4)])
    print('queues',json.dumps(active));print('distinct signed words',len(seen)*2048,'statuses',dict(total),'cpu',dict((key,round(value,4)) for key,value in times.items()),'cap/stage/maskcap costs remain open')
    for region,counts in sorted(per_region.items()):
        if sum(counts.values())==1<<24 and set(counts)<={'bare','empty/empty'}:assert set(range(region<<13,(region+1)<<13))<=seen;print('complete raw high-six region',region,'words',1<<24,'counts',dict(counts))
if __name__=='__main__':main()
