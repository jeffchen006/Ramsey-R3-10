#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>

using Record=std::vector<std::pair<int,int>>;
struct Item {int mask; std::vector<int> points,pairs;};
static int order,degree,budget,printed,labelled;
static std::array<int,9> inner{},remaining{};
static std::array<int,512> multiplicity{},capacity{},reflect{};
static std::vector<Item> sets;
static int pop(int value) {return __builtin_popcount(static_cast<unsigned int>(value));}
static void add(int left,int right) {inner[left]|=1<<right;inner[right]|=1<<left;}
static void visit(std::size_t index,int slots,int slack) {
    if(slots<0 || slack<0) return;
    if(index==sets.size()) {
        const int needed=std::accumulate(remaining.begin(),remaining.end(),0);
        if(needed>slots) return;
        assert(slots-needed==slack);
        multiplicity[0]=slots-needed;
        for(int point=0;point<9;++point) multiplicity[1<<point]=remaining[point];
        Record here,other;
        for(int mask=0;mask<512;++mask) if(multiplicity[mask]) {
            here.emplace_back(mask,multiplicity[mask]);other.emplace_back(reflect[mask],multiplicity[mask]);
        }
        ++labelled;
        std::sort(other.begin(),other.end());
        if(here<=other) {
            ++printed;
            for(std::size_t ind=0;ind<here.size();++ind) std::cout<<(ind?" ":"")<<here[ind].first<<':'<<here[ind].second;
            std::cout<<'\n';
        }
        return;
    }
    const auto& set=sets[index];
    int limit=slots;
    for(int point:set.points) limit=std::min(limit,remaining[point]);
    for(int pair:set.pairs) limit=std::min(limit,capacity[pair]);
    const int width=static_cast<int>(set.points.size());
    const int cost=(width-1)*(width-2)/2;
    const int room=width==2?capacity[set.mask]:0;
    const int low=width==2?std::max(0,room-slack):0;
    for(int take=low;take<=limit;++take) {
        for(int point:set.points) remaining[point]-=take;
        for(int pair:set.pairs) capacity[pair]-=take;
        multiplicity[set.mask]=take;
        visit(index+1,slots-take,slack-(width==2?room-take:cost*take));
        for(int point:set.points) remaining[point]+=take;
        for(int pair:set.pairs) capacity[pair]+=take;
    }
    multiplicity[set.mask]=0;
}
int main(int argc,char** argv) {
    if(argc!=3) return 2;
    order=std::stoi(argv[1]);degree=std::stoi(argv[2]);
    add(0,1);
    for(int point=2;point<=8;++point){add(point%2,point);if(point<8)add(point,point+1);}
    budget=order-9;
    for(int point=0;point<9;++point) {
        remaining[point]=degree-pop(inner[point]);budget-=remaining[point];
        for(int other=0;other<point;++other) if(!(inner[point]&(1<<other))) {
            int pair=(1<<point)|(1<<other);
            capacity[pair]=3-pop(inner[point]&inner[other]);budget+=capacity[pair];
        }
    }
    for(int mask=0;mask<512;++mask) {
        Item set{mask,{},{}};
        bool possible=true;
        for(int point=0;point<9;++point) if(mask&(1<<point)) {
            reflect[mask]|=1<<(point<2?point:10-point);
            if(inner[point]&mask) possible=false;
            for(int other:set.points) {
                int pair=(1<<point)|(1<<other);
                if(!capacity[pair]) possible=false;
                set.pairs.push_back(pair);
            }
            set.points.push_back(point);
        }
        if(possible && set.points.size()>=2) sets.push_back(set);
    }
    std::sort(sets.begin(),sets.end(),[](const Item& left,const Item& right){return std::make_pair(-int(left.points.size()),left.mask)<std::make_pair(-int(right.points.size()),right.mask);});
    visit(0,order-9,budget);
    std::cerr<<"labelled "<<labelled<<" reflection reps "<<printed<<" initial slack "<<budget<<'\n';
}
