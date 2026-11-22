from collections import Counter
from pathlib import Path
from datetime import datetime
import json
import os
import sys
import time
from wing24 import OUT

def snapshot(previous):
    rows={path.parent.name:json.loads(path.read_text()) for path in OUT.glob('*/result.json')};manifest=(OUT/'manifest').read_text().splitlines();known=set(manifest);success={key for key,row in rows.items() if row['status']=='dual_checked'};stages=sum(step['cpu'] for row in rows.values() for step in row['log']);charged=int((OUT/'charged').read_text() or 0);reserves=list(OUT.glob('reserve.*'));live=0
    for path in reserves:
        sub=OUT/path.name[8:];
        for name in ['input.cnf','base.bin','proof.lrat','proof.zst']:
            try:live+=(sub/name).stat().st_size
            except FileNotFoundError:pass
    print(json.dumps(dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),terminal_attempts=len(rows),checked_roots=len(known&success),open_roots=len(known-success),checked_subleaves=len(success-known),completed_child_cpu_s=round(stages,2),delta_completed_cpu_s=round(stages-previous,2),statuses=Counter(row['status'] for row in rows.values()),charged_bytes=charged,live_temp_bytes=live,reserved_bytes=110000000*len(reserves)),sort_keys=True),flush=True);return stages

if __name__=='__main__':
    last=0
    while True:last=snapshot(last);time.sleep(300-time.time()%300)
