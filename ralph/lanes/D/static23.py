import fcntl
import json
import os
import sys
import time

from dispatch23 import BASE,NEW,PROGRAM,LIMIT,task


def worker(shard):
    for line in (NEW/'refill.tsv').read_text().splitlines():
        slot,key=line.split();
        if int(slot)!=shard:continue
        old=BASE/key/'progress.json'
        if old.is_file() and json.loads(old.read_text())['status']=='dual_checked':continue
        if (NEW/key).exists():
            receipt=NEW/key/'progress.json'
            if not receipt.exists() or json.loads(receipt.read_text())['status']!='staging_guard':continue
            remove_guard(key)
        while True:
            with (NEW/'staging.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_SH);saved=int((NEW/'accounted.bytes').read_text());reserved=sum(int(path.read_text()) for path in NEW.glob('reserve.*'))
            if saved+reserved+285000000>LIMIT:
                if saved+285000000>LIMIT:print('GUARD_RETAINED',key,saved,flush=True);return
                time.sleep(3+shard%3);continue
            task(key,[],120,120000000,NEW,str(PROGRAM),LIMIT,BASE/'lrat-trim')
            result=json.loads((NEW/key/'progress.json').read_text());
            if result['status']!='staging_guard':break
            remove_guard(key)
    print('DONE',shard,flush=True)


def remove_guard(key):
    sub=NEW/key;receipt=sub/'progress.json';assert list(sub.iterdir())==[receipt] and json.loads(receipt.read_text())['status']=='staging_guard'
    (NEW/'guardhistory'/f'{key}.{time.time_ns()}.json').write_bytes(receipt.read_bytes());receipt.unlink();sub.rmdir()


def recover(shard):
    with (NEW/f'recover.{shard}.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);worker(shard)


if __name__=='__main__':
    for number in sys.argv[1:]:recover(int(number))
