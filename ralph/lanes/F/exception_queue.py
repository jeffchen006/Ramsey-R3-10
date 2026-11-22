"""Freeze disjoint signed-row shards, then meter each isolated stage."""
from pathlib import Path
import subprocess
import sys
from round20_census import load,totals


def prepare():
    rows=sorted(row for row in load('../r21/mark.left') if row[1]); assert len(rows)==405
    pilot={(1952,544),(4064,1088),(1936,128)}
    for first,second in pilot:assert Path(f'{first}_{second}.status').is_file()
    rest=[row for row in rows if row[:2] not in pilot];assert len(rest)==402
    for index,shard in enumerate((rest[::2],rest[1::2])):
        Path(f'shard{index}.tsv').write_text(''.join(f'{first} {second} {weight}\n' for first,second,weight in shard))
    print('frozen reps/labels/fixed',totals(rows),'3 pilot + 201 + 201')


def run(index):
    lane=Path(__file__).parent
    for first,second,weight in [line.split() for line in Path(f'shard{index}.tsv').read_text().splitlines()]:
        tag=f'{first}_{second}'; assert not Path(tag+'.status').exists()
        if sum(p.stat().st_size for p in Path().iterdir() if p.is_file())>400_000_000:print('stage reservation cap',flush=True);break
        with open(tag+'.log','w') as out:
            proc=subprocess.run(['/usr/bin/time','-f','%U %S %M %x','-o',tag+'.time','timeout','55','prlimit','--cpu=45:48','--',sys.executable,'-B',lane/'exception_sign.py',tag],stdout=out,stderr=subprocess.STDOUT)
        print(tag,'exit',proc.returncode,Path(tag+'.status').read_text().strip() if Path(tag+'.status').exists() else 'OPEN',flush=True)


if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else run(int(sys.argv[1]))
