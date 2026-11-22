#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <vector>
using namespace std;
using Word=uint32_t;
int bits(Word word){return __builtin_popcount(word);}
struct Engine{
    int cycle,length,stages;long limit;bool reverse_only;array<long,17> visits{};long finished=0;
    vector<Word> transform(const vector<Word>& profile,int step,int offset){vector<Word> out;for(auto word:profile){Word after=0;for(int point=0;point<length;point++)if(word>>point&1)after|=1u<<((offset+step*point+2*length)%length);out.push_back(after);}sort(out.begin(),out.end());return out;}
    void run(vector<Word> profile,int stage){
        if(limit&&finished>=limit)return;
        ++visits[stage];
        if(stage==length){++finished;for(int step:{-1,1})for(int offset=0;offset<length;offset++){if(cycle!=length&&!(step==1&&offset==0)&&!(step==-1&&offset==length-1))continue;if(transform(profile,step,offset)<profile)return;}
            for(auto word:profile)cout<<word<<' ';cout<<'\n';return;}
        vector<int> left(stage),upper(stage),freq;vector<Word> words;for(auto word:profile){if(words.empty()||words.back()!=word){words.push_back(word);freq.push_back(0);}++freq.back();}
        int debit=0;for(int first=0;first<stage;first++)for(int second=first+1;second<stage;second++){int dist=min(second-first,cycle-second+first);if(dist==1)continue;int common=int((first%2)==(second%2))+(dist==2);for(auto word:profile)common+=bool(word>>first&word>>second&1);if(common<2){if(first%2==second%2)return;++debit;}}
        if(debit>1)return;
        for(int site=0;site<stage;site++){int dist=min(stage-site,cycle-stage+site);if(dist==1){left[site]=0;upper[site]=0;}else{int used=int(stage%2==site%2)+(dist==2);left[site]=2-used;upper[site]=3-used;}}
        vector<int> choice(words.size());auto visit=[&](auto&& self,int pos,int need)->void{
            if(need<0)return;if(pos==int(words.size())){if(need)return;int leaks=debit;for(int point=0;point<stage;point++)if(left[point]>0){if(point%2==stage%2 || left[point]>1 || ++leaks>1)return;}
                vector<Word> next;for(int idx=0;idx<pos;idx++){for(int copy=0;copy<freq[idx]-choice[idx];copy++)next.push_back(words[idx]);}for(int idx=0;idx<pos;idx++){for(int copy=0;copy<choice[idx];copy++)next.push_back(words[idx]|(1u<<stage));}run(move(next),stage+1);return;}
            auto word=words[pos];int maximum=min(need,freq[pos]);if(bits(word&(stage%2?0xaaaa:0x5555))>=3)maximum=0;
            for(int site=0;site<stage;site++)if(word>>site&1)maximum=min(maximum,upper[site]);
            for(int count=0;count<=maximum;count++){
                choice[pos]=count;for(int site=0;site<stage;site++)if(word>>site&1){upper[site]-=count;left[site]-=count;}
                self(self,pos+1,need-count);for(int site=0;site<stage;site++)if(word>>site&1){upper[site]+=count;left[site]+=count;}
            }
        };visit(visit,0,6);
    }
};
int main(int argc,char**argv){if(argc!=4)return 1;Engine eng;eng.cycle=stoi(argv[1]);eng.length=stoi(argv[2]);eng.limit=stol(argv[3]);vector<Word> profile(21);while(cin>>profile[0]){for(int idx=1;idx<21;idx++)if(!(cin>>profile[idx]))return 2;eng.run(profile,6);if(eng.limit&&eng.finished>=eng.limit)break;}for(int idx=6;idx<=eng.length;idx++)cerr<<idx<<':'<<eng.visits[idx]<<' ';cerr<<"raw_finals="<<eng.finished<<'\n';}
