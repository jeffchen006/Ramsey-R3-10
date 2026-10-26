// Exhaustive branch and bound over unions of edge classes (any partition of pairs, from an otabu class file).
// Finds the minimum #independent k-sets over triangle-free unions (only unions maximal w.r.t. classes matter).
// Bound: final graph is a subgraph of current + all classes still compatible, so c_k(final) >= c_k(that graph).
// usage: orbexc classfile [node_limit]   prints best, node count, and EXHAUSTIVE or LIMIT.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint64_t u64;
long long count_indep(const u64*,int,int,long long);
long long count_tri(const u64*,int);
int n,K,M,*osz,**ou,**ov; u64 (*mask)[64];
long long nodes=0,limit; long long best; u64 bestadj[64]; int okc[4096];
int compat(const u64*adj,int i){ // adding class i keeps triangle-free?
    for(int t=0;t<osz[i];t++){int a=ou[i][t],b=ov[i][t]; if(((adj[a]|mask[i][a])&(adj[b]|mask[i][b]))) return 0;}
    return 1;
}
void rec(int i,u64*adj){
    if(++nodes>limit) return;
    // upper graph: current + all compatible classes j>=i
    u64 up[64]; memcpy(up,adj,sizeof(u64)*n); int any=0;
    for(int j=i;j<M;j++) if(okc[j] && compat(adj,j)){ any=1; for(int v=0;v<n;v++) up[v]|=mask[j][v]; }
    long long lb=count_indep(up,n,K,best);
    if(lb>=best) return;
    if(!any){ // leaf: check maximality w.r.t. classes < i
        for(int j=0;j<i;j++) if(okc[j] && !(adj[0]&0) && compat(adj,j)){ int in=1; for(int t=0;t<osz[j];t++) if(!(adj[ou[j][t]]>>ov[j][t]&1)){in=0;break;} if(!in) return; }
        long long c=count_indep(adj,n,K,best);
        if(c<best){best=c;memcpy(bestadj,adj,sizeof(u64)*n); fprintf(stderr,"best %lld nodes %lld\n",best,nodes); if(best==0) limit=0;}
        return;
    }
    // find next compatible class
    int j=i; while(j<M && !(okc[j]&&compat(adj,j))) j++;
    if(j>=M) return;
    u64 nw[64]; for(int v=0;v<n;v++) nw[v]=adj[v]|mask[j][v];
    rec(j+1,nw);
    rec(j+1,adj); // exclude j
}
int main(int argc,char**argv){
    FILE*fp=fopen(argv[1],"r"); if(fscanf(fp,"%d %d %d",&n,&K,&M)!=3)return 1;
    osz=malloc(M*sizeof(int));ou=malloc(M*sizeof(int*));ov=malloc(M*sizeof(int*)); mask=calloc(M,sizeof(*mask));
    for(int o=0;o<M;o++){int g; if(fscanf(fp,"%d %d",&g,&osz[o])!=2)return 1; ou[o]=malloc(osz[o]*sizeof(int));ov[o]=malloc(osz[o]*sizeof(int));
        for(int t=0;t<osz[o];t++){ if(fscanf(fp,"%d %d",&ou[o][t],&ov[o][t])!=2)return 1; mask[o][ou[o][t]]|=1ULL<<ov[o][t]; mask[o][ov[o][t]]|=1ULL<<ou[o][t]; }}
    fclose(fp); limit=argc>2?atoll(argv[2]):1LL<<60;
    u64 z[64]={0}; for(int o=0;o<M;o++) okc[o]=compat(z,o);
    best=argc>3?atoll(argv[3]):(1LL<<60); long long best0=best; rec(0,z);
    printf("%s classes=%d best_c%d=%lld%s nodes=%lld %s\n",argv[1],M,K,best,best==best0?" (none below start bound)":"",nodes,(nodes>limit && best>0)?"LIMIT":"EXHAUSTIVE");
    if(best<best0){ // print graph6
        int bits[64*63/2],nb=0; for(int j=1;j<n;j++)for(int i=0;i<j;i++)bits[nb++]=(bestadj[i]>>j)&1;
        while(nb%6)bits[nb++]=0; printf("G6 %c",n+63); for(int i=0;i<nb;i+=6){int c=0;for(int b=0;b<6;b++)c=2*c+bits[i+b];putchar(c+63);} printf("\n");}
    return 0;
}
