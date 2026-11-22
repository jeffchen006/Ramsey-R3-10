"""Fresh-binary deterministic replay: bind verdicts and node counts, not clocks."""
from pathlib import Path
import subprocess
import sys


def compare(executable,argv,input_rows,expected):
    finished=subprocess.run(['nice','-n','5','timeout','80','prlimit','--cpu=65:66',executable,*map(str,argv)],input='\n'.join(input_rows)+'\n',text=True,capture_output=True,check=True)
    actual=[line.split()[1:3] for line in finished.stdout.splitlines()];assert actual==expected


def mixed(folder):
    caps=[500,1200,1900,3000,5000];path=folder/'trans'
    for index,cap in enumerate(caps,1):
        directory=path/f'level{index}';sample=[];expected=[]
        for shard in sorted(directory.glob('p[0-9][0-9]')):
            inputs=shard.read_text().splitlines();outputs=shard.with_suffix('.out').read_text().splitlines()
            for pos in ({0,len(inputs)//2,len(inputs)-1} if index<5 else range(len(inputs))):sample.append(inputs[pos]);expected.append(outputs[pos].split()[1:3])
        arguments=[40,9,8,160,9,5 if index==1 else 269,cap]+([] if index==1 else [path/f'level{index-1}'/'live.tsv'])
        compare(folder/'recheck-trans',arguments,sample,expected);print('PASS mixed stage',index,len(sample),'verdict/node pairs')


def dense(folder):
    for name,cap in [('dense500',500),('dense3500',3500),('dense18000',18000)]:
        sample=[];expected=[]
        for shard in sorted((folder/name).glob('p[0-9][0-9]')):
            inputs=shard.read_text().splitlines();outputs=shard.with_suffix('.out').read_text().splitlines()
            for pos in ({0,len(inputs)//2,len(inputs)-1} if cap<18000 else range(len(inputs))):sample.append(inputs[pos]);expected.append(outputs[pos].split()[1:3])
        compare(folder/'recheck-dense',[40,9,0,4,3,4194305,cap],sample,expected);print('PASS dense',name,len(sample),'verdict/node pairs')
    rows=(folder/'pendant/c40.in').read_text().splitlines();truth=(folder/'pendant/all.out').read_text().splitlines();compare(folder/'recheck-dense',[40,9,0,4,3,4194305,6000],rows,[row.split()[1:3]for row in truth]);compare(folder/'recheck-dense',[40,9,0,4,3,4194305,50000],[rows[10]],[['0','6147']]);print('PASS all 42 pendant inputs and last deep reply')


if __name__=='__main__':
    directory=Path(sys.argv[1]).resolve();mixed(directory);dense(directory)
