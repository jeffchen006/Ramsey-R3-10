// Tabu search for an induced m-vertex subgraph of a host graph (N <= 256) minimizing
// WT*triangles + #indep k-sets + W9*#indep (k-1)-sets. Move = swap one chosen vertex with one unchosen.
// usage: subtabu host.txt m k seed iters tenure W9 outprefix [stag]
// host.txt: "N" then N lines of 0/1 strings (adjacency matrix).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef uint64_t u64;
static inline long long capll(double x){ return x>4e18?4000000000000000000LL:(long long)x+1; }
long long count_indep(const u64*,int,int,long long);
long long count_tri(const u64*,int);
int N,m,K; char H[256][256]; int sel[64], uns[256], nu; double W9;
static u64 rs; static inline u64 rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
u64 adj[64];
void build(){ for(int i=0;i<m;i++){u64 a=0; for(int j=0;j<m;j++) if(H[sel[i]][sel[j]]) a|=1ULL<<j; adj[i]=a;} }
double evalf(double cap){ build(); long long t=count_tri(adj,m); double f=50.0*t; if(f>=cap)return f;
    long long c=count_indep(adj,m,K,capll(cap-f)); f+=c; if(f>=cap||W9==0)return f;
    long long c9=count_indep(adj,m,K-1,capll((cap-f)/W9)); return f+W9*c9; }
void write_g6(FILE*fp){ build(); int bits[64*63/2],nb=0; for(int j=1;j<m;j++)for(int i=0;i<j;i++)bits[nb++]=(adj[i]>>j)&1;
    while(nb%6)bits[nb++]=0; fputc(m+63,fp); for(int i=0;i<nb;i+=6){int c=0;for(int b=0;b<6;b++)c=2*c+bits[i+b];fputc(c+63,fp);} fputc('\n',fp);}
int main(int argc,char**argv){
    FILE*fp=fopen(argv[1],"r"); if(fscanf(fp,"%d",&N)!=1)return 1; char buf[300];
    for(int i=0;i<N;i++){ if(fscanf(fp,"%s",buf)!=1)return 1; for(int j=0;j<N;j++)H[i][j]=buf[j]=='1';} fclose(fp);
    m=atoi(argv[2]);K=atoi(argv[3]);rs=strtoull(argv[4],0,10)*2654435761ULL+99; long long iters=atoll(argv[5]); int ten=atoi(argv[6]); W9=atof(argv[7]); char*pre=argv[8];
    long long stag=argc>9?atoll(argv[9]):1000000000LL;
    int perm[256]; for(int i=0;i<N;i++)perm[i]=i; for(int i=N-1;i>0;i--){int j=rnd()%(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
    for(int i=0;i<m;i++)sel[i]=perm[i]; nu=N-m; for(int i=0;i<nu;i++)uns[i]=perm[m+i];
    long long *tabu=calloc(N,sizeof(long long)); double f=evalf(1e18),best=f,cbest=f; long long lastimp=0;
    char fn[512]; time_t t0=time(0);
    for(long long it=1;it<=iters;it++){
        double bf=1e18; int bi=-1,bj=-1,nt=0;
        for(int i=0;i<m;i++) for(int j=0;j<nu;j++){
            int a=sel[i],b=uns[j]; int tb=(tabu[b]>it);
            sel[i]=b; double fv=evalf(tb?best:(bf+1e-9)); sel[i]=a;
            if(tb && !(fv<best)) continue;
            if(fv<bf){bf=fv;bi=i;bj=j;nt=1;} else if(fv==bf){nt++; if(rnd()%nt==0){bi=i;bj=j;}}
        }
        if(bi<0)continue;
        int a=sel[bi]; sel[bi]=uns[bj]; uns[bj]=a; tabu[a]=it+ten+rnd()%(ten+1); f=bf;
        if(f<cbest){cbest=f;lastimp=it;}
        if(f<best){best=f; build(); long long t=count_tri(adj,m),c=count_indep(adj,m,K,1LL<<60),c9=count_indep(adj,m,K-1,1LL<<60);
            printf("it %lld t %lds best f=%.3f tri=%lld c%d=%lld c%d=%lld\n",it,(long)(time(0)-t0),f,t,K,c,K-1,c9);fflush(stdout);
            sprintf(fn,"%s.best",pre); FILE*o=fopen(fn,"w");write_g6(o);fclose(o);
            if(t==0&&c==0){sprintf(fn,"%s.FOUND",pre);o=fopen(fn,"a");write_g6(o);fclose(o);printf("FOUND\n");return 0;}}
        if(it-lastimp>stag){ for(int r=0;r<m/5;r++){int i=rnd()%m,j=rnd()%nu;int t=sel[i];sel[i]=uns[j];uns[j]=t;}
            memset(tabu,0,N*sizeof(long long)); f=evalf(1e18); cbest=f; lastimp=it; }
    }
    printf("done best=%.3f\n",best); return 0;
}
