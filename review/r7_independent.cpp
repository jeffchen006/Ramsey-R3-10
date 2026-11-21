// Independent R(7) check (Claude review). Written from the math, no trace input.
// Shape: G d-regular, triangle-free, alpha<=d; u,w nonadjacent, |C|=d-2, A={a1,a2}, B={b1,b2}, A-B complete.
// X = G - N[u] - N[w]. Unknowns: X-neighbourhoods of a1,a2 (M1,M2), b1,b2 (N1,N2), c1..c_{d-2}.
// Modes:
//   mine r7 FILE.g6 IDX         -> X = line IDX (d=9, cap=7); enumerate everything, report counts.
//   mine control G.g6           -> G a known graph; find every anchor (u,w) of this shape, check the
//                                  search finds G's own completion (calibration that can fail).
#include <bits/stdc++.h>
using namespace std;
using M = uint32_t;
constexpr int W = 16;  // 1024 colours max
struct BS { uint64_t w[W]{};
  void set(int i){w[i>>6]|=1ull<<(i&63);} bool get(int i)const{return w[i>>6]>>(i&63)&1;}
  void andnot(const BS&o){for(int k=0;k<W;k++)w[k]&=~o.w[k];}
  int cnt_and(const BS&o)const{int c=0;for(int k=0;k<W;k++)c+=__builtin_popcountll(w[k]&o.w[k]);return c;}
  bool any_and(const BS&o)const{for(int k=0;k<W;k++)if(w[k]&o.w[k])return true;return false;} };

vector<uint64_t> g6(const string&s){ int n=s[0]-63; vector<uint64_t> a(n); int bit=0; size_t p=1;
  for(int j=1;j<n;j++)for(int i=0;i<j;i++){ int byte=s[p+bit/6]-63; if(byte>>(5-bit%6)&1){a[i]|=1ull<<j;a[j]|=1ull<<i;} bit++; } return a; }

int maxind(const vector<uint64_t>&a, uint64_t cand){ // exact max independent set size, simple B&B
  if(!cand) return 0; int v=__builtin_ctzll(cand);
  // branch: v in or out
  int with=1+maxind(a, cand & ~(1ull<<v) & ~a[v]);
  int without=maxind(a, cand & ~(1ull<<v));
  return max(with,without);
}
int maxind_fast(const vector<uint64_t>&a, uint64_t cand, int need){ // returns >=need early
  if(__builtin_popcountll(cand)<need) return 0; if(need<=0) return 1;
  // pick vertex of max degree in cand
  int best=-1,bd=-1; for(uint64_t r=cand;r;r&=r-1){int v=__builtin_ctzll(r);int d=__builtin_popcountll(a[v]&cand); if(d>bd){bd=d;best=v;}}
  if(bd==0) return __builtin_popcountll(cand)>=need;
  if(maxind_fast(a, cand&~(1ull<<best)&~a[best], need-1)) return 1;
  return maxind_fast(a, cand&~(1ull<<best), need);
}

