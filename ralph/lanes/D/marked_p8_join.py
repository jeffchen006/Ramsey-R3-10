"""Small conditional join of induced P8s. Refuse an unpriced source."""

import argparse
from collections import Counter
from itertools import product
from pathlib import Path

from hub_lift import survey
from induced_pilot import catalog,children,flip,line


def run(source,library,dest):
    tables,directed=catalog(source);groups=tables[0].keys()&tables[1].keys();pairs=sum(len(tables[0][key])*len(tables[1][key])for key in groups);assert pairs<=25000
    found=set();stats=Counter();labelled=0
    for common in groups:
        for (_,left),(_,right) in product(tables[0][common],tables[1][common]):
            for key in children(common,left,right,stats):found.add(min(key,flip(key)));labelled+=1
    assert labelled==sum(1+(key!=flip(key))for key in found)
    raw=dest.with_suffix('.unmarked');raw.write_text(''.join(line(key)+'\n'for key in sorted(found)));print('oriented parents',directed,'matched pairs',pairs,'unmarked labelled',labelled,'orbits',len(found));survey(raw,library,10,dest)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('library',type=Path);parser.add_argument('dest',type=Path);args=parser.parse_args();run(args.source,args.library,args.dest)
