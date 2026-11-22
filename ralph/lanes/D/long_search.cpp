#define LONG_SEARCH
#include "long_filter.cpp"
#include <ctime>
#include <fstream>
#include <map>
#include <set>
#include <unordered_set>
#include <unordered_map>

struct Profiles {
    std::array<std::unordered_set<Mask>,512> keys;
    std::array<std::unordered_map<Mask,std::vector<unsigned>>,512> indices;
    std::vector<std::vector<int>> patterns;
    bool enabled=false;
    bool cycle_only=false;
    static Mask weight(unsigned signature) {
        Mask value=signature+0x9e3779b97f4a7c15ULL;
        value=(value^(value>>30))*0xbf58476d1ce4e5b9ULL;
        value=(value^(value>>27))*0x94d049bb133111ebULL;
        return value^(value>>31);
    }
    void load(const std::string& file) {
        enabled=true;
        std::ifstream input(file); assert(input);
        std::string line;
        while(std::getline(input,line)) {
            std::stringstream fields(line);
            std::vector<std::pair<int,int>> table;
            std::string field;
            while(fields>>field) {
                const auto split=field.find(':');
                table.emplace_back(std::stoi(field.substr(0,split)),std::stoi(field.substr(split+1)));
            }
            for(int orient=0;orient<2;++orient) {
                std::vector<int> contents;
                for(auto [mask,size]:table) while(size--) contents.push_back(mask);
                patterns.push_back(contents);
                for(int keep=0;keep<512;++keep) if(count(keep)>=4) {
                    Mask hash=0;
                    for(auto [mask,size]:table) hash+=weight(mask&keep)*size;
                    keys[keep].insert(hash);
                    indices[keep][hash].push_back(patterns.size()-1);
                }
                for(auto& item:table) {
                    int reflected=item.first&3;
                    for(int pos=2;pos<9;++pos) if(item.first&(1<<pos)) reflected|=1<<(10-pos);
                    item.first=reflected;
                }
            }
        }
    }
    template<class Judge> bool traverse(const Graph& graph,int order,int degree,Judge judge) const {
        if(!enabled) return true;
        Mask fixed=0;
        for(int vertex=0;vertex<order;++vertex) if(count(graph[vertex])==degree) fixed|=bit(vertex);
        for(int root=0;root<order;++root) {
            Mask adjacent=graph[root];
            while(adjacent) {
                int other=take(adjacent);
                Mask block=(graph[root]|graph[other])&~(bit(root)|bit(other));
                std::array<int,9> core{root,other};
                auto matches=[&](Mask vertices) {
                    if(core[2]>core[8]) return true;
                    if(cycle_only && !(graph[core[2]]&graph[core[8]]&block&~vertices)) return true;
                    int keep=0;
                    for(int pos=0;pos<9;++pos) if(fixed&bit(core[pos])) keep|=1<<pos;
                    if(count(keep)<4) return true;
                    std::array<int,40> signatures{};
                    Mask positions=keep;
                    while(positions) {
                        const int pos=take(positions);
                        Mask neighbors=graph[core[pos]];
                        while(neighbors) signatures[take(neighbors)]|=1<<pos;
                    }
                    Mask hash=0;
                    Mask exterior=(bit(order)-1)^vertices;
                    while(exterior) hash+=weight(signatures[take(exterior)]);
                    return judge(core,vertices,keep,hash);
                };
                auto walk=[&](auto&& self,int pos,Mask used)->bool {
                    if(pos==9) return matches(used);
                    Mask choices=(pos==2?graph[root]:graph[core[pos-1]])&block&~used;
                    while(choices) {
                        core[pos]=take(choices);
                        if(!self(self,pos+1,used|bit(core[pos]))) return false;
                    }
                    return true;
                };
                if(!walk(walk,2,bit(root)|bit(other))) return false;
            }
        }
        return true;
    }
    bool fits(const Graph& graph,int order,int degree) const {
        return traverse(graph,order,degree,[&](const auto&,Mask,int keep,Mask hash){return keys[keep].count(hash)!=0;});
    }
    static bool support(const std::vector<int>& slots,const std::vector<int>& low,const std::vector<int>& high,
                        std::vector<int>& mandatory,std::vector<int>& possible) {
        const int size=int(slots.size());
        std::array<Mask,40> allowed{},reach{};
        std::array<int,40> mate{};
        mate.fill(-1);
        for(int point=0;point<size;++point) {
            for(int slot=0;slot<size;++slot) if(!(low[point]&~slots[slot]) && !(slots[slot]&~high[point])) allowed[point]|=bit(slot);
            if(!allowed[point]) return false;
        }
        for(int point=0;point<size;++point) {
            Mask seen=0;
            auto match=[&](auto&& self,int left)->bool {
                Mask options=allowed[left]&~seen;
                while(options&~seen) {
                    options&=~seen;
                    const int slot=take(options);
                    seen|=bit(slot);
                    if(mate[slot]==-1 || self(self,mate[slot])) {mate[slot]=left;return true;}
                }
                return false;
            };
            if(!match(match,point)) return false;
        }
        for(int point=0;point<size;++point) {
            Mask opts=allowed[point];
            while(opts) reach[point]|=bit(mate[take(opts)]);
        }
        for(int mid=0;mid<size;++mid) for(int point=0;point<size;++point) if(reach[point]&bit(mid)) reach[point]|=reach[mid];
        for(int point=0;point<size;++point) {
            Mask opts=allowed[point];
            while(opts) {
                const int slot=take(opts);
                if(reach[mate[slot]]&bit(point)) {mandatory[point]&=slots[slot];possible[point]|=slots[slot];}
            }
        }
        return true;
    }
    int refine(Graph& graph,Graph& upper,int order,int degree) const {
        bool changed=false;
        const Graph initial=graph;
        bool consistent=traverse(initial,order,degree,[&](const auto& core,Mask inside,int keep,Mask hash) {
            auto found=indices[keep].find(hash);
            if(found==indices[keep].end()) return false;
            if(keep==511) return true;
            Mask rest=(bit(order)-1)^inside;
            std::vector<int> lower,ceiling,points;
            while(rest) {
                const int vertex=take(rest);
                int low=0,high=0;
                for(int pos=0;pos<9;++pos) {
                    if(graph[core[pos]]&bit(vertex)) low|=1<<pos;
                    if(upper[core[pos]]&bit(vertex)) high|=1<<pos;
                }
                points.push_back(vertex); lower.push_back(low);ceiling.push_back(high);
            }
            std::vector<int> mandatory(points.size(),511),possible(points.size(),0);
            bool any=false;
            for(unsigned id:found->second) any|=support(patterns[id],lower,ceiling,mandatory,possible);
            if(!any) return false;
            for(std::size_t index=0;index<points.size();++index) {
                const int vertex=points[index];
                for(int pos=0;pos<9;++pos) {
                    const int anchor=core[pos];
                    if((mandatory[index]&~lower[index])&(1<<pos)) {link(graph,anchor,vertex);changed=true;}
                    if((ceiling[index]&~possible[index])&(1<<pos)) {upper[anchor]&=~bit(vertex);upper[vertex]&=~bit(anchor);changed=true;}
                }
            }
            return true;
        });
        return consistent?int(changed):-1;
    }
};

