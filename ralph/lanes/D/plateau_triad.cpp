#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <string>
#include <vector>
using namespace std;
int pop(int mask){return __builtin_popcount(mask);}
int main(int argc,char**argv){
    assert(argc==3);int width=stoi(argv[1]),alpha=stoi(argv[2]);int full=(1<<width)-1;vector<int>perm(width),first(width);iota(perm.begin(),perm.end(),0);for(int site=0;site<width;site++)first[site]=1<<site|1<<((site+1)%width);int index=0;int64_t leaves=0,nodes=0;
    do{if(perm[0]!=0||perm[1]>perm.back())continue;vector<int>second(width),seenFirst(full+1),seenSecond(full+1);for(int idx=0;idx<width;idx++)second[idx]=1<<perm[idx]|1<<perm[(idx+1)%width];for(int mask=1;mask<=full;mask++){int site=__builtin_ctz(mask);seenFirst[mask]=seenFirst[mask&(mask-1)]|first[site];seenSecond[mask]=seenSecond[mask&(mask-1)]|second[site];}
        vector<vector<bool>>valid(full+1,vector<bool>(full+1));for(int left=0;left<=full;left++)for(int right=0;right<=full;right++){bool pass=pop(left)+pop(right)+width-pop(seenFirst[left]|seenSecond[right])<=alpha;for(int bits=right;bits&&pass;bits&=bits-1)pass=valid[left][right^(bits&-bits)];valid[left][right]=pass;}
        vector<int>rows(width),cols(width),blocked(full+1);auto visit=[&](auto&& self,int depth)->void{nodes++;if(depth==width){assert(all_of(cols.begin(),cols.end(),[](int score){return score==2;}));leaves++;cout<<index;for(int x:perm)cout<<' '<<x;for(int x:rows)cout<<' '<<x;cout<<'\n';return;}
            int available=0,mandatory=0;for(int idx=0;idx<width;idx++){if(cols[idx]+width-depth<2)return;if(!(first[depth]&second[idx])&&cols[idx]<2)available|=1<<idx;if(cols[idx]+width-depth==2)mandatory|=1<<idx;}
            for(int word=available;word;word=(word-1)&available){if(pop(word)!=2||(mandatory&~word))continue;bool pass=true;int raised=1<<depth;for(int low=0;low<raised&&pass;low++){int mask=blocked[low]|word;blocked[raised|low]=mask;pass=valid[raised|low][full^mask];}if(!pass)continue;rows[depth]=word;for(int bits=word;bits;bits&=bits-1)cols[__builtin_ctz(bits)]++;self(self,depth+1);for(int bits=word;bits;bits&=bits-1)cols[__builtin_ctz(bits)]--;}
        };visit(visit,0);index++;
    }while(next_permutation(perm.begin(),perm.end()));cerr<<"width "<<width<<" alpha "<<alpha<<" cycles "<<index<<" nodes "<<nodes<<" leaves "<<leaves<<'\n';
}
