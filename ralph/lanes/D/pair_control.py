"""Verify the complete colour domain of known graphs after arbitrary star pins."""
import argparse
import random
import subprocess
from pathlib import Path


def run(binary, graph, ell, square, mode):
    order = len(graph)
    degree = graph[0].bit_count()
    all_sites = (1<<order)-1
    actual = [graph, [0]*order, [0]*order]
    for first, neighbors in enumerate(graph):
        for second, other in enumerate(graph):
            if first == second or neighbors>>second&1:
                continue
            value = (neighbors & other).bit_count()-ell
            assert value in (0,1)
            actual[1+value][first] |= 1<<second
        if square >= 0:
            assert all((neighbors & actual[2][second]).bit_count() == square-(ell-1)*(degree-1) for second in range(first) if neighbors>>second&1)
    rng = random.Random(9068412)
    pins = {0,all_sites,*(1<<point for point in range(order)),*(rng.getrandbits(order) for _ in range(100))}
    records = ''.join(' '.join(map(str,(mask,*graph)))+'\n' for mask in sorted(pins))
    cmd = [str(binary),str(order),str(degree),str(ell),str(square),'0',str(mode)]
    rows = subprocess.check_output(cmd, input=records, text=True).splitlines()
    forced = 0
    assert len(rows) == len(pins)
    for mask, text in zip(sorted(pins),rows):
        fields = list(map(int,text.split()));assert fields[1]==0 and len(fields)==3+3*order
        for color, truth in enumerate(actual):
            for point, row in enumerate(truth):
                possible = fields[3+color*order+point]
                assert row & ~possible == 0, (mask,color,point)
                if mask==all_sites:
                    assert row == possible
        forced += int(fields[2]==0)
    bad = cmd.copy();bad[4] = str(square+1 if square>=0 else 0)
    invalid = subprocess.check_output(bad,input=' '.join(map(str,(all_sites,*graph)))+'\n',text=True)
    assert invalid.split()[1]!='0'
    print('PASS',order,degree,ell,square,mode,'planted-domain inclusions',len(rows),'fully resolved',forced,'wrong square quota rejected')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary',type=Path);args=parser.parse_args()
    for mode in (0,1):
        run(args.binary,[sum(1<<((point+step)%13) for step in (-5,-1,1,5)) for point in range(13)],1,2,mode)
        run(args.binary,[sum(1<<(point^mask) for mask in (1,2,4,8,15)) for point in range(16)],2,4,mode)
