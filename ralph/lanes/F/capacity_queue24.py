from pathlib import Path
from datetime import datetime
import json,sys,subprocess,resource,time
from cards24 import ROOT,DIR

def main():
    plan=Path('manifest.keys').read_text().split();lastclock=0;lastcpu=0
    for name in plan:
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic()
        with open(name+'.stdout','x') as out,open(name+'.err','x') as err:job=subprocess.run(['timeout','105','prlimit','--cpu=90:95','--',sys.executable,'-B',ROOT/'ralph/lanes/F/capacity24.py','solve',name],stdout=out,stderr=err)
        text=Path(name+'.stdout').read_text().splitlines();state='open' if job.returncode or not text else 'dual' if text[-1].startswith('dual verified ') else 'LP_not_excluding';after=resource.getrusage(resource.RUSAGE_CHILDREN);cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
        with open('worker.jsonl','a') as log:print(json.dumps(dict(name=name,rc=job.returncode,state=state,cpu=round(cpu,5),wall=round(time.monotonic()-start,5),summary=text[-1:])),file=log)
        if time.monotonic()-lastclock>240:
            size=int(subprocess.run(['du','-sb',DIR.parent],capture_output=True,text=True).stdout.split()[0]);total=after.ru_utime+after.ru_stime;lastclock=time.monotonic()
            with open('meter.tsv','a') as out:print(datetime.now().astimezone().isoformat(timespec='seconds'),name,round(total-lastcpu,5),size,40000000,file=out)
            lastcpu=total
            if size>250000000:return
if __name__=='__main__':main()
