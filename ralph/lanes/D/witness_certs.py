"""Produce and dual-check each tiny triangle/independent-set CNF; bind proof and input."""
from hashlib import sha256
from pathlib import Path
import resource
import subprocess
import sys


def digest(path):return sha256(path.read_bytes()).hexdigest()


def check(directory, part, total, stop):
    tools=Path(__file__).resolve().parents[3]/'opt/bin';used=0
    with (directory/f'certs-{part}-{total}-{stop}.tsv').open('w') as record:
        for index,line in enumerate((directory/'witnesses.tsv').read_text().splitlines()):
            if index%total!=part or (stop and used>=stop):continue
            tag,child,vertices,reason,cnf_sha=line.split('\t');form=directory/f'{tag}.cnf';proof=form.with_suffix('.lrat');assert digest(form)==cnf_sha
            logged=[]
            for name,args,code,message in [('cadical',['-q','-n','--lrat','--no-binary',form,proof],20,b'UNSATISFIABLE'),('lrat-check',[form,proof],0,b'c VERIFIED'),('cake_lpr',[form,proof],0,b's VERIFIED UNSAT')]:
                result=subprocess.run(['nice','-n','5','timeout','25','prlimit','--cpu=15:16',tools/name,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT);assert result.returncode==code and message in result.stdout,(tag,name,result.returncode,result.stdout)
                log=form.with_suffix('.'+name+'.log');log.write_bytes(result.stdout);logged.append(digest(log))
            print(tag,child,cnf_sha,digest(proof),*logged,sep='\t',file=record,flush=True);used+=1
    stats=resource.getrusage(resource.RUSAGE_CHILDREN);print('dual accepted',used,'child CPU-s',round(stats.ru_utime+stats.ru_stime,4))


if __name__=='__main__':check(Path(sys.argv[1]),*map(int,sys.argv[2:]))
