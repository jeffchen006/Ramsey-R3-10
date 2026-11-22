#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using Text=std::string;
using Matrix=std::array<std::array<int,20>,20>;
using Degrees=std::array<int,3>;

std::vector<Text> lines(const Text& file){std::ifstream stream(file);assert(stream);std::vector<Text> result;Text line;while(stream>>line)result.push_back(line);return result;}
int slot(int left,int right){if(left>right)std::swap(left,right);return 1+right*(right+1)/2+left;}

int main(int argc,char**argv){
    assert(argc==7);Text tag=argv[1];int length=std::stoi(argv[2]),low=std::stoi(argv[3]),high=std::stoi(argv[4]),minimum=std::stoi(argv[5]);
    int size=5*length/2,half=length/2;auto targets=lines(tag+".q");std::vector<Text> old;
    if(std::stoi(argv[6]))for(auto file:{"../r8/target.q","../r9/target.q","../r9/bitarget.q"})for(auto& text:lines(file))old.push_back(text);
    std::ifstream source(tag+".rows"),maps(tag+".maps"),raw(tag+".raw");assert(source && maps && raw);
    std::unordered_set<Text> distinct,reps,oldUsed;std::set<int> newUsed;
    std::unordered_map<Text,Text> owner;std::map<Text,int> masses;std::map<Degrees,int64_t> bins;
    Text text,group,permutation;int index,mult,mapIndex,dest,rows=0,oldRows=0;int64_t total=0;
    auto advance=[&](int vertex){int start=std::min(vertex/length,2)*length;return start+(vertex-start+1)%(start==2*length?half:length);};
    while(source>>index>>mult>>text){
        assert(index==rows++ && distinct.insert(text).second && maps>>mapIndex>>group>>dest>>permutation && mapIndex==index);
        assert((group=="new"||group=="old") && dest>=0);auto& image=(group=="new"?targets:old).at(dest);
        if(group=="new")newUsed.insert(dest);else{oldUsed.insert(image);++oldRows;}
        std::replace(permutation.begin(),permutation.end(),',',' ');std::istringstream data(permutation);std::array<int,20> mapping{};uint64_t seen=0;
        for(int vertex=0;vertex<size;++vertex){int imageVertex;assert(data>>imageVertex && imageVertex>=0 && imageVertex<size);seen|=uint64_t(1)<<imageVertex;mapping[vertex]=imageVertex;}
        assert(std::popcount(seen)==size && !(data>>permutation));
        assert(int(text.size())==1+size*(size+1)/2 && text[0]=='A'+size && image.size()==text.size() && image[0]==text[0]);
        Matrix matrix{};std::array<uint64_t,40> graph{};
        for(int right=0;right<size;++right)for(int left=0;left<=right;++left){
            int weight=text[slot(left,right)]-'0';assert(weight>=0 && weight<=(left==right?1:2));
            assert(text[slot(left,right)]==image[slot(mapping[left],mapping[right])] && text[slot(left,right)]==text[slot(advance(left),advance(right))]);
            matrix[left][right]=matrix[right][left]=weight;
            for(int first=2*left;first<2*left+2;++first)for(int second=2*right;second<2*right+2;++second)
                if(first!=second && (weight==2 || (weight==1 && ((first^second)&1)))){graph[first]|=uint64_t(1)<<second;graph[second]|=uint64_t(1)<<first;}
        }
        int edges=0;Degrees degrees{};
        for(int vertex=0;vertex<2*size;++vertex){auto mask=graph[vertex];int degree=std::popcount(mask);edges+=degree;assert(low<=degree && degree<=high);
            int block=std::min(vertex/(2*length),2);if(vertex==block*2*length)degrees[block]=degree;else assert(degrees[block]==degree);
            while(mask){int other=std::countr_zero(mask);mask&=mask-1;assert(!(graph[vertex]&graph[other]));}}
        assert(edges>=2*minimum);
        auto signature=[&](int unit,int shiftB,int shiftC){
            Text result;
            for(int pos=0;pos<length;++pos)result+=char('0'+matrix[0][length+(unit*pos+shiftB)%length]);
            for(int pos=0;pos<half;++pos)result+=char('0'+matrix[0][2*length+(unit*pos+shiftC)%half]);
            for(int pos=0;pos<half;++pos)result+=char('0'+matrix[length+shiftB][2*length+(unit*pos+shiftC)%half]);
            return result;};
        Text cross=signature(1,0,0);
        if(!masses.count(cross)){
            std::set<Text> images;for(int unit=1;unit<length;++unit)if(std::gcd(unit,length)==1)
                for(int shiftB=0;shiftB<length;++shiftB)for(int shiftC=0;shiftC<half;++shiftC)images.insert(signature(unit,shiftB,shiftC));
            for(auto& key:images){assert(!owner.count(key));owner[key]=cross;}masses[cross]=int(images.size());
        }
        assert(mult==masses[cross]);bins[degrees]+=mult;total+=mult;
    }
    assert(source.eof() && !(maps>>text) && newUsed.size()==targets.size());
    std::map<Degrees,int64_t> expected;Text first;int64_t physicalTotal=-1;
    while(raw>>first){if(first=="total"){assert(raw>>physicalTotal);break;}Degrees degrees{std::stoi(first),0,0};int64_t value;assert(raw>>degrees[1]>>degrees[2]>>value);assert(expected.emplace(degrees,value).second);}
    assert(!(raw>>text) && expected==bins && total==physicalTotal);
    std::cout<<"PASS "<<tag<<" distinct rows "<<rows<<" cross reps "<<masses.size()<<" labelled cross keys "<<owner.size()<<" weighted profiles "<<total<<" degrees "<<bins.size()<<" mapped old "<<oldRows<<" to "<<oldUsed.size()<<" previous inputs; new maps land on "<<newUsed.size()<<" different row indices\n";
}
