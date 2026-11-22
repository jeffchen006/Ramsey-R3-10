#define main six_historical_main
#include "six_complete.cpp"
#undef main
using Blocks=vector<Word>;
struct Fixed {
    Graph core{},shape{},model{};int order,target,outer=8,width;vector<Word> masks;vector<Blocks> absent,present,touch;Blocks all;array<int,8> selected{};long long nodes=0,limit;bool capped=false,paired=false;
    void make(Word picked,Word domain){
        Word witness=independent(core,(bit(order)-1)&~picked,target-1);if(!witness)masks.push_back(picked);
        if(size_of(picked)==target-1)return;Word branch=witness?domain&witness:domain;
        while(branch){int next=low(branch);branch&=branch-1;domain&=~bit(next);make(picked|bit(next),domain&~core[next]);}
    }
    void witnesses(Word pool,int need,Word picked){
        if(need){while(size_of(pool)>=need){int place=low(pool);pool&=pool-1;witnesses(pool&~core[place],need-1,picked|bit(place));}return;}
        Blocks misses(width);for(int idx=0;idx<int(masks.size());++idx)if(!(picked&masks[idx]))misses[idx/64]|=bit(idx%64);
        for(int block=0;block<width;++block)for(Word rest=misses[block];rest;rest&=rest-1){auto& row=absent[block*64+low(rest)];for(int j=0;j<width;++j)row[j]&=~misses[j];}
    }
    bool prepare(){if(independent(core,bit(order)-1,target))return false;Word domain=bit(order)-1;for(int vertex=0;vertex<order;++vertex)if(size_of(core[vertex])>=target-1)domain&=~bit(vertex);
        if(paired){Completion census(core,order,target,6,2000000);census.subsets(0,bit(order)-1);masks=move(census.masks);if(census.capped){capped=true;return false;}}else make(0,domain);sort(masks.begin(),masks.end());assert(adjacent_find(masks.begin(),masks.end())==masks.end());if(masks.size()>5000)return false;
        width=(masks.size()+63)/64;all.assign(width,~Word(0));if(masks.size()%64)all.back()=bit(masks.size()%64)-1;absent.assign(masks.size(),all);present.assign(masks.size(),Blocks(width));touch.assign(order,Blocks(width));
        for(int idx=0;idx<int(masks.size());++idx){for(Word rest=masks[idx];rest;rest&=rest-1)touch[low(rest)][idx/64]|=bit(idx%64);for(int other=0;other<int(masks.size());++other)if(!(masks[idx]&masks[other]))present[idx][other/64]|=bit(other%64);}
        witnesses(bit(order)-1,target-2,0);return true;}
    using Domains=array<Blocks,8>;
#ifdef ORDERED24
    array<Word,8> smaller{},larger{};vector<Word> obstructions;
    void setup_bounds(){smaller={};larger={};obstructions.clear();array<int,8> perm{};for(int slot=0;slot<outer;++slot)perm[slot]=slot;
        do{int changed=0;while(changed<outer&&perm[changed]==changed)++changed;if(changed==outer)continue;bool automorphism=true;for(int left=changed;left<outer&&automorphism;++left)for(int right=0;right<left;++right)if(bool(shape[left]&bit(right))!=bool(shape[perm[left]]&bit(perm[right]))){automorphism=false;break;}if(automorphism){int other=perm[changed];larger[changed]|=bit(other);smaller[other]|=bit(changed);}}while(next_permutation(perm.begin(),perm.begin()+outer));
        for(Word subset=1;subset<bit(outer);++subset){if(size_of(subset)<3||size_of(subset)>=target)continue;Word neighborhoods=0;for(Word rest=subset;rest;rest&=rest-1)neighborhoods|=shape[low(rest)];if(!(neighborhoods&subset)&&(neighborhoods|subset)==bit(outer)-1)obstructions.push_back(subset);}}
    bool possible(Word remaining,const Graph& graph,const Domains& domains){array<Word,8> maybe{};for(int slot=0;slot<outer;++slot){if(!(remaining&bit(slot))){maybe[slot]=graph[order+slot]&(bit(order)-1);continue;}
            for(int old=0;old<order;++old)for(int block=0;block<width;++block)if(touch[old][block]&domains[slot][block]){maybe[slot]|=bit(old);break;}}
        for(Word outside:obstructions){Word contacts=0;for(Word rest=outside;rest;rest&=rest-1)contacts|=maybe[low(rest)];Word missed=(bit(order)-1)&~contacts;int need=target-size_of(outside);if(size_of(missed)>=need&&independent(graph,missed,need))return false;}return true;}
#endif
    bool solve(Word remaining,const Graph& graph,const Domains& domains){
        if(!remaining){model=graph;return true;}int chosen=-1,best=1000000;
        for(Word slots=remaining;slots;slots&=slots-1){int slot=low(slots),size=0;for(Word word:domains[slot])size+=size_of(word);if(size<best){best=size;chosen=slot;}}if(!best)return false;
        Word unassigned=remaining&~bit(chosen),used=(bit(outer)-1)&~remaining,links=shape[chosen]&used;
        Blocks options=domains[chosen];int vertex=order+chosen;
        for(int block=0;block<width;++block)while(options[block]){int idx=64*block+low(options[block]);options[block]&=options[block]-1;if(++nodes>limit){capped=true;return false;}Word contacts=masks[idx],saturated=0;Graph next=graph;
            for(Word rest=contacts;rest;rest&=rest-1){int old=low(rest);edge(next,old,vertex);if(paired&&(contacts&bit(old^1)))next[old]&=~bit(old^1);int crossing=size_of(next[old]&~(paired?bit(old^1):Word(0)));if(crossing>=target-1)saturated|=bit(old);}
            for(Word rest=links;rest;rest&=rest-1)edge(next,order+low(rest),vertex);
            Word witness=paired?independent(next,(bit(order)-1)|((used|bit(chosen))<<order),target):independent(next,((bit(order)-1)|(used<<order))&~next[vertex],target-1);
            if(witness){Word old=witness&(bit(order)-1),avoid=(!paired||(witness&bit(vertex)))?old:0,require=0;if(paired)for(Word rest=old;rest;rest&=rest-1){int point=low(rest);if((old&bit(point^1))&&(graph[point]&bit(point^1)))require|=bit(point);}assert((contacts&require)==require&&!(contacts&avoid));for(int j=block;j<width;++j){Word reject=options[j];for(Word rest=avoid;reject&&rest;rest&=rest-1)reject&=~touch[low(rest)][j];for(Word rest=require;reject&&rest;rest&=rest-1)reject&=touch[low(rest)][j];options[j]&=~reject;}continue;}
            Domains reduced=domains;for(Word rest=unassigned;rest;rest&=rest-1){int slot=low(rest);const auto& relation=(shape[chosen]&bit(slot)?present:absent)[idx];for(int j=0;j<width;++j){reduced[slot][j]&=relation[j];for(Word full=saturated;reduced[slot][j]&&full;full&=full-1)reduced[slot][j]&=~touch[low(full)][j];}}
#ifdef ORDERED24
            for(Word rest=smaller[chosen]&unassigned;rest;rest&=rest-1){auto& option=reduced[low(rest)];if(idx%64!=63)option[idx/64]&=bit(idx%64+1)-1;fill(option.begin()+idx/64+1,option.end(),0);}
            for(Word rest=larger[chosen]&unassigned;rest;rest&=rest-1){auto& option=reduced[low(rest)];option[idx/64]&=~Word(0)<<(idx%64);fill(option.begin(),option.begin()+idx/64,0);}
            if(!possible(unassigned,next,reduced))continue;
#endif
            selected[chosen]=idx;if(solve(unassigned,next,reduced))return true;if(capped)return false;
        }return false;
    }
    bool shape_solve(){Domains domains;for(int slot=0;slot<outer;++slot){domains[slot]=all;for(int idx=0;idx<int(masks.size());++idx)if(size_of(masks[idx])+size_of(shape[slot])>=target)domains[slot][idx/64]&=~bit(idx%64);}
        if(const char* range=getenv("F_FIRST_MASK_RANGE")){string bounds(range);size_t split=bounds.find(':');assert(split!=string::npos);int lower=stoi(bounds.substr(0,split)),upper=stoi(bounds.substr(split+1));assert(0<=lower&&lower<upper&&upper<=int(masks.size()));for(int idx=0;idx<int(masks.size());++idx)if(idx<lower||idx>=upper)domains[0][idx/64]&=~bit(idx%64);}
        capped=false;nodes=0;
#ifdef ORDERED24
        setup_bounds();if(!possible(bit(outer)-1,core,domains))return false;
#endif
        return solve(bit(outer)-1,core,domains);}
};
int main(int argc,char**argv){assert(argc==2);string key;while(cin>>key){Fixed instance;int shapes;cin>>instance.order>>instance.target>>instance.outer>>shapes;instance.paired=instance.order<0;if(instance.paired)instance.order=-instance.order;assert(instance.order+instance.outer<=40&&instance.outer<=8&&instance.target>=3);instance.limit=stoll(argv[1]);for(int old=0;old<instance.order;++old)cin>>instance.core[old];bool ready=instance.prepare();cout<<key<<" masks "<<instance.masks.size()<<' '<<(ready?"ready":instance.masks.size()>5000||instance.capped?"maskcap":"bare")<<endl;
        for(int row=0;row<shapes;++row){int shape;cin>>shape;for(int slot=0;slot<instance.outer;++slot)cin>>instance.shape[slot];if(!ready)continue;bool yes=instance.shape_solve();cout<<key<<' '<<shape<<' '<<(yes?"model":instance.capped?"cap":"empty")<<' '<<instance.nodes;if(yes){cout<<" graph";for(int old=0;old<instance.order+instance.outer;++old)cout<<' '<<instance.model[old];}cout<<endl;}
    }}
