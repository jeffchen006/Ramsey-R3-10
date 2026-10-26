// Fast evaluator for (3,k)-graphs on n <= 64 vertices. Bitset adjacency (uint64 per vertex).
#include <stdint.h>
typedef uint64_t u64;
static int K; static long long CAP; static long long cnt;
static const u64 *A;
static void rec(u64 cand, int depth){
    if(cnt>=CAP) return;
    if(depth==K){cnt++;return;}
    if(__builtin_popcountll(cand) < K-depth) return;
    while(cand){
        if(__builtin_popcountll(cand) < K-depth) return;
        int v=__builtin_ctzll(cand); cand&=cand-1;
        rec(cand & ~A[v], depth+1);
        if(cnt>=CAP) return;
    }
}
// number of independent k-sets (stops at cap)
long long count_indep(const u64 *adj,int n,int k,long long cap){
    A=adj;K=k;CAP=cap;cnt=0;
    u64 all = (n==64)?~0ULL:((1ULL<<n)-1);
    rec(all,0); return cnt;
}
long long count_tri(const u64 *adj,int n){
    long long t=0;
    for(int u=0;u<n;u++){u64 m=adj[u]&~((2ULL<<u)-1);
        while(m){int v=__builtin_ctzll(m);m&=m-1; t+=__builtin_popcountll(adj[u]&adj[v]&~((2ULL<<v)-1));}}
    return t;
}
// independence number
static int best;
static void arec(u64 cand,int sz){
    if(!cand){ if(sz>best)best=sz; return;}
    if(sz+__builtin_popcountll(cand)<=best) return;
    // branch on vertex of max degree within cand: take it or not
    int v=__builtin_ctzll(cand);
    arec(cand&~A[v]&~(1ULL<<v),sz+1);
    // vertex v excluded: only useful if some neighbour in cand is taken
    if(A[v]&cand) arec(cand&~(1ULL<<v),sz);
}
int alpha(const u64 *adj,int n){A=adj;best=0;u64 all=(n==64)?~0ULL:((1ULL<<n)-1);arec(all,0);return best;}
// per-vertex count of independent k-sets containing it (for local search guidance)
static long long *PV; static int stack_[64];
static void rec2(u64 cand,int depth){
    if(depth==K){cnt++; for(int i=0;i<K;i++)PV[stack_[i]]++; return;}
    while(cand){
        if(__builtin_popcountll(cand) < K-depth) return;
        int v=__builtin_ctzll(cand); cand&=cand-1;
        stack_[depth]=v; rec2(cand & ~A[v], depth+1);
    }
}
long long count_indep_pv(const u64 *adj,int n,int k,long long *pv){
    A=adj;K=k;cnt=0;PV=pv;for(int i=0;i<n;i++)pv[i]=0;
    u64 all=(n==64)?~0ULL:((1ULL<<n)-1); rec2(all,0); return cnt;
}
// greedy maximal triangle-free fill: pairs (pu[i],pv[i]) in given order; out adj. Optional start adj.
void greedy_fill(int n,int np,const int*pu,const int*pv,u64*adj){
    for(int i=0;i<np;i++){int u=pu[i],v=pv[i]; if(u==v||(adj[u]>>v&1))continue; if(!(adj[u]&adj[v])){adj[u]|=1ULL<<v;adj[v]|=1ULL<<u;}}
}
