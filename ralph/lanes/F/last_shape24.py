from pathlib import Path
import json,os,sys
from source24 import DIR,R23,get,subgraph,parse_graph6
from pattern_repair24 import work

def main():
    os.environ['F_PATTERN24_FIXED']=str(Path('fixed').resolve());small=parse_graph6((R23/'sixplant12.g6').read_text().strip());core=[value|1<<(idx^1) for idx,value in enumerate(subgraph(small,range(4)))];shape=subgraph(small,range(4,12));records=[]
    for target in (4,5):
        for lower in range(9):
            os.environ['F_FIRST_MASK_RANGE']=f'{lower}:{lower+1}';row=work(f'control{target}_{lower}',core,target,True,[(0,shape)],1000000);assert row['masks']==['9','ready'] and row['rc']==row['missing']==0;records.append((target,lower,row['states']))
    assert all(states.get('empty')==1 for target,lower,states in records if target==4) and any(states.get('model')==1 for target,lower,states in records if target==5);print('matched positive and negative over 18 disjoint small ranges',records,flush=True)
    shape=json.loads((DIR/'patterns.json').read_text())['623'];assert all(row.bit_count()==1 for row in shape);core=get(955182831);records=[];cpu=0
    for lower in range(0,2906,64):
        upper=min(2906,lower+64);os.environ['F_FIRST_MASK_RANGE']=f'{lower}:{upper}';row=work(f'root_{lower}_{upper}',core,10,True,[(623,shape)],3000000);assert row['masks']==['2906','ready'];row.update(lower=lower,upper=upper);records.append(row);cpu+=row['cpu'];
        with open('intervals.jsonl','a') as out:print(json.dumps(row),file=out)
    assert [(row['lower'],row['upper']) for row in records]==[(lower,min(lower+64,2906)) for lower in range(0,2906,64)];print('last 3K2 sign',len(records),'intervals, masks 2906, empty',sum(row['rc']==row['missing']==0 and row['states']=={'empty':1} for row in records),'cpu',round(cpu,4),flush=True)
if __name__=='__main__':main()
