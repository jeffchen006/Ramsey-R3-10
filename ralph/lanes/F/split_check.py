"""Require a complete binary decision tree; independently verify every leaf's packing."""

from argparse import ArgumentParser
from pathlib import Path
from odd_check import verify


def tree(text,order,stream,conditions):
    fields=next(stream).split()
    if fields[0]=='L':
        assert int(fields[1])==verify(text,order,fields[2:],conditions);return [(int(fields[1]),len(conditions))]
    assert len(fields)==3 and fields[0]=='B';upper,lower=map(int,fields[1:]);assert 0<=upper<1<<63 and 0<=lower<1<<64
    linear=(upper<<64)|lower
    return tree(text,order,stream,conditions+[(linear,0)])+tree(text,order,stream,conditions+[(linear,1)])


def check(rows,order,cert,log,threshold):
    totals=[];nodes=[];heights=[];stream=iter(cert)
    assert len(log)==len(rows)
    for index,(text,record) in enumerate(zip(rows,log)):
        assert next(stream)==f'ROW {index}';result=tree(text,order,stream,[]);minimum=min(value for value,_ in result);maximum=max(depth for _,depth in result)
        assert tuple(map(int,record.split()))==(index,minimum,len(result),sum(value<threshold for value,_ in result),maximum)
        totals.append(minimum);nodes.append(len(result));heights.append(maximum)
    assert next(stream,None) is None
    return totals,nodes,heights


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('source');parser.add_argument('order',type=int);parser.add_argument('prefix');parser.add_argument('threshold',type=int);args=parser.parse_args();assert __debug__
    read=lambda name:Path(name).read_text().splitlines()
    totals,leaves,depth=check(read(args.source),args.order,read(args.prefix+'.tree'),read(args.prefix+'.out'),args.threshold)
    print(args.prefix,'rows',len(totals),'reach threshold',sum(value>=args.threshold for value in totals),'minimum',min(totals),'leaves',sum(leaves),'maximum depth',max(depth),flush=True)
