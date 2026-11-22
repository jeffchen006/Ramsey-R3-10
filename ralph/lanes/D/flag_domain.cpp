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
static int order,degree,anchors,defect,local,mode;
static long budget;
static Mask all,marked;
static Rows exact_low{};
static Mask coloured=0;
static int project=0,depth=0;
static Mask bit(int point){return Mask(1)<<point;}
static int count(Mask mask){return __builtin_popcountll(mask);}
static int take(Mask& mask){int point=__builtin_ctzll(mask);mask&=mask-1;return point;}
static void join(Rows& graph,int first,int second){graph[first]|=bit(second);graph[second]|=bit(first);}
static void cut(Rows& graph,int first,int second){graph[first]&=~bit(second);graph[second]&=~bit(first);}
static bool independent(const Rows& graph,Mask sites,int need){
    while(count(sites)>=need){if(need==1)return true;int point=take(sites);if(independent(graph,sites&~graph[point],need-1))return true;}
    return false;
}

#include "witness_deck.hpp"
#include "witness_pathdeck.hpp"
static HubDeck library;
static PathDeck<9> seven;
static PathDeck<10> eight;
static PathDeck<11> nine;
static bool kernel_limit(const Rows& lo,Rows& hi,int cap,bool& changed){
    for(int first=0;first<order;++first){Mask edges=hi[first]&~(bit(first+1)-1);while(edges){int second=take(edges);bool mandatory=lo[first]&bit(second);Mask block=(lo[first]|lo[second])&~(bit(first)|bit(second));if(count(block)<cap)continue;
        std::vector<Mask> groups;Mask sites=block;bool impossible=false;
        while(sites){Mask component=sites&-sites,front=component;while(front){Mask reach=0;while(front)reach|=lo[take(front)];front=reach&sites&~component;component|=front;}if(count(component)>cap){impossible=true;break;}sites&=~component;groups.push_back(component);}
        if(impossible){if(mandatory)return false;cut(hi,first,second);changed=true;continue;}if(!mandatory)continue;
        for(unsigned idx=0;idx<groups.size();++idx){Mask source=groups[idx],target=0;for(unsigned other=0;other<idx;++other)if(count(source)+count(groups[other])>cap)target|=groups[other];while(source&&target){int point=take(source);Mask omit=hi[point]&target;while(omit){cut(hi,point,take(omit));changed=true;}}}
        Mask outside=all&~(block|bit(first)|bit(second));while(outside){int point=take(outside);int span=1;for(Mask group:groups)if(lo[point]&group)span+=count(group);if(span>cap){for(int root:{first,second})if(hi[root]&bit(point)){cut(hi,root,point);changed=true;}}}
    }}return true;
}
struct Search {
    long nodes=0;
    long frontier=0, tested=0, fails=0, first_fan=-1, second_fan=0;
    Mask witnesses=0;
    int cross_cap=4;
    int visit(const Rows& explicit_graph,Mask fixed){
        if(nodes>=budget)return -1;
        ++nodes;
        Rows lo=explicit_graph,hi{},singleton{},bad_singleton{};
        for(int point=0;point<order;++point)hi[point]=lo[point]|((fixed&bit(point))?0:(all&~(fixed|bit(point))));
        if(mode&4194304)for(int point=0;point<order;++point){if(lo[point]&exact_low[point])return 0;hi[point]&=~exact_low[point];}
        if(mode&32){Mask sites=marked;while(sites){int first=take(sites);Mask others=sites;while(others){int second=take(others);if(lo[first]&bit(second))return 0;cut(hi,first,second);}}}
        bool changed;Mask sites_ok[40][40]{};
        do {
            changed=false;
            int singles=0;
            singleton.fill(0);
            for(int first=0;first<order;++first)for(int second=0;second<first;++second){
                if(!(hi[first]&bit(second)) && count(hi[first]&hi[second])<=1){++singles;join(singleton,first,second);}
            }
            if(singles>defect)return 0;
            Mask centers=(mode&65536)?marked:all;
            std::vector<Mask> flags;
            Rows used{};Mask hub=all;
            if(mode&(16384|32768)){
                for(int left=0;left<order;++left){Mask rights=singleton[left]&~(bit(left+1)-1);while(rights){
                    int right=take(rights);Mask site=hi[left]&hi[right];if(!site)return 0;
                    if(mode&16384)centers&=site;
                    if(mode&32768){flags.push_back(site|bit(left)|bit(right));hub&=flags.back();if(project&&(site&(used[left]|used[right])))return 0;used[left]|=site;used[right]|=site;}
                }}
                if(!centers)return 0;
                if(mode&32768)for(Mask left:flags)for(Mask right:flags)if(!(left&right))return 0;
            }
            if((project&2)&&!hub)return 0;
            if((project&4)&&singles>4&&!hub)return 0;
            if(mode&8192){
                bad_singleton.fill(0);
                for(int left=0;left<order;++left){Mask rights=singleton[left]&~(bit(left+1)-1);while(rights){
                    int right=take(rights);Mask outside=all&~(bit(left)|bit(right));
                    Mask groups[3]={outside&~(lo[left]|lo[right]),outside&(lo[left]^lo[right]),outside&(lo[left]&lo[right])};
                    for(int hits=0;hits<=2;++hits){Mask banned=0;for(int other=0;other<=2;++other)if(hits+other>cross_cap)banned|=groups[other];
                        if(banned){Mask sites=groups[hits];while(sites){int point=take(sites);bad_singleton[point]|=banned&~bit(point);}}
                    }
                }}
                for(int point=0;point<order;++point)if(bad_singleton[point]&singleton[point])return 0;
            }
            if(marked&&!(mode&16))for(int point=0;point<order;++point)if(!(marked&bit(point)) && (singleton[point]&~marked))return 0;
            for(int first=0;first<order;++first){
                int lower=count(lo[first]),upper=count(hi[first]);
                if(lower>degree||upper<degree||count(singleton[first])>local)return 0;
                if(lower==degree||upper==degree){Mask sites=hi[first]&~lo[first];while(sites){int second=take(sites);if(lower==degree)cut(hi,first,second);else join(lo,first,second);changed=true;}}
            }
            for(int first=0;first<order;++first)for(int second=0;second<first;++second){
                Mask certain=lo[first]&lo[second],possible=hi[first]&hi[second];
                int lower=count(certain),upper=count(possible);
                Mask ends=bit(first)|bit(second);
                bool exceptional=(mode&32)&&!(ends&~marked);
                int maxcode=exceptional?1:3;
                if((mode&4194304)&&(exact_low[first]&bit(second)))maxcode=1;
                if(lower>maxcode)return 0;
                if(lower && (hi[first]&bit(second))){if(lo[first]&bit(second))return 0;cut(hi,first,second);changed=true;}
                int mincode=(!(singleton[first]&bit(second))&&(singles==defect||count(singleton[first])==local||count(singleton[second])==local))?2:1;
                if(marked&&!(mode&16)&&!(marked&(bit(first)|bit(second))))mincode=2;
                if(mode&32)mincode=(exceptional||(mode&64))?1:2;
                if(bad_singleton[first]&bit(second))mincode=2;
                if(mode&4194304)mincode=(exact_low[first]&bit(second))?1:2;
                if(mode&16384){if(!(possible&centers)||(certain&~centers))mincode=2;}
                if(mode&32768){Mask sites=possible;for(Mask flag:flags)if(!(ends&flag))sites&=flag;
                    if(project&&!(singleton[first]&bit(second))){sites&=~(used[first]|used[second]);if(((project&2)||((project&4)&&singles>=4))&&!(hub&ends))sites&=hub;}
                    if(!sites||(certain&~sites))mincode=2;
                    sites_ok[first][second]=sites_ok[second][first]=sites;
                }
                if(upper<mincode){if(!(hi[first]&bit(second)))return 0;if(!(lo[first]&bit(second))){join(lo,first,second);changed=true;}}
                if(!(hi[first]&bit(second))&&upper==mincode){Mask missing=possible&~certain;while(missing){int point=take(missing);join(lo,first,point);join(lo,second,point);changed=true;}}
                if(lower==maxcode||(lo[first]&bit(second))){
                    Mask omit=(lo[first]&hi[second])&~certain;while(omit){cut(hi,second,take(omit));changed=true;}
                    omit=(lo[second]&hi[first])&~certain;while(omit){cut(hi,first,take(omit));changed=true;}
                }
            }
            if(independent(hi,all,degree+1))return 0;
            if(mode&1)for(int first=0;first<order;++first){Mask candidates=(hi[first]&~lo[first])&~(bit(first+1)-1);while(candidates){int second=take(candidates);Mask sites=all&~(hi[first]|hi[second]|bit(first)|bit(second));if(independent(hi,sites,degree-1)){join(lo,first,second);changed=true;}}}
            if((mode&1048576)&&!changed){Rows forced=lo,allowed=hi;if((mode&134217728)&&!nine.fits(lo,hi,&forced,&allowed))return 0;if((mode&524288)&&!eight.fits(lo,hi,&forced,&allowed))return 0;if((mode&262144)&&!seven.fits(lo,hi,&forced,&allowed))return 0;for(int point=0;point<order;++point)if(forced[point]&~allowed[point])return 0;changed=!(forced==lo&&allowed==hi);lo=forced;hi=allowed;}
            if((mode&2097152)&&!changed){Rows allowed=hi;if(mode&134217728)nine.missing(lo,hi,allowed);if(mode&524288)eight.missing(lo,hi,allowed);if(mode&262144)seven.missing(lo,hi,allowed);changed=allowed!=hi;hi=allowed;}
            if((mode&33554432)&&!changed&&!kernel_limit(lo,hi,(mode&67108864)?7:8,changed))return 0;
        }while(changed);
        if(mode&8){if(!library.fits(lo,hi,0))return 0;}
        if(!(mode&1048576)&&(mode&262144)&&!seven.fits(lo,hi))return 0;
        if(!(mode&1048576)&&(mode&524288)&&!eight.fits(lo,hi))return 0;
        if(!(mode&1048576)&&(mode&134217728)&&!nine.fits(lo,hi))return 0;
        if(depth&&count(fixed)>=depth){++frontier;return 0;}

        if((mode&1024)&&!(witnesses&~fixed)){
            ++frontier;
            if(mode&2048){std::cout<<"child "<<fixed;for(int point=0;point<order;++point)std::cout<<' '<<(explicit_graph[point]);std::cout<<'\n';}
            return 0;
        }
        std::vector<Mask> swapped;
        if(mode&512){
            for(int anchor=0;anchor<4;++anchor){
                Mask common=explicit_graph[anchor]&explicit_graph[anchor^1];assert(count(common)==1);
                swapped.push_back((explicit_graph[anchor]^common)|bit(anchor^1));
            }
        }
        int best=-1;std::vector<Mask> bin;
        std::vector<int> pivots;for(int point=0;point<order;++point)if(lo[point]!=hi[point])pivots.push_back(point);
        if(mode&131072){std::map<Mask,int> representatives;for(int point=order-1;point>=0;--point)if(!(fixed&bit(point)))representatives[explicit_graph[point]&fixed]=point;pivots.clear();for(auto item:representatives)pivots.push_back(item.second);}
        if((mode&256)&&(witnesses&~fixed)){
            Mask outstanding=witnesses&~fixed;
            pivots={take(outstanding)};
        }
        if((mode&8388608)&&(coloured&~fixed)){Mask outstanding=coloured&~fixed;pivots={take(outstanding)};}
        if((mode&16777216)&&!(coloured&~fixed)){++frontier;if(mode&2048){std::cout<<"child "<<fixed;for(int point=0;point<order;++point)std::cout<<' '<<explicit_graph[point];std::cout<<'\n';}return 0;}
        if(pivots.empty()){
            std::cout<<"model";for(int point=0;point<order;++point)std::cout<<' '<<lo[point];std::cout<<'\n';return (mode&2)?0:1;
        }
        std::stable_sort(pivots.begin(),pivots.end(),[&](int first,int second){return count(hi[first]^lo[first])<count(hi[second]^lo[second]);});
        for(int pivot:pivots){
            Mask available=hi[pivot]&~lo[pivot];std::map<Mask,Mask> classes;
            while(available){int point=take(available);classes[(explicit_graph[point]&fixed)|((marked&bit(point))?bit(40):0)|((coloured&bit(point))?(Mask(point+1)<<41):0)]|=bit(point);}
            std::vector<Mask> cells,tail,rows;
            for(const auto& item:classes)cells.push_back(item.second);
            tail.resize(cells.size()+1);for(unsigned idx=cells.size();idx>0;--idx)tail[idx-1]=tail[idx]|cells[idx-1];
            auto add=[&](auto&& self,unsigned idx,Mask row,int need)->void{
                if((best>=0&&rows.size()>=bin.size())||count(tail[idx])<need)return;
                Mask points=fixed;int ones=0;
                while(points){int point=take(points);Mask star=explicit_graph[point];int common=count(star&row),room=common+std::min(need,count(star&tail[idx]));
                    if(common>3||((row&bit(point))?common>0:room<1))return;
                    if(mode&32){Mask ends=bit(pivot)|bit(point);if(!(ends&~marked)?common>1:(!(mode&64)&&!(row&bit(point))&&room<2))return;}
                    if((bad_singleton[pivot]&bit(point))&&!(row&bit(point))&&room<2)return;
                    if((mode&4194304)&&!(row&bit(point))){if((exact_low[pivot]&bit(point))?common>1:room<2)return;}
                    if(!(row&bit(point))&&room==1){if(marked&&!(mode&16)&&!(marked&(bit(pivot)|bit(point))))return;++ones;}
                }
                if(ones>std::min(defect,local))return;
                if(!need){
                    ++tested;
                    if(project&1){Mask others=all&~(row|bit(pivot)),fresh=0;while(others){int point=take(others);Mask common=row&lo[point],possible=row&hi[point];
                        if(count(common)>3||!possible){++fails;return;}if(count(possible)==1){if(!(sites_ok[pivot][point]&possible)||(fresh&possible)){++fails;return;}fresh|=possible;}
                    }}
                    for(Mask sites:swapped)if(!(sites&bit(pivot))&&!(row&sites)){++fails;return;}
                    if((mode&4096)&&independent(hi,all&~(row|bit(pivot)),degree)){++fails;return;}
                    rows.push_back(row);return;
                }
                if(idx==cells.size())return;
                Mask group=cells[idx];
                for(;;){self(self,idx+1,row,need);if(!need||!group)break;row|=bit(take(group));--need;}
            };
            add(add,0,lo[pivot],degree-count(lo[pivot]));
            if(mode&131072){std::cout<<"rows "<<pivot;for(Mask row:rows)std::cout<<' '<<row;std::cout<<'\n';continue;}
            if(rows.empty())return 0;
            if(best<0||rows.size()<bin.size()){best=pivot;bin=std::move(rows);}
            if(bin.size()==1)break;
        }
        if(mode&131072)return 0;
        if(fixed==15)first_fan=bin.size();else if(count(fixed)==5)second_fan+=bin.size();
        for(Mask row:bin){Rows child=explicit_graph;while(row)join(child,best,take(row));int verdict=visit(child,fixed|bit(best));if(verdict)return verdict;}
        return 0;
    }
};

