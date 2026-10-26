/* kagg: aggregate genbg kernel output (bipartite n1+n2, class1 = A = 0..n1-1, class2 = B). Author: cases, 2026-10-26.
   Keeps graphs with matching >= m and (class-1 pairs) common nbrs <= z. Prints counts per edge number and
   a uniform reservoir sample of K graphs per edge number (seeded xorshift; reproducible for a fixed genbg run).
   Usage: genbg -q ... | kagg n1 m z K seed COUNTFILE SAMPLEFILE */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n, n1, adj[64], mt[64], vis[64];
static int aug(int a){ for(int b=n1;b<n;b++) if((adj[a]>>b&1)&&!vis[b]){ vis[b]=1; if(mt[b]<0||aug(mt[b])){ mt[b]=a; return 1; } } return 0; }
static uint64_t s;
static uint64_t rnd(void){ s^=s<<13; s^=s>>7; s^=s<<17; return s; }
#define EMAX 128
int main(int argc,char**argv){
  if(argc<8){ fprintf(stderr,"usage\n"); return 2; }
  n1=atoi(argv[1]); int m=atoi(argv[2]), z=atoi(argv[3]), K=atoi(argv[4]); s=strtoull(argv[5],0,10)*2654435761ULL+1;
  static long long cnt[EMAX], seen[EMAX]; static char *samp[EMAX][64]; long long tot=0, rej=0;
  if(K>64) K=64;
  char l[256];
  while(fgets(l,sizeof l,stdin)){
    int len=strlen(l); while(len&&(l[len-1]=='\n'||l[len-1]=='\r')) l[--len]=0;
    if(!len) continue;
    n=l[0]-63; memset(adj,0,sizeof adj);
    int bit=0,k=1,x=0,e=0;
    for(int j=1;j<n;j++) for(int i=0;i<j;i++){
      if(bit==0){ x=l[k++]-63; bit=6; }
      bit--; if(x>>bit&1){ adj[i]|=1<<j; adj[j]|=1<<i; e++; }
    }
    int bad=0;
    for(int i=0;i<n1&&!bad;i++) for(int j=i+1;j<n1;j++) if(__builtin_popcount(adj[i]&adj[j])>z){ bad=1; break; }
    if(!bad){ int nu=0; for(int b=0;b<n;b++) mt[b]=-1;
      for(int a=0;a<n1;a++){ memset(vis,0,sizeof vis); nu+=aug(a); } if(nu<m) bad=1; }
    if(bad){ rej++; continue; }
    tot++; cnt[e]++; long long t=seen[e]++;
    if(t<K) samp[e][t]=strdup(l);
    else { uint64_t r=rnd()%(uint64_t)(t+1); if(r<(uint64_t)K){ free(samp[e][r]); samp[e][r]=strdup(l); } }
  }
  FILE *f=fopen(argv[6],"w"); FILE *g=fopen(argv[7],"w");
  for(int e=0;e<EMAX;e++) if(cnt[e]){ fprintf(f,"%d %lld\n",e,cnt[e]);
    for(int i=0;i<K&&i<cnt[e];i++) fprintf(g,"%d %s\n",e,samp[e][i]); }
  fprintf(f,"# total %lld rejected %lld\n",tot,rej); fclose(f); fclose(g); return 0;
}
