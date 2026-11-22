"""Independent labelled cover audit and ordered stage binding for round 10."""

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path

from defect_triangle import canonical,template
from induced_pilot import line
from path_growth import fixed_graph,read_profiles
from punct_path import profile_key


def check_sources(dest):
    full=(dest/'six.tsv').read_text().splitlines();assert len(full)==len(set(full))==2434
    hubs=set((dest/'hub.tsv').read_text().splitlines());assert len(hubs)==27289
    allow=set((dest/'hub1/live.tsv').read_text().splitlines());expected=set((dest/'exactpair.tsv').read_text().splitlines());assert len(expected)==4741
    generated=set();generated_pair=set();marked_counts=Counter()
    for idx,record in enumerate(read_profiles(dest.parent/'punct8/path.tsv')):
        original=fixed_graph(record);anchors=(4,0,1,7,2,5,3,6)
        masks=[sum(1<<pos for pos,pin in enumerate(anchors) if row>>pin&1) for row in original[8:]]
        sites=anchors+tuple(sorted(range(8,40),key=lambda vertex:masks[vertex-8]));key=line(profile_key(Counter(masks)));assert key==full[idx]
        graph=[sum(1<<pos for pos,other in enumerate(sites) if original[vertex]>>other&1) for vertex in sites]
        weak=[{first,second} for first,second in combinations(range(8),2) if (graph[first]&graph[second]).bit_count()==1]
        reps=[point if point<8 else 8+graph[8:].index(graph[point]) for point in range(40)]
        for point in range(40):
            if all(point in pair for pair in weak):generated.add(f'{1<<reps[point]} {key}')
        permitted=[point for point in range(40) if f'{1<<reps[point]} {key}' in allow]
        for first,second in combinations(permitted,2):
            if any(pair!={first,second} for pair in weak) or graph[first]>>second&1:continue
            value=(graph[first]&graph[second]).bit_count()
            if value>1 or (second<8 and value!=1):continue
            a,b=reps[first],reps[second];b+=int(a==b)
            generated_pair.add(f'{(1<<a)|(1<<b)} {key}')
        marked_counts[len(weak)]+=1
    assert generated==hubs and generated_pair==expected
    print('PASS independent reindex of 2434 P6s, all 40 labelled hub positions and 780 unordered pair positions; exact 27289 and 4741. Anchor-defect histogram',dict(sorted(marked_counts.items())))


def direct_triangle(dest):
    core=template();room={};deg=[9-len(row) for row in core]
    for a,b in combinations(range(6),2):
        if b not in core[a]:room[a,b]=(1 if b<3 else 3)-len(core[a]&core[b])
    masks=[]
    for size in (6,5,4,3,2):
        for sub in combinations(range(6),size):
            edges=list(combinations(sub,2))
            if all(room.get(pair,0)>0 for pair in edges):masks.append((sum(1<<p for p in sub),sub,edges))
    table={};hits=0;keys=set()
    def visit(index,slots):
        nonlocal hits
        if index==len(masks):
            if sum(deg)>slots:return
            if any(value>1 for (a,b),value in room.items()if b>=3):return
            row=Counter(table);row[0]=slots-sum(deg)
            for point,amount in enumerate(deg):row[1<<point]=amount
            keys.add(canonical(profile_key(+row)));hits+=1;return
        mask,sub,pairs=masks[index];limit=min([slots]+[deg[p] for p in sub]+[room[pair]for pair in pairs]);
        for num in range(limit+1):
            table[mask]=num
            for p in sub:deg[p]-=num
            for pair in pairs:room[pair]-=num
            visit(index+1,slots-num)
            for p in sub:deg[p]+=num
            for pair in pairs:room[pair]+=num
        del table[mask]
    visit(0,34);actual=set((dest/'tri.keys').read_text().splitlines());assert hits==136 and {line(key)for key in keys}==actual and len(keys)==44
    print('PASS direct independent six-anchor mask recursion',hits,'labelled,',len(keys),'S3 orbits')


def rows(path):return path.read_text().splitlines()


def stage(dest,name,chunks,source,target,records):
    whole=[];caps=[];nodes=0;cpu=0
    for inp,out in chunks:
        inputs=rows(dest/inp);outputs=rows(dest/out);assert len(inputs)==len(outputs)
        for idx,(text,answer) in enumerate(zip(inputs,outputs)):
            words=answer.split();assert len(words)==4 and int(words[0])==idx and words[1] in ('-1','0');whole.append(text);cap=words[1]=='-1'
            if cap:caps.append(text)
            nodes+=int(words[2]);cpu+=float(words[3]);records.append('\t'.join((name,str(inp),str(out),str(idx),sha256(text.encode()).hexdigest(),*words[1:])))
    assert rows(dest/source)==whole and (not caps if target is None else rows(dest/target)==caps)
    print(name,'source',len(whole),'terminal',len(whole)-len(caps),'capped',len(caps),'nodes',nodes,'CPU-s',round(cpu,3))


def bind(dest):
    records=[]
    def singles(name,source,out,tgt):stage(dest,name,[(source,out)],source,tgt,records)
    def parts(name,prefix,source,tgt):
        chunks=[(p.relative_to(dest),p.relative_to(dest).with_suffix('.out'))for p in sorted((dest/name).glob(prefix+'[0-9][0-9]'))];stage(dest,name,chunks,source,tgt,records)
    singles('no1-colour','six.tsv','full6--1.out','tail6.tsv');singles('no1-tail','tail6.tsv','tail6.out',None);singles('no1-graph','six.tsv','audit6.out',None)
    parts('hub1','h','hub.tsv','hub1/live.tsv');parts('pair1','p','exactpair.tsv','pair1/live.tsv');singles('pair2','pair1/live.tsv','pair1/joint.out','pair1/six.tsv');singles('pair3','pair1/six.tsv','pair1/end.out',None)
    for index in range(2,10):
        name=f'hub{index}'
        if not (dest/name/'live.tsv').is_file():break
        parts(name,'h',f'hub{index-1}/live.tsv',name+'/live.tsv')
    if (dest/'tri-tail.out').is_file():
        singles('tri1','tri.in','tri-all.out','tri-tail.in');singles('tri2','tri-tail.in','tri-tail.out',None)
    if (dest/'four-open-live.in').is_file():
        singles('four-general','four-40.in','four-open.out','four-open-live.in');singles('four-exact2','four-40.in','four2.out','four2-tail.in')
    (dest/'terminal.tsv').write_text('stage\tinput\toutput\tordinal\tinput_sha256_no_LF\tstatus\tnodes\tcpu\n'+'\n'.join(records)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('dest',type=Path);args=parser.parse_args();check_sources(args.dest);direct_triangle(args.dest);bind(args.dest)
