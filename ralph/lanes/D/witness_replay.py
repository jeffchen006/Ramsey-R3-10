"""Rebuild check: bind per-stage samples to exact verdict/node pairs, ignoring timing."""
import os
from pathlib import Path
import subprocess
import sys


def check(folder,binary):
    stages=[('mono7',9,16385,120,None),('mono7b',9,278529,450,'mono7'),('mono8',10,16385,420,None),('mono8b',10,3686401,300,'mono8'),('mono8c',10,3686401,650,'mono8b'),('limit8',10,37240833,650,'mono8b'),('limit8b',10,37240833,6000,'limit8'),('mono9',11,16385,1300,None),('mono9a',11,3686401,5000,'mono8c'),('mono9b',11,137379841,5000,'mono9'),('mono9plain',11,16385,22000,None)]
    for name,width,mode,cap,deck in stages:
        if name=='mono9b':mode=134217728+1048576+2097152+16385
        rows=[];expect=[]
        for shard in sorted((folder/name).glob('p[0-9][0-9]')):
            lines=shard.read_text().splitlines();outs=shard.with_suffix('.out').read_text().splitlines();assert len(lines)==len(outs)
            for index in {0,len(lines)//2,len(lines)-1}:
                rows.append(lines[index]);expect.append(outs[index].split()[1:3])
        cmd=['nice','-n','5','timeout','60','prlimit','--cpu=45:46',binary,'40','9',str(width),'4','1',str(mode),str(cap)]
        if deck:cmd.append(folder/deck/'live.tsv')
        result=subprocess.run(cmd,input='\n'.join(rows)+'\n',text=True,capture_output=True,check=True);assert [line.split()[1:3] for line in result.stdout.splitlines()]==expect,name
        print(name,'PASS',len(rows),'exact verdict+nodes from shipped source',flush=True)


if __name__=='__main__':check(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
