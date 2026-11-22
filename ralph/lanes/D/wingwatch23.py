from collections import Counter
from datetime import datetime
import json
import time

from coverwing23 import OUT,STORE,enumerate_rows,record


def snapshot():
    rows=enumerate_rows();counts=Counter(row[-1].split(':')[0] if row[-1].startswith('one_flap') else row[-1] for row in rows);cpu=0
    for folder,pattern,field in [(OUT,'*/result.json','log'),(STORE,'*_*/progress.json','log'),(STORE/'flap','*/progress.json','log'),(STORE/'hub','*/progress.json','log')]:
        for path in folder.glob(pattern):cpu+=sum(x['cpu'] for x in record(path).get(field,[]))
    reserves=[]
    for path in OUT.glob('reserve.*'):
        try:reserves.append(int(path.read_text()))
        except FileNotFoundError:pass
    print(json.dumps(dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),keys=len(rows),effective=counts,complete_child_cpu_s=round(cpu,2),charged=int((OUT/'charged').read_text() or 0),reserved=sum(reserves),live_reservations=len(reserves)),sort_keys=True),flush=True)


if __name__=='__main__':
    while True:
        snapshot();time.sleep(300-time.time()%300)
