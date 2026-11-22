"""Collapse exact weighted-quotient isomorphisms, saving an explicit map for every row."""

from argparse import ArgumentParser
from pathlib import Path
from dihedral_source import canon
from relift_audit import decode


PREVIOUS=['../r8/target.q','../r9/target.q','../r9/bitarget.q']


def maps(tag,old):
    oldrows=[text for name in PREVIOUS for text in Path(name).read_text().splitlines()] if old else []
    table={}
    for index,text in enumerate(oldrows):
        key,order=canon(decode(text));table[key]=('old',index,order)
    fresh=0;counts={'old':0,'new':0}
    with open(tag+'.rows') as source,open(tag+'.q','w') as rows,open(tag+'.maps','w') as out:
        for row in source:
            number,mass,text=row.split();key,order=canon(decode(text))
            if key not in table:
                print(text,file=rows);table[key]=('new',fresh,order);fresh+=1
            group,index,dest=table[key];counts[group]+=1
            mapping=[0]*len(order)
            for orig,image in zip(order,dest):mapping[orig]=image
            print(number,group,index,','.join(map(str,mapping)),file=out)
    print(tag,counts,'distinct new',fresh,'indexed previous',len(oldrows),flush=True)


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('tag');parser.add_argument('--old',action='store_true');args=parser.parse_args();maps(args.tag,args.old)
