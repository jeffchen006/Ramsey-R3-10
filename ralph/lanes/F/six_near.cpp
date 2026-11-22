#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
using namespace std;
using Word=uint64_t;using Adj=array<Word,40>;
Word bit(int vertex){return Word(1)<<vertex;}
int count(Word values){return __builtin_popcountll(values);}
unsigned number(const Adj& graph,Word available,int target,unsigned stop){
    if(target==1)return count(available);
    unsigned total=0;
    while(count(available)>=target){int vertex=__builtin_ctzll(available);available^=bit(vertex);total+=number(graph,available&~graph[vertex],target-1,stop-total);if(total>=stop)break;}
    return total;
}
void connect(Adj& graph,int left,int right){graph[left]|=bit(right);graph[right]|=bit(left);}
int main(int argc,char** argv){assert(argc>=2);int order,target;cin>>order>>target;Adj base{};for(int vertex=0;vertex<order;++vertex)cin>>base[vertex];
    if(string(argv[1])=="count"){cout<<number(base,bit(order)-1,target,1000000000)<<'\n';return 0;}
    assert(order==34&&target==10&&argc==4);int budget=stoi(argv[2]);mt19937 random(stoul(argv[3]));vector<Word> choices;Word value;while(cin>>value)choices.push_back(value);assert(!choices.empty());unsigned best=999999999,accepted=0;vector<pair<int,int>> pairs;
    for(int left=0;left<6;++left)for(int right=0;right<left;++right)pairs.emplace_back(left,right);
    const Word low=(bit(34)-1)/3;
    for(int trial=0;trial<budget;++trial){Adj graph=base;array<Word,6> masks;
        for(int slot=0;slot<6;++slot){Word contacts=choices[random()%choices.size()];if((trial&1)&&(slot&1))contacts=((masks[slot-1]&low)<<1)|((masks[slot-1]>>1)&low);
            if(trial%4==2||trial%4==3){Word seed=contacts;contacts=0;array<int,34> order;for(int vertex=0;vertex<34;++vertex)order[vertex]=vertex;shuffle(order.begin(),order.end(),random);
                for(bool preferred:{true,false})for(int vertex:order){if(bool(seed&bit(vertex))!=preferred||count(contacts)>=8||count(graph[vertex])>=9)continue;
                    if(!(contacts&base[vertex]&~bit(vertex^1)))contacts|=bit(vertex);}}
            masks[slot]=contacts;
            for(Word rest=contacts;rest;rest&=rest-1){int vertex=__builtin_ctzll(rest);connect(graph,34+slot,vertex);if(contacts&bit(vertex^1))graph[vertex]&=~bit(vertex^1);}}
        bool bad=false;
        for(int vertex=0;vertex<34;vertex+=2){if(max(count(graph[vertex]),count(graph[vertex+1]))>9){graph[vertex]&=~bit(vertex+1);graph[vertex+1]&=~bit(vertex);}if(max(count(graph[vertex]),count(graph[vertex+1]))>9)bad=true;}
        if(bad)continue;
        shuffle(pairs.begin(),pairs.end(),random);for(auto [left,right]:pairs){left+=34;right+=34;if(count(graph[left])<9&&count(graph[right])<9&&!(graph[left]&graph[right]))connect(graph,left,right);}
        int summed=0;for(int vertex=0;vertex<40;++vertex){int degree=count(graph[vertex]);if(degree<6||degree>9)bad=true;summed+=degree;}
        if(bad||summed<322)continue;++accepted;
        unsigned score=number(graph,bit(40)-1,10,best);if(score<best){best=score;cout<<"best "<<trial<<' '<<score<<' '<<summed/2<<" graph";for(Word adjacency:graph)cout<<' '<<adjacency;cout<<'\n';}
    }
    cout<<"trials "<<budget<<" degree_valid "<<accepted<<" best "<<best<<'\n';
}
