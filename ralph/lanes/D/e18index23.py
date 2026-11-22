from collections import Counter
from datetime import datetime
from pathlib import Path
import json
import time

from closure22 import digest
from square23 import WORK,STORE


def snapshot():
    keys=[line.split()[1] for line in (WORK/'hex/manifest.tsv').read_text().splitlines()];assert len(set(keys))==len(keys)==2752;counts=Counter();cpu=0;size=0;closed=[];openrows=[]
    for key in keys:
        folder=STORE/'wing'/key;path=folder/'result.json';record=json.loads(path.read_text()) if path.exists() else {};status=record.get('status','pending');cpu+=sum(step['cpu'] for step in record.get('log',[]));counts[status]+=1
        if status=='dual_checked':
            files=record['files'];assert record['token']==key and all(step['ok'] for step in record['log']);assert (folder/'proof.zst').stat().st_size==files['proof.zst'][1];size+=files['proof.zst'][1];closed.append([key,files['input.cnf'][0],files['proof.lrat'][0],files['proof.zst'][0]])
        else:openrows.append([key,status])
    summary=dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),counts=counts,completed_stage_s=round(cpu,2),retained_archive_bytes=size);print(json.dumps(summary,sort_keys=True),flush=True)
    if not openrows:
        dest=WORK/'hex/final23';dest.mkdir(exist_ok=True);(dest/'receipts.tsv').write_text('key\tcnf\tlrat\tzst\n'+''.join('\t'.join(row)+'\n' for row in closed));(dest/'open.tsv').write_text('key\tstatus\n');(dest/'summary.json').write_text(json.dumps(summary,sort_keys=True)+'\n');(dest/'SHA256SUMS').write_text(''.join(f'{digest(dest/name)}  {name}\n' for name in ['receipts.tsv','open.tsv','summary.json']));return True
    return False


if __name__=='__main__':
    while not snapshot():time.sleep(300-time.time()%300)
