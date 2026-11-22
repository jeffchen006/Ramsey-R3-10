"""Bind original four-star indices and six-star front ordinals before running joins."""
import json
import sys
from pathlib import Path
from collections import Counter
from book_controls import book,bitset,sites
from kernel_cnf import ROOT


def write(dest,tag,rows):
    (dest/(tag+'.in')).write_text(''.join(json.dumps(row,separators=(',',':'))+'\n' for row in rows));print(tag,len(rows))


def inputs(dest):
    folder=ROOT/'scratch/D';source=(folder/'ind10/four-40.in').read_text().splitlines();kept=(folder/'flag12/disjoint102.in').read_text().splitlines()
    target=[(source.index(row),list(map(int,row.split())),None) for row in kept];assert len(target)==102
    write(dest,'roots',target);square=[row for row in target if row[0] in (189,190,191)];assert len(square)==3;write(dest,'square',square)
    two_list=(folder/'flag12/two/old-live.in').read_text().splitlines();two_set=set(two_list);two=[row for row in target if source[row[0]] in two_set];write(dest,'two',two)
    parents=(folder/'ind10/four-open-live.in').read_text().splitlines();children={};current=[]
    for line in (folder/'wit11/all3840.out').read_text().splitlines():
        if line.startswith('child '):current.append(list(map(int,line.split()[1:])))
        else:
            idx=int(line.split()[0]);children[source.index(parents[idx])]=current;current=[]
    assert not current
    for name,ids in [('general-panel',[target[idx][0] for idx in (0,24,49,64,78,93,99,101)]),('square-front',[189,190,191])]:
        rows=[];panel=[]
        for pid in ids:
            front=children[pid];choices={0,len(front)//4,len(front)//2,3*len(front)//4,len(front)-1}
            for pos,frame in enumerate(front):
                record=([pid,pos],frame,None);rows.append(record)
                if pos in choices:panel.append(record)
        write(dest,name,rows);write(dest,name+'-price',panel)
    frames=[]
    for host,first,second,third,fourth,truth in map(json.loads,(dest/'panel.jsonl').read_text().splitlines()):
        anchors=bitset((*book(truth,(0,1))[0],*book(truth,(2,3))[0]))
        frames.append(([host,first,second,third,fourth],[anchors,*[row if anchors>>pos&1 else row&anchors for pos,row in enumerate(truth)]],truth))
    write(dest,'cal',frames)


if __name__=='__main__':inputs(Path(sys.argv[1]))
