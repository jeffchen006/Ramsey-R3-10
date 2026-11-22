"""Bonferroni footprint bound from one book toward the other, before the interface is filled."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json,sys
from book_controls import bitset,sites


def standard(type_rows):
    size=len(type_rows);graph=[0]*(3+2*size)
    def edge(first,second):graph[first]|=1<<second;graph[second]|=1<<first
    edge(0,1);edge(0,2)
    for idx,row in enumerate(type_rows):
        edge(1,3+idx);edge(2,3+size+idx)
        for pos in sites(row):edge(3+idx,3+size+pos)
    return graph


def scores(graph,degree):
    size=len(graph);res=[degree-row.bit_count() for row in graph];limits=[[0]*size for _ in graph]
    for first,second in combinations(range(size),2):
        if graph[first]>>second&1:continue
        limit=1 if (first,second)==(1,2) else 3;limits[first][second]=limits[second][first]=limit-(graph[first]&graph[second]).bit_count();assert limits[first][second]>=0
    result=[0]*(1<<size)
    for word in range(1,1<<size):
        site=word&-word;point=site.bit_length()-1;rest=word^site;result[word]=result[rest]+res[point]-sum(limits[point][other]for other in sites(rest))
    return result


def main(folder):
    plants=list(map(json.loads,(folder/'cal.in').read_text().splitlines()));packs=list(map(json.loads,(folder/'cal-pack2.jsonl').read_text().splitlines()));checked=0
    for (_,_,truth),record in zip(plants,packs,strict=True):
        books=[]
        for (a,b),petals in zip(((0,1),(2,3)),record['bouquet']):
            cen,=sites(truth[a]&truth[b]);books.append([cen,a,b,*[edge[0] for edge in petals],*[edge[1] for edge in petals]])
        for side,points in enumerate(books):
            internal=[bitset(idx for idx,point in enumerate(points) if truth[site]>>point&1)for site in points];other=books[1-side]
            for word,bound in enumerate(scores(internal,6)):
                count=sum(any(truth[points[idx]]>>site&1 for idx in sites(word)) for site in other);assert count>=bound-(22-2*len(points));checked+=1
    print('PASS planted individual subset footprints',checked);hist=Counter();table=[]
    for line in (folder/'booktypes4.tsv').read_text().splitlines():
        *rows,_=map(int,line.split());values=scores(standard(rows),9);bound=max(values)-18;hist[bound]+=1;word=values.index(max(values));table.append([rows,word,bound])
    (folder/'book-footprints.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in table));print('guaranteed distinct opposite sites touched, by type:',dict(sorted(hist.items())))
    for record in map(json.loads,(folder/'outside-panel.jsonl').read_text().splitlines()):
        if not record['general']:continue
        graph=record['rows'];rows=[]
        for off in (0,11):
            inside=[(graph[off+idx]>>off)&2047 for idx in range(11)];cross=[(graph[off+idx]>>(11-off))&2047 for idx in range(11)];metrics=[]
            for word,bound in enumerate(scores(inside,9)):
                touched=0
                for site in sites(word):touched|=cross[site]
                metrics.append(bound-18-touched.bit_count())
            rows.append(max(metrics))
        print('labelled core',record['cross'],'max Bonferroni violations, both orientations',*rows)


if __name__=='__main__':main(Path(sys.argv[1]))
