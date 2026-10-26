# gluing/ (agent gluing)

Code (C, single files, `gcc -O3 -march=native`; binaries in bin/):
- src/gutil.h      graph6 I/O, bitset alpha test (n <= 62)
- src/glue.c       neighbourhood gluing extender (GR2013 Sec. 3). `glue -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX]`
                   input graph6 H with alpha(H) <= K-1; output all G = H + v + u_1..u_D, alpha(G) <= K, no iso rejection.
- src/onepoint.c   one-point extensions.
- src/mcount.c     MCMC (Wang-Landau + broad-histogram) estimate of labelled counts g(e) of (3,K;n,e)-graphs.
- src/combine.py   turns mcount output into ln-count curves / estimated counts.
- src/tcheck.py    checks GR-style increments t_d (which input classes suffice), exact enumeration of degree sequences.
- src/build_all.py rebuilds all R(3,k;n) for small k (validation).
- src/target.sh    min-degree gluing of all (3,K+1;N)-graphs from R(3,K;*) files.
- src/satglue.py   hybrid test: fixed H, SAT (CaDiCaL via pysat) finds a 9-regular gluing.
- src/exact_lab.py exact labelled counts (sum n!/|Aut|) per edge level of a graph file.

Data: val/ = all R(3,3..6;n), R(3,7;21), R(3,7;22) (own generation). cls/ = partial classes (own generation).
Logs: ../runs/gluing/.
