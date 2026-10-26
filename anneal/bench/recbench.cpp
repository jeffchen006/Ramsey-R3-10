// time pairDelta-style counting on a fixed graph (all pairs), variants of rec
#include <bits/stdc++.h>
using namespace std; typedef uint64_t u64; typedef int64_t i64;
static int N, K; static u64 adj[64], ALLV;
static inline int pc(u64 x){return __builtin_popcountll(x);} static inline int ctz(u64 x){return __builtin_ctzll(x);}
static long calls=0;
static void rec(u64 P, int m, i64 &a, i64 &b) {
    calls++;
    int p = pc(P);
    if (m == 1) { a += p; b += 1; return; }
    if (m == 2) { int e = 0; u64 Q = P; while (Q) { int v = ctz(Q); Q &= Q - 1; e += pc(adj[v] & Q); } a += (i64)p*(p-1)/2 - e; b += p; return; }
    if (p < m - 1) return;
    u64 Q = P;
    while (pc(Q) >= m - 1) { int v = ctz(Q); Q &= Q - 1; rec(Q & ~adj[v], m - 1, a, b); }
}
// variant: only count a (size m), with m==3 base fused
static i64 rec3(u64 P, int m) {
    if (m == 2) { int p = pc(P), e = 0; u64 Q = P; while (Q) { int v = ctz(Q); Q &= Q - 1; e += pc(adj[v] & Q); } return (i64)p*(p-1)/2 - e; }
    if (m == 1) return pc(P);
    i64 a = 0; u64 Q = P;
    while (pc(Q) >= m) { int v = ctz(Q); Q &= Q - 1; a += rec3(Q & ~adj[v], m - 1); }
    return a;
}
// triangle-free closed forms: I2, I3 (and I4)
static inline i64 I3tf(u64 X) {
    i64 p = pc(X), e2 = 0, s2 = 0; u64 Q = X;
    while (Q) { int w = ctz(Q); Q &= Q - 1; i64 d = pc(adj[w] & X); e2 += d; s2 += d * (d - 1) / 2; }
    return p * (p - 1) * (p - 2) / 6 - (e2 / 2) * (p - 2) + s2;
}
static i64 recF(u64 P, int m) {
    if (m == 3) return I3tf(P);
    if (m == 2) { int p = pc(P), e = 0; u64 Q = P; while (Q) { int v = ctz(Q); Q &= Q - 1; e += pc(adj[v] & Q); } return (i64)p*(p-1)/2 - e; }
    if (m == 1) return pc(P);
    i64 a = 0; u64 Q = P;
    while (pc(Q) >= m) { int v = ctz(Q); Q &= Q - 1; a += recF(Q & ~adj[v], m - 1); }
    return a;
}
static inline i64 I4tf(u64 X) {
    // I4 = C(p,4) - e C(p-2,2) + (p-3) S2 + M2 - S3 - P4 + C4  (triangle-free)
    int vs[64], n = 0; int d[64]; u64 Q = X;
    while (Q) { int w = ctz(Q); Q &= Q - 1; vs[n] = w; d[n] = pc(adj[w] & X); n++; }
    i64 p = n, e = 0, S2 = 0, S3 = 0, P4 = 0, C4 = 0;
    int dd[64]; for (int i = 0; i < n; i++) dd[vs[i]] = d[i];
    for (int i = 0; i < n; i++) { i64 x = d[i]; e += x; S2 += x*(x-1)/2; S3 += x*(x-1)*(x-2)/6; }
    e /= 2;
    for (int i = 0; i < n; i++) {
        u64 R = adj[vs[i]] & X & ~((2ULL << vs[i]) - 1);
        while (R) { int w = ctz(R); R &= R - 1; P4 += (i64)(d[i] - 1) * (dd[w] - 1); }
        for (int j = i + 1; j < n; j++) { i64 c = pc(adj[vs[i]] & adj[vs[j]] & X); C4 += c * (c - 1) / 2; }
    }
    C4 /= 2;
    i64 M2 = e * (e - 1) / 2 - S2;
    return p*(p-1)*(p-2)*(p-3)/24 - e * ((p-2)*(p-3)/2) + (p-3) * S2 + M2 - S3 - P4 + C4;
}
static i64 recG(u64 P, int m) {
    if (m == 4) return I4tf(P);
    if (m == 3) return I3tf(P);
    i64 a = 0; u64 Q = P;
    while (pc(Q) >= m) { int v = ctz(Q); Q &= Q - 1; a += recG(Q & ~adj[v], m - 1); }
    return a;
}
int main(int argc, char **argv) {
    string g = argv[1]; K = atoi(argv[2]);
    N = g[0]-63; ALLV = (1ULL<<N)-1; int pos=1,bit=5;
    for (int j=1;j<N;j++) for (int i=0;i<j;i++){ int x=g[pos]-63; if (x>>bit&1){adj[i]|=1ULL<<j;adj[j]|=1ULL<<i;} if(--bit<0){bit=5;pos++;} }
    auto t=chrono::steady_clock::now(); i64 tot=0, tot2=0; int np=0; double csz=0;
    for (int rep=0;rep<20;rep++) for (int u=0;u<N;u++) for (int v=u+1;v<N;v++){ u64 C=ALLV&~(adj[u]|adj[v]|1ULL<<u|1ULL<<v); i64 a=0,b=0; rec(C,K-2,a,b); tot+=a; np++; csz+=pc(C);}
    double dt=chrono::duration<double>(chrono::steady_clock::now()-t).count();
    printf("rec: %.2f us/pair, calls/pair=%.0f avg|C|=%.1f sum=%lld\n", dt/np*1e6, (double)calls/np, csz/np, (long long)tot);
    t=chrono::steady_clock::now();
    for (int rep=0;rep<20;rep++) for (int u=0;u<N;u++) for (int v=u+1;v<N;v++){ u64 C=ALLV&~(adj[u]|adj[v]|1ULL<<u|1ULL<<v); tot2+=rec3(C,K-2);}
    dt=chrono::duration<double>(chrono::steady_clock::now()-t).count();
    printf("rec3: %.2f us/pair sum=%lld\n", dt/np*1e6, (long long)tot2);
    for (int var = 0; var < 2; var++) {
    t=chrono::steady_clock::now(); i64 tot3=0;
    for (int rep=0;rep<20;rep++) for (int u=0;u<N;u++) for (int v=u+1;v<N;v++){ u64 C=ALLV&~(adj[u]|adj[v]|1ULL<<u|1ULL<<v); tot3+= var ? recG(C,K-2) : recF(C,K-2);}
    dt=chrono::duration<double>(chrono::steady_clock::now()-t).count();
    printf("%s: %.2f us/pair sum=%lld\n", var ? "recG(I4)" : "recF(I3)", dt/np*1e6, (long long)tot3); }
}
