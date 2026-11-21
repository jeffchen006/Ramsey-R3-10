# Signature graph at equality in the private-cell bound (hand)

Let `G` be triangle-free, maximal, of order `n` and independence number
at most `a`. Let a root of degree `d` have neighbours `A`, exterior `H`,
and `p=a+1-d`. Write `P_i` for the exterior vertices adjacent to just
the `i`-th neighbour. The independent set `(A-{i}) ∪ P_i` shows
`|P_i| <= p`. Maximality assigns every exterior vertex a nonempty
signature in `A`. If `Z=d+2|H|-dp`, then the identity

`Z-(d+2|H|-dp) = (dp-Σ_i |P_i|) + Σ_{x:|signature(x)|≥3} (|signature(x)|-2)`

forces `|P_i|=p` and all remaining signatures to be pairs. For a pair
`{i,j}`, the private cell `P_i` and all exterior vertices with this pair
as signature are jointly independent, since all are neighbours of `i`.
They can be joined to `A-{i,j}` in the same independent set. Therefore
there is at most one such pair signature. The distinct pair signatures
form a simple graph `J` on `A`, with degrees `d_G(i)-1-p`. If `ij` is an
edge of `J`, the codegree of `i,j` in `G` is two: the root and the one
exterior vertex with signature `{i,j}`. Thus such an edge is forbidden
when the degree-pair codegree cap is less than two.

For `n=40,a=9,d=6,e(G)=168` and the independently certified degree-six
residue floor 120, one has equality, `p=4`, and `J` has six vertices and
nine edges. Its degrees are in `{1,2,3,4}`; two degree-one vertices may
not be joined. Non-adjacency in `J` is not a statement about any
exterior edge. The new LP row sets the count of all unsupported root
profiles to zero. It does not assume that an allowed `J` extends.

The calibration on C13(1,5) uses 13 actual equality roots and 52 pair
signatures; C35 and saturated Exoo39 also pass the inequality (neither
has equality roots). The enumeration has 3,700 admissible labelled `J`s
and precisely the six profiles listed in `private_packing.md`.

At all 47 still-open e168 distributions with `n6>0`, the matched LP
with the new row closes six and tightens seven checked t9 thresholds
using the original gluing bounds. All six closures also have exact
Farkas certificates with only the published `e(H8)>=95`, `e(H9)>=86`
floors, together with the accepted `e(H6)>=120`, `e(H7)>=107` floors.
The ordinary relaxation without the new row was numerically feasible
for all six at the same assumptions. See `../private_equality_cuts.jsonl`
for the stronger (gluing-independent) exclusions and
`../private_equality_t9.jsonl` for the 13 threshold certificates; the
bound-tightening records only assume H8's gluing floor, and converting
`t9<=87` to an exclusion would use H9's gluing floor. The separate pair
packing gives two additional independent cuts, not counted here.
