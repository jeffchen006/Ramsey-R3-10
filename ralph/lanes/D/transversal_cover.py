"""One marked site must meet each full singleton-codegree path in the frozen core."""
import argparse
from collections import Counter
from pathlib import Path

from induced_pilot import line
from path_growth import read_profiles


def roots(source):
    for index, row in enumerate(read_profiles(source)):
        text=line(tuple(sorted(row.items())))
        neighbors=[0]*8;neighbors[0]=2;neighbors[1]=1
        for point in range(2,8):
            neighbors[point]|=1<<(point%2);neighbors[point%2]|=1<<point
            if point+1<8:neighbors[point]|=1<<(point+1);neighbors[point+1]|=1<<point
        reps=list(range(8));outside=8
        for mask,number in sorted(row.items()):
            reps.append(outside)
            for anchor in range(8):
                if mask>>anchor&1:neighbors[anchor]|=((1<<number)-1)<<outside
            outside+=number
        defects=[{left,right,(neighbors[left]&neighbors[right]).bit_length()-1} for left in range(8) for right in range(left) if not (neighbors[left]>>right&1) and (neighbors[left]&neighbors[right]).bit_count()==1]
        yield index,[(point,str(1<<point)+' '+text) for point in reps if all(point in pair for pair in defects)]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('dest',type=Path);args=parser.parse_args()
    hist=Counter()
    with (args.dest/'hub.tsv').open('w') as cases,(args.dest/'hub.ids').open('w') as ids:
        for index,options in roots(args.source):
            hist[len(options)]+=1
            for point,text in options:
                print(text,file=cases);print(index,point,file=ids)
    print('Hubplacements vs source roots',sorted(hist.items()),'total',sum(size*number for size,number in hist.items()))
