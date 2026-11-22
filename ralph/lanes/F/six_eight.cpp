#define main six_cli_main
#include "six_complete.cpp"
#undef main
struct Eight{
    int order,target;bool paired;Graph core{},model{};vector<Word> masks;array<int,8> choice{};array<long long,9> reached{};long long nodes=0,limit;bool cap=false;
    bool search(int depth,bool cycle,const Graph& state){
        int front=cycle?5:4;int start=(depth==0||depth==front)?0:cycle&&depth<front?choice[0]:choice[depth-1];
        for(int idx=start;idx<int(masks.size());++idx){Word contact=masks[idx];if(cycle&&depth<front&&size_of(contact)>target-3)continue;
            Word initial=0,final=bit(depth);
            if(depth<front){if(cycle&&depth){initial=bit(depth-1);if(depth==4){initial|=1;if(idx<choice[1])continue;}}final=initial+1;}
            for(Word links=initial;links<final;++links){if(++nodes>limit){cap=true;return false;}bool valid=true;
                for(Word neighbors=links;neighbors;neighbors&=neighbors-1)if(state[order+low(neighbors)]&(contact|(links<<order))){valid=false;break;}
                if(!valid)continue;Graph next=state;int vertex=order+depth;
                for(Word rest=contact;rest;rest&=rest-1){int old=low(rest);edge(next,old,vertex);if(paired&&(contact&bit(old^1)))next[old]&=~bit(old^1);}
                for(Word rest=links;rest;rest&=rest-1)edge(next,vertex,order+low(rest));
                if(independent(next,bit(vertex+1)-1,target))continue;++reached[depth+1];choice[depth]=idx;
                if(depth==7){model=next;return true;}if(search(depth+1,cycle,next))return true;if(cap)return false;
            }
        }return false;
    }
};
int main(int argc,char** argv){assert(argc==2);string key;int order,target,paired,count;
    while(cin>>key>>order>>target>>paired>>count){Eight test;test.order=order;test.target=target;test.paired=paired;test.limit=stoll(argv[1]);for(int old=0;old<order;++old)cin>>test.core[old];
        if(count<0){assert(paired);Completion masks(test.core,order,target,6,2000000);
            if(independent(test.core,bit(order)-1,target)){cout<<key<<" bare\n";continue;}masks.subsets(0,bit(order)-1);if(masks.capped){cout<<key<<" maskcap\n";continue;}test.masks=move(masks.masks);sort(test.masks.begin(),test.masks.end());}
        else{test.masks.resize(count);for(Word& mask:test.masks)cin>>mask;}
        for(Word mask:test.masks)for(Word rest=mask;rest;rest&=rest-1){int vertex=low(rest);assert(!(test.core[vertex]&mask&~(paired?bit(vertex^1):Word(0))));}
        cout<<key<<' '<<test.masks.size();for(bool cycle:{false,true}){test.cap=false;test.nodes=0;test.reached={};bool model=test.search(0,cycle,test.core);cout<<' '<<(cycle?"C5":"I4")<<' '<<(model?"model":test.cap?"cap":"empty")<<' '<<test.nodes;
            for(int depth=1;depth<=8;++depth)cout<<' '<<test.reached[depth];if(model){cout<<" graph";for(int old=0;old<order+8;++old)cout<<' '<<test.model[old];break;}}
        cout<<'\n';
    }
}
