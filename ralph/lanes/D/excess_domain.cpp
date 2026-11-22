#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <ctime>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using Mask=std::uint64_t;
using Rows=std::array<Mask,40>;
enum Color { Edge=0, Low=1, High=2 };
static int order,degree,ell,square,anchors,mode;
static Mask all;
static Rows exceptional{};
static int edge_quota[40][40];
static inline Mask bit(int point) {return Mask(1)<<point;}
static inline int pop(Mask value) {return __builtin_popcountll(value);}
static inline int next(Mask& value) {int point=__builtin_ctzll(value);value&=value-1;return point;}
struct Conflict {int rule;};
struct Domain {
    std::array<Rows,3> may{},must{};
    bool changed=false;
    int rule=0;
    Domain() {for(auto& relation:may)for(int point=0;point<order;++point)relation[point]=all^bit(point);}
    void remove(int color,int first,Mask sites) {
        sites&=may[color][first];
        if(!sites)return;
        if(sites&must[color][first])throw Conflict{rule};
        changed=true;
        may[color][first]&=~sites;
        while(sites) {
            int second=next(sites);may[color][second]&=~bit(first);
            int other=(color+1)%3,last=(color+2)%3;
            if(!(may[other][first]&bit(second)))std::swap(other,last);
            if(!(may[last][first]&bit(second))) {
                if(!(may[other][first]&bit(second)))throw Conflict{rule};
                must[other][first]|=bit(second);must[other][second]|=bit(first);
            }
        }
    }
    void force(int color,int first,Mask sites) {
        if(sites&~may[color][first])throw Conflict{rule};
        for(int other=0;other<3;++other)if(other!=color)remove(other,first,sites);
    }
    void cardinal(int color,int point,int count) {
        int lower=pop(must[color][point]),upper=pop(may[color][point]);
        if(lower>count||upper<count)throw Conflict{rule};
        if(lower==count)remove(color,point,may[color][point]&~must[color][point]);
        if(upper==count)force(color,point,may[color][point]);
    }
    void intersection(int left,int first,int right,int second,int low,int high) {
        Mask need=must[left][first]&must[right][second],can=may[left][first]&may[right][second];
        if(pop(need)>high||pop(can)<low)throw Conflict{rule};
        if(pop(can)==low) {force(left,first,can);force(right,second,can);}
        if(pop(need)==high) {remove(left,first,must[right][second]&~need);remove(right,second,must[left][first]&~need);}
    }
    void propagate() {
        int nonedges=order-1-degree,hi=degree*(degree-1)-ell*nonedges;
        int edge_high=square-(ell-1)*(degree-1);
        do {
            changed=false;rule=1;
            for(int point=0;point<order;++point){int high_degree=hi+pop(exceptional[point]);cardinal(Edge,point,degree);cardinal(High,point,high_degree);cardinal(Low,point,nonedges-high_degree);}
            for(int first=0;first<order;++first)for(int second=0;second<first;++second) {
                rule=2;
                int low=pop(must[Edge][first]&must[Edge][second]),high=pop(may[Edge][first]&may[Edge][second]);
                int low_value=ell-int(bool(exceptional[first]&bit(second)));
                if(low)remove(Edge,first,bit(second));
                if(low>low_value||high<low_value)remove(Low,first,bit(second));
                if(low>ell+1||high<ell+1)remove(High,first,bit(second));
                int need=(may[Edge][first]&bit(second))?0:(may[Low][first]&bit(second))?low_value:ell+1;
                int room=(may[High][first]&bit(second))?ell+1:(may[Low][first]&bit(second))?low_value:0;
                intersection(Edge,first,Edge,second,need,room);
                if(!(mode&1)&&square<0&&!(mode&64))continue;
                rule=3;
                int low_f=pop(must[Edge][first]&must[High][second]),high_f=pop(may[Edge][first]&may[High][second]);
                int low_s=pop(must[Edge][second]&must[High][first]),high_s=pop(may[Edge][second]&may[High][first]);
                int off_lo=pop(must[Edge][first]&exceptional[second])-pop(may[Edge][second]&exceptional[first]);
                int off_hi=pop(may[Edge][first]&exceptional[second])-pop(must[Edge][second]&exceptional[first]);
                int lower=std::max(low_f,low_s+off_lo),upper=std::min(high_f,high_s+off_hi);
                int lower_s=std::max(low_s,low_f-off_hi),upper_s=std::min(high_s,high_f-off_lo);
                if((mode&1)&&lower>upper)throw Conflict{rule};
                if(mode&64){
                    rule=8;
                    int base=edge_quota[first][second]-(ell-1)*(degree-1);
                    int first_low=base+pop(must[Edge][first]&exceptional[second]),first_high=base+pop(may[Edge][first]&exceptional[second]);
                    int second_low=base+pop(must[Edge][second]&exceptional[first]),second_high=base+pop(may[Edge][second]&exceptional[first]);
                    if(lower>first_high||upper<first_low||lower_s>second_high||upper_s<second_low)remove(Edge,first,bit(second));
                    if(must[Edge][first]&bit(second)){
                        intersection(Edge,first,High,second,std::max(lower,first_low),std::min(upper,first_high));
                        intersection(Edge,second,High,first,std::max(lower_s,second_low),std::min(upper_s,second_high));
                    }
                }
                if(square>=0) {
                    rule=4;
                    if(lower>edge_high||upper<edge_high)remove(Edge,first,bit(second));
                    if(must[Edge][first]&bit(second)) {lower=lower_s=edge_high;upper=upper_s=edge_high;}
                }
                if((mode&1)||(square>=0&&(must[Edge][first]&bit(second)))) {
                    intersection(Edge,first,High,second,lower,upper);
                    intersection(Edge,second,High,first,lower_s,upper_s);
                }
            }
            extra();
        } while(changed);
    }
    int unknown()const {int unknown=0;for(int point=0;point<order;++point)unknown+=pop(may[Edge][point]^must[Edge][point]);return unknown/2;}
    static bool independent(const Rows& upper,Mask free,int need) {
        if(!need)return true;
        while(pop(free)>=need){int point=next(free);if(independent(upper,free&~upper[point],need-1))return true;}
        return false;
    }
    bool cycles()const {
        for(int first=0;first<order;++first){Mask edges=must[Edge][first]&~(bit(first+1)-1);
            while(edges){int second=next(edges);Mask block=(must[Edge][first]|must[Edge][second])&~(bit(first)|bit(second));
                Mask points=block;
                while(points){int point=next(points);if(pop(must[Edge][point]&block)<2)block&=~bit(point);}
                while(block){Mask old=block;points=block;while(points){int point=next(points);if(pop(must[Edge][point]&block)<2)block&=~bit(point);}if(block==old)return true;}
            }
        }
        return false;
    }
    void extra(){
        if(mode&2){rule=5;
            for(int first=0;first<order;++first){Mask others=must[Low][first]&~(bit(first+1)-1);while(others){int second=next(others);Mask common=must[Edge][first]&must[Edge][second];while(common){int point=next(common);remove(Low,point,common);}}}
        }
        if((mode&4)&&cycles())throw Conflict{6};
        if(mode&8){rule=7;if(independent(may[Edge],all,degree+1))throw Conflict{7};
            for(int first=0;first<order;++first){Mask others=may[Edge][first]&~must[Edge][first]&~(bit(first+1)-1);
                while(others){int second=next(others);Mask room=all&~(bit(first)|bit(second)|may[Edge][first]|may[Edge][second]);if(independent(may[Edge],room,degree-1))force(Edge,first,bit(second));}
            }
        }
    }
};

