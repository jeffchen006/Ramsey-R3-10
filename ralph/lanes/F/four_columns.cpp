#define main legacy_relift_main
#include "relift.cpp"
#undef main
#include <map>
#include <tuple>

struct Screen {
    const Quotient& base;
    int target,degree,universe;
    bool model,verbose;
    std::vector<int> independent_number;
    std::vector<Mask> balance;
    std::array<std::array<Form,MAXF>,MAXF> labels{};
    std::vector<std::vector<Mask>> components;
    std::map<std::tuple<int,int,int>,long> counts;
    std::ofstream& rows;
    Screen(const Quotient& card,int order,bool template_mode,bool logall,std::ofstream& output):base(card),target(order),degree(0),universe((1<<base.size)-1),model(template_mode),verbose(logall),independent_number(universe+1),rows(output){
        for(auto [left,right,mark]:base.singles)labels[left][right]=labels[right][left]=base.structural.reduce(mark);
        degree=std::popcount(base.simple[0])+2*std::popcount(base.occupied[0]&~base.simple[0]);
        for(int mask=1;mask<=universe;++mask){
            int site=std::countr_zero(unsigned(mask)),rest=mask&(mask-1);
            independent_number[mask]=std::max(independent_number[rest],1+independent_number[rest&~base.occupied[site]]);
            if(std::popcount(unsigned(mask))==target-1)collect(mask);
        }
    }
    void collect(Mask mask){
        std::array<Form,MAXF> offset{};Mask unseen=mask;std::vector<Mask> parts;
        while(unseen){Mask todo=bit(take(unseen)),component=0;
            while(todo){int left=take(todo);component|=bit(left);
                if((base.occupied[left]&~base.simple[left])&mask)return;
                Mask neighbors=base.simple[left]&mask;
                while(neighbors){int right=take(neighbors);Form implied=offset[left]^labels[left][right];
                    if(unseen&bit(right)){unseen^=bit(right);todo|=bit(right);offset[right]=implied;}
                    else if(implied!=offset[right])return;
                }
            }parts.push_back(component);
        }balance.push_back(mask);components.push_back(parts);
    }
    bool connected(Mask mask){
        if(!mask)return true;Mask todo=bit(take(mask));
        while(todo&&mask){int left=take(todo);Mask fresh=base.simple[left]&mask;mask^=fresh;todo|=fresh;}
        return !mask;
    }
    int stage(Mask full,Mask single){
        int size=std::popcount(single);Mask spare=universe&~(full|single),weak=0;
        while(spare){int site=take(spare);
            int touches=std::popcount(single&base.simple[site])+2*std::popcount(single&base.occupied[site]&~base.simple[site]);
            if(touches<=1)weak|=bit(site);
        }
        if(size+independent_number[weak]>=target-1)return 1;
        for(size_t pos=0;pos<balance.size();++pos){
            if(balance[pos]&full)continue;
            bool witness=true;for(Mask component:components[pos])if(!connected(component&single)){witness=false;break;}
            if(witness)return 2;
        }
        return 3;
    }
    void run(int lo){
        for(int full=0;full<=universe;++full){
            int both=std::popcount(unsigned(full));if(2*both>=target||independent_number[full]!=both)continue;
            Mask allowed=universe^full,sites=full;
            bool legal=true;
            while(sites){int site=take(sites);allowed&=~base.occupied[site];if(!model&&(base.frozen[2*site]&bit(2*site+1)))legal=false;}
            if(!legal)continue;
            for(Mask single=allowed;;single=(single-1)&allowed){
                int size=2*both+std::popcount(single);
                if(size>=lo&&size<target){
                    Mask scan=single;legal=true;while(scan){int site=take(scan);if((base.occupied[site]&~base.simple[site])&single){legal=false;break;}}
                    if(legal){int pass=stage(full,single);++counts[{size,both,pass}];
                        if((verbose||pass==3))rows<<full<<' '<<single<<' '<<size<<' '<<pass<<'\n';}
                }
                if(!single)break;
            }
        }
    }
};

int main(int argc,char**argv){
    if(argc!=6)return 2;
    std::ifstream input(argv[1]);std::ofstream out(argv[5]);std::string text;
    while(input>>text){Quotient base(text,0,100,0,10000);bool model=std::stoi(argv[4]);Screen screen(base,std::stoi(argv[2]),model,!model,out);screen.run(std::stoi(argv[3]));
        std::cout<<"basis "<<base.singles.size()-base.structural.rank<<" universal "<<screen.balance.size()<<'\n';
        for(auto [key,num]:screen.counts){auto [size,both,stage]=key;std::cout<<size<<' '<<both<<' '<<stage<<' '<<num<<'\n';}
    }return !input.eof()||!out;
}
