// Tabu search over edge orbits for (3,k)-graphs.
// Input file: "n k M" then M lines "g p u1 v1 ... up vp" (g = group id, -1 = free bit;
// orbits with the same g >= 0 form an exactly-one group).
// Objective f = WT*triangles + #indep k-sets + W9 * #indep (k-1)-sets (W9 may be 0).
// usage: otabu orbits.txt seed iters tenure WT W9 outprefix [stagnation_limit perturb_frac [init.g6]]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef uint64_t u64;
static inline long long capll(double x){ return x>4e18?4000000000000000000LL:(long long)x+1; }
long long count_indep(const u64*,int,int,long long);
long long count_tri(const u64*,int);
int n,K,M; int *osz; int **ou,**ov; int *grp;
u64 adj[64]; char *x; double WT,W9;
static u64 rs; static inline u64 rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
void flip(int o){for(int i=0;i<osz[o];i++){int u=ou[o][i],v=ov[o][i];adj[u]^=1ULL<<v;adj[v]^=1ULL<<u;} x[o]^=1;}
double evalf(double cap){
    long long t=count_tri(adj,n); double f=WT*t; if(f>=cap) return f;
    long long c=count_indep(adj,n,K,capll(cap-f)); f+=c; if(f>=cap) return f;
    if(W9>0){ long long c9=count_indep(adj,n,K-1,capll((cap-f)/W9)); f+=W9*c9;}
    return f;
}
void write_g6(FILE*fp){
    int bits[64*63/2],nb=0; for(int j=1;j<n;j++)for(int i=0;i<j;i++)bits[nb++]=(adj[i]>>j)&1;
    while(nb%6)bits[nb++]=0; fputc(n+63,fp);
    for(int i=0;i<nb;i+=6){int c=0;for(int b=0;b<6;b++)c=2*c+bits[i+b];fputc(c+63,fp);} fputc('\n',fp);
}
int main(int argc,char**argv){
    if(argc<8){fprintf(stderr,"usage\n");return 1;}
    FILE*fp=fopen(argv[1],"r"); if(fscanf(fp,"%d %d %d",&n,&K,&M)!=3)return 1;
    osz=malloc(M*sizeof(int));ou=malloc(M*sizeof(int*));ov=malloc(M*sizeof(int*));grp=malloc(M*sizeof(int));x=calloc(M,1);
    for(int o=0;o<M;o++){if(fscanf(fp,"%d %d",&grp[o],&osz[o])!=2)return 1;ou[o]=malloc(osz[o]*sizeof(int));ov[o]=malloc(osz[o]*sizeof(int));
        for(int i=0;i<osz[o];i++)if(fscanf(fp,"%d %d",&ou[o][i],&ov[o][i])!=2)return 1;}
    fclose(fp);
    rs=strtoull(argv[2],0,10)*2654435761ULL+12345; long long iters=atoll(argv[3]); int ten=atoi(argv[4]);
    WT=atof(argv[5]);W9=atof(argv[6]); char*pre=argv[7];
    int G=0; for(int o=0;o<M;o++) if(grp[o]+1>G) G=grp[o]+1;
    int *gcur=malloc((G+1)*sizeof(int)); for(int g=0;g<G;g++)gcur[g]=-1;
    memset(adj,0,sizeof adj);
    // random init: free bits with prob 1/2? use sparse-ish init; groups: random choice
    u64 init[64]={0}; int haveinit=0;
    if(argc>10){ FILE*fi=fopen(argv[10],"r"); char line[4096]; if(fi&&fgets(line,sizeof line,fi)){ haveinit=1;
        int nn=line[0]-63; int bit=0; for(int j=1;j<nn;j++)for(int i=0;i<j;i++){ int c=line[1+bit/6]-63; if((c>>(5-bit%6))&1){init[i]|=1ULL<<j;init[j]|=1ULL<<i;} bit++; } } if(fi)fclose(fi); }
    for(int o=0;o<M;o++){ if(grp[o]<0){ if(haveinit){ int all=1; for(int i=0;i<osz[o];i++) if(!(init[ou[o][i]]>>ov[o][i]&1)) all=0; if(all) flip(o);} else if(rnd()%4==0) flip(o);} }
    for(int g=0;g<G;g++){ int cnt=0,ch=-1; for(int o=0;o<M;o++) if(grp[o]==g){cnt++; if(rnd()%cnt==0)ch=o;} gcur[g]=ch; flip(ch);}
    long long *tabu=calloc(M,sizeof(long long));
    double f=evalf(1e18),best=f; char*bx=malloc(M); memcpy(bx,x,M);
    char fn[512]; sprintf(fn,"%s.best",pre);
    long long stag=argc>8?atoll(argv[8]):1000000000LL; double pfrac=argc>9?atof(argv[9]):0.1; long long lastimp=0; double cbest=f;
    time_t t0=time(0);
    for(long long it=1;it<=iters;it++){
        double bf=1e18; int bo=-1,bo2=-1; int nties=0;
        for(int o=0;o<M;o++){
            int o2=-1;
            if(grp[o]>=0){ if(x[o]) continue; o2=gcur[grp[o]]; }
            if(tabu[o]>it){ /* aspiration only */ }
            flip(o); if(o2>=0) flip(o2);
            double fv=evalf( (tabu[o]>it)? best : (bf<best?bf+1e-9:1e18) );
            if(o2>=0) flip(o2); flip(o);
            int ok = (tabu[o]<=it) || fv<best;
            if(!ok) continue;
            if(fv<bf){bf=fv;bo=o;bo2=o2;nties=1;}
            else if(fv==bf){nties++; if(rnd()%nties==0){bo=o;bo2=o2;}}
        }
        if(bo<0) continue;
        flip(bo); if(bo2>=0){flip(bo2); gcur[grp[bo]]=bo; tabu[bo2]=it+ten+rnd()%(ten+1);}
        tabu[bo]=it+ten+rnd()%(ten+1); f=bf;
        if(f<cbest){cbest=f;lastimp=it;}
        if(it-lastimp>stag){ // perturb
            for(int o=0;o<M;o++){ if((double)(rnd()%100000)/100000.0>=pfrac) continue;
                if(grp[o]<0) flip(o); else if(!x[o]){int o2=gcur[grp[o]]; flip(o2); flip(o); gcur[grp[o]]=o;} }
            memset(tabu,0,M*sizeof(long long)); f=evalf(1e18); cbest=f; lastimp=it;
        }
        if(f<best){best=f;memcpy(bx,x,M);
            long long t=count_tri(adj,n),c=count_indep(adj,n,K,1LL<<60),c9=count_indep(adj,n,K-1,1LL<<60);
            printf("it %lld t %lds best f=%.3f tri=%lld c%d=%lld c%d=%lld\n",it,(long)(time(0)-t0),f,t,K,c,K-1,c9);fflush(stdout);
            FILE*o=fopen(fn,"w");write_g6(o);fclose(o);
            if(t==0&&c==0){ sprintf(fn,"%s.FOUND",pre); FILE*o2=fopen(fn,"a");write_g6(o2);fclose(o2); printf("FOUND\n"); return 0;}
        }
    }
    printf("done best=%.3f\n",best); return 0;
}