int main(int argc,char**argv){
    if(argc!=8&&argc!=9)return 2;
    if(std::getenv("FLAG_PROJECT"))project=std::stoi(std::getenv("FLAG_PROJECT"));
    if(std::getenv("FLAG_DEPTH"))depth=std::stoi(std::getenv("FLAG_DEPTH"));
    if(project)assert(std::stoi(argv[6])&32768);
    order=std::stoi(argv[1]);degree=std::stoi(argv[2]);anchors=std::stoi(argv[3]);defect=std::stoi(argv[4]);local=std::stoi(argv[5]);mode=std::stoi(argv[6]);budget=std::stol(argv[7]);assert(order<=40&&order>=2);all=bit(order)-1;
    if(mode&8){assert(argc==9);library.load(argv[8]);}
    if(mode&262144){assert(argc==9);seven.load(argv[8]);}
    if(mode&524288){assert(argc==9);eight.load(argv[8]);}
    if(mode&134217728){assert(argc==9);nine.load(argv[8]);}
    int index=0;std::string line;
    while(std::getline(std::cin,line)){
        std::istringstream input(line);Rows graph{};Mask fixed=bit(anchors)-1;
        marked=0;if(mode&4)input>>marked;
        if(anchors){
            join(graph,0,1);for(int point=2;point<anchors;++point){join(graph,point%2,point);if(point+1<anchors)join(graph,point,point+1);}
            int point=anchors;std::string field;while(input>>field){auto sep=field.find(':');Mask mask=std::stoi(field.substr(0,sep));auto num=std::stoi(field.substr(sep+1));while(num--){Mask neighbors=mask;while(neighbors)join(graph,point,take(neighbors));++point;}}assert(point==order);
        }else{input>>fixed;for(int point=0;point<order;++point)input>>graph[point];assert(input);}
        coloured=0;exact_low.fill(0);if(mode&4194304){for(int point=0;point<order;++point){input>>exact_low[point];if(exact_low[point])coloured|=bit(point);}assert(input);}
        Search search;if(!anchors&&(mode&(256|512|1024))){if(mode&4194304){for(int first=0;first<order;++first){Mask pairs=exact_low[first];while(pairs){int second=take(pairs);assert((fixed&bit(first))&&(fixed&bit(second)));Mask common=graph[first]&graph[second];assert(count(common)==1);search.witnesses|=common;}}assert(!(mode&512));}else for(int anchor:{0,2}){Mask common=graph[anchor]&graph[anchor+1];assert(count(common)==1);search.witnesses|=common;}}
        search.cross_cap=count(graph[0]&12)+count(graph[1]&12);
        auto start=std::clock();int verdict=search.visit(graph,fixed);
        std::cout<<index++<<' '<<verdict<<' '<<search.nodes<<' '<<double(std::clock()-start)/CLOCKS_PER_SEC<<std::endl;
        std::cerr<<index-1<<' '<<search.witnesses<<' '<<search.first_fan<<' '<<search.second_fan<<' '<<search.frontier<<' '<<search.tested<<' '<<search.fails<<'\n';
    }
}