static const Profiles* edge_library=nullptr;
static bool edge_supported(const Graph& graph,int order,int degree) {return edge_library->fits(graph,order,degree);}
static int refine(Graph& graph,Graph& upper,int order,int degree) {return edge_library->refine(graph,upper,order,degree);}

class Search {
    int order,degree,path_cap;
    long budget;
    Mask all;
    const Profiles& library;
    int rule;
    bool enumerate;

    std::vector<Mask> options(const Graph& base,const Graph& forced,const Graph& upper,Mask fixed,int pivot,std::size_t limit) {
        std::map<Mask,Mask> grouped;
        Mask others=upper[pivot]&~forced[pivot];
        while(others) {
            int point=take(others);
            grouped[base[point]&fixed]|=bit(point);
        }
        std::vector<std::pair<Mask,Mask>> cells(grouped.begin(),grouped.end());
        std::sort(cells.begin(),cells.end(),[](const auto& left,const auto& right){return count(left.first)>count(right.first);});
        std::vector<Mask> tails(cells.size()+1);
        for(std::size_t index=cells.size();index>0;--index) tails[index-1]=tails[index]|cells[index-1].second;
        std::vector<Mask> rows;
        auto enumerate=[&](auto&& self,std::size_t index,Mask row,int need)->void {
            if(rows.size()>=limit||count(tails[index])<need) return;
            Mask marked=fixed;
            while(marked) {
                int point=take(marked);
                if(count(row&base[point])>3 || (!(base[pivot]&bit(point))&&!((row|tails[index])&base[point]))) return;
            }
            if(!need) {
                marked=fixed;
                while(marked) {
                    int point=take(marked);
                    if(!(base[pivot]&bit(point)) && !(row&base[point])) return;
                }
                rows.push_back(row);
                return;
            }
            Mask available=cells[index].second;
            int used=0;
            for(;;) {
                self(self,index+1,row,need-used);
                if(!available || used==need || rows.size()>=limit) break;
                row|=bit(take(available)); ++used;
            }
        };
        enumerate(enumerate,0,forced[pivot],degree-count(forced[pivot]));
        return rows;
    }

public:
    long nodes=0;
    std::array<long,10> deaths{};
    Graph result{};
    Search(int order_,int degree_,int cap,long budget_,const Profiles& profiles,int rule_,bool enumerate_=false):order(order_),degree(degree_),path_cap(cap),budget(budget_),all(bit(order)-1),library(profiles),rule(rule_),enumerate(enumerate_) {}
    int visit(const Graph& base,Mask fixed) {
        if(nodes>=budget) return -1;
        ++nodes;
        Graph forced=base, upper{};
        int before=0,after=0;
        const int rejected=prune(forced,order,degree,path_cap,before,after,&upper,rule&1,(rule&2)&&count(fixed)<=10?edge_supported:nullptr,(rule&4)?refine:nullptr,(rule&8)?1:((rule&16)?2:0));
        if(rejected) {++deaths[rejected];return 0;}
        if(!library.fits(forced,order,degree)) {++deaths[9];return 0;}
        if(fixed==all || upper==forced) {
            result=forced;
            if(enumerate) {
                std::cout<<"model";
                for(int vertex=0;vertex<order;++vertex) std::cout<<' '<<result[vertex];
                std::cout<<'\n';
                return 0;
            }
            return 1;
        }
        std::set<Mask> seen;
        Mask unfixed=all^fixed;
        int selected=-1;
        std::vector<Mask> best;
        std::vector<int> pivots;
        while(unfixed) {
            int vertex=take(unfixed);
            if(seen.insert(base[vertex]&fixed).second) pivots.push_back(vertex);
        }
        std::sort(pivots.begin(),pivots.end(),[&](int left,int right){return count(upper[left]^forced[left])<count(upper[right]^forced[right]);});
        for(int pivot:pivots) {
            auto rows=options(base,forced,upper,fixed,pivot,selected>=0?best.size():100000000);
            if(rows.empty()) {++deaths[7];return 0;}
            if(selected<0||rows.size()<best.size()) {best=std::move(rows);selected=pivot;}
            if(best.size()==1) break;
        }
        for(Mask row:best) {
            auto next=base;
            while(row) link(next,selected,take(row));
            int status=visit(next,fixed|bit(selected));
            if(status) return status;
        }
        ++deaths[8];
        return 0;
    }
};

