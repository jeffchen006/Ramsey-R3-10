from collections import Counter
from pathlib import Path
import json
from front24 import BASE,REGIONS

def main():
    root=BASE/'global';pilot=list(map(json.loads,(root/'pilot.jsonl').read_text().splitlines()));assert len(pilot)==27;blocked={row['first'] for row in pilot};rates=Counter()
    for row in pilot:rates[row['first']>>13]+=row['counts'][-1]
    regions=[region for region,num in rates.most_common() if num][:4];assert len(regions)==4
    for idx,region in enumerate(regions):
        work=root/f'work{idx}';work.mkdir();rows=[]
        for lower in range(region<<13,(region+1)<<13,8):
            pending=[]
            for prefix in range(lower,lower+8):
                if prefix not in blocked and prefix>>7 not in REGIONS:pending.append(prefix)
                elif pending:rows.append((pending[0],pending[-1]+1));pending=[]
            if pending:rows.append((pending[0],pending[-1]+1))
        (work/'manifest.tsv').write_text(''.join(f'{start} {end}\n' for start,end in rows));print('slot',idx,'high6',region,'windows',len(rows),'fresh words',sum(end-start for start,end in rows)*2048,'previous pilot physical count',rates[region]);
if __name__=='__main__':main()
