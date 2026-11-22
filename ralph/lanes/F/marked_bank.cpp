#define main historical_column_main
#include "column_join.cpp"
#undef main

int main(int argc,char** argv){
    if(argc!=7)return 2;
    std::ifstream base(argv[1]),bank(argv[3]),roster(argv[4]);
    std::ofstream trace(argv[5]);std::string encoded;base>>encoded;
    int order=std::stoi(argv[2]),passes=std::stoi(argv[6]);Join engine(encoded,order);
    std::set<Mask> allowed;Mask mask;
    while(bank>>mask){if(!allowed.insert(mask).second)return 3;}
    size_t kept=0;
    for(auto& group:engine.supports){
        std::erase_if(group,[&](const auto& record){return !allowed.contains(record.sites);});
        kept+=group.size();
    }
    if(kept!=allowed.size()||!bank.eof()||!kept)return 4;
    unsigned occupied,full,weight;
    while(roster>>occupied>>full>>weight){
        if(full||occupied>=(1u<<engine.sites))return 5;
        engine.run(std::to_string(occupied),1,{occupied},{0},0,trace,passes,nullptr);
    }
    return !roster.eof()||!trace;
}
