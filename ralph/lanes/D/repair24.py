import json
import sys
from functools import lru_cache
from high24 import HIGH,OUT,graph_masks,expand,population
from split24 import children

@lru_cache(None)
def shapes(edges):return {row['number']:row for row in json.loads((HIGH/f'spec{edges}.json').read_text())}

def prepare(key):
    edges,number,idx=map(int,key[1:].split('_'));row=shapes(edges)[number];points=row['points'];wing=graph_masks(row['g6']);words=row['decks'][idx];assert len(points)==4,'larger-patch cap requires separately priced repair';choices=[]
    for site in set(range(16))-set(points):
        decks=children(wing,points,words,site,9,1);choices.append((len(decks),site,decks))
    size,site,decks=min(choices);reference=population(wing,[*points,site],9,21,1);assert set(decks)=={deck for deck in reference if tuple(sorted(mask&15 for mask in deck))==tuple(words)};return dict(added=site,decks=decks)

def prepare_all(edges):
    area=HIGH/'repairs';area.mkdir(exist_ok=True);manifest=[];other=[];caps=[]
    for key in (HIGH/f'plan{edges}').read_text().splitlines():
        path=OUT/key/'result.json'
        if not path.exists() or json.loads(path.read_text())['status']=='dual_checked':continue
        size,number,idx=map(int,key[1:].split('_'));row=shapes(size)[number];caps.append(key)
        if len(row['points'])!=4:other.append(key);continue
        target=area/f'{key}.json'
        if not target.exists():spec=prepare(key);target.write_text(json.dumps(spec))
        else:spec=json.loads(target.read_text())
        manifest.extend(f'b{key[1:]}-{idx}' for idx in range(len(spec['decks'])))
    (area/f'man{edges}').write_text(''.join(key+'\n' for key in manifest));(area/f'other{edges}').write_text(''.join(key+'\n' for key in other));print('density',edges,'caps seen',len(caps),'unpriced larger repairs',other,'root-replacing children',len(manifest),flush=True)

def formula_repair(key):
    parent,child=key[1:].split('-');edges,number,idx=map(int,parent.split('_'));row=shapes(edges)[number];spec=json.loads((HIGH/'repairs'/f'h{parent}.json').read_text());return expand(graph_masks(row['g6']),[*row['points'],spec['added']],spec['decks'][int(child)],27+edges,9,True)

if __name__=='__main__':prepare_all(int(sys.argv[1]))
