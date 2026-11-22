from pathlib import Path
import json,os,shutil
from collections import Counter
from front24 import BASE

def main():
    snapshot=BASE/'static24';snapshot.mkdir();wide=snapshot/'global';wide.mkdir();caps=[]
    for source,tag,plan in [(BASE/'global','pilot','pilot.tsv'),*((folder,'prod','manifest.tsv') for folder in sorted((BASE/'global').glob('work*')))]:
        dest=wide if tag=='pilot' else wide/source.name;dest.mkdir(exist_ok=True);shutil.copyfile(source/plan,dest/plan);seen=[]
        for line in (source/(tag+'.jsonl')).open():
            if not line.endswith('\n'):break
            row=json.loads(line);idx=row['idx'];assert idx==len(seen);seen.append(line)
            for ext in ('rows','count'):shutil.copyfile(source/f'{tag}_{idx}.{ext}',dest/f'{tag}_{idx}.{ext}')
            if not row['stages'].get('cap/empty'):continue
            for values in (dest/f'{tag}_{idx}.rows').read_text().splitlines():
                fields=values.split();
                if len(fields)>15 and fields[2:4]==['I4','cap'] and fields[13:15]==['C5','empty']:caps.append((int(fields[0]),int(fields[1])))
        (dest/(tag+'.jsonl')).write_text(''.join(seen))
    assert len(caps)==len(dict(caps));(snapshot/'wideI4.tsv').write_text(''.join(f'{key} {size}\n' for key,size in sorted(caps)))
    work=BASE/'fixed/successor';items=[];states=Counter();ids=[];elapsed=0;fresh=list(map(int,(work/'manifest.keys').read_text().split()));closed=[]
    for line in (work/'deck.jsonl').open():
        if not line.endswith('\n'):break
        row=json.loads(line);assert row['card']==fresh[len(items)];items.append(line);elapsed+=row['cpu'];values=[entry.split() for entry in (work/(row['tag']+'.rows')).read_text().splitlines()][1:];assert [int(entry[1]) for entry in values]==list(range(len(values))) and Counter(entry[2] for entry in values)==row['states'];states.update(row['states']);states['missing']+=row['missing'];assert len(values)+row['missing']==410
        if row['rc']==0 and row['states']=={'empty':410}:closed.append(row['card'])
        shutil.copyfile(work/(row['tag']+'.rows'),snapshot/(row['tag']+'.rows'))
    (snapshot/'successor.jsonl').write_text(''.join(items));print('extra fixed cards: attempted',len(items),'of 480;',len(closed),'whole terminal, states',dict(states),'cpu',round(elapsed,3),'whole IDs',closed);print('wide exact I4-only tails price queue',len(caps),'keys; all complementary C5 really exhausted')
if __name__=='__main__':main()
