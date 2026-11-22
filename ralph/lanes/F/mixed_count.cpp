#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>

using Mask=uint64_t;
using Graph=std::array<Mask,40>;
using Word=std::array<int,8>;
struct Patch { Graph adj{}; };
using Choices=std::array<std::vector<int>,10>;

Mask bit(int vertex){return Mask(1)<<vertex;}
void edge(Patch& patch,int left,int right,int weight){
    if(left==right || !weight || (weight==1 && !((left^right)&1)))return;
    patch.adj[left]|=bit(right);patch.adj[right]|=bit(left);
}
std::vector<Word> words(int size){
    int total=1;for(int iter=0;iter<size;++iter)total*=3;
    std::vector<Word> answer(total);
    for(int code=0;code<total;++code){int value=code;for(int pos=0;pos<size;++pos){answer[code][pos]=value%3;value/=3;}}
    return answer;
}
std::vector<Patch> internals(int start,int size){
    std::vector<Patch> answer;
    for(auto half:words(size/2))for(int vertical:{0,1}){
        Patch patch;
        for(int left=0;left<2*size;++left)for(int right=left+1;right<2*size;++right){
            int dist=right/2-left/2;edge(patch,2*start+left,2*start+right,dist?half[std::min(dist,size-dist)-1]:vertical);
        }
        answer.push_back(patch);
    }
    return answer;
}
std::vector<Patch> joins(int leftStart,int leftSize,int rightStart,int rightSize){
    int period=std::min(leftSize,rightSize);std::vector<Patch> answer;
    for(auto word:words(period)){
        Patch patch;
        for(int left=0;left<2*leftSize;++left)for(int right=0;right<2*rightSize;++right)
            edge(patch,2*leftStart+left,2*rightStart+right,word[(right/2-left/2+leftSize+rightSize)%period]);
        answer.push_back(patch);
    }
    return answer;
}
bool good(int root,const Patch& first,const Patch& second,const Patch& third){
    Mask neighbors=first.adj[root]|second.adj[root]|third.adj[root], todo=neighbors;
    while(todo){int vertex=std::countr_zero(todo);todo&=todo-1;
        if(neighbors&(first.adj[vertex]|second.adj[vertex]|third.adj[vertex]))return false;}
    return true;
}
std::vector<Choices> compatible(int root,const std::vector<Patch>& layers,const std::vector<Patch>& links){
    std::vector<Choices> answer;Patch empty;
    for(auto& link:links){Choices options;
        for(int index=0;index<int(layers.size());++index){int degree=std::popcount(layers[index].adj[root]);
            if(degree<=9 && good(root,layers[index],link,empty)) options[degree].push_back(index);}
        answer.push_back(options);
    }
    return answer;
}
using Counts=std::array<int,10>;
using Table=std::vector<std::vector<Counts>>;
Table counts(int root,int low,int high,const std::vector<Patch>& layers,const std::vector<Patch>& first,const std::vector<Patch>& second){
    auto left=compatible(root,layers,first),right=compatible(root,layers,second);
    Table table(left.size(),std::vector<Counts>(right.size()));
    for(size_t outer=0;outer<left.size();++outer)for(size_t inner=0;inner<right.size();++inner){
        int fixed=std::popcount(first[outer].adj[root]|second[inner].adj[root]);
        for(int degree=std::max(low,fixed);degree<=high;++degree){
            auto& one=left[outer][degree-fixed];auto& two=right[inner][degree-fixed];
            for(int index:one) table[outer][inner][degree]+=std::binary_search(two.begin(),two.end(),index);
        }
    }
    return table;
}
int main(int argc,char**argv){
    if(argc!=5)return 2;
    int size=std::atoi(argv[1]),low=std::atoi(argv[2]),high=std::atoi(argv[3]),cut=std::atoi(argv[4]);
    if((size!=2 && size!=4 && size!=8)||high>9||low<0)return 2;
    auto across=joins(0,size,size,size),first=joins(0,size,2*size,size/2),second=joins(size,size,2*size,size/2);
    auto left=counts(0,low,high,internals(0,size),across,first);
    auto right=counts(2*size,low,high,internals(size,size),across,second);
    auto small=counts(4*size,low,high,internals(2*size,size/2),first,second);
    std::array<std::array<std::array<Mask,10>,10>,10> result{};
    for(size_t outer=0;outer<across.size();++outer)for(size_t middle=0;middle<first.size();++middle)for(size_t inner=0;inner<second.size();++inner){
        if(std::popcount(first[middle].adj[4*size]|second[inner].adj[4*size])>high)continue;
        if(!good(0,across[outer],first[middle],second[inner]))continue;
        for(int da=low;da<=high;++da)if(left[outer][middle][da])for(int db=low;db<=high;++db)if(right[outer][inner][db])
            for(int dc=low;dc<=high;++dc)if(size*(da+db)+size/2*dc>=cut)result[da][db][dc]+=Mask(left[outer][middle][da])*right[outer][inner][db]*small[middle][inner][dc];
    }
    Mask total=0;for(int da=low;da<=high;++da)for(int db=low;db<=high;++db)for(int dc=low;dc<=high;++dc)
        if(auto count=result[da][db][dc]){std::cout<<da<<' '<<db<<' '<<dc<<' '<<count<<'\n';total+=count;}
    std::cout<<"total "<<total<<'\n';
}
