from collections import Counter
import hashlib
import json
import sys
import time
from wing24 import OUT

def snapshot():
    return {path.parent.name:json.loads(path.read_text())['status'] for path in OUT.glob('*/result.json')}

def plan(require_done=False):
    records=json.loads((OUT/'spec.json').read_text());split=json.loads((OUT/'split.json').read_text());orbits=json.loads((OUT/'orbits.json').read_text());shapes=json.loads((OUT/'shapeorbits.json').read_text());status=snapshot()
    direct={key for key,val in status.items() if val=='dual_checked'};covered={key for group in orbits if set(group['keys'])&direct for key in group['keys']};sets={row['number']:{f'{row["number"]}_{idx}' for idx in range(len(row['decks']))} for row in records};queue=[];leaders=[]
    if require_done:assert all(key in status for group in sets.values() for key in group)
    for group in shapes:
        options=[]
        for number in group:
            openkeys=sets[number]-covered;leaves=[f's{key}-{idx}' for key in sorted(openkeys) for idx in range(len(split[key]['decks']))];options.append((len(set(leaves)-direct),len(openkeys),number,leaves))
        cost,num,leader,leaves=min(options);leaders.append((group,leader,sorted(sets[leader]-covered)));queue.extend(leaves)
    return sorted(set(queue)-direct,key=lambda key:hashlib.sha256(key.encode()).digest()),leaders

if __name__=='__main__':
    if sys.argv[1]=='pilot':
        split=json.loads((OUT/'split.json').read_text());status=snapshot();bad=sorted((key for key,val in status.items() if val!='dual_checked' and key in split),key=lambda key:(len(split[key]['decks']),key));chosen=[bad[idx*(len(bad)-1)//4] for idx in range(5)];keys=[f's{key}-{len(split[key]["decks"])//2}' for key in chosen];(OUT/'splitpilot').write_text('\n'.join(keys)+'\n');print(keys)
    else:
        keys,leaders=plan(True);(OUT/'splitmanifest').write_text('\n'.join(keys)+'\n');(OUT/'leaders.json').write_text(json.dumps(leaders));print('35 unoriented shapes; unresolved leaders',sum(bool(row[2]) for row in leaders),'leader key tails',sum(len(row[2]) for row in leaders),'complement leaves not yet checked',len(keys))
