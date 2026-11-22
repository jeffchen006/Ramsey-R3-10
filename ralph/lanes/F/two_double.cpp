#include <ctime>
#define main historical_column_main
#include "column_join.cpp"
#undef main

int main(int argc,char** argv){
    if(argc!=7)return 2;
    std::ifstream quotient(argv[1]),bank(argv[3]),rows(argv[4]);std::ofstream trace(argv[5]);
    std::string text;quotient>>text;Join lift(text,std::stoi(argv[2]));int passes=std::stoi(argv[6]);
    std::set<Mask> allowed;Mask mask;while(bank>>mask)if(!allowed.insert(mask).second)return 3;
    size_t kept=0;for(auto& group:lift.supports){std::erase_if(group,[&](const Support& item){return !allowed.contains(item.sites);});kept+=group.size();}
    if(!kept||kept!=allowed.size()||!bank.eof())return 3;
    Mask occupied,doubled,weight;
    while(rows>>occupied>>doubled>>weight){
        auto started=std::clock();
        if(std::popcount(doubled)!=2||(occupied&doubled)!=doubled||occupied>=(1u<<lift.sites))return 4;
        int steps=0;Mask singles=occupied^doubled,first=doubled&-doubled,second=doubled^first;
        auto reach=[&](Mask padding){Mask result=0;for(;padding;padding&=padding-1)result|=lift.adjacent[std::countr_zero(padding)];return result;};
        trace<<"begin "<<occupied<<' '<<doubled<<' '<<occupied<<' '<<doubled<<' '<<doubled<<'\n';
        if(reach(doubled)&occupied){trace<<"end triangle 0\n";continue;}
        Space space=lift.initial;for(int right=0;right<lift.sites;++right)if(singles>>right&1u)
            for(int left=0;left<right;++left)if((singles>>left&1u)&&lift.edge[left][right])space.impose(lift.edge[left][right]);
        bool cut=false;
        for(int pass=0;pass<passes&&!cut;++pass){int previous=steps;
            for(auto [mode,padding]:{std::pair{4,doubled},{2,first},{2,second},{1,0u},{0,0u}}){if(cut)break;
                for(const auto& item:lift.supports[lift.target-mode]){
                    if(item.sites&(padding|reach(padding)))continue;
                    if(mode==1&&(item.sites&doubled))continue;
                    Word residual=0;bool viable=true;auto add=[&](Word form){Word next=space.reduce(form);if(next){if(next==1||(residual&&next!=residual))return false;residual=next;}return true;};
                    for(auto cycle:item.cycles)if(!add(cycle)){viable=false;break;}
                    Mask pins=mode==1?singles&item.sites:0;
                    for(int part=0;viable&&pins&&part<item.parts;++part){Mask hits=pins&item.components[part];if(!hits)continue;
                        Word anchor=item.path[std::countr_zero(hits)];for(hits&=hits-1;hits;hits&=hits-1)
                            if(!add(anchor^item.path[std::countr_zero(hits)])){viable=false;break;}}
                    if(!viable)continue;
                    trace<<"step "<<mode<<' '<<padding<<' '<<item.sites<<' '<<(item.sites^pins)<<' '<<item.sites<<' '<<residual<<'\n';++steps;
                    if(!residual){cut=true;break;}if(!space.impose(residual^one))return 6;
                }
            }
            if(steps==previous)break;
        }
        trace<<"end "<<(cut?"I":"open")<<' '<<steps<<'\n';
        std::cout<<occupied<<' '<<doubled<<' '<<double(std::clock()-started)/CLOCKS_PER_SEC<<'\n';
    }
    return !rows.eof()||!trace;
}
