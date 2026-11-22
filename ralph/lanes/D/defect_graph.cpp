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
static Mask bit(int point){return Mask(1)<<point;}
static int count(Mask mask){return __builtin_popcountll(mask);}
static int take(Mask& mask){int point=__builtin_ctzll(mask);mask&=mask-1;return point;}
static void join(Rows& graph,int first,int second){graph[first]|=bit(second);graph[second]|=bit(first);}
static void cut(Rows& graph,int first,int second){graph[first]&=~bit(second);graph[second]&=~bit(first);}
static bool independent(const Rows& graph,Mask sites,int need){
    while(count(sites)>=need){if(need==1)return true;int point=take(sites);if(independent(graph,sites&~graph[point],need-1))return true;}
    return false;
}

#include "hub_deck.hpp"
static HubDeck library;
struct Search {
    long nodes=0;
    int visit(const Rows& explicit_graph,Mask fixed){
        if(nodes>=budget)return -1;
        ++nodes;
        Rows lo=explicit_graph,hi{},singleton{};
        for(int point=0;point<order;++point)hi[point]=lo[point]|((fixed&bit(point))?0:(all&~(fixed|bit(point))));
        if(mode&32){Mask sites=marked;while(sites){int first=take(sites);Mask others=sites;while(others){int second=take(others);if(lo[first]&bit(second))return 0;cut(hi,first,second);}}}
        bool changed;
        do {
            changed=false;
            int singles=0;
            singleton.fill(0);
            for(int first=0;first<order;++first)for(int second=0;second<first;++second){
                if(!(hi[first]&bit(second)) && count(hi[first]&hi[second])<=1){++singles;join(singleton,first,second);}
            }
            if(singles>defect)return 0;
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
                if(lower>maxcode)return 0;
                if(lower && (hi[first]&bit(second))){if(lo[first]&bit(second))return 0;cut(hi,first,second);changed=true;}
                int mincode=(!(singleton[first]&bit(second))&&(singles==defect||count(singleton[first])==local||count(singleton[second])==local))?2:1;
                if(marked&&!(mode&16)&&!(marked&(bit(first)|bit(second))))mincode=2;
                if(mode&32)mincode=(exceptional||(mode&64))?1:2;
                if(upper<mincode){if(!(hi[first]&bit(second)))return 0;if(!(lo[first]&bit(second))){join(lo,first,second);changed=true;}}
                if(!(hi[first]&bit(second))&&upper==mincode){Mask missing=possible&~certain;while(missing){int point=take(missing);join(lo,first,point);join(lo,second,point);changed=true;}}
                if(lower==maxcode||(lo[first]&bit(second))){
                    Mask omit=(lo[first]&hi[second])&~certain;while(omit){cut(hi,second,take(omit));changed=true;}
                    omit=(lo[second]&hi[first])&~certain;while(omit){cut(hi,first,take(omit));changed=true;}
                }
            }
            if(independent(hi,all,degree+1))return 0;
            if(mode&1)for(int first=0;first<order;++first){Mask candidates=(hi[first]&~lo[first])&~(bit(first+1)-1);while(candidates){int second=take(candidates);Mask sites=all&~(hi[first]|hi[second]|bit(first)|bit(second));if(independent(hi,sites,degree-1)){join(lo,first,second);changed=true;}}}
        }while(changed);
        if(mode&8){if(mode&128){if(!library.fits(lo,hi,marked))return 0;}else{Mask sites=marked;while(sites)if(!library.fits(lo,hi,bit(take(sites))))return 0;}}

        int best=-1;std::vector<Mask> bin;
        std::vector<int> pivots;for(int point=0;point<order;++point)if(lo[point]!=hi[point])pivots.push_back(point);
        if(pivots.empty()){
            std::cout<<"model";for(int point=0;point<order;++point)std::cout<<' '<<lo[point];std::cout<<'\n';return (mode&2)?0:1;
        }
        std::stable_sort(pivots.begin(),pivots.end(),[&](int first,int second){return count(hi[first]^lo[first])<count(hi[second]^lo[second]);});
        for(int pivot:pivots){
            Mask available=hi[pivot]&~lo[pivot];std::map<Mask,Mask> classes;
            while(available){int point=take(available);classes[(explicit_graph[point]&fixed)|((marked&bit(point))?bit(40):0)]|=bit(point);}
            std::vector<Mask> cells,tail,rows;
            for(const auto& item:classes)cells.push_back(item.second);
            tail.resize(cells.size()+1);for(unsigned idx=cells.size();idx>0;--idx)tail[idx-1]=tail[idx]|cells[idx-1];
            auto add=[&](auto&& self,unsigned idx,Mask row,int need)->void{
                if((best>=0&&rows.size()>=bin.size())||count(tail[idx])<need)return;
                Mask points=fixed;int ones=0;
                while(points){int point=take(points);Mask star=explicit_graph[point];int common=count(star&row),room=common+std::min(need,count(star&tail[idx]));
                    if(common>3||((row&bit(point))?common>0:room<1))return;
                    if(mode&32){Mask ends=bit(pivot)|bit(point);if(!(ends&~marked)?common>1:(!(mode&64)&&!(row&bit(point))&&room<2))return;}
                    if(!(row&bit(point))&&room==1){if(marked&&!(mode&16)&&!(marked&(bit(pivot)|bit(point))))return;++ones;}
                }
                if(ones>std::min(defect,local))return;
                if(!need){rows.push_back(row);return;}
                if(idx==cells.size())return;
                Mask group=cells[idx];
                for(;;){self(self,idx+1,row,need);if(!need||!group)break;row|=bit(take(group));--need;}
            };
            add(add,0,lo[pivot],degree-count(lo[pivot]));
            if(rows.empty())return 0;
            if(best<0||rows.size()<bin.size()){best=pivot;bin=std::move(rows);}
            if(bin.size()==1)break;
        }
        for(Mask row:bin){Rows child=explicit_graph;while(row)join(child,best,take(row));int verdict=visit(child,fixed|bit(best));if(verdict)return verdict;}
        return 0;
    }
};

int main(int argc,char**argv){
    if(argc!=8&&argc!=9)return 2;
    order=std::stoi(argv[1]);degree=std::stoi(argv[2]);anchors=std::stoi(argv[3]);defect=std::stoi(argv[4]);local=std::stoi(argv[5]);mode=std::stoi(argv[6]);budget=std::stol(argv[7]);assert(order<=40&&order>=2);all=bit(order)-1;
    if(mode&8){assert(argc==9&&(mode&4));library.load(argv[8]);}
    int index=0;std::string line;
    while(std::getline(std::cin,line)){
        std::istringstream input(line);Rows graph{};Mask fixed=bit(anchors)-1;
        marked=0;if(mode&4)input>>marked;
        if(anchors){
            join(graph,0,1);for(int point=2;point<anchors;++point){join(graph,point%2,point);if(point+1<anchors)join(graph,point,point+1);}
            int point=anchors;std::string field;while(input>>field){auto sep=field.find(':');Mask mask=std::stoi(field.substr(0,sep));auto num=std::stoi(field.substr(sep+1));while(num--){Mask neighbors=mask;while(neighbors)join(graph,point,take(neighbors));++point;}}assert(point==order);
        }else{input>>fixed;for(int point=0;point<order;++point)input>>graph[point];assert(input);}
        Search search;auto start=std::clock();int verdict=search.visit(graph,fixed);
        std::cout<<index++<<' '<<verdict<<' '<<search.nodes<<' '<<double(std::clock()-start)/CLOCKS_PER_SEC<<std::endl;
    }
}
