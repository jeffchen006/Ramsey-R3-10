"""Generate a small static-domain variant of the R12 row search, with exact twin refinement."""
from pathlib import Path
import sys


def build(target):
    text=Path(__file__).with_name('flag_domain.cpp').read_text()
    def replace(before,after):
        nonlocal text
        assert text.count(before)==1;text=text.replace(before,after)
    replace('static Mask coloured=0;', 'static Rows forbidden{};static int tint[40];static Mask coloured=0;')
    replace('if(mode&4194304)for(int point=0;point<order;++point){if(lo[point]&exact_low', 'for(int point=0;point<order;++point){if(lo[point]&forbidden[point])return 0;hi[point]&=~forbidden[point];}\n        if(mode&4194304)for(int point=0;point<order;++point){if(lo[point]&exact_low')
    replace('classes[(explicit_graph[point]&fixed)|','classes[(Mask(tint[point])<<48)|(explicit_graph[point]&fixed)|')
    replace('Search search;if(!anchors', '''assert(!anchors && !(mode&131072));for(int point=0;point<order;++point)input>>forbidden[point];assert(input);
        for(int point=0;point<order;++point){tint[point]=point;for(int other=0;other<point;++other){Mask outside=~(bit(point)|bit(other));if(!((graph[point]^graph[other])&outside)&&!((forbidden[point]^forbidden[other])&outside)){tint[point]=tint[other];break;}}}
        Search search;if(!anchors''')
    target.write_text(text)


if __name__=='__main__':build(Path(sys.argv[1]))