static Rows core_graph(std::istringstream& fields) {
    Rows graph{};
    auto edge=[&](int first,int second){graph[first]|=bit(second);graph[second]|=bit(first);};
    edge(0,1);
    for(int point=2;point<anchors;++point){edge(point%2,point);if(point+1<anchors)edge(point,point+1);}
    int index=anchors;std::string term;
    while(fields>>term){auto split=term.find(':');assert(split!=std::string::npos);auto mask=std::stoi(term.substr(0,split));auto count=std::stoi(term.substr(split+1));
        while(count--){assert(index<order);for(int point=0;point<anchors;++point)if(mask&(1<<point))edge(point,index);++index;}}
    assert(index==order);return graph;
}

struct Search {
    long budget,nodes=0;
    bool census;
    int visit(Domain domain,Mask fixed) {
        if(nodes>=budget)return -1;
        ++nodes;
        try {domain.propagate();} catch(Conflict) {return 0;}
        int selected=-1;
        std::vector<Mask> best;
        for(int pivot=0;pivot<order;++pivot) {
            if(fixed&bit(pivot))continue;
            Mask known=domain.must[Edge][pivot],unknown=domain.may[Edge][pivot]&~known;
            if(!unknown)continue;
            std::map<Mask,Mask> groups;
            while(unknown){int point=next(unknown);groups[fixed&domain.must[Edge][point]]|=bit(point);}
            std::vector<Mask> cells,rows;
            for(auto [signature,group]:groups)cells.push_back(group);
            std::vector<Mask> tail(cells.size()+1);for(unsigned idx=cells.size();idx>0;--idx)tail[idx-1]=tail[idx]|cells[idx-1];
            auto generate=[&](auto&& self,unsigned index,Mask row,int need)->void {
                if(selected>=0 && rows.size()>=best.size())return;
                if(need>pop(tail[index]))return;
                Mask sites_left=fixed;
                while(sites_left){int point=next(sites_left);Mask actual=domain.must[Edge][point];int low=pop(actual&row),high=low+std::min(need,pop(actual&tail[index]));
                    int low_value=ell-int(bool(exceptional[pivot]&bit(point)));
                    if((domain.must[Edge][pivot]&bit(point))?low!=0:((!(domain.may[High][pivot]&bit(point))||ell+1<low||ell+1>high)&&(!(domain.may[Low][pivot]&bit(point))||low_value<low||low_value>high)))return;}
                if(!need){rows.push_back(row);return;}
                if(index==cells.size())return;
                Mask sites=cells[index];
                for(;;){self(self,index+1,row,need);if(!need||!sites)break;row|=bit(next(sites));--need;}
            };
            generate(generate,0,known,degree-pop(known));
            if(rows.empty())return 0;
            if(selected<0||rows.size()<best.size()){selected=pivot;best=std::move(rows);}
            if(best.size()==1)break;
        }
        if(selected<0) {
            auto independent=[&](auto&& self,Mask sites,int need)->bool {
                if(!need)return true;
                while(pop(sites)>=need){int point=next(sites);if(self(self,sites&~domain.must[Edge][point],need-1))return true;}
                return false;
            };
            if(independent(independent,all,degree+1))return 0;
            if(census){std::cout<<"model";for(int point=0;point<order;++point)std::cout<<' '<<domain.must[Edge][point];std::cout<<'\n';return 0;}
            return 1;
        }
        for(Mask row:best){
            Domain child=domain;
            try {child.force(Edge,selected,row);child.remove(Edge,selected,all^row);} catch(Conflict){continue;}
            int status=visit(child,fixed|bit(selected));if(status)return status;
        }
        return 0;
    }
};