int main(int argc,char** argv) {
    if(argc<5 || argc>8) return 2;
    const int order=std::stoi(argv[1]),degree=std::stoi(argv[2]),maximum=std::stoi(argv[3]);
    assert(order<=40&&order>=9);
    const long budget=std::stol(argv[4]);
    Profiles library;
    if(argc>=6 && std::string(argv[5])!="none") library.load(argv[5]);
    edge_library=&library;
    const int rule=argc>=7?std::stoi(argv[6]):0;
    library.cycle_only=(rule&32)!=0;
    const bool enumerate=argc==8;
    if(enumerate && std::string(argv[7])!="enumerate") return 2;
    std::string line;
    int index=0;
    while(std::getline(std::cin,line)) {
        std::clock_t start=std::clock();
        auto graph=parse(line,order,degree);
        Search search(order,degree,maximum,budget,library,rule,enumerate);
        int status=search.visit(graph,bit(anchors)-1);
        std::cout<<index++<<' '<<status<<' '<<search.nodes<<' '<<double(std::clock()-start)/CLOCKS_PER_SEC;
        for(auto value:search.deaths) std::cout<<' '<<value;
        if(status==1) for(int vertex=0;vertex<order;++vertex) std::cout<<' '<<search.result[vertex];
        std::cout<<std::endl;
    }
}
