from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

from flap23 import masks
from patch23 import STORE
from shadow import decode,bits

OUT=STORE/'wing'; GENERIC=STORE/'flap'


def record(path):
    if not path.is_file():return {}
    return json.loads(path.read_text())


def checked(folder,name):
    row=record(folder/name)
    if row.get('status')!='dual_checked':return False
    assert all(step['ok'] for step in row['log']);assert {'solve','cake','check'}<={step['stage'] for step in row['log']};assert 's VERIFIED UNSAT' in (folder/'cake.log').read_text().splitlines() and 'c VERIFIED' in (folder/'check.log').read_text().splitlines()
    file=row['files']['proof.zst'];size=file[1] if isinstance(file,list) else file['size'];return (folder/'proof.zst').stat().st_size==size


def enumerate_rows():
    table={tuple(deck):idx for idx,deck in enumerate(masks())};rows=[]
    for line in (STORE/'shapes.jsonl').read_text().splitlines():
        spec=json.loads(line);number=spec['shape'];points=spec['pinned'];wing=decode(spec['g6']);supported=set(points);modes=[]
        if spec['slack'] in (0,1):
            assert all(sum((wing[v]>>w)&1 for w in points)==2 for v in points);apices=[v for v in points if wing[v].bit_count()!=2];assert len(apices)==spec['slack']
            if apices:
                first,=apices
                for second in sorted(supported.intersection(bits(wing[first]))):
                    order=[first,second]
                    while len(order)<6:
                        nxt,=supported.intersection(bits(wing[order[-1]]))-set(order);order.append(nxt)
                    assert wing[order[-1]]>>first&1
                    modes.append([points.index(site) for site in order])
        for idx,line in enumerate((STORE/f'decks{number}.jsonl').read_text().splitlines()):
            token=f'{number}_{idx}';deck=json.loads(line);candidates=sorted({table[tuple(sorted(sum(1<<pos for pos,site in enumerate(order) if mask>>site&1) for mask in deck))] for order in modes});generic=next((k for k in candidates if checked(GENERIC/str(k),'progress.json')),None)
            hubby=next((k for k in candidates if k in (1,4) and (STORE/'hub'/f'cover{k}.tsv').exists() and all(checked(STORE/'hub'/line.split()[0],'progress.json') for line in (STORE/'hub'/f'cover{k}.tsv').read_text().splitlines() if int(line.split()[1]))),None)
            if spec['slack']==0:result='isolated_hex'
            elif generic is not None:result=f'one_flap:{generic}'
            elif hubby is not None:result=f'one_flap:hub{hubby}'
            elif checked(OUT/token,'result.json'):result='binary_direct'
            elif checked(STORE/token,'progress.json'):result='direct'
            else:result=record(OUT/token/'result.json').get('status','pending')
            rows.append((token,spec['slack'],','.join(map(str,candidates)) or '-',result))
    assert len(rows)==3114;return rows


def dispatch():
    entries=enumerate_rows();scopes={token:(slack,mode) for token,slack,_,mode in entries};pending=[token for token in scopes if scopes[token][1]=='pending'];pending.sort(key=lambda token:(scopes[token][0]>2,hashlib.sha256(token.encode()).digest()));(OUT/'manifest.tsv').write_text(''.join(f'{i%28}\t{key}\n' for i,key in enumerate(pending)));print('total pending',len(pending), 'excluded',Counter(row[-1] for row in entries))


if __name__=='__main__':
    if sys.argv[1]=='dispatch':dispatch()
    else:
        entries=enumerate_rows();output=Path(sys.argv[1]);output.mkdir();(output/'status.tsv').write_text('token\tslack\tflap_orients\teffective\n'+''.join('\t'.join(map(str,row))+'\n' for row in entries));counts=Counter(row[-1] for row in entries);print('counts',dict(counts));
        for shape in range(1,16):
            rows=[row[-1] for row in entries if int(row[0].split('_')[0])==shape];print(shape,len(rows),dict(Counter(rows)))
