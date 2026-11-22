from pathlib import Path
from datetime import datetime
import json,os,time,subprocess,sys
from cards24 import DIR,ROOT,parse_graph6,run

def main():
    cards=json.loads((DIR/'cards.json').read_text());promoted=json.loads((DIR.parent/'transfer/promoted.json').read_text());assert len({entry['canon'] for entry in cards+promoted})==527;ids=list(map(int,Path('manifest.keys').read_text().split()));previous={base+idx for base in (0,128,256,384) for idx in range(8)};assert len(ids)==len(set(ids))==480 and set(ids).isdisjoint(previous) and set(ids)|previous==set(range(512));shape=[(idx,parse_graph6(row)) for idx,row in enumerate((DIR/'shapes.g6').read_text().splitlines())];assert len(shape)==410;total=0;lastwall=0;lastcpu=0;attempted=0;completed=0;os.environ['F_CARDS24_BIN']=str(DIR/'sym/fixed')
    for idx,card in enumerate(ids):
        entry=cards[card];record=run(entry['tag'],parse_graph6(entry['core']),10,shape,200000,140);record['card']=card;total+=record['cpu'];attempted+=len(shape);completed+=record['states'].get('empty',0) if record['rc']==0 else 0
        with open('deck.jsonl','a') as out:print(json.dumps(record),file=out)
        if idx==3:
            Path('pilot.price').write_text(f'Four disjoint full fixed-card pilots: {total:.6f} CPU-s for 1640 shape keys, {completed} terminal negatives. Remaining 476 linear estimate {476*total/4:.2f} CPU-s; actual 4h outer budget.\n');
            if total>180 or completed==0:return
        if time.monotonic()-lastwall>235:
            lastwall=time.monotonic();measured=subprocess.run(['du','-sb',DIR.parent],capture_output=True,text=True);size=int(measured.stdout.split()[0]);
            with open('meter.tsv','a') as out:print(datetime.now().astimezone().isoformat(timespec='seconds'),idx+1,attempted,completed,round(total-lastcpu,4),size,30000000,file=out)
            lastcpu=total
            if size>250000000:return
if __name__=='__main__':main()
