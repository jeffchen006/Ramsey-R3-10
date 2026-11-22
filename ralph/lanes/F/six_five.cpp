#define main complete_cli_main
#include "six_complete.cpp"
#undef main
#include <queue>
struct Five{
    int order,target;bool paired;Graph core{},model{};vector<Word> masks;vector<vector<int>> disjoint;array<int,5> chosen{};long long nodes=0,limit;bool capped=false;
    bool bipartite(){
        vector<int> colors(masks.size(),-1);for(int start=0;start<int(colors.size());++start)if(colors[start]<0){queue<int> visit;colors[start]=0;visit.push(start);
            while(!visit.empty()){int here=visit.front();visit.pop();for(int there:disjoint[here]){if(colors[there]==colors[here])return false;if(colors[there]<0){colors[there]=1-colors[here];visit.push(there);}}}}
        return true;
    }
    bool add(int depth,int index,const Graph& old){
        if(++nodes>limit){capped=true;return false;}
        if(depth>0&&index<chosen[0])return false;
        if(depth==4&&(index<chosen[1]||(masks[chosen[0]]&masks[index])))return false;
        Graph next=old;Word contact=masks[index];int newv=order+depth;
        for(Word rest=contact;rest;rest&=rest-1){int vertex=low(rest);edge(next,newv,vertex);if(paired&&(contact&bit(vertex^1)))next[vertex]&=~bit(vertex^1);}
        if(depth)edge(next,newv,newv-1);
        if(depth==4)edge(next,newv,order);
        if(independent(next,bit(newv+1)-1,target))return false;
        chosen[depth]=index;if(depth==4){model=next;return true;}
        for(int adjacent:disjoint[index]){if(add(depth+1,adjacent,next))return true;if(capped)return false;}
        return false;
    }
    string solve(){
        masks.erase(remove_if(masks.begin(),masks.end(),[&](Word mask){return size_of(mask)>target-3;}),masks.end());disjoint.resize(masks.size());
        for(int left=0;left<int(masks.size());++left)for(int right=0;right<int(masks.size());++right)if(!(masks[left]&masks[right]))disjoint[left].push_back(right);
        if(bipartite())return "bipartite";
        for(int index=0;index<int(masks.size());++index){if(add(0,index,core))return "model";if(capped)return "cap";}return "noC5";
    }
};
int main(int argc,char** argv){assert(argc==2);int order,target,paired,count;string key;
    while(cin>>key>>order>>target>>paired>>count){Five test;test.order=order;test.target=target;test.paired=paired;test.limit=stoll(argv[1]);for(int vertex=0;vertex<order;++vertex)cin>>test.core[vertex];
        if(count<0){assert(paired);Completion census(test.core,order,target,6,2000000);census.subsets(0,bit(order)-1);if(census.capped){cout<<key<<" maskcap 0 0\n";continue;}test.masks=move(census.masks);}
        else{test.masks.resize(count);for(Word& mask:test.masks)cin>>mask;}
        for(Word mask:test.masks)for(Word rest=mask;rest;rest&=rest-1){int vertex=low(rest);assert(!(test.core[vertex]&mask&~(paired?bit(vertex^1):Word(0))));}
        string result=test.solve();cout<<key<<' '<<result<<' '<<test.masks.size()<<' '<<test.nodes;
        if(result=="model"){cout<<" graph";for(int vertex=0;vertex<order+5;++vertex)cout<<' '<<test.model[vertex];}cout<<'\n';
    }
}
