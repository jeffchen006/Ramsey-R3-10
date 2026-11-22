#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using Mask = std::uint64_t;
using Graph = std::array<Mask,40>;
#if defined(OCTAGON_ROOT)
static constexpr int anchors=10;
#elif defined(CYCLE_ROOT)
static constexpr int anchors=8;
#else
static constexpr int anchors=9;
#endif
static inline int count(Mask mask) { return __builtin_popcountll(mask); }
static inline Mask bit(int index) { return Mask(1)<<index; }
static inline int take(Mask &mask) { const int result=__builtin_ctzll(mask); mask&=mask-1; return result; }
static inline void link(Graph& graph,int first,int second) { graph[first]|=bit(second); graph[second]|=bit(first); }

static int longest(const Graph& graph,int order) {
    int longest_path=0;
    for (int first=0;first<order;++first) {
        Mask neighbors=graph[first]&~(bit(first+1)-1);
        while (neighbors) {
            const int second=take(neighbors);
            Mask remaining=(graph[first]|graph[second])&~(bit(first)|bit(second));
            while(count(remaining)>longest_path) {
                Mask wave=remaining&-remaining,found=wave;
                while(wave) {
                    Mask adjacent=0;
                    while(wave) adjacent|=graph[take(wave)];
                    wave=adjacent&remaining&~found;
                    found|=wave;
                }
                longest_path=std::max(longest_path,count(found));
                remaining&=~found;
            }
        }
    }
    return longest_path;
}

static bool independent(const Graph& upper,Mask candidates,int need) {
    if (!need) return true;
    while (count(candidates)>=need) {
        const int vertex=take(candidates);
        if (independent(upper,candidates&~upper[vertex],need-1)) return true;
    }
    return false;
}

static int require_closed(Graph& graph,const Graph& upper,int order,int scope,bool hypothetical) {
    bool changed=false;
    const Graph before=graph;
    for(int first=0;first<order;++first) {
        Mask adjacent=before[first]&~(bit(first+1)-1);
        while(adjacent) {
            const int second=take(adjacent);
            if(scope==2 && !(first==0&&second==1)) continue;
            Mask remaining=(before[first]|before[second])&~(bit(first)|bit(second));
            while(count(remaining)>=8) {
                Mask found=remaining&-remaining,front=found;
                while(front) {
                    Mask fresh=0;
                    while(front) fresh|=before[take(front)];
                    front=fresh&remaining&~found;
                    found|=front;
                }
                remaining&=~found;
                if(count(found)<8) continue;
                if(count(found)>8) return -1;
                Mask trial=found,ends=0;
                while(trial) {
                    const int point=take(trial);
                    const int links=count(before[point]&found);
                    if(links>2) return -1;
                    if(links==1) ends|=bit(point);
                }
                if(!ends) continue;
                if(count(ends)!=2) return -1;
                const int left=take(ends),right=take(ends);
                if(!(upper[left]&bit(right))) return -1;
                if(!hypothetical && !(graph[left]&bit(right))) {link(graph,left,right);changed=true;}
            }
        }
    }
    return int(changed);
}

static int residual(Graph& graph,Graph& upper,int order,int degree) {
    constexpr int ramsey[]={0,1,3,6,9,14,18,23,28,36,41};
    const Mask all=bit(order)-1;
    Mask frozen=0;
    for(int point=0;point<order;++point) if(count(graph[point])==degree) frozen|=bit(point);
    bool changed=false;
    auto visit=[&](auto&& self,Mask eligible,Mask outer,int size)->bool {
        const int target=degree+1-size;
        if(size>=2) {
            const int number=count(outer);
            if(target<=1) return !number;
            if(number>=ramsey[target]) return false;
            const int lower=number-ramsey[target-1],high=target-1;
            Mask vertices=outer;
            while(vertices) {
                const int point=take(vertices);
                const Mask must=graph[point]&outer, can=upper[point]&outer;
                if(count(must)>high || count(can)<lower) return false;
                if(count(can)==lower || count(must)==high) {
                    Mask unknown=can&~must;
                    while(unknown) {
                        const int other=take(unknown);
                        if(count(can)==lower) link(graph,point,other);
                        else {upper[point]&=~bit(other);upper[other]&=~bit(point);}
                        changed=true;
                    }
                }
            }
        }
        if(size>=degree-2) return true;
        while(eligible) {
            const int point=take(eligible);
            if(!self(self,eligible&~graph[point],outer&~(bit(point)|graph[point]),size+1)) return false;
        }
        return true;
    };
    if(!visit(visit,frozen,all,0)) return -1;
    return int(changed);
}

