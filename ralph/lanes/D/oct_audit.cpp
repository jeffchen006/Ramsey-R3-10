#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

using Key=std::vector<int>;
using Library=std::set<Key>;

static Library read(const std::string& path) {
    std::ifstream input(path);assert(input);
    Library result;
    std::string line;
    while(std::getline(input,line)) {
        Key key;
        std::stringstream fields(line);
        std::string field;
        while(fields>>field) {
            const auto split=field.find(':');
            int mask=std::stoi(field.substr(0,split));
            int number=std::stoi(field.substr(split+1));
            while(number--) key.push_back(mask);
        }
        std::sort(key.begin(),key.end());assert(result.insert(key).second);
    }
    return result;
}

static int move(int mask,const Key& order) {
    int value=0;
    for(std::size_t pos=0;pos<order.size();++pos) if(mask&(1<<order[pos])) value|=1<<pos;
    return value;
}

static Key mapped(const Key& row,const Key& trans) {
    Key output;
    for(int mask:row) output.push_back(trans[mask]);
    std::sort(output.begin(),output.end());
    return output;
}

int main(int argc,char** argv) {
    if(argc!=5 && argc!=6) return 2;
    const int degree=std::stoi(argv[1]),order=std::stoi(argv[2]);
    int limit=argc==6?std::stoi(argv[5]):0;
    const Library views_in=read(argv[3]),oct=read(argv[4]);
    Library views,expected;
    Key reverse(512);
    for(int mask=0;mask<512;++mask) reverse[mask]=move(mask,{0,1,8,7,6,5,4,3,2});
    for(const auto& key:views_in) if(std::count(key.begin(),key.end(),262)) {
        views.insert(key);views.insert(mapped(key,reverse));
    }
    std::vector<Key> restrictions;
    for(int parity=0;parity<8;++parity) for(int step:{-1,1}) {
        Key rank{parity%2,1-parity%2};
        for(int offset=0;offset<8;++offset) rank.push_back(2+((parity+step*offset+16)%8));
        Key trans(1024);
        for(int mask=0;mask<1024;++mask) trans[mask]=move(mask,rank);
        for(const auto& key:oct) expected.insert(mapped(key,trans));
        if(step==1) {
            rank.pop_back();
            for(int mask=0;mask<1024;++mask) trans[mask]=move(mask,rank);
            restrictions.push_back(trans);
        }
    }
    long visited=0,accepted=0,cases=0;
    for(const auto& root:views) {
        ++cases;
        std::map<int,int> counts;
        for(int mask:root) if(mask!=262) ++counts[mask];
        assert(int(root.size())==order-9 && std::count(root.begin(),root.end(),262)==1);
        std::vector<std::pair<int,int>> cells(counts.begin(),counts.end());
        std::vector<int> avail(cells.size()+1);
        for(int ind=int(cells.size())-1;ind>=0;--ind) avail[ind]=avail[ind+1]+((cells[ind].first&262)?0:cells[ind].second);
        std::array<int,9> pairs_used{};
        std::array<int,9> boundary{};boundary[0]=2;boundary[1]=1;
        for(int pos=2;pos<9;++pos) {boundary[pos]|=1<<(pos%2);boundary[pos%2]|=1<<pos;if(pos>2){boundary[pos]|=1<<(pos-1);boundary[pos-1]|=1<<pos;}}
        for(int pos=0;pos<9;++pos) pairs_used[pos]=__builtin_popcount(static_cast<unsigned>(262&boundary[pos]));
        Key record;
        auto search=[&](auto&& self,int index,int need)->void {
            if(need>avail[index]) return;
            if(index==int(cells.size())) {
                ++visited;
                for(const auto& trans:restrictions) {
                    Key test=mapped(record,trans);
                    test.insert(std::lower_bound(test.begin(),test.end(),262),262);
                    if(!views.count(test)) return;
                }
                Key output=record;
                std::sort(output.begin(),output.end());
                assert(expected.erase(output)==1);
                ++accepted;
                return;
            }
            const auto [mask,number]=cells[index];
            int upper=(mask&262)?0:std::min(need,number);
            for(int pos=0;pos<9;++pos) if(mask&(1<<pos)) upper=std::min(upper,3-pairs_used[pos]);
            for(int nbor=0;nbor<=upper;++nbor) {
                for(int pos=0;pos<9;++pos) if(mask&(1<<pos)) pairs_used[pos]+=nbor;
                record.insert(record.end(),number-nbor,mask);record.insert(record.end(),nbor,512|mask);
                self(self,index+1,need-nbor);
                record.resize(record.size()-number);
                for(int pos=0;pos<9;++pos) if(mask&(1<<pos)) pairs_used[pos]-=nbor;
            }
        };
        search(search,0,degree-3);
        if(limit && cases>=limit) break;
    }
    if(!limit) assert(expected.empty());
    std::cout<<"PASS direct tenth-row census: oriented parents "<<cases<<" possible rows "<<visited<<" all-eight-compatible "<<accepted<<" unvisited labelled expected "<<expected.size()<<'\n';
}
