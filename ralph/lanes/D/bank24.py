import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from closure22 import ROOT,stage,digest
from wing24 import OUT

def prune(binary,target):
    trim=ROOT/'scratch/D/m14r22/lrat-trim';runner=subprocess.Popen([str(trim),'-a','input.cnf',binary,'/dev/stdout'],stdout=subprocess.PIPE,stderr=sys.stderr.buffer);dropped=kept=0
    with Path(target).open('wb') as stream:
        for line in runner.stdout:
            if line[:1].isdigit():
                if b' d ' in line[:40]:dropped+=1
                else:stream.write(line);kept+=1
            else:sys.stdout.buffer.write(line)
    code=runner.wait();print('retained additions',kept,'omitted deletion lines',dropped,flush=True);return code

def test(key):
    sub=OUT/key;row=json.loads((sub/'result.json').read_text());assert row['status']=='dual_checked'
    with TemporaryDirectory(dir=OUT) as temp:
        os.chdir(temp);result=stage('bind',[sys.executable,'-B',Path(__file__).with_name('work24.py'),'bind',key],45,19000000);assert result['ok'] and digest('input.cnf')==row['files']['input.cnf'][0]
        result=stage('unpack',['zstd','-dq',sub/'proof.zst','-o','old.lrat'],60,55000000);assert result['ok'];filtered=Path('proof.lrat')
        with Path('old.lrat').open('rb') as source,filtered.open('wb') as dest:
            for line in source:
                if b' d ' not in line[:40]:dest.write(line)
        for name,cmd,marker in [('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],'s VERIFIED UNSAT'),('pack',['zstd','--single-thread','-7','-q','proof.lrat','-o','proof.zst'],None)]:
            step=stage(name,cmd,120,25000000,0,marker);assert step['ok'],(key,name,step)
        print(key,row['files']['proof.zst'][1],Path('proof.zst').stat().st_size,flush=True);os.chdir(OUT)

def compact(path):
    original=Path(path).stat().st_size
    with open(path,'rb') as source:
        for line in source:
            if b' d ' in line[:40]:continue
            _,sep,hints=line.partition(b' 0 ')
            if not sep or b'-' in hints:print('unchanged, possible RAT line',original);return
    with open(path,'rb') as source,open(path,'r+b') as dest:
        for line in source:
            if b' d ' not in line[:40]:dest.write(line)
        dest.truncate();print('deletion-free bytes',original,dest.tell(),flush=True)

if __name__=='__main__':
    if sys.argv[1]=='compact':compact(sys.argv[2])
    elif sys.argv[1]=='trim':sys.exit(prune(sys.argv[2],sys.argv[3]))
    else:
        for key in sys.argv[2:]:test(key)
