from collections import Counter
from pathlib import Path
from datetime import datetime
import json,sys
from front24 import BASE,OLD,REGIONS,RETIRED,outcome,readkeys

def main(final):
    seen={};statuses=Counter();times=Counter();pending=0;repairs={};ranges=mask_starts=0
    for folder,tags,group in [(OLD,['pilot','wave0','wave1','wave2','wave3'],'old'),*((BASE/f'slot{slot}',[f'w{i}' for i in range(3)],'new') for slot in range(4))]:
        for tag in tags:
            pool=readkeys(folder/(tag+'.keys'));log=folder/(tag+'.jsonl');done=0
            for line in log.open() if log.is_file() else []:
                if not line.endswith('\n'):break
                item=json.loads(line);chunk=item['keys'];assert item['start']==done and chunk==pool[done:done+len(chunk)];done+=len(chunk);times[group]+=item['cpu'];valid=item['status']=='complete' and item['rc']==0;assert not valid or [int(row[0]) for row in item['rows']]==chunk
                for key,row in zip(chunk,item['rows'] if valid else [None]*len(chunk)):
                    assert key not in seen and key>>18 in REGIONS and key>>12 not in RETIRED;state=outcome(row) if valid else 'stage';seen[key]=(state,int(row[1]) if row and state=='cap/empty' else None);statuses[group,state]+=1
            pending+=len(pool)-done
        file=folder/'tail.jsonl'
        if not file.exists():continue
        for line in file.open():
            if not line.endswith('\n'):break
            row=json.loads(line);key=row['key'];size=row['size'];expected=list(range(0,size,16));trace=[values.split() for values in (folder/f'{key}.rows').read_text().splitlines()];exact=[(int(values[0]),int(values[1]),int(values[2]),values[3]) for values in trace];assert (key not in repairs and key in seen and seen[key]==('cap/empty',size));terminal=(row['rc']==row['missing']==0 and exact==[(key,start,min(start+16,size),'empty') for start in expected]);repairs[key]=terminal;times['repair']+=row['cpu'];ranges+=len(expected) if terminal else 0;mask_starts+=size if terminal else 0
    assert sum(statuses.values())==len(seen) and len(seen)+pending==774144
    print(datetime.now().astimezone().isoformat(timespec='seconds'),'attempted',len(seen),'pending',pending,'stages',sorted(statuses.items()),'cpu_s',dict((key,round(value,2)) for key,value in times.items()));print('I4-only replacements',len(repairs),'empty',sum(repairs.values()),'full intervals',ranges,'mask starts',mask_starts)
    opens=[key for key,(state,size) in seen.items() if state not in ('bare','empty/empty') and not repairs.get(key,False)];print('current open excluding pending',len(opens),'terminal',len(seen)-len(opens),'other 12288 nested words inherited only')
    if final:
        assert not pending and set(seen)=={key for region in REGIONS for key in range(region<<18,(region+1)<<18) if key>>12 not in RETIRED};(BASE/'residual.keys').write_text(''.join(f'{key} {seen[key][0]} {seen[key][1]}\n' for key in sorted(opens)));print('three full high-12 regions',3*(1<<18),'minus open',len(opens),'scope 32+8 only')
if __name__=='__main__':main(len(sys.argv)>1 and sys.argv[1]=='final')
