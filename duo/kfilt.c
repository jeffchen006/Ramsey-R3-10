/* Filter genbg graph6 output (bipartite n1+n2, class1 = 0..n1-1): keep graphs with maximum matching >= m.
   Output: "e|degA|degB<TAB>g6" (degA, degB = sorted degree sequences, descending). Usage: kfilt n1 m < in > out */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int n, n1, adj[64], mt[64], vis[64];
static int aug(int a){ for(int b=n1;b<n;b++) if((adj[a]>>b&1)&&!vis[b]){ vis[b]=1; if(mt[b]<0||aug(mt[b])){ mt[b]=a; return 1; } } return 0; }
static int cmp(const void*x,const void*y){ return *(int*)y-*(int*)x; }
int main(int argc,char**argv){
  n1=atoi(argv[1]); int m=atoi(argv[2]); char l[256];
  while(fgets(l,sizeof l,stdin)){
    int len=strlen(l); while(len&&(l[len-1]=='\n'||l[len-1]=='\r')) l[--len]=0;
    n=l[0]-63; memset(adj,0,sizeof adj);
    int bit=0, k=1, x=0, e=0;
    for(int j=1;j<n;j++) for(int i=0;i<j;i++){
      if(bit==0){ x=l[k++]-63; bit=6; }
      bit--; if(x>>bit&1){ adj[i]|=1<<j; adj[j]|=1<<i; e++; }
    }
    int nu=0; for(int b=0;b<n;b++) mt[b]=-1;
    for(int a=0;a<n1;a++){ memset(vis,0,sizeof vis); nu+=aug(a); }
    if(nu<m) continue;
    int da[32],db[32]; for(int i=0;i<n1;i++) da[i]=__builtin_popcount(adj[i]); for(int i=n1;i<n;i++) db[i-n1]=__builtin_popcount(adj[i]);
    qsort(da,n1,sizeof(int),cmp); qsort(db,n-n1,sizeof(int),cmp);
    printf("%d|",e); for(int i=0;i<n1;i++) printf("%d",da[i]); printf("|"); for(int i=0;i<n-n1;i++) printf("%d",db[i]); printf("\t%s\n",l);
  }
  return 0;
}
