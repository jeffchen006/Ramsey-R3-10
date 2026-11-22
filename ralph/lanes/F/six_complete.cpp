#include <array>
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <sstream>
#include <set>
#include <string>
#include <vector>
using namespace std;
using Word=uint64_t;
using Graph=array<Word,42>;
Word bit(int vertex){return Word(1)<<vertex;}
int low(Word mask){return __builtin_ctzll(mask);}
int size_of(Word mask){return __builtin_popcountll(mask);}
Word independent(const Graph& graph,Word pool,int need){
    if(need==1)return pool&-pool;
    while(size_of(pool)>=need){int vertex=low(pool);pool&=pool-1;
        if(Word tail=independent(graph,pool&~graph[vertex],need-1))return bit(vertex)|tail;
    }return 0;
}
void edge(Graph& graph,int left,int right){graph[left]|=bit(right);graph[right]|=bit(left);}
struct Completion{
    int order,target,outer;Word universe;Graph base;vector<Word> masks;long long nodes=0,workcap;
    array<long long,7> reached{};Graph model{};bool capped=false;
    Completion(Graph core,int order_,int target_,int outer_,long long cap):order(order_),target(target_),outer(outer_),universe(bit(order)-1),base(core),workcap(cap){}
    Graph adjoin(Graph graph,int depth,Word contacts,Word links)const{
        int vertex=order+depth;
        for(Word rest=contacts;rest;rest&=rest-1){int old=low(rest);edge(graph,vertex,old);if(contacts&bit(old^1))graph[old]&=~bit(old^1);}
        for(Word rest=links;rest;rest&=rest-1)edge(graph,vertex,order+low(rest));
        return graph;
    }
    void subsets(Word contacts,Word pool){
        if(capped)return;
        if(++nodes>workcap){capped=true;return;}
        Graph graph=adjoin(base,0,contacts,0);
        if(independent(graph,universe,target))return;
        Word missing=independent(graph,universe&~contacts,target-1);
        Word branches=missing?missing&pool:pool;
        if(!missing)masks.push_back(contacts);
        while(branches&&!capped){int vertex=low(branches);branches&=branches-1;pool&=~bit(vertex);
            subsets(contacts|bit(vertex),pool&~(base[vertex]&~bit(vertex^1)));
        }
    }
    bool place(const Graph& graph,int depth,int start){
        if(depth==outer){model=graph;return true;}
        for(int index=start;index<int(masks.size());++index){Word contacts=masks[index];
            for(Word links=0;links<bit(depth);++links){
                if(++nodes>workcap){capped=true;return false;}
                if(outer>=3&&depth<3&&links)continue;
                bool ok=true;for(Word rest=links;rest;rest&=rest-1){int vertex=order+low(rest);
                    if(graph[vertex]&(contacts|(links<<order))){ok=false;break;}}
                if(!ok)continue;
                Graph next=adjoin(graph,depth,contacts,links);
                if(independent(next,bit(order+depth+1)-1,target))continue;
                ++reached[depth+1];
                if(place(next,depth+1,depth==2?0:index))return true;
                if(capped)return false;
            }
        }return false;
    }
    string run(){
        if(independent(base,universe,target))return "bare";
        subsets(0,universe);if(capped)return "cap";
        sort(masks.begin(),masks.end());assert(adjacent_find(masks.begin(),masks.end())==masks.end());
        if(masks.empty())return "one";
        if(place(base,0,0))return "model";
        return capped?"cap":"multi";
    }
};
string check(string key, Graph graph,int order,int target,int outer,long long cap,bool quiet){
        assert(order%2==0&&order+outer<=40&&outer<=6&&(outer==6||outer<=2));
        for(int left=0;left<order;++left)assert(graph[left]&bit(left^1));
        for(int left=0;left<order;++left)for(int right=0;right<order;++right){assert(bool(graph[left]&bit(right))==bool(graph[right]&bit(left)));if(graph[left]&bit(right))assert(!(graph[left]&graph[right]));}
        Completion solve(graph,order,target,outer,cap);string status=solve.run();if(quiet&&status=="bare")return status;cout<<key<<' '<<status<<' '<<solve.masks.size()<<' '<<solve.nodes;
        for(int depth=1;depth<=outer;++depth)cout<<' '<<solve.reached[depth];
        if(status=="model"){cout<<" graph";for(int vertex=0;vertex<order+outer;++vertex)cout<<' '<<solve.model[vertex];}
        cout<<'\n';return status;
}
struct Table{vector<Word> rows;vector<Word> lookup;};
int syndrome(Word key,const vector<Word>& rows){int result=0;for(int pos=0;pos<int(rows.size());++pos)result|=__builtin_parityll(key&rows[pos])<<pos;return result;}
int main(int argc,char** argv){
    assert(argc==2||argc==7);long long cap=stoll(argv[1]);
    if(argc==2){string key;int order,target,outer;while(cin>>key>>order>>target>>outer){Graph graph{};for(int left=0;left<order;++left)cin>>graph[left];check(key,graph,order,target,outer,cap,false);}return 0;}
    int order=34,lowbits=stoi(argv[2]),banklimit=stoi(argv[3]),width=1<<lowbits,words=width/64;Word first=stoull(argv[4]),last=stoull(argv[5]);assert(first*width<last*width&&last*width<=bit(35));
    vector<pair<int,int>> edges;vector<Word> columns;ifstream matrix("columns.tsv");int left,right;Word value;while(matrix>>left>>right>>value){edges.emplace_back(left,right);columns.push_back(value);}assert(edges.size()==56);
    vector<Table> bank;ifstream input("bank.tsv");assert(input);string line;
    while(int(bank.size())<banklimit&&getline(input,line)){istringstream stream(line);Word support;int rank;stream>>support>>rank;Table table;while(stream>>value)table.rows.push_back(value);assert(int(table.rows.size())==rank&&rank<=7);
        table.lookup.resize((1<<rank)*words);for(int key=0;key<width;++key)table.lookup[syndrome(key,table.rows)*words+key/64]|=bit(key%64);bank.push_back(move(table));}
    assert(int(bank.size())==banklimit);Word tests=0,bare=0,one=0,multi=0,model=0,capped=0;ofstream checkpoint(argv[6]);assert(checkpoint);
    for(Word prefix=first;prefix<last;++prefix){vector<Word> alive(words,~Word(0));Word high=prefix*width;
        for(const Table& table:bank){const Word* masks=table.lookup.data()+syndrome(high,table.rows)*words;for(int pos=0;pos<words;++pos)alive[pos]&=~masks[pos];}
        for(int pos=0;pos<words;++pos)for(Word rest=alive[pos];rest;rest&=rest-1){Word key=high+pos*64+low(rest);Graph graph{};
            for(int vertex=0;vertex<order;++vertex)graph[vertex]=bit(vertex^1);
            for(int index=0;index<56;++index){auto [left,right]=edges[index];int crossed=1^__builtin_parityll(key&columns[index]);for(int side=0;side<2;++side)edge(graph,2*left+side,2*right+(side^crossed));}
            string status=check(to_string(key),graph,order,10,6,cap,true);++tests;
            if(status=="bare")++bare;else if(status=="one")++one;else if(status=="multi")++multi;else if(status=="cap")++capped;else{assert(status=="model");++model;}}
        if((prefix-first)%16==15||prefix+1==last){checkpoint<<prefix+1<<' '<<(prefix+1-first)*width<<' '<<tests<<' '<<bare<<' '<<one<<' '<<multi<<' '<<model<<' '<<capped<<endl;cout.flush();}
    }
}
