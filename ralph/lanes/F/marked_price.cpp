#include <algorithm>
#include <array>
#include <cassert>
#include <cstdlib>
#include <fstream>
#include <immintrin.h>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
using namespace std;

int countbits(unsigned mask){return __builtin_popcount(mask);}
int indexof(unsigned mask){return __builtin_ctz(mask);}

struct Support { unsigned mask; array<unsigned char,512> accepts{}; int weight=0; };

struct Price {
    int sites, target; unsigned all;
    vector<unsigned> adj,reach,mirror; vector<int> forestmax; vector<Support> supports;
    Price(int size,int threshold):sites(size),target(threshold),all((1u<<size)-1),adj(size),reach(all+1),mirror(all+1),forestmax(all+1){
        for(int left=0;left<sites;left++)for(int right=0;right<sites;right++){
            int dist=abs(left-right);if((sites==3 && dist==1)||(sites==17 && dist>=6 && dist<=12))adj[left]|=1u<<right;
        }
        for(unsigned mask=1;mask<=all;mask++){
            unsigned bit=mask&-mask;int site=indexof(bit);reach[mask]=reach[mask^bit]|adj[site];mirror[mask]=mirror[mask^bit]|(1u<<(sites-1-site));
            if(pinned_forest(mask,0))forestmax[mask]=countbits(mask);
            else for(unsigned rest=mask;rest;rest&=rest-1)forestmax[mask]=max(forestmax[mask],forestmax[mask^(rest&-rest)]);
        }
        for(unsigned mask=1;mask<=all;mask++)if(countbits(mask)==target-1){
            Support item;item.mask=mask;
            for(unsigned pins=mask;;pins=(pins-1)&mask){
                bool good=pinned_forest(mask,pins);item.accepts[_pext_u32(pins,mask)]=good;item.weight+=good;if(!pins)break;
            }
            supports.push_back(item);
        }
        sort(supports.begin(),supports.end(),[](const auto &first,const auto &second){return first.weight!=second.weight?first.weight>second.weight:first.mask<second.mask;});
    }
    bool pinned_forest(unsigned mask,unsigned pins) const {
        unsigned remaining=mask&~pins;
        while(remaining){
            unsigned layer=remaining&-remaining;remaining^=layer;int twice=0,contacts=0,size=0;
            while(layer){unsigned bit=layer&-layer;layer^=bit;unsigned neighbors=adj[indexof(bit)];unsigned more=neighbors&remaining;remaining^=more;layer|=more;
                size++;twice+=countbits(neighbors&mask&~pins);contacts+=countbits(neighbors&pins);if(contacts>1)return false;
            }
            if(twice!=2*(size-1))return false;
        }
        return true;
    }
    int stage(unsigned occupied,unsigned doubles,unsigned &witness,bool exterior=false) const {
        witness=0;
        if(reach[doubles]&occupied)return 0;
        for(unsigned holes=doubles;holes;holes=(holes-1)&doubles){unsigned available=all&~(holes|reach[holes]);
            if(2*countbits(holes)+forestmax[available]>=target){witness=holes;return 1;}
        }
        if(!exterior && doubles && 2+forestmax[all^occupied]>=target)return 2;
        if(countbits(occupied^doubles)>=target-1)return 3;
        for(auto &support:supports)if(!(support.mask&doubles)&&support.accepts[_pext_u32(occupied,support.mask)]){witness=support.mask;return 4;}
        return 5;
    }
    void census(int stride,const string &prefix,bool exterior) const {
        ofstream residual(prefix+".rows"),rejects(prefix+".rejects"),breakdown(prefix+".counts");long long totals[6][10][5][2]={};long long saved=0;
        for(unsigned occupied=0;occupied<=all;occupied++){
            if(countbits(occupied)>target-1)continue;
            for(unsigned doubles=occupied;;doubles=(doubles-1)&occupied){
                int degree=countbits(occupied)+countbits(doubles);
                if(degree<target && pair(occupied,doubles)<=pair(mirror[occupied],mirror[doubles])){
                    int orbit=1+(occupied!=mirror[occupied]||doubles!=mirror[doubles]);
                    if(saved++%stride==0){unsigned witness;int status=stage(occupied,doubles,witness,exterior);
                        totals[status][degree][countbits(doubles)][0]++;totals[status][degree][countbits(doubles)][1]+=orbit;
                        if(status==5)residual<<occupied<<' '<<doubles<<' '<<orbit<<'\n';
                        if(status>0 && status<5){
                            unsigned forest=0;
                            if(status<=2){forest=status==1?(all&~(witness|reach[witness])):(all^occupied);
                                for(unsigned bits=forest;bits;bits&=bits-1){unsigned bit=bits&-bits;if(forestmax[forest]==forestmax[forest^bit])forest^=bit;}
                                assert(pinned_forest(forest,0) && countbits(forest)+(status==1?2*countbits(witness):2)>=target);
                            }
                            rejects<<occupied<<' '<<doubles<<' '<<orbit<<' '<<status<<' '<<witness<<' '<<forest<<'\n';
                        }
                    }
                }
                if(!doubles)break;
            }
        }
        for(int status=0;status<6;status++){
            long long reps=0,labels=0;for(int degree=0;degree<target;degree++)for(int doubles=0;2*doubles<=degree;doubles++){
                auto entry=totals[status][degree][doubles];if(entry[0])breakdown<<status<<' '<<degree<<' '<<doubles<<' '<<entry[0]<<' '<<entry[1]<<'\n';reps+=entry[0];labels+=entry[1];
            }
            cout<<"stage "<<status<<" reps "<<reps<<" labelled "<<labels<<'\n';
        }
        cout<<"total reps before sampling "<<saved<<" stride "<<stride<<" supports "<<supports.size()<<'\n';
    }
};

int main(int argc,char **argv){assert(argc==4);string mode=argv[1];bool control=mode=="control"||mode=="smallpole";assert(control || mode=="price" || mode=="pole");Price price(control?3:17,control?4:10);
    if(control){unsigned witness;assert(price.stage(5,0,witness)==5);assert(price.stage(0,0,witness)==4 && witness==7);}
    price.census(stoi(argv[2]),argv[3],mode=="pole"||mode=="smallpole");
}
