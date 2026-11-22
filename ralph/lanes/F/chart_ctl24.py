from pathlib import Path
import json,subprocess
from front24 import BASE,ROOT,BIN
from eight_chart import roots
from orbit_extend import parse_graph6
from six_five import encode
from cards24 import gate

def main():
    first=232982*2;last=first+2;seen={}
    for path in (ROOT/'scratch/F/r23/chart').glob('*.jsonl'):
        for line in path.open():
            item=json.loads(line);assert item['rc']==0 and item['status']=='complete'
            for row in item['rows']:
                key=int(row[0]);assert key not in seen;seen[key]=row[1]!='bare'
    for key in roots():assert key not in seen;seen[key]=True
    scope=set(range(first*2048,last*2048));assert scope<=seen.keys();want=sorted(key for key in scope if seen[key]);run=subprocess.run(['timeout','25','prlimit','--cpu=20','--','./sieve','768',str(first),str(last),'compare.count'],capture_output=True,text=True,check=True);got=list(map(int,run.stdout.split()));assert got==want
    known=parse_graph6((ROOT/'ralph/lanes/F/round1_seed39.g6').read_text().strip());low=(1<<31)-1;data=encode('known39',[row&low for row in known[:31]],10,False,[row&low for row in known[31:]]);run=subprocess.run(['timeout','25','prlimit','--cpu=20','--',BIN,'300000'],input=data,capture_output=True,text=True,check=True);row=run.stdout.split();assert 'model' in row;gate(list(map(int,row[row.index('graph')+1:])),10,Path('known39.g6'))
    print('matched independent physical bare-key sweep on all',len(scope),'words; exactly',len(got),'survive; gated positive 31+8 control')
if __name__=='__main__':main()
