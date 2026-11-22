from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,sys

def fixed():
    directory=Path('split');whole={tuple(map(int,line.split())) for line in (directory/'whole.tsv').read_text().splitlines()};actual={};summed=[0]*8;nodes=discarded=0
    for tag in ('pilot',*(f'slot{slot}' for slot in range(4))):
        expected={tuple(map(int,line.split())) for line in (directory/(tag+'.tsv')).read_text().splitlines()}
        for line in (directory/(tag+'.rows')).read_text().splitlines():
            data=line.split();key=tuple(map(int,data[:3]));expected.remove(key);assert key not in actual and data[3]=='empty';actual[key]=line;nodes+=int(data[4]);discarded+=int(data[5]);summed=[a+int(b) for a,b in zip(summed,data[6:14])]
        assert not expected
    assert set(actual)==whole
    for key in sorted({row[0] for row in whole}):
        rows=sorted((begin,end) for other,begin,end in whole if other==key);assert rows[0][0]==0 and all(left[1]==right[0] for left,right in zip(rows,rows[1:]));assert rows[-1][1]==len((directory/f'old32_{key}.masks').read_text().splitlines())
    cycle={line.split()[0]:line.split() for line in Path('wild/four.rows').read_text().splitlines()};assert all(cycle[str(key)][cycle[str(key)].index('C5')+1]=='empty' for key,_,_ in whole);print('3 fixed cores; 369 complete independent-four intervals; three whole C5 branches separately empty. Masks',summed[0],'visits',nodes,'wildcard siblings bypassed',discarded,'prefixes by reached depth',summed)
def accounting():
    main=3039.91;five=252.99;four=302.87;scanned32=247.02;stage=0;metered=0
    for path in Path('.').rglob('*.time'):
        if path.is_symlink() or 'clean23' in path.parts or 'chart' in path.parts or (len(path.parts)==1 and path.stem.startswith(('trial','price','strata'))):continue
        fields=path.read_text().split();
        if len(fields)!=5:continue
        stage+=float(fields[1])+float(fields[2]);metered+=1
    print('Completed main interval/pilot CPU-s',main,'C5 batches',five,'four-shape batches',four,'other GNU-time stages',round(stage,2),'across',metered,'files; fixed32 native+supervisors sampled lower bound',scanned32,'total accounted seconds',round(main+five+four+stage+scanned32,2),'core-h',round((main+five+four+stage+scanned32)/3600,5),'; excludes live chart production, chart pilot, lightweight unmetered wrappers')
def capture():
    directory=Path('chart');seen=set();counts=Counter();remaining=[];cpu=0;records=[];caps=[];unscanned=[];claimed=set(map(int,(directory/'roots.keys').read_text().split()));seen.update(claimed);counts['fixed']=len(claimed)
    for tag in ('pilot',*(f'slot{slot}' for slot in range(4))):
        keys=list(map(int,(directory/(tag+'.keys')).read_text().split()));path=directory/(tag+'.jsonl');rows=path.read_text().splitlines() if path.exists() else [];covered=0
        for line in rows:
            item=json.loads(line);data=item['keys'];assert len(data)>0 and data==keys[item['start']:item['start']+len(data)] and not seen.intersection(data);seen.update(data);cpu+=item['cpu'];covered+=len(data);records.append(line)
            if item['status']!='complete':counts['stage_open']+=len(data);unscanned.extend(data);continue
            assert data==[int(row[0]) for row in item['rows']]
            for row in item['rows']:
                status='bare' if 'bare' in row else 'maskcap' if 'maskcap' in row else 'cap' if 'cap' in row else 'model' if 'model' in row else 'physical';counts[status]+=1
                if status in ('cap','maskcap'):caps.append(int(row[0]))
        remaining.extend(keys[covered:])
    assert len(seen)+len(set(remaining))==12288 and not seen.intersection(remaining);Path('chart_handoff.jsonl').write_text('\n'.join(records)+'\n');Path('chart_residual.keys').write_text(''.join(f'{key}\n' for key in sorted(caps+unscanned)));print('word statuses',dict(counts),'unattempted',len(remaining),'pilot+completed production child CPU-s',round(cpu,2),'new residual',len(caps+unscanned))
def tailaudit():
    residual={};chart=Path('chart');directory=Path('chart_tail');seen=set();cpu=0;intervals=masks=0
    for path in chart.glob('*.jsonl'):
        for entry in map(json.loads,path.read_text().splitlines()):
            assert entry['status']=='complete'
            for row in entry['rows']:
                if 'cap' in row:assert row[3]=='cap' and row[14]=='empty';residual[int(row[0])]=int(row[1])
    for file in directory.glob('slot*.jsonl'):
        for entry in map(json.loads,file.read_text().splitlines()):
            key=entry['key'];assert key not in seen and entry['status']=='closed' and not entry['missing'] and entry['rc']==0;seen.add(key);rows=sorted((line.split() for line in (directory/f'{key}.rows').read_text().splitlines()),key=lambda row:int(row[1]));lo=0
            for row in rows:
                assert int(row[0])==key and int(row[1])==lo<int(row[2]) and row[3]=='empty';masks+=int(row[2])-lo;lo=int(row[2]);intervals+=1
            assert lo==residual[key];cpu+=entry['cpu']
    assert seen==set(residual)==set(map(int,Path('chart_residual.keys').read_text().split())) and len(seen)==24;print('24/24 cap replacements,',intervals,'minimum-first-mask ranges;',masks,'mask starts, zero open;',round(cpu,2),'child CPU-s. All 12,288 words in the three explicit regions excluded; not the full 2^30 chart.')
def hashes():
    paths=[]
    for path in Path('.').rglob('*'):
        if not path.is_file() or path.is_symlink() or 'clean23' in path.parts or path.name=='receipts23.sha256' or (path.parts[0]=='front' and path.name not in {'plan.stdout','pilot.keys','pilot.jsonl','pilot.time','pilot.stdout','forecast.txt','slot0.keys','slot1.keys','slot2.keys','slot3.keys','wave0.keys','wave1.keys','wave2.keys','wave3.keys'}):continue
        paths.append(path)
    with open('receipts23.sha256','w') as out:
        for path in sorted(paths):print(sha256(path.read_bytes()).hexdigest(),str(path),sep='  ',file=out)
    print('hashed',len(paths),'artifacts')
if __name__=='__main__':{'fixed':fixed,'cost':accounting,'capture':capture,'tailaudit':tailaudit,'hash':hashes}[sys.argv[1]]()
