import fcntl
import json
import os
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

from closure22 import task
from m14queue22 import BASE

NEW = BASE.parent / 'm14r23'
OLDPIDS = {int(i): int(pid) for i,pid,_ in map(str.split,(BASE/'pids.tsv').read_text().splitlines())}
PROGRAM = Path(__file__).with_name('m14queue22.py')
LIMIT = 11_500_000_000
SLOT = 330_000_000


def running(pid):
    try:
        return b'm14queue22.py\0worker' in Path(f'/proc/{pid}/cmdline').read_bytes()
    except OSError:
        return False


def state(key):
    place = BASE/key
    if not place.is_dir(): return 'unstarted'
    receipt = place/'progress.json'
    return json.loads(receipt.read_text())['status'] if receipt.exists() else 'no_progress'


def init():
    db = sqlite3.connect(NEW/'work.db'); db.execute('create table jobs(key text primary key, shard integer, status text, worker integer)')
    dispatch = [line.split() for line in (BASE/'dispatch.tsv').read_text().splitlines()]
    assert len({key for _,key in dispatch}) == len(dispatch) == 8233
    assert set(key for _,key in dispatch) == {line.split()[1] for line in (BASE/'manifest.tsv').read_text().splitlines()}
    counts = Counter()
    for index,key in dispatch:
        old = state(key); counts[key[0],old] += 1
        if key[0]!='D' and old in ('unstarted','staging_guard','no_progress','open'):
            db.execute('insert into jobs values(?,?,?,null)',(key,int(index),'ready'))
    db.commit(); print('initial', sorted(counts.items()), 'new queue', db.execute('select count(*) from jobs').fetchone())
    (NEW/'accounted.bytes').write_text('0'); (NEW/'init_counts.txt').write_text(str(sorted(counts.items()))+'\n')


def worker(number,maximum):
    db = sqlite3.connect(NEW/'work.db',timeout=60,isolation_level=None); done=0
    while done<maximum:
        db.execute('begin immediate'); active=db.execute("select count(*) from jobs where status='busy'").fetchone()[0]
        with (NEW/'staging.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_SH); charged=int((NEW/'accounted.bytes').read_text())
        live=[i for i,pid in OLDPIDS.items() if running(pid)]
        excludes=','.join(map(str,live)) or '-1'; row=db.execute("select key from jobs where status='ready' and shard not in ("+excludes+") order by rowid limit 1").fetchone()
        if not row or charged+(active+1)*SLOT>LIMIT:
            ready=db.execute("select count(*) from jobs where status='ready'").fetchone()[0]; db.commit()
            if not ready or charged+SLOT>LIMIT:break
            time.sleep(2+number%3);continue
        key=row[0]; old=state(key)
        if old not in ('unstarted','staging_guard'):
            db.execute('update jobs set status=? where key=?',('old:'+old,key));db.commit();continue
        db.execute("update jobs set status='busy',worker=? where key=?",(number,key));db.commit()
        task(key,[],120,120000000,NEW,str(PROGRAM),LIMIT,BASE/'lrat-trim')
        result=json.loads((NEW/key/'progress.json').read_text())['status'];assert result!='staging_guard'
        db.execute('update jobs set status=? where key=?',(result,key));done+=1
    print('DONE',number,done,flush=True)


if __name__=='__main__':
    if sys.argv[1]=='init':init()
    else:worker(int(sys.argv[1]),int(sys.argv[2]) if len(sys.argv)>2 else 99999)
