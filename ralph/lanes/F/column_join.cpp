#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Word=uint64_t;
using Mask=unsigned;
constexpr int sites_limit=18;
constexpr Word one=1;
struct Space {
    std::array<Word,64> pivots{};
    Word reduce(Word value) const {
        for(Word rest=value;rest>1;){int top=std::bit_width(rest)-1;
            if(pivots[top]){value^=pivots[top];rest^=pivots[top];}else rest^=one<<top;}
        return value;
    }
    bool impose(Word value){value=reduce(value);if(value>1)pivots[std::bit_width(value)-1]=value;return value!=1;}
};
struct Support {
    Mask sites;
    std::vector<Word> cycles;
    std::array<Word,sites_limit> path{};
    std::array<Mask,sites_limit> components{};
    int parts=0;
};
struct Join {
    int sites,target;
    std::array<std::array<Word,sites_limit>,sites_limit> edge{};
    std::array<Mask,sites_limit> adjacent{};
    Space initial;
    std::vector<Support> supports[sites_limit+1];
    Join(const std::string& text,int order):sites(text.at(0)-'A'),target(order){
        if(sites<1||sites>sites_limit)throw std::runtime_error("order");
        int pos=1,number=0;
        for(int right=0;right<sites;++right)for(int left=0;left<=right;++left){int weight=text.at(pos++)-'0';
            if(weight<0||weight>1||(left==right&&!weight))throw std::runtime_error("requires all-vertical simple card");
            if(!weight||left==right)continue;
            if(++number>=64)throw std::runtime_error("edge count");
            edge[left][right]=edge[right][left]=one<<number;adjacent[left]|=1u<<right;adjacent[right]|=1u<<left;}
        for(int left=0;left<sites;++left)for(int mid=0;mid<left;++mid)for(int right=0;right<mid;++right)
            if(edge[left][mid]&&edge[mid][right]&&edge[left][right])initial.impose(edge[left][mid]^edge[mid][right]^edge[left][right]);
        for(Mask mask=0;mask<(1u<<sites);++mask){int size=std::popcount(mask);if(size>target||size<target-4)continue;
            Support record{};record.sites=mask;Mask unseen=mask;Space cycle_basis;
            while(unseen){Mask todo=unseen&-unseen,part=0;unseen^=todo;
                while(todo){int left=std::countr_zero(todo);todo&=todo-1;part|=1u<<left;
                    for(Mask neighbors=adjacent[left]&mask;neighbors;neighbors&=neighbors-1){int right=std::countr_zero(neighbors);
                        Word path=record.path[left]^edge[left][right];
                        if(unseen>>right&1){record.path[right]=path;unseen^=1u<<right;todo|=1u<<right;}
                        else {Word cycle=initial.reduce(path^record.path[right]);if(cycle_basis.reduce(cycle)){cycle_basis.impose(cycle);record.cycles.push_back(cycle);}}}}
                record.components[record.parts++]=part;}
            supports[size].push_back(std::move(record));}
        for(auto& group:supports)std::stable_sort(group.begin(),group.end(),[](const auto& left,const auto& right){return left.cycles.size()<right.cycles.size();});
    }
    void run(std::string name,int count, const std::vector<Mask>& footprint,const std::vector<Mask>& high,Mask pole_edges,std::ofstream& trace,int maxpasses,std::ostream* quadratic){
        Space space=initial;Mask used[2]={};int steps=0;
        auto finish=[&](const std::string& status){trace<<name<<" end "<<status<<' '<<steps<<'\n';std::cout<<name<<' '<<status<<' '<<steps<<'\n';};
        for(int col=0;col<count;++col){if(high[col]&~footprint[col])throw std::runtime_error("bad endpoint");
            Mask lo=footprint[col]^high[col];if((used[0]&lo)||(used[1]&high[col])){finish("collision");return;}used[0]|=lo;used[1]|=high[col];
            for(Mask ends=footprint[col];ends;ends&=ends-1){int left=std::countr_zero(ends);
                for(Mask rest=adjacent[left]&footprint[col]&(~0u<<left);rest;rest&=rest-1){int right=std::countr_zero(rest);
                    if(!space.impose(edge[left][right]^(((high[col]>>left)^(high[col]>>right))&1))){finish("triangles");return;}}}}
        std::set<std::vector<Word>> flats;bool price=false;
        for(int pass=0;pass<maxpasses+int(quadratic!=nullptr);++pass){int start=steps;
            for(Mask poles=0;poles<(1u<<count);++poles){bool ok=true;Mask forbidden[2]={};
                for(int left=0;left<count;++left)if(poles>>left&1){for(int right=0;right<left;++right)if((poles>>right&1)&&(pole_edges>>(left*(left-1)/2+right)&1))ok=false;
                    forbidden[0]|=footprint[left]^high[left];forbidden[1]|=high[left];}
                int size=target-std::popcount(poles);if(!ok||size<0||size>sites)continue;
                for(const Support& item:supports[size]){
                    if(item.sites&forbidden[0]&forbidden[1])continue;
                    Word only=0,second=0;auto add=[&](Word raw){Word row=space.reduce(raw);if(!row||row==only||row==second||row==(only^second))return true;if(row==1)return false;
                        if(!only){only=row;return true;}if(!price||second||(only^row)==1)return false;second=row;return true;};
                    bool low_rank=true;for(Word cycle:item.cycles)if(!add(cycle)){low_rank=false;break;}
                    for(int part=0;low_rank&&part<item.parts;++part){Mask hits=item.components[part]&(forbidden[0]|forbidden[1]);if(!hits)continue;
                        auto offset=[&](int site){return item.path[site]^((forbidden[0]>>site)&1);};
                        Word anchor=offset(std::countr_zero(hits));hits&=hits-1;
                        while(hits){int other=std::countr_zero(hits);hits&=hits-1;if(!add(anchor^offset(other))){low_rank=false;break;}}}
                    if(!low_rank)continue;
                    if(price){if(second){std::vector<Word> flat={only,second,only^second};std::sort(flat.begin(),flat.end());if(flats.insert(flat).second)*quadratic<<name<<' '<<poles<<' '<<item.sites<<' '<<flat[0]<<' '<<flat[1]<<'\n';}continue;}
                    trace<<name<<" step "<<poles<<' '<<item.sites<<' '<<only<<'\n';++steps;
                    if(!only){finish("I");return;}if(!space.impose(only^one))throw std::logic_error("bad deduction");
                }}
            if(price)break;
            if(steps==start||pass+1==maxpasses){if(!quadratic)break;price=true;}
        }finish("open");
    }
};
int main(int argc,char**argv){if(argc!=6&&argc!=7)return 2;std::ifstream base(argv[1]),requests(argv[3]);std::ofstream trace(argv[4]),quadratic;std::string text,name; base>>text;Join join(text,std::stoi(argv[2]));if(argc==7)quadratic.open(argv[6]);
    int count;Mask pole_edges;while(requests>>name>>count>>pole_edges){if(count<0||count>4)return 2;std::vector<Mask> footprint(count),high(count);for(int col=0;col<count;++col)requests>>footprint[col]>>high[col];join.run(name,count,footprint,high,pole_edges,trace,std::stoi(argv[5]),argc==7?&quadratic:nullptr);}return !requests.eof()||!trace||(argc==7&&!quadratic);}
