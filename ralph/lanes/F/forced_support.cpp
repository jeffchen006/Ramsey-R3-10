#define main relift_old_main
#include "relift.cpp"
#undef main

struct Forced {
    const Quotient& quotient;
    int target, limit, total = 0, support_count = 0;
    Mask vertical = 0;
    std::array<Mask, MAXF> doubles{};
    std::array<std::array<Form,MAXF>,MAXF> voltage{};
    std::ostream& out;

    Forced(const Quotient& source, int order, int cutoff, std::ostream& output)
        :quotient(source), target(order), limit(cutoff), out(output) {
        for(int vertex=0;vertex<quotient.size;++vertex){
            if(quotient.frozen[2*vertex]&bit(2*vertex+1)) vertical |= bit(vertex);
            doubles[vertex]=quotient.occupied[vertex]^quotient.simple[vertex];
        }
        for(auto [left,right,mark]:quotient.singles)
            voltage[left][right]=voltage[right][left]=quotient.structural.reduce(mark);
    }

    int multiplicity(Mask single) const {
        std::array<Form,MAXF> offsets{};
        int count=1;
        Mask unseen=single;
        while(unseen){
            count*=2;
            Mask pending=bit(take(unseen));
            while(pending){
                int left=take(pending);
                Mask neighbors=quotient.simple[left]&single;
                while(neighbors){
                    int right=take(neighbors);
                    Form implied=offsets[left]^voltage[left][right];
                    if(unseen&bit(right)){
                        unseen^=bit(right);pending|=bit(right);offsets[right]=implied;
                    }else if(offsets[right]!=implied) return 0;
                }
            }
        }
        return count;
    }

    void singles(Mask full, Mask chosen, Mask allowed, int need){
        if(total>=limit) return;
        if(need==0){
            int count=multiplicity(chosen);
            if(count){total+=count;++support_count;out<<' '<<full<<':'<<chosen<<':'<<count;}
            return;
        }
        while(std::popcount(allowed)>=need && total<limit){
            int next=take(allowed);
            singles(full,chosen|bit(next),allowed&~doubles[next],need-1);
        }
    }

    void fulls(Mask full, Mask allowed, Mask pool, int need){
        if(total>=limit) return;
        if(!need){singles(full,0,pool,target-2*std::popcount(full));return;}
        while(std::popcount(allowed)>=need && total<limit){
            int next=take(allowed);
            Mask forbidden=quotient.occupied[next]|bit(next);
            fulls(full|bit(next),allowed&~forbidden,pool&~forbidden,need-1);
        }
    }

    void run(){
        Mask all=bit(quotient.size)-1;
        for(int count=target/2;count>=0 && total<limit;--count) fulls(0,all&~vertical,all,count);
    }
};

int main(int argc,char**argv){
    if(argc!=5) return 2;
    std::ifstream source(argv[1]); std::string text;
    std::ofstream out(argv[4]); int index=0;
    while(source>>text){
        Quotient base(text,0,100,0,10000);
        Forced cert(base,std::stoi(argv[2]),std::stoi(argv[3]),out);
        out<<index;cert.run();out<<'\n';
        std::cout<<index++<<' '<<cert.total<<' '<<cert.support_count<<'\n';
    }
    return !source.eof()||!out;
}
