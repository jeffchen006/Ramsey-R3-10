import json
import os
import sys
from pathlib import Path

from twins23 import BASE,HARD,NEW,run
from prefix22 import inventory


def process(key):
    path=HARD/(key+'.json')
    if not path.is_file():
        temporary=path.with_suffix('.pending');temporary.write_text(json.dumps(inventory(key),sort_keys=True)+'\n');os.replace(temporary,path)
    meta=json.loads(path.read_text()); possible=set(meta['heads'])
    (HARD/(key+'.complement.tsv')).write_text('mask\tstatus\tprofiles\tmatched_identity\n'+''.join(f"{mask}\t{'split' if mask in possible else 'empty:no_sorted_short_profile'}\t{meta['per_head_profiles'].get(str(mask),0)}\t{meta['per_head_fixed'].get(str(mask),{}).get('0123456',0)}\n" for mask in range(128) if mask.bit_count()==2))
    for head in meta['heads']:
        token=f'{key}-{head}'
        if not (HARD/token/'progress.json').is_file():run(token)


if __name__=='__main__':
    for key in sys.argv[1:]:process(key)
