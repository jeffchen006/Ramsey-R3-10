from itertools import combinations,permutations,product
from collections import Counter
from book_strata import DEST,independent_sets
from book_controls import bitset


def cal(width,cap):
    first=[(1<<site)|(1<<((site+1)%width)) for site in range(width)];expected=set()
    for perm in permutations(range(width)):
        if perm[0] or perm[1]>perm[-1]:continue
        second=[1<<perm[i]|1<<perm[(i+1)%width] for i in range(width)];options=[[bitset(pair) for pair in combinations([idx for idx,col in enumerate(second) if not(col&row)],2)] for row in first]
        for rows in product(*options):
            if any(sum(mask>>site&1 for mask in rows)!=2 for site in range(width)):continue
            graph=[0]*(3*width)
            for i in range(width):
                for j in range(width):
                    for flag,a,b in ((first[i]>>j&1,j,width+i),(second[i]>>j&1,j,2*width+i),(rows[i]>>j&1,width+i,2*width+j)):
                        if flag:graph[a]|=1<<b;graph[b]|=1<<a
            if max(mask.bit_count() for mask in independent_sets(graph))<=cap:expected.add(perm+rows)
    actual={tuple(map(int,line.split()[1:])) for line in (DEST/f'triad-{width}-{cap}.tsv').read_text().splitlines()};assert expected==actual;return len(actual)


if __name__=='__main__':
    for width,cap in ((4,4),(5,5),(5,6),(5,7)):print('independent labelled equality',width,cap,cal(width,cap))
