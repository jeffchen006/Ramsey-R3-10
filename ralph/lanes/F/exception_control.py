"""Literal small physical experiment and baseline controls."""
from itertools import combinations
from pathlib import Path
import sys

from one_double_pilot import graph_build,tri_free


def oldsrc():
    source=Path(__file__).with_name('marked_price.cpp').read_text(); original='(sites==17 && dist>=6 && dist<=12)'
    assert source.count(original)==1
    source=source.replace(original,original+'||(sites==4 && dist>0)')
    Path('old.cpp').write_text('#define main old_main\n'+source+'\n#undef main\nint main(){Price old(4,5);unsigned witness;int s=old.stage(1,1,witness);std::cout<<"neg old stage "<<s<<"\\n";return s!=5;}\n')


def literal():
    for tag,ordinary,edges,contacts in [('neg',4,list(combinations(range(4),2)),[3,0,0,0]),('pos',3,[(0,1)],[0,3,3])]:
        counts=[0,0,0]; maximum=2*ordinary+2
        fives={n:list(combinations(range(n),5)) for n in (maximum,maximum-1)}
        for signs in range(1<<len(edges)):
            for verticals in range(1<<(ordinary+1)):
                full=graph_build(ordinary,edges,signs,verticals,contacts);counts[0]+=1
                for offset in (0,1):
                    order=maximum-offset; graph=[row&((1<<order)-1) for row in full[:order]]
                    if tri_free(graph) and not any(all(not(graph[a]>>b&1) for a,b in combinations(subset,2)) for subset in fives[order]):counts[1+offset]+=1
        status=Path(tag+'.status').read_text().split()[1];assert (status=='card')==(counts[1]>0)==(tag=='pos') and counts[2]>0
        print(tag,'signed controls,total/whole positives/delete-one positives',*counts)


if __name__=='__main__':{'oldsrc':oldsrc,'literal':literal}[sys.argv[1]]()
