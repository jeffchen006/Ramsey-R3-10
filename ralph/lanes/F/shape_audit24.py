from collections import Counter
from pathlib import Path
import json,sys
from source24 import DIR

def main():
    wanted=set();states={};counts=Counter();rep=Counter();times=Counter()
    for manifest,journal,group in [(DIR/'pilot.tsv',DIR/'pilot.jsonl','pilot'),(DIR/'work0/seven.tsv',DIR/'work0/seven/worker.jsonl','seven'),*[(DIR/f'work{slot}/six.tsv',DIR/f'work{slot}/six.jsonl','six') for slot in range(2)]]:
        plan=[tuple(map(int,line.split())) for line in manifest.read_text().splitlines()];
        for key,*names in plan:
            for name in names:assert (key,name) not in wanted;wanted.add((key,name))
        for idx,line in enumerate(journal.open() if journal.is_file() else []):
            if not line.endswith('\n'):break
            row=json.loads(line);key,*names=plan[idx];assert str(key)==row['tag'];values=[record.split() for record in (journal.parent/(str(key)+'.rows')).read_text().splitlines()];assert [int(record[1]) for record in values]==names[:len(values)] and Counter(record[2] for record in values)==row['states'];times[group]+=row['cpu']
            for record in values:
                name=int(record[1]);assert record[0]==str(key) and (key,name) not in states;state=record[2] if row['rc']==0 else 'stage';states[key,name]=state;counts[name//100,state]+=1
    repair=DIR/'repair';plans=[(repair/'sample.keys',repair/'sample'),(repair/'balance.keys',repair/'balance'),*[(work/'manifest.tsv',work) for work in sorted(repair.glob('work*'))]]
    for manifest,folder in plans:
        if not (folder/'worker.jsonl').is_file():continue
        plan=[tuple(map(int,line.split())) for line in manifest.read_text().splitlines()]
        for idx,line in enumerate((folder/'worker.jsonl').open()):
            if not line.endswith('\n'):break
            row=json.loads(line);key,*names=plan[idx];tag=row['tag'];assert tag==f'{key}_{names[0]//100}';values=[record.split() for record in (folder/(tag+'.rows')).read_text().splitlines()][1:];assert [int(record[1]) for record in values]==names[:len(values)] and Counter(record[2] for record in values)==row['states'];times['repair']+=row['cpu'];
            for record in values:
                name=int(record[1]);assert record[0]==tag and states[key,name] in ('cap','stage','maskcap');state=record[2] if row['rc']==0 else 'stage';states[key,name]=state;rep[name//100,state]+=1
    finalsplit=DIR/'last/intervals.jsonl'
    if finalsplit.is_file():
        items=[json.loads(line) for line in finalsplit.open() if line.endswith('\n')];accepted=[]
        for row in items:
            lower,upper=row['lower'],row['upper'];assert row['tag']==f'root_{lower}_{upper}';trace=(DIR/'last'/(row['tag']+'.rows')).read_text().splitlines();accepted.append(row['rc']==row['missing']==0 and row['states']=={'empty':1} and trace[0].split()==[row['tag'],'masks','2906','ready'] and trace[1].split()[:3]==[row['tag'],'623','empty']);times['lastsplit']+=row['cpu']
        if [(row['lower'],row['upper']) for row in items]==[(lower,min(2906,lower+64)) for lower in range(0,2906,64)] and all(accepted):assert states[955182831,623]=='cap';states[955182831,623]='empty';rep[6,'split-empty']+=1
    assert len({key for key,name in wanted if name==700})==237 and len(wanted)==237+2596*12
    print('original outcomes',sorted(counts.items()),'distinct cap replacements',sorted(rep.items()),'cpu_s',dict((name,round(value,4)) for name,value in times.items()));
    for size in (7,6):
        summary=Counter(states.get((key,name),'unattempted') for key,name in wanted if name//100==size);print('size',size,'exact projected (sign,shape) keys',sum(summary.values()),'states',dict(summary),'unresolved',sum(value for state,value in summary.items() if state not in ('empty','bipartite','model')))
if __name__=='__main__':main()
