# Involution (2,32), three size-five and one size-six attachment

**Hand review of the new no-isolate coverage** in
`ralph/lanes/E/crown32_t1.md`; earlier isolate argument remains E-006.
The finite zero-partition result keeps E's `enum` label.

The side-independence bounds are needed at two scales. A full side of
four moving vertices adds to W, forcing alpha(W) ≤ 5. Omit the moving
vertex at attachment j from that side and the other three add to
W ∪ A_j, forcing alpha at most six there. Both moving vertices in
an orbit may be added to H_i since the orbit is nonadjacent in the
crown reduction: alpha(H_i) ≤ 7 and triangle-freeness gives Delta ≤ 7.
Consequently a W vertex with fixed degree nine loses at least two
neighbours to every attachment. In the no-isolate case its other
neighbour is in W, so it cannot be costly by either test.

The multiplicities four / three / two in the sum over H_i for edges
with two / one / zero W endpoints equal the corresponding endpoint
weights. The maximum at 21 attachment and 11 W vertices is
`21*7 + 2*11*9 - 2*b = 345 - 2*b`. For the minimum of the three order-27
anchors, `3e + 73` is a lower bound. An odd cycle in W forces b ≥ 5;
e85/e86/e87 have b ≤ 8/7/5. No shortest odd cycle of length ≥9 survives.
At e87, exactly five vertices have W-degree ≥2, making the induced
cycle a C5. A leaf attached to one of those five would allow an
independent vertex extension from the other nine after removing the
leaf and its neighbour. The other nine would need alpha ≤4, hence an
odd cycle, although at most four vertices can have degree ≥2 there.
Thus the six remaining W vertices form three disjoint edges, and each
has anchor degree seven. The specialized replay can enumerate that
matching without losing an admissible W.

For a valid W the complement in H0 really is partitioned into the
other three attachments of sizes 6,5,5, each independent and with
alpha ≤6 after adjoining W. Rejection at this stage is sound without
relying on the later extension implementation. Scope: t=1 only;
the prior all-graphs minimum-degree-five dependency and the published
GR e85/e86/e87 counts remain explicit.