using Filter = bool (*)(const Graph&,int,int);
using Extend = int (*)(Graph&,Graph&,int,int);
static int prune(Graph& graph,int order,int degree,int path_cap,int& before,int& after,Graph* envelope=nullptr,bool apply_residual=false,Filter edge_filter=nullptr,Extend extend=nullptr,int closed_scope=0) {
    const Mask all=bit(order)-1;
    Graph upper=graph;
    for(int first=anchors;first<order;++first) for(int second=first+1;second<order;++second)
        if (!(graph[first]&graph[second])) link(upper,first,second);
    for(;;) {
        Graph saturated{};
        for(int first=0;first<order;++first) {
            if(count(graph[first])>degree) return 1;
            for(int second=0;second<first;++second) {
                const int common=count(graph[first]&graph[second]);
                if(common>3 || (common && (graph[first]&bit(second)))) return 2;
                if(common==3) link(saturated,first,second);
            }
        }
        if(!before) before=longest(graph,order);
        if(path_cap && longest(graph,order)>path_cap) return 6;
        bool changed=false;
        if(closed_scope) {
            int state=require_closed(graph,upper,order,closed_scope,false);
            if(state<0) return 6;
            changed=state;
        }
        if(extend) {
            const int state=extend(graph,upper,order,degree);
            if(state<0) return 9;
            changed|=bool(state);
        }
        for(int first=anchors;first<order;++first) {
            Mask options=upper[first]&~graph[first];
            while(options) {
                const int second=take(options);
                if (second<=first) continue;
                if (count(graph[first])==degree || count(graph[second])==degree || (graph[first]&graph[second]) ||
                    (saturated[first]&graph[second]) || (saturated[second]&graph[first])) {
                    upper[first]&=~bit(second);
                    upper[second]&=~bit(first);
                } else if(path_cap) {
                    link(graph,first,second);
                    const bool impossible=longest(graph,order)>path_cap || (closed_scope && require_closed(graph,upper,order,closed_scope,true)<0) || (edge_filter && !edge_filter(graph,order,degree));
                    graph[first]^=bit(second);
                    graph[second]^=bit(first);
                    if(impossible) {
                        upper[first]&=~bit(second);
                        upper[second]&=~bit(first);
                    }
                }
            }
        }
        if(apply_residual) {
            int state=residual(graph,upper,order,degree);
            if(state<0) return 7;
            changed|=bool(state);
        }
        if(path_cap) {
            if(independent(upper,all,degree+1)) return 5;
            for(int first=anchors;first<order;++first) {
                Mask options=upper[first]&~graph[first]&~(bit(first+1)-1);
                while(options) {
                    const int second=take(options);
                    const Mask room=all&~(upper[first]|upper[second]|bit(first)|bit(second));
                    if(independent(upper,room,degree-1)) {link(graph,first,second);changed=true;}
                }
            }
        }
        for(int first=0;first<order;++first) {
            const int available=count(upper[first]);
            if(available<degree) return 3;
            if(available==degree) {
                Mask forced=upper[first]&~graph[first];
                while(forced) { link(graph,first,take(forced));changed=true; }
            }
            for(int second=0;second<first;++second) if(!(upper[first]&bit(second))) {
                Mask common=upper[first]&upper[second];
                if(!common) return 4;
                if(count(common)==1) {
                    int pivot=take(common);
                    if(!(graph[first]&bit(pivot))) {link(graph,first,pivot);changed=true;}
                    if(!(graph[second]&bit(pivot))) {link(graph,second,pivot);changed=true;}
                }
            }
        }
        if(!changed) break;
    }
    after=longest(graph,order);
    if(independent(upper,all,degree+1)) return 5;
    if(envelope) *envelope=upper;
    return 0;
}

static Graph parse(const std::string& line,int order,int degree) {
        Graph graph{};
#if defined(OCTAGON_ROOT)
        link(graph,0,1);
        for(int point=2;point<10;++point){link(graph,point%2,point);link(graph,point,2+(point-1)%8);}
#elif defined(CYCLE_ROOT)
        for(int first=0;first<4;++first) for(int second=4;second<8;++second)
            if(!first || second==4 || first!=second-4) link(graph,first,second);
#else
        link(graph,0,1);
        for(int vertex=2;vertex<9;++vertex) {
            link(graph,vertex%2,vertex);
            if(vertex<8) link(graph,vertex,vertex+1);
        }
#endif
        int next=anchors;
        std::stringstream fields(line);
        std::string field;
        while(fields>>field) {
            const auto split=field.find(':');
            const int mask=std::stoi(field.substr(0,split)),multiplicity=std::stoi(field.substr(split+1));
            for(int copy=0;copy<multiplicity;++copy) {
                assert(next<order);
                for(int anchor=0;anchor<anchors;++anchor) if(mask&bit(anchor)) link(graph,anchor,next);
                ++next;
            }
        }
        assert(next==order);
        for(int anchor=0;anchor<anchors;++anchor) assert(count(graph[anchor])==degree);
        return graph;
}

#ifndef LONG_SEARCH
int main(int argc,char** argv) {
    if(argc<3 || argc>5) return 2;
    const int order=std::stoi(argv[1]),degree=std::stoi(argv[2]);
    const int path_cap=argc>=4?std::stoi(argv[3]):0;
    const int closed_scope=argc==5?std::stoi(argv[4]):0;
    assert(order<=40&&order>=9);
    std::string line;
    unsigned int index=0;
    while(std::getline(std::cin,line)) {
        auto graph=parse(line,order,degree);
        int before=0,after=0;
        const int status=prune(graph,order,degree,path_cap,before,after,nullptr,false,nullptr,nullptr,closed_scope);
        std::cout<<index++<<' '<<status<<' '<<before<<' '<<after<<'\n';
    }
}
#endif
