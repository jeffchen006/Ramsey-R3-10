# Mixed 9/8 three-root branches and a small antineighbour CNF

Use `path_three.md` and `high_f_paths.md` for the P3 structure and
notation. Assume the checked diagonal-three/four residue cap e(X)<=63
from round five. This is not a bound on an isolated pair. In a P3
with arm counts 9 and 8, reverse the roots if necessary to make
Y--(B2+B1) complete. The other 3-by-3 block Z--(B0+B1) lacks one
edge. The formula e(X)=45+9+8+b=62+b leaves b=e(Y,Z)<=1.
Diagonal five is already excluded when both counts are at least 8.

At diagonal three, B1 is empty. The missing edge can be placed at a
fixed position by permuting Z and B0. If b=1, the Z endpoint of
the wing edge is either the row of that hole or one of the other
two rows (which can be interchanged). Therefore there are three
layouts: zero wing edges, one at the hole row, or one off it.
They are keys 1, 6, 7 in the stable diagonal-three high-f listing
from `p3_antineighbour.py`. At diagonal four, the singleton of B1
sees all of Y. If it saw all of Z then b=0 and T+Y+Z would be
independent of size ten. Thus the missing incidence is from B1 to
some z*. Triangle freeness permits Y--Z edges only at z*, and
b=1 to avoid that independent ten-set. The wing permutations put
this unique layout in the form produced by `p3_mixed_arms.py`.

## Four arbitrary antineighbours of T, diagonal three only

The three T vertices send exactly 18 edges to the 22-vertex X, so
at least four X vertices avoid T. Each avoids all three roots by
the definition of X. Choose any four of them. All possible edges
of the graph induced on the 18-vertex boundary and these four are
now fixed (boundary edges and root/T nonedges) or CNF variables
(a pair of selected vertices or selected-to-eligible boundary).

The CNF only imposes triangle-freeness and independence at most nine.
For triangles use the one-, two-, or three-selected-vertex clauses;
the fixed boundary has no triangle. For each independent fixed-boundary
subset I of size t and each 10-t-subset J of the four vertices, add
one clause requiring an edge within J or between I and J. Every
independent ten-set has this form, and fixed boundary/root incidences
are respected. This is a necessary relaxation, not a completion test.
The C21 analogous calibration finds two required antineighbours;
its actual assignments satisfy the formula and deleting all their
edges violates it. Three layouts have CakeLPR-checked refutations
(identical hash bindings on replay): keys 1, 5, 6. Key 5 is the
previously excluded pair of complete arms. The other 13 layouts
checked have satisfying relaxation assignments, not extensions.

Thus the only mixed candidate at diagonal three is the one off the
hole row, at e63. Together with the unique diagonal-four e63 layout
there are exactly 60+60 fixed boundary/residue keys whose refutations
would exclude mixed arms. The fixed-boundary encoding is the same
Lite6 relaxation proved in `p3_e63_relaxation.md`; changing the
boundary has no effect on its soundness. The C21 sorted positive and
one-edge negative controls are retained. Coverage and caps are recorded
separately in `ROUND5_REPLAY.md` and the final index.
