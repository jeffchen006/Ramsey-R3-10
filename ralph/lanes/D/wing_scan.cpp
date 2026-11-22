#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
using namespace std;
using Bits=unsigned;
int countbits(Bits word){return __builtin_popcount(word);}
bool augment(int point,const vector<Bits>&rows,vector<int>&mate,Bits&seen){
    for(Bits avail=rows[point]&~seen;avail;avail&=avail-1){int col=__builtin_ctz(avail);if(seen>>col&1)continue;seen|=1u<<col;
        if(mate[col]<0||augment(mate[col],rows,mate,seen)){mate[col]=point;return true;}}
    return false;
}
int main(int argc,char**argv){
    assert(argc==5);int width=stoi(argv[1]),outsideZ=stoi(argv[2]);Bits full=(1u<<width)-1;
    ifstream table(argv[3],ios::binary),badfile(argv[4]);array<unsigned char,65536>types;table.read((char*)types.data(),types.size());assert(table.gcount()==65536);
    array<bool,42>bad{};int idx;while(badfile>>idx)bad[idx+1]=true;
    vector<array<int,4>>fours;vector<array<unsigned char,256>>compress;
    for(Bits mask=0;mask<=full;mask++)if(countbits(mask)==4){array<int,4>indices;int pos=0;for(int site=0;site<width;site++)if(mask>>site&1)indices[pos++]=site;fours.push_back(indices);array<unsigned char,256> cache{};
        for(Bits word=0;word<=full;word++)for(int place=0;place<4;place++)cache[word]|=((word>>indices[place])&1)<<place;
        compress.push_back(cache);}
    string line;int rank=0;
    while(cin>>line){assert(line[0]==63+2*width);vector<Bits>rows(width),cols(width);int edge=0,pos=0;
        for(int v=0;v<2*width;v++)for(int u=0;u<v;u++,pos++)if((line[1+pos/6]-63)>>(5-pos%6)&1){assert(u<width&&v>=width);rows[u]|=1u<<(v-width);cols[v-width]|=1u<<u;edge++;}
        bool valid=true;for(auto&side:{rows,cols})for(int u=0;u<width;u++){valid&=countbits(side[u])<=3;for(int v=0;v<u;v++)valid&=countbits(side[u]&side[v])<=2;}
        vector<int>mate(width,-1);for(int point=0;point<width&&valid;point++){Bits marked=0;valid=augment(point,rows,mate,marked);}
        if(!valid){cout<<rank++<<' '<<edge<<" pre\n";continue;}
        uint64_t seen=0;int forbidden=0;
        for(auto&part:compress){array<int,8>patterns;for(int point=0;point<width;point++)patterns[point]=part[rows[point]];
            for(auto&inds:fours){auto type=types[patterns[inds[0]]|(patterns[inds[1]]<<4)|(patterns[inds[2]]<<8)|(patterns[inds[3]]<<12)];if(type)seen|=1ull<<(type-1);if(width==8&&bad[type])forbidden++;}}
        vector<Bits>reach(width);for(int point=0;point<width;point++)for(int col=0;col<width;col++)if(rows[point]>>col&1)reach[point]|=1u<<mate[col];
        for(int middle=0;middle<width;middle++)for(int point=0;point<width;point++)if(reach[point]>>middle&1)reach[point]|=reach[middle];
        int paths=0;vector<Bits>pairs(width);
        for(int col=0;col<width;col++)for(int point=0;point<width;point++)if(!(rows[point]>>col&1)&&(reach[mate[col]]>>point&1)){pairs[point]|=1u<<col;paths++;}
        int cut=3*paths;
        for(Bits left=0;left<=full;left++){
            int demand=0;vector<int>weight(width);
            for(int point=0;point<width;point++)if(left>>point&1)demand+=width-countbits(rows[point]);else for(Bits active=pairs[point];active;active&=active-1)weight[__builtin_ctz(active)]+=3;
            for(int col=0;col<width;col++)demand+=min(weight[col],width-countbits(cols[col]));cut=min(cut,demand);}
        cout<<rank++<<' '<<edge<<' '<<(forbidden?"minor":cut<outsideZ?"return":"live")<<' '<<seen<<' '<<forbidden<<' '<<paths<<' '<<cut<<'\n';
    }
}
