# Ramsey-R3-10: a progress report on R(3,10)

Author: **Zhiyang Chen**

This repository is a **progress report**: it marks the progress of an ongoing project on the Ramsey number R(3,10).
It is not a formal publication.

> **Warning: work in progress, not a definite answer.** R(3,10) is still open. The results here are partial,
> and some computations are still running (see Sec. 10 of the report). Each result has a status (certified,
> CONFIRMED, enumeration-only, estimate); check the status before you rely on a result.

R(3,10) is known to be 40 or 41 (Exoo 1989; Angeltveit 2024/2025). It equals 41 exactly when a (3,10,40)-graph
exists: a triangle-free graph on 40 vertices with independence number at most 9. This repository contains the code,
notes and progress report of a computational study of such graphs. It proves partial results and measures what remains.

## Progress report (PDF)

*On (3,10,40)-graphs: structure, symmetry, and certified computations — a progress report* (version 2), Zhiyang Chen.
PDF: [`paper/latex/main.pdf`](paper/latex/main.pdf). Permanent record (Zenodo): **DOI [10.5281/zenodo.23678020](https://doi.org/10.5281/zenodo.23678020)** (version 2;
all versions: [10.5281/zenodo.23677794](https://doi.org/10.5281/zenodo.23677794)).
Please cite the report (see `CITATION.cff`).

## Results so far (partial; each labelled in the report as certified, reviewed, or enumeration-only)

- Structure: in any (3,10,40)-graph the maximum degree is 9; one may assume the graph is maximal triangle-free
  (then the minimum degree is at least 6); an averaging theorem leaves 545 degree distributions. The case split is
  formalised in Lean 4 (only published computational facts are used as hypotheses).
- Symmetry: no (3,10,40)-graph is a Cayley graph of any of the 14 groups of order 40, and many automorphism types
  of prime order are excluded (DRAT certificates).
- Gluing: no degree-8 vertex v has e(G - N[v]) <= 96 and no degree-9 vertex has e(G - N[v]) <= 87
  (exhaustive gluing over published-count-checked classes).
- Certified SAT: a SAT Modulo Symmetries pipeline with a lazy independent-set propagator and a fully checked proof
  chain (LRAT/cake_lpr, VeriPB/CakePB, a Lean-verified symmetry-clause checker); 365 of 464 cubes of one
  9-regular sub-case are certified UNSAT.
- What remains: the 9-regular case and the near-regular degree distributions; the report gives measured costs of
  every route we tried.

## Layout

| folder | content |
|---|---|
| `paper/` | LaTeX sources and PDF |
| `notes/` | technical notes (case split, gluing, symmetric searches, SAT plan, dependencies) |
| `cases/`, `lean/` | case-split scripts and certificates; Lean 4 formalisation |
| `sms/`, `satcore/`, `cert/` | SAT encodings, our SMS patches (`sms/sms-patches/`), proof-certificate pipeline |
| `gluing/`, `symsat/`, `known39/`, `anneal/`, `algebra/`, `critic/`, `duo/` | gluing, symmetric search, construction searches, independent checks, research notes |
| `tools/` | job and cube runners, independent graph checker `tools/check_graph.py` |

Third-party software (SAT Modulo Symmetries, CaDiCaL, kissat, nauty, drat-trim, cake_lpr, VeriPB, CakePB,
MathCheckRamsey, triangleramsey, MTF) is not included; versions and sources are listed in `tools/README.md`.
Large proof files and graph lists are not included; `LARGE_FILES.tsv` lists them. `MANIFEST.tsv` gives the
sha256 of every file here.

## How this work was done

The computations, notes and the report were produced by a team of AI agents (Claude, with OpenAI Codex as a
research assistant) working under the direction of the author, with an independent reviewer agent checking every
claim. All published facts used are listed with sources in `notes/DEPENDENCIES.md`.

## Licence

Code: MIT (`LICENSE`). Report and notes: CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`).
