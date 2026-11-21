# Bounds on full one-side pin families

Fix an orientation and the identities of the singleton masks. Let C be
the entire remaining profile family (or any subset obtained by adding
sound constraints). Encode a profile by entries for size-two and size-three
masks. For each coordinate i project onto all entries involving i (a
star); additionally project onto all size-two entries. Each entry now
occurs in exactly three projections. Order all entries arbitrarily and
take the uniform random profile in C. Expand the entropy of each
projection by the chain rule. The conditional entropy of an entry in
that projection is at least its entropy conditioned on *all* preceding
entries. Summing gives `3 log |C| <= sum log |projection(C)|`. The floor
of the integer cube root of the product of upper bounds on the local
projection sizes therefore bounds the family for the fixed singleton
pattern. Sum those floors over all patterns.

`pin_bound.py` counts a superset of each local projection exactly:
the complete degree, order and total incidence determine the global
numbers of size-two/three masks once the singleton pattern is fixed.
Enumerate triple supports through i, starting with any legal mask and
consuming both corresponding pair capacities. Independently fill the
remaining star pair capacities by a cardinality polynomial. Require
the degree at i and the min-edge count at its edge to the root (the
row in `factor_sat.py`); cap counts by global mask numbers and the
maximum capacities of types away from i. The extra all-pairs
projection counts all multisets of the specified size under the
individual pair capacities. There is no assumption that the projected
solutions extend. Computations use exact integers only.

`--matching` also enforces the known singleton-codegree matching
condition at the selected root. Two root coordinates have codegree
one iff no support, fixed or variable, contains both. Such absent
pairs must be a matching. Within star i a remaining capacity 2 means
no fixed or selected triple support has covered the pair yet. All but
at most one of those pairs must receive positive multiplicity; allow
none if i already forms a codegree-one pair with the other root.
`pair_match.py` also encodes the same condition directly in Boolean
clauses by forbidding two absent pairs with a common endpoint.

## Measurements (`enum`)

Exact C16 relaxed-family counts agree between direct enumeration and
the independent SAT formulation on all 26 oriented sides: 700 total
before the matching cut, 678 after. Every exact count is below its
computed bound. On the stronger 241 C16 baseline profiles, the
Boolean cut preserves all 43 labelled completions. On the same eight
matched target buckets as round 3 (800 profiles), 496/501 baseline
profiles survive the cut; evidence in `scratch/D/pair_match40.tsv`.

For the 110 surviving root-swap representatives, take the smaller
bound over the two orientations. Without the matching rule the bounds
range from 61,433,965,539,012 to 356,217,116,224,673,843; with it the
minimum is unchanged, median ~4.90e16, maximum 288,702,339,556,998,326.
With the rule the sum of bounds is 6,915,542,604,894,630,664. This is
an explicit upper bound for this cover, **not** a model count, lower
bound, or cost forecast. The bound is too loose to authorize a sweep.
The two target runs take 2.38 and 2.59 CPU-s, and the control runs 1.18
and 1.69 CPU-s. TSV row index refers to `survivor_orbits/survivors.g6`,
not to the initial 238-kernel catalogue.

```sh
# from scratch/D, with ulimit -v 16777216
nice -n 5 timeout 45 ../../opt/venv/bin/python -B ../../ralph/lanes/D/pin_bound.py 16 5 calibration16/kernels.g6 --control --matching
nice -n 5 timeout 45 ../../opt/venv/bin/python -B ../../ralph/lanes/D/pin_bound.py 40 9 survivor_orbits/survivors.g6 --matching
```
