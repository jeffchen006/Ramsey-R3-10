from collections import Counter
from datetime import datetime
from pathlib import Path
import json
import os
import sys

from closure22 import digest
from coverwing23 import enumerate_rows,OUT,STORE


def freeze(dest,verify):
    dest.mkdir();leaves=enumerate_rows();proofs={};cover=[];openrows=[];counts=Counter();cost=Counter()
    def retain(folder,kind):
        if str(folder) in proofs:return
        if kind=='isolated':
            tag='hexone-1-0-1-1';source=STORE.parent/'roles15';proof=source/f'{tag}.lrat';cnf=STORE/f'{tag}.cnf';assert 'c VERIFIED' in (STORE/'hex.lrat-check.log').read_text().splitlines() and 's VERIFIED UNSAT' in (STORE/'hex.cake256.log').read_text().splitlines();proofs[str(folder)]=(digest(cnf),digest(proof),digest(proof),proof.stat().st_size);return
        binary=kind=='binary';row=json.loads((folder/('result.json' if binary else 'progress.json')).read_text());assert row['status']=='dual_checked'
        files=row['files'];take=lambda key:files[key] if binary else (files[key]['sha256'],files[key]['size']);cnf=take('input.cnf');lrat=take('proof.lrat');packed=take('proof.zst');assert (folder/'proof.zst').stat().st_size==packed[1];assert 'c VERIFIED' in (folder/'check.log').read_text().splitlines() and 's VERIFIED UNSAT' in (folder/'cake.log').read_text().splitlines()
        if verify:assert digest(folder/'proof.zst')==packed[0]
        if verify and not binary:assert digest(folder/'cards')==take('cards')[0]
        proofs[str(folder)]=(cnf[0],lrat[0],packed[0],packed[1]);cost[kind]+=sum(step['cpu'] for step in row['log'])
    for key,slack,orient,effective in leaves:
        counts[effective.split(':')[0]]+=1;paths=[]
        if effective=='isolated_hex':paths=[(STORE/'hexone-1-0-1-1.cnf','isolated')]
        elif effective.startswith('one_flap:'):
            source=effective.split(':')[1]
            if source.startswith('hub'):
                number=source[3:];paths=[(STORE/'hub'/line.split()[0],'hub') for line in (STORE/'hub'/f'cover{number}.tsv').read_text().splitlines() if int(line.split()[1])]
            else:paths=[(STORE/'flap'/source,'flap')]
        elif effective=='binary_direct':paths=[(OUT/key,'binary')]
        elif effective=='direct':paths=[(STORE/key,'direct')]
        else:openrows.append([key,effective])
        for path,kind in paths:retain(path,kind)
        cover.append([key,str(slack),orient,effective,';'.join(str(path.relative_to(STORE)) for path,_ in paths) or '-'])
    for name,header,rows in [('coverage.tsv',['key','slack','orientations','effective','receipts_rel_to_c6r23'],cover),('open.tsv',['key','status'],openrows),('receipts.tsv',['receipt_rel_to_c6r23','cnf_sha256','proof_sha256','archive_sha256','archive_bytes'],[[str(Path(folder).relative_to(STORE)),*map(str,value)] for folder,value in sorted(proofs.items())])]:
        (dest/name).write_text(''.join('\t'.join(row)+'\n' for row in [header,*rows]));os.chmod(dest/name,0o444)
    summary=dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),keys=len(leaves),counts=counts,residual=len(openrows),different_receipts=len(proofs),selected_stage_core_h={key:round(value/3600,6) for key,value in cost.items()},archive_hashes_read=verify)
    (dest/'summary.json').write_text(json.dumps(summary,sort_keys=True)+'\n');(dest/'SHA256SUMS').write_text(''.join(f'{digest(path)}  {path.name}\n' for path in sorted(dest.iterdir())));os.chmod(dest,0o555);print(json.dumps(summary,sort_keys=True),flush=True)


if __name__=='__main__':freeze(Path(sys.argv[1]),'--hash' in sys.argv[2:])
