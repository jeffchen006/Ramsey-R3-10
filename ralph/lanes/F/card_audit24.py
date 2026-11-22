from collections import Counter,defaultdict
from pathlib import Path
import json
from cards24 import DIR

def main():
    catalogue=json.loads((DIR/'cards.json').read_text());lookup={card['tag']:idx for idx,card in enumerate(catalogue)};assert len(lookup)==len({card['canon'] for card in catalogue})==512
    outcomes={};times=Counter();original=Counter();replaced=Counter()
    for group,folder,manifest,log in [('pilot',DIR,DIR/'pilot.tsv',DIR/'pilot.jsonl'),('prod',DIR/'prod',DIR/'prod.tsv',DIR/'prod/worker.jsonl'),('sym',DIR/'sym',DIR/'sym/pilot.tsv',DIR/'sym/pilot.jsonl'),*[(path.name,path,path/'manifest.tsv',path/'worker.jsonl') for path in sorted((DIR/'sym').glob('work*'))]]:
        if not log.is_file():continue
        plan=[tuple(map(int,line.split())) for line in manifest.read_text().splitlines()];count=0
        for line in log.open():
            if not line.endswith('\n'):break
            row=json.loads(line);tag,low,high=row['tag'].rsplit('_',2);card=lookup[tag];low,high=int(low),int(high);assert plan[count]==(card,low,high) and catalogue[card]['core']==row['core'];count+=1;times[group]+=row['cpu'];trace=[record.split() for record in (folder/(row['tag']+'.rows')).read_text().splitlines()];values={}
            for record in trace[1:]:
                name=int(record[1]);assert low<=name<high and name not in values;values[name]=record[2]
            assert Counter(values.values())==row['states'] and high-low-len(values)==row['missing'];
            for name in range(low,high):
                state=values.get(name,'stage') if row['rc']==0 else 'stage';key=(card,name)
                if group in ('pilot','prod'):assert key not in outcomes;original[state]+=1
                else:assert outcomes[key] not in ('empty','model');replaced[state]+=1
                outcomes[key]=state
    bycard=defaultdict(Counter)
    for (card,name),state in outcomes.items():bycard[card][state]+=1
    closed=[card for card,states in bycard.items() if states==Counter(empty=410)];print('physical deck/shape keys',len(outcomes),'original',dict(original),'separate cap replacements',dict(replaced),'net',dict(Counter(outcomes.values())),'full 410-shape decks',closed,'times',dict((group,round(value,4)) for group,value in times.items()))
if __name__=='__main__':main()
