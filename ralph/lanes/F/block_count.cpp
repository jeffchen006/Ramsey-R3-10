#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>

using Word=std::array<int,10>;
struct Layer { Word steps{}; int degree=0; };

int main(int argc,char** argv){
    if(argc!=5)return 2;
    int size=std::atoi(argv[1]),low=std::atoi(argv[2]),high=std::atoi(argv[3]),cut=std::atoi(argv[4]);
    if(size<2||size>10||size%2||high>20)return 2;
    std::vector<Layer> layers;
    int inners=1,outers=1;
    for(int step=0;step<size;++step){outers*=3;if(step<size/2)inners*=3;}
    for(int code=0;code<inners;++code)for(int vertical=0;vertical<=1;++vertical){
        Layer layer;layer.steps[0]=vertical;int value=code;
        for(int step=1;step<=size/2;++step){layer.steps[step]=layer.steps[size-step]=value%3;value/=3;}
        for(int step=0;step<size;++step)layer.degree+=layer.steps[step];
        layers.push_back(layer);
    }
    std::array<std::array<int64_t,21>,21> pairs{};std::array<int64_t,21> dihedral{};
    for(int code=0;code<outers;++code){
        int value=code,mass=0;Word cross{};
        for(int step=0;step<size;++step){cross[step]=value%3;value/=3;mass+=cross[step];}
        if(mass>high)continue;
        std::array<int64_t,21> eligible{};
        for(auto& layer:layers){
            int degree=mass+layer.degree;if(degree<low||degree>high)continue;
            auto edge=[&](int left,int right){
                int left_fiber=left/2,right_fiber=right/2;
                if(left==right)return false;
                if(left_fiber>=size && right_fiber>=size)return false;
                if(left_fiber>right_fiber)std::swap(left_fiber,right_fiber);
                int step=(right_fiber-left_fiber)%size;
                int weight=right_fiber>=size?cross[step]:layer.steps[step];
                return weight==2 || (weight==1 && ((left^right)&1));
            };
            bool triangle=false;uint64_t neighbors=0;
            for(int vertex=1;vertex<4*size&&!triangle;++vertex)if(edge(0,vertex)){
                uint64_t mask=neighbors;
                while(mask){int other=std::countr_zero(mask);mask&=mask-1;
                    if(edge(other,vertex)){triangle=true;break;}}
                neighbors|=uint64_t(1)<<vertex;
            }
            if(!triangle)++eligible[degree];
        }
        for(int first=low;first<=high;++first){
            if(2*first>=cut)dihedral[first]+=eligible[first];
            for(int second=low;second<=high;++second)if(first+second>=cut)
                pairs[first][second]+=eligible[first]*eligible[second];
        }
    }
    for(int first=low;first<=high;++first){
        if(dihedral[first])std::cout<<"D "<<first<<' '<<first<<' '<<dihedral[first]<<'\n';
        for(int second=low;second<=high;++second)if(pairs[first][second])
            std::cout<<"B "<<first<<' '<<second<<' '<<pairs[first][second]<<'\n';
    }
}
