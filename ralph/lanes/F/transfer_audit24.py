from collections import Counter
from pathlib import Path
import json
from transfer24 import STORE,DIR,ROOT,canonical,parse_graph6,subgraph,to_graph6

def main():
    jobs=json.loads((STORE/'promoted.json').read_text());sources=json.loads((STORE/'sources.json').read_text());assert len({row[1] for row in sources})==len(sources);cards=json.loads((DIR/'cards.json').read_text());old={row['canon'] for row in cards};assert not old.intersection(row['canon'] for row in jobs) and len({row['canon'] for row in jobs})==len(jobs)
    for row in jobs:
        physical=parse_graph6((STORE/row['source']).read_text().strip());assert len(physical)==39 and len(set(row['remove']))==7 and set(row['remove'])<=set(range(32));target=subgraph(physical,[vertex for vertex in range(39) if vertex not in row['remove']]);assert to_graph6(target)==row['core'];assert json.loads((STORE/row['source']).with_suffix('.gate').read_text())['graphs'][0]['ok']
    assert canonical([parse_graph6(row['core']) for row in jobs])==[row['canon'] for row in jobs];outcomes={};cost=Counter();by=Counter()
    for folder,log in [(STORE/'targetpilot','worker.jsonl'),(STORE/'balance','balance.jsonl'),(STORE/'balance','full.jsonl')]:
        if not (folder/log).exists():continue
        for line in (folder/log).open():
            if not line.endswith('\n'):break
            entry=json.loads(line);tag=entry['tag'];idx=int(tag.split('_')[0][6:]);values=[line.split() for line in (folder/(tag+'.rows')).read_text().splitlines()][1:];assert Counter(record[2] for record in values)==entry['states'];cost['target']+=entry['cpu'];
            for record in values:
                name=int(record[1]);assert record[0]==tag and (idx,name) not in outcomes and 0<=name<410;outcomes[idx,name]=record[2] if entry['rc']==0 else 'stage'
    repairs=STORE/'retry';
    if (repairs/'worker.jsonl').is_file():
        for line in (repairs/'worker.jsonl').open():
            if not line.endswith('\n'):break
            entry=json.loads(line);tag=entry['tag'];idx=int(tag.split('_')[0][5:]);values=[line.split() for line in (repairs/(tag+'.rows')).read_text().splitlines()][1:];assert Counter(record[2] for record in values)==entry['states'];cost['retry']+=entry['cpu'];
            for record in values:
                name=int(record[1]);assert record[0]==tag and outcomes[idx,name] in ('cap','stage');outcomes[idx,name]=record[2] if entry['rc']==0 else 'stage'
    for idx in range(len(jobs)):by[sum(outcomes.get((idx,name))=='empty' for name in range(410))]+=1
    print('gated canonical 39 sources',len(sources),'outside local-only comparison',sum(not row[2] for row in sources),'disjoint new canonical target decks',len(jobs),'total possible',len(jobs)*410,'attempted',len(outcomes),'statuses',dict(Counter(outcomes.values())),'fully closed decks',by[410],'cpu',dict((name,round(value,4)) for name,value in cost.items()))
if __name__=='__main__':main()
