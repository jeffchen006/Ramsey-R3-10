#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
using namespace std;
using Mask=uint64_t;using Graph=array<Mask,40>;
Mask singleton(int point){return Mask(1)<<point;}
Mask first_set(const Graph& adjacency,Mask pool,int need){
    if(!need)return Mask(-1);
    while(__builtin_popcountll(pool)>=need){int vertex=63-__builtin_clzll(pool);pool^=singleton(vertex);Mask inside=first_set(adjacency,pool&~adjacency[vertex],need-1);
        if(inside)return singleton(vertex)|(need==1?0:inside);}
    return 0;
}
int main(){int order,target,count;cin>>order>>target>>count;Graph base{};for(int vertex=0;vertex<order;++vertex)cin>>base[vertex];vector<Mask> contacts(count);for(Mask& mask:contacts)cin>>mask;
    auto test=[&](initializer_list<int> indices){Graph graph=base;int slot=order;for(int index:indices){Mask mask=contacts[index];graph[slot]=mask;
        for(int vertex=0;vertex<order;++vertex)if(mask&singleton(vertex)){graph[vertex]|=singleton(slot);if(mask&singleton(vertex^1))graph[vertex]&=~singleton(vertex^1);}++slot;}
        Mask result=first_set(graph,singleton(slot)-1,target);unsigned char bytes[8];for(int index=0;index<8;++index)bytes[index]=result>>(8*index);cout.write((char*)bytes,8);return !result;};
    vector<vector<int>> followers(count);long long pairs=0,triples=0,passed=0;
    for(int left=0;left<count;++left)for(int right=left;right<count;++right)if(test({left,right})){followers[left].push_back(right);++pairs;}
    for(int left=0;left<count;++left)for(int right:followers[left]){vector<int> next;
        set_intersection(followers[left].begin(),followers[left].end(),followers[right].begin(),followers[right].end(),back_inserter(next));for(int third:next){++triples;if(test({left,right,third}))++passed;}}
    cerr<<count<<' '<<pairs<<' '<<triples<<' '<<passed<<'\n';
}
