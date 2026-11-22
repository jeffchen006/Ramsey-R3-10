import json
import sys
from collections import Counter
from wing24 import OUT,graph_masks,expand
from split24 import children
from wingaudit23 import independent

def inputs(parent):
    root,child=parent[1:].split('-');number,index=map(int,root.split('_'));row=next(row for row in json.loads((OUT/'spec.json').read_text()) if row['number']==number);prior=json.loads((OUT/'split.json').read_text())[root];return graph_masks(row['g6']),[*row['points'],prior['added']],prior['decks'][int(child)]

def prepare(parent):
    wing,points,words=inputs(parent);choices=[]
    for site in sorted(set(range(16))-set(points)):
        decks=children(wing,points,words,site,9,1);choices.append((len(decks),site,decks))
    _,added,decks=min(choices);core=wing[:]+[0,0,0]
    for site in range(16):tip=16+(site>=8);core[site]|=1<<tip;core[tip]|=1<<site
    for tip in (16,17):core[tip]|=1<<18;core[18]|=1<<tip
    target=tuple(words);ind=independent(core,[*points,added],(1<<19)-1,21,1);assert set(decks)=={deck for deck in ind if tuple(sorted(mask&31 for mask in deck))==target};(OUT/'deep'/f'{parent}.json').write_text(json.dumps(dict(added=added,decks=decks)));return [f'z{parent[1:]}-{idx}' for idx in range(len(decks))]

def formula_deep(key):
    stem,idx=key[1:].rsplit('-',1);parent='s'+stem;wing,points,_=inputs(parent);row=json.loads((OUT/'deep'/f'{parent}.json').read_text());return expand(wing,[*points,row['added']],row['decks'][int(idx)],45,9,True)

if __name__=='__main__':
    area=OUT/'deep';area.mkdir(exist_ok=True);caps=[];keys=[]
    for child in (OUT/'splitmanifest').read_text().splitlines():
        path=OUT/child/'result.json'
        if path.is_file() and json.loads(path.read_text())['status']!='dual_checked':caps.append(child);keys.extend(prepare(child))
    (area/'manifest').write_text(''.join(key+'\n' for key in keys));print('5site caps',len(caps),caps,'6site children',len(keys),flush=True)