struct Solver {
  int d, cap, m; vector<M> adj; M full;
  vector<M> cols;               // independent (d-2)-sets: C colours and also alpha rows
  vector<BS> has;               // has[x]: colours containing x
  vector<BS> bad;               // bad[i]: colours overlapping i in > cap-2 (incl. i)
  vector<BS> disj;              // disj[i]: colours disjoint from colour/row i
  vector<vector<int>> rows_of;  // rows disjoint from colour i
  long long nodes=0, complete=0, real=0; vector<vector<M>> found;
  void enumk(int k, int from, M sel, M ban, vector<M>&out){ if(!k){out.push_back(sel);return;}
    for(int v=from; v<m; v++) if(!(ban>>v&1)) enumk(k-1,v+1,sel|1u<<v,ban|adj[v]|1u<<v,out); }
  void init(){ full=(m==32)?~0u:((1u<<m)-1); enumk(d-2,0,0,0,cols); if(cols.size()>64*W) throw runtime_error("too many colours");
    int n=cols.size(); has.assign(m,{}); bad.assign(n,{}); disj.assign(n,{}); rows_of.assign(n,{});
    for(int i=0;i<n;i++){ for(int x=0;x<m;x++) if(cols[i]>>x&1) has[x].set(i);
      for(int j=0;j<n;j++){ int o=__builtin_popcount(cols[i]&cols[j]); if(o>cap-2) bad[i].set(j); if(!o){disj[i].set(j); rows_of[i].push_back(j);} } } }
  // root
  M S[4]; int dem[32]; vector<int> bud; vector<pair<int,int>> req;  // required pairs
  vector<int> chosen;
  void dfs(BS perm, uint64_t reqmask){
    nodes++;
    if((int)chosen.size()==d-2){ // demands all must be zero by sum argument; verify
      for(int x=0;x<m;x++) if(dem[x]) throw runtime_error("demand left at completion");
      if(reqmask) return; complete++; if(full_check()) real++; return; }
    // MRV pivot
    int bestc=INT_MAX, bv=-1, bp=-1;
    for(int x=0;x<m;x++) if(dem[x]>0){ int c=perm.cnt_and(has[x]); if(c<dem[x]) return; if(c<bestc){bestc=c;bv=x;bp=-1;} }
    for(uint64_t r=reqmask;r;r&=r-1){ int p=__builtin_ctzll(r); auto[x,y]=req[p]; BS t=has[x]; for(int k=0;k<W;k++)t.w[k]&=has[y].w[k];
      int c=perm.cnt_and(t); if(!c) return; if(c<bestc){bestc=c;bp=p;bv=-1;} }
    BS opt; if(bp<0) opt=has[bv]; else { auto[x,y]=req[bp]; for(int k=0;k<W;k++)opt.w[k]=has[x].w[k]&has[y].w[k]; }
    for(int k=0;k<W;k++) opt.w[k]&=perm.w[k];
    for(int k=0;k<W;k++) while(opt.w[k]){ int i=k*64+__builtin_ctzll(opt.w[k]); opt.w[k]&=opt.w[k]-1;
      perm.w[i>>6]&=~(1ull<<(i&63));           // later siblings: first-present argument
      BS ch=perm; ch.andnot(bad[i]); bool okay=true;
      for(int x=0;x<m;x++) if(cols[i]>>x&1){ if(--dem[x]<0) okay=false; if(dem[x]==0) ch.andnot(has[x]); }
      for(int r: rows_of[i]){ if(--bud[r]<0) okay=false; if(bud[r]==0) ch.andnot(disj[r]); }
      uint64_t nr=reqmask; for(uint64_t r=reqmask;r;r&=r-1){int p=__builtin_ctzll(r); auto[x,y]=req[p]; if((cols[i]>>x&1)&&(cols[i]>>y&1)) nr&=~(1ull<<p);}
      chosen.push_back(i);
      if(okay) dfs(ch,nr);
      chosen.pop_back();
      for(int x=0;x<m;x++) if(cols[i]>>x&1) ++dem[x];
      for(int r: rows_of[i]) ++bud[r];
    }
  }
  bool full_check(){ // build the whole graph: X(0..m-1), u, w, a1,a2,b1,b2, c1..c_{d-2}
    int n=m+4+d; if(n>64) throw runtime_error("n>64"); vector<uint64_t> a(n);
    auto E=[&](int i,int j){a[i]|=1ull<<j;a[j]|=1ull<<i;};
    for(int x=0;x<m;x++) for(int y=x+1;y<m;y++) if(adj[x]>>y&1) E(x,y);
    int u=m,w=m+1,a1=m+2,a2=m+3,b1=m+4,b2=m+5,c0=m+6;
    int ab[4]={a1,a2,b1,b2}; E(u,a1);E(u,a2);E(w,b1);E(w,b2); E(a1,b1);E(a1,b2);E(a2,b1);E(a2,b2);
    for(int j=0;j<4;j++) for(int x=0;x<m;x++) if(S[j]>>x&1) E(ab[j],x);
    for(int t=0;t<d-2;t++){ E(u,c0+t);E(w,c0+t); for(int x=0;x<m;x++) if(cols[chosen[t]]>>x&1) E(c0+t,x); }
    for(int i=0;i<n;i++){ if(__builtin_popcountll(a[i])!=d) return false; for(uint64_t r=a[i];r;r&=r-1) if(a[i]&a[__builtin_ctzll(r)]) return false; }
    uint64_t all=(n==64)?~0ull:((1ull<<n)-1);
    if(maxind_fast(a,all,d+1)) return false;
    vector<M> rec(S,S+4); for(int t:chosen) rec.push_back(cols[t]); found.push_back(rec); return true; }
  bool run_root(const M s[4]){ // returns false if root has an infeasible start (counted separately)
    for(int j=0;j<4;j++) S[j]=s[j]; int tot=0;
    for(int x=0;x<m;x++){ dem[x]=d-__builtin_popcount(adj[x]); for(int j=0;j<4;j++) dem[x]-=S[j]>>x&1; if(dem[x]<1) return false; tot+=dem[x]; }
    if(tot!=(d-2)*(d-2)) throw runtime_error("total demand");
    int n=cols.size(); bud.assign(n,0); BS perm; for(int i=0;i<n;i++) perm.set(i);
    for(int r=0;r<n;r++){ int mA=!(S[0]&cols[r])+!(S[1]&cols[r]), mB=!(S[2]&cols[r])+!(S[3]&cols[r]);
      bud[r]=2-max(mA,mB); if(bud[r]<0) return false; if(bud[r]==0) perm.andnot(disj[r]); }
    req.clear(); uint64_t rm=0;
    for(int x=0;x<m;x++) for(int y=x+1;y<m;y++){ if(adj[x]>>y&1) continue; if(adj[x]&adj[y]) continue;
      bool inside=false; for(int j=0;j<4;j++) if((S[j]>>x&1)&&(S[j]>>y&1)) inside=true;
      if(inside) continue; if(req.size()>=64) throw runtime_error("req>64"); rm|=1ull<<req.size(); req.push_back({x,y}); }
    chosen.clear(); dfs(perm,rm); return true; }
};

