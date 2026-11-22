from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path
import sys
import pynauty
from wing24 import OUT
from high24 import HIGH
from orbit24 import graph,join
from index24 import verified

def plan(edges):
    spec=json.loads((HIGH/f'spec{edges}.json').read_text());cut=set(line.split()[0] for line in (HIGH/f'rowcuts{edges}.tsv').read_text().splitlines());groups=defaultdict(list);graphs={};keys={}
    for row in spec:
        number=row['number'];graphs[number]=graph({**row,'points':[]},[]);groups[pynauty.certificate(graphs[number])].append(number);keys[number]=[f'h{edges}_{number}_{idx}' for idx in range(len(row['decks']))]
    manifest=[];cover={};leaders=[]
    for group in groups.values():
        leader=min(group,key=lambda number:(len(set(keys[number])-cut),number));leaders.append(leader);manifest.extend(key for key in keys[leader] if key not in cut)
        for number in group:cover[number]=[leader,join(graphs[leader],graphs[number])]
    manifest.sort(key=lambda key:hashlib.sha256(key.encode()).digest());(HIGH/f'plan{edges}').write_text(''.join(key+'\n' for key in manifest));(HIGH/f'cover{edges}.json').write_text(json.dumps(cover));print('density',edges,'retained shapes',len(spec),'leaders',len(leaders),'noncut leader roots',len(manifest))

def freeze(edges,name,sector=None):
    keys=(HIGH/f'keys{edges}').read_text().splitlines();spec=json.loads((HIGH/f'spec{edges}.json').read_text());cover_path=HIGH/f'cover{edges}.json';direct={};leaves={};cut={};leaders={}
    if cover_path.exists():
        transport=json.loads(cover_path.read_text());leaders={int(key):value[0] for key,value in transport.items()};cut={line.split()[0]:line.split()[1] for line in (HIGH/f'rowcuts{edges}.tsv').read_text().splitlines()}
    else:leaders={row['number']:row['number'] for row in spec}
    if sector=='rare':
        rings=json.loads((HIGH/f'rings{edges}.json').read_text());spec=[row for row in spec if str(row['number']) in rings and len(rings[str(row['number'])])<=1];keep={row['number'] for row in spec};assert all(leaders[number] in keep for number in keep);keys=[key for key in keys if int(key.split('_')[1]) in keep]
    for row in spec:
        number=row['number']
        if leaders[number]!=number:continue
        for idx in range(len(row['decks'])):
            key=f'h{edges}_{number}_{idx}'
            if key in cut:direct[key]='cut:'+cut[key]
            elif verified(key):direct[key]=key;leaves[key]=True
            else:
                splits=HIGH/'repairs'/f'{key}.json'
                if splits.is_file():
                    children=[f'b{key[1:]}-{idx}' for idx in range(len(json.loads(splits.read_text())['decks']))]
                    if all(verified(child) for child in children):direct[key]=','.join(children);leaves.update((child,True) for child in children)
    missing=[f'h{edges}_{row["number"]}_{idx}' for row in spec if leaders[row['number']]==row['number'] for idx in range(len(row['decks'])) if f'h{edges}_{row["number"]}_{idx}' not in direct];print('density',edges,'key denominator',len(keys),'unique terminal LRATs',len(leaves),'open leader roots',len(missing),missing[:50],flush=True)
    if name:
        area=HIGH/name;area.mkdir();(area/'open.tsv').write_text(''.join(key+'\n' for key in missing));(area/'coverage.tsv').write_text(''.join(f'{key}\t{reason}\n' for key,reason in sorted(direct.items())));cpu=0;archive=0
        with (area/'receipts.tsv').open('w') as stream:
            for key in sorted(leaves):
                assert verified(key,True);row=json.loads((OUT/key/'result.json').read_text());seconds=sum(step['cpu'] for step in row['log']);cpu+=seconds;archive+=row['files']['proof.zst'][1];print(key,*[row['files'][file][0] for file in ['input.cnf','proof.lrat','proof.zst']],row['files']['proof.zst'][1],round(seconds,2),sep='\t',file=stream)
        (area/'summary.json').write_text(json.dumps(dict(denominator=len(keys),open=len(missing),receipts=len(leaves),used_stages_s=round(cpu,2),archive_bytes=archive))+'\n')

if __name__=='__main__':
    if sys.argv[1]=='plan':plan(int(sys.argv[2]))
    else:freeze(int(sys.argv[2]),sys.argv[3] if len(sys.argv)>3 and sys.argv[3]!='-' else None,sys.argv[4] if len(sys.argv)>4 else None)
