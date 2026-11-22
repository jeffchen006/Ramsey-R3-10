"""One bounded proof-producing pilot, or verification against archived proofs."""
import gzip,hashlib,json,math,os,resource,subprocess,sys,time
from pathlib import Path
from middle16_cnf import target
from middle16_roster import SCOUT,ROOT
sys.path.insert(0,str(SCOUT))
import fixedstars

BIN=ROOT/'opt/bin'
def cpu():
    children=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+children.ru_utime+children.ru_stime

def digest(data):return hashlib.sha256(data).hexdigest()

def program(args,returncode,marker,out,tag,remaining):
    before=cpu();limit=max(1,math.floor(remaining));assert remaining>0
    result=subprocess.run(['timeout','24','prlimit',f'--cpu={limit}:{limit+1}','--fsize=16777216:16777216','--',*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    elapsed=cpu()-before
    (out/f'{tag}.{args[0].name}.log').write_bytes(result.stdout)
    if result.returncode!=returncode or marker not in result.stdout.splitlines():
        raise RuntimeError(f'{tag} {args[0]} status={result.returncode} expected={returncode}/{marker!r}')
    return elapsed

def check_one(rec,out,archive=None):
    tag=f"{rec['kind']}-{rec['host']}-{rec['id']}";result=dict(tag=tag,host=rec['host'],id=rec['id'],weight=rec['weight'],kind=rec['kind']);start=cpu()
    first=out/'producer.cnf';second=out/'rebound.cnf';proof=out/'unpacked.lrat'
    left,right=rec['word'][:2],rec['word'][2:]
    fixedstars.run([rec['Y'],fixedstars.fromprofile(*left),fixedstars.fromprofile(*right)],7,17,9,16,1,rules=1,export=first)
    result['encode']=cpu()-start;tick=cpu();target(rec,second);source=first.read_bytes();assert source==second.read_bytes(),tag
    result.update(rebind=cpu()-tick,cnf_bytes=len(source),cnf_sha=digest(source),cnf_gzip=len(gzip.compress(source,compresslevel=1,mtime=0)))
    if rec['kind']=='tail':assert source==(SCOUT/f"tail-{rec['host']}-{rec['old']}.cnf").read_bytes()
    if archive is None:
        result['produce']=program([BIN/'cadical','--lrat','--no-binary',first,proof],20,b's UNSATISFIABLE',out,tag,10-(cpu()-start))
    else:
        proof.write_bytes(gzip.decompress((archive/f'{tag}.lrat.gz').read_bytes()))
    for tool,marker in [('cake_lpr',b's VERIFIED UNSAT'),('lrat-check',b'c VERIFIED')]:
        result[tool]=program([BIN/tool,second,proof],0,marker,out,tag,10-(cpu()-start))
    raw=proof.read_bytes();tick=cpu();packed=gzip.compress(raw,compresslevel=1,mtime=0)
    result.update(pack=cpu()-tick,proof_bytes=len(raw),gzip_bytes=len(packed),proof_sha=digest(raw))
    if archive is None:(out/f'{tag}.lrat.gz').write_bytes(packed)
    if rec['kind']=='tail':result['matches_old_lrat']=(SCOUT/f"tail-{rec['host']}-{rec['old']}.lrat").read_bytes()==raw
    for path in (first,second,proof):path.unlink()
    result['total']=cpu()-start;assert result['total']<=10 and sum(path.stat().st_size for path in out.iterdir() if path.is_file())<480*2**20
    return result

def main():
    out=Path(sys.argv[1]).resolve();data=Path(sys.argv[2]).resolve();archive=Path(sys.argv[3]).resolve() if len(sys.argv)>3 else None
    out.mkdir(exist_ok=True,parents=True);rows=[json.loads(line) for line in data.read_text().splitlines()];rows.sort(key=lambda row:row['kind']!='tail');assert len(rows)<=157
    start=cpu()
    for rec in rows:
        assert cpu()-start<800
        print(json.dumps(check_one(rec,out,archive)),flush=True)

if __name__=='__main__':main()
