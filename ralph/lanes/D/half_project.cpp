#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
int main(int argc,char**argv){
    assert(argc==4);ifstream lookup(argv[1]),scan(argv[2]),extra(argv[3]);unordered_map<uint32_t,int>classes;uint32_t word;int id,valid;while(lookup>>word>>id>>valid)classes[word]=valid?-(id+1):id;
    while(extra>>id)for(auto&entry:classes)if(entry.second==-(id+1))entry.second=id;
    vector<array<unsigned char,256>>compress;for(int subset=0;subset<256;subset++)if(__builtin_popcount(subset)==4){array<unsigned char,256>image{};for(int mask=0;mask<256;mask++){int rank=0;for(int site=0;site<8;site++)if(subset>>site&1)image[mask]|=((mask>>site&1)&1)<<rank++;}compress.push_back(image);}
    string header,text;int rank=0;while(cin>>text){assert(getline(scan,header));istringstream row(header);int parent,edges;string status;row>>parent>>edges>>status;assert(rank++==parent);if(status!="live"){cout<<parent<<" skip\n";continue;}
        array<array<int,8>,2>sides{};int pos=0;for(int right=0;right<16;right++)for(int left=0;left<right;left++,pos++)if((text[1+pos/6]-63)>>(5-pos%6)&1){assert(left<8&&right>=8);sides[0][left]|=1<<(right-8);sides[1][right-8]|=1<<left;}
        int fail=-1;for(auto&side:sides){if(fail>=0)break;for(auto&projection:compress){array<int,8>parts;for(int idx=0;idx<8;idx++)parts[idx]=projection[side[idx]];sort(parts.begin(),parts.end());uint32_t key=0;for(int idx=0;idx<8;idx++)key|=uint32_t(parts[idx])<<(4*idx);int which=classes.at(key);if(which>=0){fail=which;break;}}}
        cout<<parent<<' '<<(fail<0?"live":"half")<<' '<<fail<<' '<<edges;uint64_t seen;row>>seen;cout<<' '<<seen<<'\n';
    }
}
