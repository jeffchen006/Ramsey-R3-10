from pathlib import Path
from collections import Counter
import json,os,sys
from cards24 import DIR

def plan(work):
    cards=json.loads((DIR/'cards.json').read_text());lookup={row['tag']:idx for idx,row in enumerate(cards)};old=set();demand=set()
    for path in [DIR/'sym/pilot.tsv',*sorted((DIR/'sym').glob('work*/manifest.tsv'))]:
        for line in path.read_text().splitlines():
            card,start,stop=map(int,line.split());assert not {(card,name) for name in range(start,stop)}&old;old.update((card,name) for name in range(start,stop))
    for folder,log,plan_path in [(DIR,DIR/'pilot.jsonl',DIR/'pilot.tsv'),(DIR/'prod',DIR/'prod/worker.jsonl',DIR/'prod.tsv')]:
        count=0
        for line in log.open():
            if not line.endswith('\n'):break
            row=json.loads(line);tag,low,high=row['tag'].rsplit('_',2);assert row['rc']==row['missing']==0;card=lookup[tag];count+=1
            for values in (folder/(row['tag']+'.rows')).read_text().splitlines()[1:]:
                record=values.split();
                if record[2]=='cap' and (card,int(record[1])) not in old:demand.add((card,int(record[1])))
        assert count==len(plan_path.read_text().splitlines())
    (work/'manifest.tsv').write_text(''.join(f'{card} {name} {name+1}\n' for card,name in sorted(demand)));print('finished shape-baseline anti-join; prior cap ownership',len(old),'new isolated (fixed deck,shape) caps',len(demand))
if __name__=='__main__':plan(Path.cwd())
