#define main previous_relift_main
#include "relift.cpp"
#undef main
#include <bitset>
#include <map>
#include <sstream>

struct Piece{Mask full,single;int remaining;};
struct Odd {
    const Quotient& base;int target,limit,total=0,baseline=0,added=0,packs=0;
    Mask vertical=0;std::array<Mask,MAXF> doubles{};
    std::array<std::array<Form,MAXF>,MAXF> labels{};
    std::map<Form,std::vector<Piece>> pools;
    Form fallback=0;
    std::ostringstream log;
    Odd(const Quotient& input,int order,int goal,const Basis* cell=nullptr):base(input),target(order),limit(goal){
        for(int vertex=0;vertex<base.size;++vertex){if(base.frozen[2*vertex]&bit(2*vertex+1))vertical|=bit(vertex);doubles[vertex]=base.occupied[vertex]^base.simple[vertex];}
        for(auto [left,right,form]:base.singles)labels[left][right]=labels[right][left]=(cell?*cell:base.structural).reduce(form);
    }
    bool circuit(){
        std::array<Form,127> equations{};std::array<std::bitset<128>,127> provenance{};std::vector<Form> keys;
        for(auto& [character,stack]:pools){
            if(stack.empty())continue;
            Form pending=character^RHS;std::bitset<128> indices;indices.set(keys.size());
            while(pending&~RHS){int pivot=top(pending&~RHS);if(!equations[pivot]){equations[pivot]=pending;provenance[pivot]=indices;keys.push_back(character);break;}
                pending^=equations[pivot];indices^=provenance[pivot];}
            if(pending!=RHS)continue;
            keys.push_back(character);std::vector<Form> conflict;int gain=limit-total;
            for(size_t pos=0;pos<keys.size();++pos)if(indices.test(pos)){conflict.push_back(keys[pos]);gain=std::min(gain,pools[keys[pos]].back().remaining);}
            if(conflict.size()<2||gain<=0)throw std::logic_error("invalid affine conflict");
            log<<" C"<<gain;
            for(Form form:conflict){auto& stock=pools[form];auto& piece=stock.back();log<<':'<<piece.full<<','<<piece.single;
                piece.remaining-=gain;if(!piece.remaining)stock.pop_back();}
            total+=gain;++packs;return true;
        }
        return false;
    }
    void packing(){while(total<limit && circuit()){};}
    void process(Mask full,Mask single){
        std::array<Form,MAXF> dist{};Mask unseen=single;Form character=0;int weight=1;
        while(unseen){weight*=2;Mask todo=bit(take(unseen));while(todo){int left=take(todo);Mask neighbors=base.simple[left]&single;
            while(neighbors){int right=take(neighbors);Form path=dist[left]^labels[left][right];
                if(unseen&bit(right)){unseen^=bit(right);todo|=bit(right);dist[right]=path;}
                else if(Form cycle=path^dist[right]){if(cycle==RHS)return;if(!fallback)fallback=cycle&~RHS;if(character && cycle!=character)return;character=cycle;}}}}
        if(!character){log<<" U"<<weight<<':'<<full<<','<<single;baseline+=weight;total+=weight;}
        else {pools[character].push_back({full,single,weight});if(++added%64==0)packing();}
    }
    void singles(Mask full,Mask chosen,Mask eligible,int need){
        if(total>=limit)return;if(!need){process(full,chosen);return;}
        while(std::popcount(eligible)>=need && total<limit){int vertex=take(eligible);singles(full,chosen|bit(vertex),eligible&~doubles[vertex],need-1);}
    }
    void fulls(Mask full,Mask eligible,Mask pool,int need){
        if(total>=limit)return;if(!need){singles(full,0,pool,target-2*std::popcount(full));return;}
        while(std::popcount(eligible)>=need && total<limit){int vertex=take(eligible);Mask compatible=~(base.occupied[vertex]|bit(vertex));fulls(full|bit(vertex),eligible&compatible,pool&compatible,need-1);}
    }
    void run(){Mask all=bit(base.size)-1;for(int need=target/2;need>=0 && total<limit;--need)fulls(0,all&~vertical,all,need);packing();}
};
int main(int argc,char**argv){
    if(argc!=5 && argc!=6)return 2;std::ifstream input(argv[1]);std::ofstream receipt(argv[4]);std::string text;int id=0;
    while(input>>text){Quotient base(text,0,100,0,10000);Odd odd(base,std::stoi(argv[2]),std::stoi(argv[3]));odd.run();
        if(argc==5){receipt<<id<<odd.log.str()<<'\n';std::cout<<id++<<' '<<odd.total<<' '<<odd.baseline<<' '<<odd.packs<<' '<<odd.added<<'\n';continue;}
        Basis start;
        for(auto [left,right,form]:base.singles)for(int third=right+1;third<base.size;++third)
            if(base.marks[left][third] && base.marks[right][third])start.insert(form^base.marks[left][third]^base.marks[right][third]);
        int leaves=0,unresolved=0,depth=0,minimum=1000000;receipt<<"ROW "<<id<<'\n';
        auto solve=[&](auto&& recurse,const Basis& cell,int level)->void{
            Odd node(base,odd.target,odd.limit,&cell);node.run();depth=std::max(depth,level);Form split=node.fallback;int strongest=-1;
            for(auto& [form,stock]:node.pools){int mass=0;for(auto& piece:stock)mass+=piece.remaining;
                if(mass>strongest){split=form&~RHS;strongest=mass;}}
            if(node.total>=node.limit || level==std::stoi(argv[5]) || !split){
                minimum=std::min(minimum,node.total);++leaves;unresolved+=node.total<node.limit;receipt<<"L "<<node.total<<node.log.str()<<'\n';return;}
            receipt<<"B "<<Mask(split>>64)<<' '<<Mask(split)<<'\n';
            for(int value:{0,1}){Basis child=cell;child.insert(split^(value?RHS:0));recurse(recurse,child,level+1);}
        };
        solve(solve,start,0);std::cout<<id++<<' '<<minimum<<' '<<leaves<<' '<<unresolved<<' '<<depth<<std::endl;
    }
    return !input.eof()||!receipt;
}
