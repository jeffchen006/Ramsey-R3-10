#include <algorithm>
#include <array>
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;
using Deck=array<int,21>;
struct Catalog {
    int width; vector<int> order; long raw=0,canon=0;
    int distance(int left,int right){int span=abs(left-right);return width==8?min(span,8-span):span;}
    bool minimal(const Deck& deck){
        for(int sign:{1,-1})for(int shift=0;shift<width;shift++){
            if(width==6&&!((sign==1&&shift==0)||(sign==-1&&shift==5)))continue;
            Deck relabel{};for(int slot=0;slot<21;slot++)for(int point=0;point<width;point++)if(deck[slot]&(1<<point))relabel[slot]|=1<<((width+shift+sign*point)%width);
            sort(relabel.begin(),relabel.end());if(relabel<deck)return false;
        }return true;
    }
    void enumerate(const Deck& deck,int depth){
        if(depth==width){raw++;if(!minimal(deck))return;canon++;for(auto word:deck)cout<<word<<' ';cout<<'\n';return;}
        int point=order[depth];array<int,8> floors{},ceilings{};int forbidden=0;
        for(int prior=0;prior<depth;prior++){int other=order[prior],dist=distance(point,other);if(dist==1){forbidden|=1<<other;continue;}int used=(dist%2==0)+(dist==2);floors[other]=2-used;ceilings[other]=3-used;}
        array<int,6> picks{};auto choose=[&](auto&& self,int start,int count)->void{
            if(count==6){auto lows=floors;auto highs=ceilings;for(int slot:picks){int row=deck[slot];for(int before=0;before<depth;before++){int site=order[before];if(row>>site&1){lows[site]--;if(--highs[site]<0)return;}}}
                if(*max_element(lows.begin(),lows.end())>0)return;auto next=deck;for(int slot:picks)next[slot]|=1<<point;sort(next.begin(),next.end());enumerate(next,depth+1);return;}
            for(int slot=start;slot<=21-(6-count);slot++){
                if(slot>start&&deck[slot]==deck[slot-1])continue;
                int row=deck[slot];if((row&forbidden)||__builtin_popcount(row&(point%2?0xAA:0x55))>=3)continue;picks[count]=slot;self(self,slot+1,count+1);
            }
        };choose(choose,0,0);
    }
};
int main(int argc,char**argv){if(argc!=2)return 2;Catalog engine;engine.width=atoi(argv[1]);engine.order=engine.width==6?vector<int>{2,3,1,4,0,5}:vector<int>{2,3,1,4,0,5,7,6};engine.enumerate(Deck{},0);cerr<<"physical ordered columns: "<<engine.raw<<" stabilizer representatives: "<<engine.canon<<'\n';}