int main(int argc,char** argv) {
    if(argc<7||argc>9)return 2;
    order=std::stoi(argv[1]);degree=std::stoi(argv[2]);ell=std::stoi(argv[3]);square=std::stoi(argv[4]);anchors=std::stoi(argv[5]);mode=std::stoi(argv[6]);
    assert(order<=40 && order>1);all=bit(order)-1;std::string line;long index=0;
    while(std::getline(std::cin,line)) {
        std::istringstream fields(line);Domain dom;Mask fixed=0;Rows graph{};
        if(anchors) {fixed=bit(anchors)-1;graph=core_graph(fields);}
        else {fields>>fixed;for(int point=0;point<order;++point)fields>>graph[point];assert(fields);}
        exceptional.fill(0);
        if(mode&16){assert(square<0&&ell==2);for(int first=0;first<order;++first)for(int second=0;second<first;++second)if((fixed&bit(first))&&(fixed&bit(second))&&pop(graph[first]&graph[second])==1){exceptional[first]|=bit(second);exceptional[second]|=bit(first);}}
        if(mode&32){assert(square<0&&ell==2);for(int point=0;point<order;++point)fields>>exceptional[point];assert(fields);}
        if(mode&64){for(int first=0;first<order;++first)for(int second=0;second<first;++second){int quota;fields>>quota;assert(fields);edge_quota[first][second]=edge_quota[second][first]=quota;}}
        try {
            Mask rest=fixed;
            while(rest){int point=next(rest);assert(pop(graph[point])==degree);dom.force(Edge,point,graph[point]);dom.remove(Edge,point,all&~graph[point]);}
            for(int point=0;point<order;++point)dom.force(Low,point,exceptional[point]);
            if(argc>=8){Search search{std::stol(argv[7]),0,argc==9};auto start=std::clock();int status=search.visit(dom,fixed);std::cout<<index++<<' '<<status<<' '<<search.nodes<<' '<<double(std::clock()-start)/CLOCKS_PER_SEC<<'\n';continue;}
            dom.propagate();
            std::cout<<index<<" 0 "<<dom.unknown();
            if(!anchors){for(int color=0;color<3;++color)for(int point=0;point<order;++point)std::cout<<' '<<dom.may[color][point];}
            std::cout<<'\n';
        } catch(Conflict conflict){std::cout<<index<<' '<<conflict.rule<<" 0\n";}
        ++index;
    }
}
