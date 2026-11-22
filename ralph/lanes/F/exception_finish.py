"""Inventory, clean-room replay and accounting for the marked signing experiment."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import shutil
import subprocess
import sys
from cyclic_check import read_base
from exception_bind import bare,bind,cardbind,reference
from marked_joint import count
from marked_replay import reverse_count
from one_double_pilot import ROOT,write
from orbit_extend import parse_graph6
from round20_census import ADJ,load,totals

def entries(folder):
    old=folder.parent/'r21';roster=load(old/'mark.left');assert totals(roster)==(668,1305,31)
    for row in sorted(roster):
        first,second,weight=row;tag=f'{first}_{second}';stem=folder/tag;board,target=reference(tag);ext=folder/'ext'/(tag+'-p1')
        statusfile=stem.with_suffix('.status');polefile=ext.with_suffix('.status');artifacts=[]
        if not statusfile.exists():yield row,'open_unserved',artifacts;continue
        status=statusfile.read_text().split();assert status[0]==tag
        artifacts+=[statusfile,stem.with_suffix('.q')];assert read_base(artifacts[-1].read_text().strip())==board
        if status[1]=='cert':
            artifacts += [stem.with_suffix(suffix) for suffix in ('.cnf','.trace','.lrat')];verdict='bare_cert'
        elif status[1]=='card':
            graph=stem.with_suffix('.g6');gate=stem.with_suffix('.gate');cardbind(tag,parse_graph6(graph.read_text().strip()),board);assert json.loads(gate.read_text())['graphs'][0]['ok']
            artifacts += [graph,gate];verdict='open_pole'
            if polefile.exists():
                fields=polefile.read_text().split();assert fields[:2]==[tag,'1'];artifacts.append(polefile)
                if fields[2]=='dual' and all(ext.with_suffix(suff).is_file() for suff in ('.deck.gz','.lrat.gz')):
                    artifacts += [ext.with_suffix(suff) for suff in ('.deck.gz','.lrat.gz')];verdict='pole_cert'
                elif fields[2]=='card':
                    artifacts += [ext.with_suffix('.g6'),ext.with_suffix('.gate')];cardbind(tag,parse_graph6(artifacts[-2].read_text().strip()),board,1,True);verdict='open_37'
                else:verdict='open_'+fields[2]
        else:verdict='open_'+status[1]
        for path in artifacts:assert path.exists()
        yield row,verdict,artifacts

def inventory(digest=False):
    folder=Path.cwd();old=folder.parent/'r21';data=list(entries(folder));md=Counter();groups={}
    final=[]; paths=[];taildir=folder/'signcount';tot_masks=tot_pairs=tot_signs=0
    with Path('terminal37.tsv').open('w') as polelist,Path('terminal.tsv').open('w') as listing:
        for row,verdict,artifacts in data:
            print(*row,verdict,file=polelist)
            if verdict=='open_37':
                tag=f'{row[0]}_{row[1]}';base=taildir/tag;cover=taildir/(tag+'-cover');signs=base.with_suffix('.signs').read_text().splitlines()
                artifacts += [base.with_suffix('.trace'),base.with_suffix('.signs'),cover.with_suffix('.cnf'),cover.with_suffix('.lrat')]
                masks=pairs=0
                for index,line in enumerate(signs):
                    stem=taildir/f'{tag}-s{index}';parts=stem.with_suffix('.result').read_text().split()
                    assert parts[:4]==[tag,str(index),line.split()[0],'closed'] and parts[6]=='0'
                    masks+=int(parts[4]);pairs+=int(parts[5]);artifacts+=[stem.with_suffix(suffix) for suffix in ('.masks','.cnf','.lrat','.pairs','.result')]
                assert (taildir/f'fbind_{tag}.stdout').read_text().split()[-4:]==list(map(str,(len(signs),masks,pairs,0)))
                assert (taildir/f'cov_{tag}.stdout').read_text().split()[:3]==[tag,'cover',str(len(signs))]
                tot_masks+=masks;tot_pairs+=pairs;tot_signs+=len(signs);verdict='nonadjacent_pair_cert'
            print(*row,verdict,file=listing);groups.setdefault((row[1].bit_count(),verdict),set()).add(row);final.append((row,verdict));paths+=artifacts
    print('tail signing / pole mask / pair count',tot_signs,tot_masks,tot_pairs)
    for key,values in sorted(groups.items()):print(*key,'reps/labels/fixed',*totals(values))
    left={row for row,verdict in final if verdict not in ('bare_cert','pole_cert','nonadjacent_pair_cert')};poles=load(old/'pole.left');assert len(poles)==1137
    write('mark.left',sorted(left));write('pole.left',sorted(poles));assert Path('pole.left').read_bytes()==(old/'pole.left').read_bytes()
    orbits=count(17,10,ADJ,left,poles);reversed_orbits=reverse_count('mark.left','pole.left');assert reversed_orbits==[orbits[mult,'orbits'] for mult in range(3)]
    print('open marked',totals(left),'exterior unchanged',totals(poles),'unsigned surviving joint headers',sum(reversed_orbits))
    for path in Path('.').rglob('*.time'):
        parts=path.read_text().splitlines()
        if not parts:continue
        fields=parts[-1].split()
        if len(fields)==4:md['cpu_s']+=float(fields[0])+float(fields[1]);md['stages']+=1;md['peak_kib']=max(md['peak_kib'],int(fields[2]))
    print('metered',dict(md),'core_h',md['cpu_s']/3600)
    Path('receipt-files.txt').write_text(''.join(str(path.relative_to(folder))+'\n' for path in paths))
    if digest:
        with Path('receipts.part').open('w') as hashes:
            for path in paths:print(sha256(path.read_bytes()).hexdigest(),path.relative_to(folder),sep='  ',file=hashes)
        Path('receipts.part').replace('receipts.sha256')

def replay(folder,index,shards):
    caller=Path.cwd();done=Counter()
    for row,status,artifacts in list(entries(folder))[index::shards]:
        tag=f'{row[0]}_{row[1]}';assert status in ('bare_cert','pole_cert','open_37'),(tag,status)
        with TemporaryDirectory(dir=caller) as dst:
            for path in artifacts:shutil.copyfile(path,Path(dst)/path.name)
            os.chdir(dst)
            try:
                bare_status=bare(tag)
                if bare_status=='card':
                    result=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',tag+'.g6','36','10'],capture_output=True,text=True,check=True);assert json.loads(result.stdout)['graphs'][0]['ok']
                    assert bind(tag,1)==('card' if status=='open_37' else 'rebound')
                else:assert status=='bare_cert'
            finally:os.chdir(caller)
        done[status]+=1;print(tag,status,flush=True)
    print('clean replay totals',dict(done),flush=True)

if __name__=='__main__':
    if sys.argv[1] in ('index','digest'):inventory(sys.argv[1]=='digest')
    else:replay(Path(sys.argv[2]).resolve(),int(sys.argv[3]),int(sys.argv[4]))