struct Pack { M m1,m2,U,D; };
// Side packages: unordered {M1,M2} of independent (d-3)-sets with the necessary conditions.
vector<Pack> packages(Solver&s){
  vector<M> masks; s.enumk(s.d-3,0,0,0,masks); vector<Pack> out;
  for(size_t i=0;i<masks.size();i++) for(size_t j=i+1;j<masks.size();j++){
    M a=masks[i],b=masks[j],U=a|b,sh=a&b; if(__builtin_popcount(sh)>s.cap-3) continue;
    bool ok=true; for(int x=0;x<s.m&&ok;x++){ int use=(a>>x&1)+(b>>x&1); if(use>s.d-__builtin_popcount(s.adj[x])-1) ok=false; }
    if(!ok) continue;
    M D=0; for(M mk: {a,b}){ M dom=mk; for(int x=0;x<s.m;x++) if(mk>>x&1) dom|=s.adj[x]; D|=s.full&~dom; }
    if(U&D) continue;
    for(M I: s.cols) if(!(I&U)){ok=false;break;} if(!ok) continue;
    out.push_back({a,b,U,D}); }
  return out; }

int main(int argc,char**argv){
  string mode=argv[1];
  if(mode=="r7"){
    ifstream f(argv[2]); vector<string> L; for(string l;getline(f,l);) if(!l.empty()) L.push_back(l);
    int idx=atoi(argv[3]); auto a=g6(L[idx]); Solver s; s.d=9; s.cap=7; s.m=a.size(); for(auto r:a) s.adj.push_back((M)r); s.init();
    auto P=packages(s); printf("seed %d: m=%d colours=%zu packages=%zu\n",idx,s.m,s.cols.size(),P.size()); fflush(stdout);
    // compatible unordered pairs: bucket packages by union, compare all pairs i<j
    long long pairs=0, roots_bad=0; auto t0=clock();
    for(size_t i=0;i<P.size();i++) for(size_t j=i+1;j<P.size();j++){
      const Pack&p=P[i],&q=P[j]; if(p.U&q.U) continue; if(p.D&~q.U) continue; if(q.D&~p.U) continue;
      pairs++; M r[4]={p.m1,p.m2,q.m1,q.m2}; if(!s.run_root(r)) roots_bad++; }
    printf("seed %d: compatible_pairs=%lld bad_start=%lld nodes=%lld complete_lists=%lld REAL_GRAPHS=%lld cpu=%.1fs\n",
      idx,pairs,roots_bad,s.nodes,s.complete,s.real,double(clock()-t0)/CLOCKS_PER_SEC);
    return 0; }
  if(mode=="control"){ // G known; try every ordered nonadjacent pair (u,w) with |C|=d-2 and A-B complete
    ifstream f(argv[2]); string l; getline(f,l); auto G=g6(l); int n=G.size(), d=__builtin_popcountll(G[0]);
    int cstar=0; for(int u=0;u<n;u++) for(int w=u+1;w<n;w++) if(!(G[u]>>w&1)) cstar=max(cstar,__builtin_popcountll(G[u]&G[w]));
    printf("control: n=%d d=%d cstar=%d\n",n,d,cstar); int anchors=0, hits=0;
    for(int u=0;u<n;u++) for(int w=u+1;w<n;w++){ if(G[u]>>w&1) continue; uint64_t C=G[u]&G[w]; if(__builtin_popcountll(C)!=d-2) continue;
      uint64_t A=G[u]&~C, B=G[w]&~C; bool comp=true; for(uint64_t r=A;r;r&=r-1) if((G[__builtin_ctzll(r)]&B)!=B) comp=false; if(!comp) continue;
      anchors++;
      uint64_t Xs=((n==64)?~0ull:((1ull<<n)-1)) & ~G[u] & ~G[w] & ~(1ull<<u) & ~(1ull<<w); vector<int> xs; for(uint64_t r=Xs;r;r&=r-1) xs.push_back(__builtin_ctzll(r));
      Solver s; s.d=d; s.cap=cstar; s.m=xs.size(); auto proj=[&](uint64_t nb){M r=0; for(int i=0;i<s.m;i++) if(nb>>xs[i]&1) r|=1u<<i; return r;};
      for(int i=0;i<s.m;i++) s.adj.push_back(proj(G[xs[i]])); s.init();
      vector<int> av,bv,cv; for(uint64_t r=A;r;r&=r-1) av.push_back(__builtin_ctzll(r)); for(uint64_t r=B;r;r&=r-1) bv.push_back(__builtin_ctzll(r));
      for(uint64_t r=C;r;r&=r-1) cv.push_back(__builtin_ctzll(r));
      M Mt[4]={proj(G[av[0]]),proj(G[av[1]]),proj(G[bv[0]]),proj(G[bv[1]])}; set<M> truec; for(int c:cv) truec.insert(proj(G[c]));
      auto P=packages(s); bool pa=false,pb=false; for(auto&p:P){ if(set<M>{p.m1,p.m2}==set<M>{Mt[0],Mt[1]}) pa=true; if(set<M>{p.m1,p.m2}==set<M>{Mt[2],Mt[3]}) pb=true; }
      M r[4]={min(Mt[0],Mt[1]),max(Mt[0],Mt[1]),min(Mt[2],Mt[3]),max(Mt[2],Mt[3])}; s.run_root(r);
      bool hit=false; for(auto&rec:s.found){ set<M> cs(rec.begin()+4,rec.end()); if(cs==truec) hit=true; }
      if(pa&&pb&&hit) hits++;
      printf("anchor u=%d w=%d: X=%d colours=%zu packages=%zu trueA=%d trueB=%d real_completions=%lld own_completion_found=%d\n",
        u,w,s.m,s.cols.size(),P.size(),pa,pb,s.real,hit); }
    printf("control: anchors=%d all_found=%d\n",anchors,hits); return anchors&&hits==anchors?0:3; }
}
