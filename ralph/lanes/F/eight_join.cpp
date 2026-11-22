#define main six_cli_main
#include "six_complete.cpp"
#undef main
using Bits=vector<Word>;
struct JoinEight{
    int order,target,width,first_lo=0,first_hi=1000000;bool paired;Graph base{},model{};vector<Word> contacts;Bits all;vector<Bits> separate,together,contains;array<int,8> choice{};array<long long,9> reached{};long long nodes=0,limit,oldsets=0,covered=0;bool cap=false;
    void mark(Word available,int need,Word selected){
        if(need){while(size_of(available)>=need){int vertex=low(available);available&=available-1;mark(available&~base[vertex],need-1,selected|bit(vertex));}return;}
        ++oldsets;Bits misses(width,0);
        for(int index=0;index<int(contacts.size());++index)if(!(contacts[index]&selected))misses[index/64]|=bit(index%64);
        for(int section=0;section<width;++section)for(Word rest=misses[section];rest;rest&=rest-1){Bits& allowed=separate[64*section+low(rest)];for(int block=0;block<width;++block)allowed[block]&=~misses[block];}
    }
    void prepare(){
        width=(contacts.size()+63)/64;all.assign(width,~Word(0));if(contacts.size()%64)all.back()=bit(contacts.size()%64)-1;separate.assign(contacts.size(),all);together.assign(contacts.size(),Bits(width));contains.assign(order,Bits(width));
        for(int index=0;index<int(contacts.size());++index)for(Word points=contacts[index];points;points&=points-1)contains[low(points)][index/64]|=bit(index%64);
        for(int left=0;left<int(contacts.size());++left)for(int right=0;right<int(contacts.size());++right)if(!(contacts[left]&contacts[right]))together[left][right/64]|=bit(right%64);
        mark(bit(order)-1,target-2,0);
        if(getenv("F_PAIR_EXACT"))for(int first=0;first<int(contacts.size());++first){Graph one=base;auto attach=[&](Graph& graph,int vertex,Word mask){for(Word rest=mask;rest;rest&=rest-1){int old=low(rest);edge(graph,old,vertex);if(paired&&(mask&bit(old^1)))graph[old]&=~bit(old^1);}};attach(one,order,contacts[first]);
            for(int block=first/64;block<width;++block){Word possible=together[first][block]|separate[first][block];if(block==first/64)possible&=~Word(0)<<(first%64);
                for(Word rest=possible;rest;rest&=rest-1){int second=64*block+low(rest);Graph two=one;attach(two,order+1,contacts[second]);for(int adjacent=0;adjacent<2;++adjacent){auto& list=adjacent?together:separate;if(!(list[first][block]&bit(second%64)))continue;if(adjacent)edge(two,order,order+1);
                    if(independent(two,bit(order+2)-1,target)){list[first][block]&=~bit(second%64);list[second][first/64]&=~bit(first%64);}}}}
        }
    }
    bool search(int depth,bool cycle,const Graph& state){
        int front=cycle?5:4;int start=!depth?first_lo:depth==front?0:cycle&&depth<front?choice[0]:choice[depth-1];if(cycle&&depth==4)start=max(start,choice[1]);
        Word initial=0,final=bit(depth);if(depth<front){if(cycle&&depth){initial=bit(depth-1);if(depth==4)initial|=1;}final=initial+1;}
        for(Word links=initial;links<final;++links){bool triangle=false;for(Word rest=links;rest;rest&=rest-1)if((state[order+low(rest)]>>order)&links){triangle=true;break;}if(triangle)continue;
            Bits alive=all;for(int section=start/64;section<width;++section){if(section==start/64)alive[section]&=~Word(0)<<(start%64);
                if(!depth&&first_hi<(section+1)*64)alive[section]&=first_hi<=section*64?0:bit(first_hi%64)-1;
                for(int slot=0;alive[section]&&slot<depth;++slot)alive[section]&=(links&bit(slot)?together:separate)[choice[slot]][section];}
            for(int section=start/64;section<width;++section){while(alive[section]){int index=64*section+low(alive[section]);alive[section]&=alive[section]-1;Word contact=contacts[index];if(size_of(contact)+(cycle&&depth<front?2:size_of(links))>=target)continue;
                    if(++nodes>limit){cap=true;return false;}Graph next=state;int vertex=order+depth;
                    for(Word points=contact;points;points&=points-1){int old=low(points);edge(next,old,vertex);if(paired&&(contact&bit(old^1)))next[old]&=~bit(old^1);}
                    for(Word points=links;points;points&=points-1)edge(next,vertex,order+low(points));
                    if(Word witness=independent(next,bit(vertex+1)-1,target)){
                        if(getenv("F_NO_WILDCARD"))continue;
                        Word before=witness&(bit(order)-1),avoid=(witness&bit(vertex))?before:0,require=0;
                        if(paired)for(Word points=before;points;points&=points-1){int old=low(points);if((before&bit(old^1))&&(state[old]&bit(old^1)))require|=bit(old);}
                        assert((require&contact)==require&&!(avoid&contact));
                        for(int block=section;block<width;++block){Word discard=alive[block];for(Word points=avoid;discard&&points;points&=points-1)discard&=~contains[low(points)][block];for(Word points=require;discard&&points;points&=points-1)discard&=contains[low(points)][block];covered+=size_of(discard);alive[block]&=~discard;}continue;}
                    ++reached[depth+1];choice[depth]=index;
                    if(depth==7){model=next;return true;}if(search(depth+1,cycle,next))return true;if(cap)return false;
                }
            }
        }return false;
    }
};
int main(int argc,char** argv){assert(argc==2||argc==3);string key;int order,target,paired,count;
    while(cin>>key>>order>>target>>paired>>count){JoinEight test;test.order=order;test.target=target;test.paired=paired;test.limit=stoll(argv[1]);for(int old=0;old<order;++old)cin>>test.base[old];
        if(count<0){assert(paired);Completion masks(test.base,order,target,6,2000000);if(independent(test.base,bit(order)-1,target)){cout<<key<<" bare\n";continue;}masks.subsets(0,bit(order)-1);if(masks.capped||masks.masks.size()>5000){cout<<key<<" maskcap "<<masks.masks.size()<<'\n';continue;}test.contacts=move(masks.masks);sort(test.contacts.begin(),test.contacts.end());}
        else{test.contacts.resize(count);for(Word& mask:test.contacts)cin>>mask;}
        for(Word mask:test.contacts)for(Word rest=mask;rest;rest&=rest-1){int vertex=low(rest);assert(!(test.base[vertex]&mask&~(paired?bit(vertex^1):Word(0))));}
        test.prepare();if(argc==3){ifstream parts(argv[2]);assert(parts);string requested;int lower,upper;while(parts>>requested>>lower>>upper){if(key!=requested)continue;assert(0<=lower&&lower<upper&&upper<=int(test.contacts.size()));test.first_lo=lower;test.first_hi=upper;test.cap=false;test.nodes=test.covered=0;test.reached={};bool model=test.search(0,false,test.base);cout<<key<<' '<<lower<<' '<<upper<<' '<<(model?"model":test.cap?"cap":"empty")<<' '<<test.nodes<<' '<<test.covered;for(int depth=1;depth<=8;++depth)cout<<' '<<test.reached[depth];if(model){cout<<" graph";for(int old=0;old<order+8;++old)cout<<' '<<test.model[old];}cout<<endl;}continue;}
        cout<<key<<' '<<test.contacts.size();for(bool cycle:{false,true}){test.cap=false;test.nodes=0;test.reached={};bool model=test.search(0,cycle,test.base);cout<<' '<<(cycle?"C5":"I4")<<' '<<(model?"model":test.cap?"cap":"empty")<<' '<<test.nodes;
            for(int depth=1;depth<=8;++depth)cout<<' '<<test.reached[depth];if(model){cout<<" graph";for(int old=0;old<order+8;++old)cout<<' '<<test.model[old];break;}}
        cout<<'\n';
    }
}
