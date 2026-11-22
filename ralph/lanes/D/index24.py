from collections import Counter
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import sys
from closure22 import ROOT,digest,stage
from wing24 import OUT,formula
from orbit24 import graph,join

def verified(key,hashcheck=False):
    sub=OUT/key;path=sub/'result.json'
    if not path.exists():return False
    row=json.loads(path.read_text());assert row['key']==key
    if row['status']!='dual_checked':return False
    assert all(step['ok'] for step in row['log']) and [step['stage'] for step in row['log'] if step['stage']!='thin']==['bind','solve','trim','check','cake','compress','integrity'];assert 'c VERIFIED' in (sub/'check.log').read_text().splitlines() and 's VERIFIED UNSAT' in (sub/'cake.log').read_text().splitlines();expected,size=row['files']['proof.zst'];assert size==(sub/'proof.zst').stat().st_size and (not hashcheck or expected==digest(sub/'proof.zst'));return True

def cover18(freeze):
    spec=json.loads((OUT/'spec.json').read_text());orbits=json.loads((OUT/'orbits.json').read_text());shapes=json.loads((OUT/'shapeorbits.json').read_text());split=json.loads((OUT/'split.json').read_text());host={row['number']:row for row in spec};keys=set((OUT/'manifest').read_text().splitlines());exhausted=set();direct={key for key in keys if verified(key)};sources={};leaves={}
    for orbit in orbits:
        root=next((key for key in orbit['keys'] if key in direct),None)
        if root is not None:
            for key in orbit['keys']:sources[key]=root;leaves[key]=[root]
    for key in sorted(keys-sources.keys()):
        finer=[f's{key}-{idx}' for idx in range(len(split[key]['decks']))]
        if all(verified(child) for child in finer):sources[key]='split';leaves[key]=finer
        elif all(deepdone(child) for child in finer):sources[key]='deep';leaves[key]=[piece for child in finer for piece in deepleaves(child)]
    shape_sources={};shape_maps={};byshape={}
    for group in shapes:
        for n in group:byshape[n]=[f'{n}_{idx}' for idx in range(len(host[n]['decks']))]
        choices=[n for n in group if set(byshape[n])<=sources.keys()]
        if not choices:continue
        source=min(choices,key=lambda n:(sum(len(leaves[key]) for key in byshape[n]),n));src=graph({**host[source],'points':[]},[])
        for number in group:shape_sources[number]=source;shape_maps[number]=join(src,graph({**host[number],'points':[]},[]))
    used=set(key for source in set(shape_sources.values()) for root in byshape[source] for key in leaves[root]);summary=dict(direct=len(direct),direct_or_alias=sum(val not in ('split','deep') for val in sources.values()),root_or_split=len(sources),whole_shapes=len(shape_sources),total_shapes=len(host),semantic_root_coverage=sum(len(byshape[n]) for n in shape_sources),distinct_used_receipts=len(used),open_shapes=sorted(host.keys()-shape_sources.keys()));print(json.dumps(summary,sort_keys=True),flush=True)
    if freeze:
        dest=OUT/freeze;dest.mkdir();(dest/'summary.json').write_text(json.dumps(summary,sort_keys=True)+'\n');(dest/'shape-maps.json').write_text(json.dumps(dict(leader=shape_sources,permutation=shape_maps),sort_keys=True));(dest/'cover.tsv').write_text(''.join(f'{root}\t{sources[root]}\t{",".join(leaves[root])}\n' for n in sorted(set(shape_sources.values())) for root in byshape[n]));(dest/'open-shapes.tsv').write_text(''.join(f'{n}\t'+','.join(key for key in byshape[n] if key not in sources)+'\n' for n in summary['open_shapes']));
        with (dest/'receipts.tsv').open('w') as stream:
            for key in sorted(used):
                assert verified(key,True);row=json.loads((OUT/key/'result.json').read_text());print(key,*[row['files'][name][0] for name in ['input.cnf','proof.lrat','proof.zst']],row['files']['proof.zst'][1],round(sum(step['cpu'] for step in row['log']),2),sep='\t',file=stream)

def deepleaves(key):
    if verified(key):return [key]
    path=OUT/'deep'/f'{key}.json'
    if not path.exists():return None
    return [f'z{key[1:]}-{idx}' for idx in range(len(json.loads(path.read_text())['decks']))]

def deepdone(key):
    leaves=deepleaves(key);return leaves is not None and all(verified(child) for child in leaves)

def replay(key):
    from work24 import SLOT,LIMIT
    import fcntl,time
    sub=OUT/key;assert verified(key,True);row=json.loads((sub/'result.json').read_text());needed=row['files']['input.cnf'][1]+row['files']['proof.lrat'][1]+2_000_000;lease=OUT/f'reserve.verify-{os.getpid()}';assert needed<SLOT
    while True:
        with (OUT/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);charged=int((OUT/'charged').read_text());reserved=SLOT*len(list(OUT.glob('reserve.*')))
            if charged+SLOT>LIMIT:raise RuntimeError('replay too large')
            if charged+reserved+SLOT<=LIMIT:lease.write_text(str(SLOT));break
        time.sleep(1)
    try:
        with TemporaryDirectory(dir=OUT) as temp:
            os.chdir(temp);log=[]
            for name,cmd,rc,marker in [('bind',[sys.executable,'-B',Path(__file__).with_name('work24.py'),'bind',key],0,None),('extract',['zstd','-dq',sub/'proof.zst','-o','proof.lrat'],0,None),('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],0,'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],0,'s VERIFIED UNSAT')]:
                step=stage(name,cmd,160,55_000_000,rc,marker);assert step['ok'];log.append(step)
            assert all(digest(file)==row['files'][file][0] for file in ['input.cnf','proof.lrat']);print(key,'replayed',round(sum(step['cpu'] for step in log),2),flush=True);os.chdir(OUT)
    finally:
        with (OUT/'lock').open('a') as lock:fcntl.flock(lock,fcntl.LOCK_EX);lease.unlink()

if __name__=='__main__':
    if sys.argv[1]=='cover':cover18(sys.argv[2] if len(sys.argv)>2 else None)
    else:
        for key in sys.argv[2:]:replay(key)
