#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <string>
#include <vector>
using namespace std;
using Rows=array<int,8>;
int pop(int word){return __builtin_popcount(word);}
bool local(const Rows&rows){
    Rows column{};for(int site=0;site<8;site++)for(int other=0;other<8;other++)if(rows[site]>>other&1)column[other]|=1<<site;
    for(auto&side:{rows,column})for(int first=0;first<8;first++){if(pop(side[first])>3)return false;for(int second=0;second<first;second++)if(pop(side[first]&side[second])>2)return false;}return true;
}
int matchings(const Rows&rows){array<int,256>ways{};ways[0]=1;for(int mask=0;mask<255;mask++)for(int choices=rows[pop(mask)]&~mask;choices;choices&=choices-1)ways[mask|(choices&-choices)]+=ways[mask];return ways[255];}
int main(int argc,char**argv){
    assert(argc==3);int maxExtra=stoi(argv[1]);ifstream meta(argv[2]);vector<pair<int,int>>arcs;for(int first=0;first<8;first++)for(int last=0;last<8;last++)if(first!=last)arcs.emplace_back(first,last);
    vector<uint64_t>raw(maxExtra+1),weighted(maxExtra+1);Rows diagonal;for(int idx=0;idx<8;idx++)diagonal[idx]=1<<idx;
    auto generate=[&](auto&&self,Rows&rows,int first,int level)->void{raw[level]++;if(level==maxExtra)return;for(int idx=first;idx<(int)arcs.size();idx++){auto [src,dst]=arcs[idx];rows[src]^=1<<dst;if(local(rows))self(self,rows,idx+1,level+1);rows[src]^=1<<dst;}};generate(generate,diagonal,0,0);
    Rows perm; iota(perm.begin(),perm.end(),0);vector<array<uint8_t,256>>images;do{array<uint8_t,256>image{};for(int mask=1;mask<256;mask++)image[mask]=image[mask&(mask-1)]|1<<perm[__builtin_ctz(mask)];images.push_back(image);}while(next_permutation(perm.begin(),perm.end()));
    set<uint64_t>unique;string graph,receipt;int idx=0;
    while(cin>>graph){assert(getline(meta,receipt));int parent=idx++;Rows rows{};int pos=0,edges=0;for(int right=0;right<16;right++)for(int left=0;left<right;left++,pos++)if((graph[1+pos/6]-63)>>(5-pos%6)&1){rows[left]|=1<<(right-8);edges++;}if(edges>8+maxExtra)continue;
        int match=matchings(rows);if(!match||!local(rows)){assert(receipt.find(" pre")!=string::npos);continue;}assert(receipt.find(" pre")==string::npos);sort(rows.begin(),rows.end());int stabilizer=0,rowperm=1;int multiplicity=0,last=-1;for(int row:rows){multiplicity=row==last?multiplicity+1:1;last=row;rowperm*=multiplicity;}
        uint64_t best=UINT64_MAX;for(auto&image:images){Rows moved;for(int slot=0;slot<8;slot++)moved[slot]=image[rows[slot]];sort(moved.begin(),moved.end());if(moved==rows)stabilizer++;uint64_t key=0;for(int row:moved)key=key<<8|row;best=min(best,key);}assert(unique.insert(best).second);int aut=stabilizer*rowperm;assert((40320ll*match)%aut==0);int weight=(40320ll*match)/aut;weighted[edges-8]+=weight;cout<<parent<<' '<<edges<<' '<<best<<' '<<aut<<' '<<match<<' '<<weight<<'\n';
    }
    for(int level=0;level<=maxExtra;level++){assert(raw[level]==weighted[level]);cerr<<level+8<<' '<<raw[level]<<' '<<weighted[level]<<'\n';}cerr<<"PASS independent labelled diagonal cover, distinct oriented classes "<<unique.size()<<'\n';
}
