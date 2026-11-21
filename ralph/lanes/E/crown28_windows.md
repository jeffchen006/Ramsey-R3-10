# Involution with 28 fixed points and maximum attachment 4

**`enum`: `|W|≤6`, where `W` is the fixed vertices with no moved
neighbors.** This rules out sizes 7 and 8, not the whole `(2,28,a=4)`
case. Scope: all graphs, no maximality hypothesis or min-degree lower
bound.

The six-pair crown reduction is in `involution.md`. The fixed attachment
sets are disjoint independent sets of size at most four. Since a whole
crown side is independent, `α(W)≤3`, hence `|W|≤8`. Also `|W|≥4` from
the sum of attachment sizes. Each of the six attachments falls short of
size four by a nonnegative integer, with total shortfall `|W|−4`. Hence
there are at least `10−|W|` full size-four attachments. For any `j` such
attachments the `6−j` other moved vertices from a side are independent
and avoid those attachments and `W`, so their union with `W` has
independence number at most `3+j`.

Use the profile sieve of `crown30_windows.md`: enumerate a full
attachment by its multiset of independent neighbor masks into `W`, and
allow all possible edges between disjoint masks in different attachment
groups. This supergraph need not be triangle-free; an independent set in
it nonetheless certifies failure of that profile combination. Require
all singleton/pair/triple independence bounds and the degree bound on
`W`. The generation and sieve operate on unrooted copies with all masks
permitted in each copy, including repeats.

| `|W|` | `W` isomorphism classes | Full profiles | Viable pairs | Viable triples |
|---:|---:|---:|---:|---:|
| 8 | 3 | 2 | 0 | 0 |
| 7 | 9 | 110 | 14 | 0 |

Thus no pair is possible at size eight (two required), and no triple
at size seven (three required). The smaller-window pilot checked higher
multiplicity packings with the same mask relaxation; 3/15, 6/9 and 6/6
unrooted cores survive at `|W|=6,5,4`, respectively. These are only
profiles, not actual order-40 models. Missing cross-group triangle
constraints are the next target, beginning with the three `|W|=6` cores.

## Replay

`geng -t` produces all triangle-free isomorphism classes, then the script
checks `α≤3` independently. The counts for order seven and eight match
`notes/gluing.md`. The planted Petersen fixed star tests repeat profiles
on a valid smaller crown. The generic packer also rejects a forced
independent four-set in its two-attachment toy.

```sh
cd scratch/E
for order in 4 5 6 7 8; do
  nice -n 5 timeout 30 bash ../../ralph/lanes/E/limited.sh 20 \
    ../../opt/bin/geng -q -t "$order" > "crown28.trianglefree$order.g6"
done
nice -n 5 timeout 180 bash ../../ralph/lanes/E/limited.sh 90 \
  python3 -u ../../ralph/lanes/E/crown28_windows.py . 8 7 6 5 4
```

Evidence `scratch/E/crown28.w78.log`, `scratch/E/crown28.w456.probe.log`;
0.46 and 17.11 CPU s, respectively. The survivors at sizes 4–6 were not
sent to the graph gate because the profiles are not graphs satisfying
the target conditions.
