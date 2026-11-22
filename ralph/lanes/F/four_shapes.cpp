#define main six_cli_main
#include "six_complete.cpp"
#undef main
struct Four{
    int order,target;bool paired;Graph base{},model{};vector<Word> masks;long long nodes=0,limit;bool capped=false;
    bool search(int depth,int shape,const Graph& state){
        if(depth==4){model=state;return true;}
        Word links=0;if(depth==1)links=1;else if(depth==2&&shape!=0)links=2;else if(depth==3)links=(shape==2?5:4);
        for(Word mask:masks){if(++nodes>limit){capped=true;return false;}int degree=shape==0?1:shape==2?2:(depth==0||depth==3?1:2);if(size_of(mask)+degree>=target)continue;
            bool triangle=false;for(Word rest=links;rest;rest&=rest-1)if(state[order+low(rest)]&mask){triangle=true;break;}if(triangle)continue;
            Graph next=state;int vertex=order+depth;for(Word rest=mask;rest;rest&=rest-1){int old=low(rest);edge(next,old,vertex);if(paired&&(mask&bit(old^1)))next[old]&=~bit(old^1);}
            for(Word rest=links;rest;rest&=rest-1)edge(next,order+low(rest),vertex);
            if(!independent(next,bit(vertex+1)-1,target)&&search(depth+1,shape,next))return true;if(capped)return false;
        }return false;
    }
};
int main(int argc,char** argv){assert(argc==2);string key;int order,target,paired,size;
    while(cin>>key>>order>>target>>paired>>size){Four test;test.order=order;test.target=target;test.paired=paired;test.limit=stoll(argv[1]);for(int index=0;index<order;++index)cin>>test.base[index];
        if(size<0){Completion census(test.base,order,target,6,2000000);census.subsets(0,bit(order)-1);if(census.capped){cout<<key<<" maskcap\n";continue;}test.masks=move(census.masks);sort(test.masks.begin(),test.masks.end());}
        else{test.masks.resize(size);for(Word& mask:test.masks)cin>>mask;}
        for(Word mask:test.masks)for(Word rest=mask;rest;rest&=rest-1){int vertex=low(rest);assert(!(test.base[vertex]&mask&~(paired?bit(vertex^1):Word(0))));}
        cout<<key;for(int shape=0;shape<3;++shape){test.nodes=0;test.capped=false;if(test.search(0,shape,test.base)){cout<<" model "<<shape<<" graph";for(int index=0;index<order+4;++index)cout<<' '<<test.model[index];break;}
            cout<<' '<<(test.capped?"cap":"empty")<<':'<<test.nodes;}cout<<'\n';
    }
}
