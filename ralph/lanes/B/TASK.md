# Lane B: gluing (t9 <= 88, then a faster gluer)

Start share: 20 cores.

Background: `paper/latex/sec6.tex`, `notes/gluing.md`, `gluing/README.md`, code `gluing/src/`.
Every graph in R(3,9;30,<=e) is a possible G - N[v] of a degree-9 vertex; if the gluer extends none
of them to a (3,10,40)-graph, every degree-9 vertex has e(G - N[v]) > e. Done before (enum): e <= 87
(149,135 inputs). A t9 <= 88 run with no output closes 15 more degree distributions (510 open); it was
started on the old machine and its result is lost. Class size estimates: R(3,9;30,88) ~ 5.9e6,
89 ~ 1.5e8, 90 ~ 2.8e9. Our generation was ~100x slower than Angeltveit's (~0.5-1 s vs ~4 ms per graph).

## Do
1. BOOTSTRAP: build the gluers (`glue.c`, `glue2.c`, `glue5.c`, generator scripts) under
   `scratch/B/build` (nauty from opt/ when lane A has it; build your own copy if it is not there yet).
   Re-validate on the published counts (sec6.tex "Validation": R(3,7;21) = 1,118,436 per e-level,
   R(3,9;30,86) = 1,800, R(3,9;31,95) = 560), and rebuild C35 and Exoo's 39-graph from their own G - N[v].
2. Speed: generation is the cost. Read Angeltveit (arXiv:2401.00392, Sec. 4) and GR (their increment
   method) and make generation of R(3,9;30,e) at least 10x faster; measure per-graph cost on a sample;
   check that the output on e <= 87 equals GR Table 14 exactly, level by level.
3. Run t9 <= 88 (`gluing/src/t9_88.sh`, sec10.tex: increments t5 = 3, t6 = 4, t7 = 3; built-in check:
   the e <= 87 part must equal GR T14). Estimate the wall time before the launch; it must fit the run.
4. If (3) fits easily: plan t9 <= 89 and t8 levels (degree-8 vertices, e(G - N[v]) >= 98?) by cost.
Label: enum (no certificate), CONFIRMED only after an independent re-check (own SAT gluer on a sample).
