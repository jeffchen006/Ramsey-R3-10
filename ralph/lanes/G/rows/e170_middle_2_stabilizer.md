# Physical transport for aligned middle+middle.2 (hand)

Use the marked adjacent d6 reduction and labelled grid from
`e170_aligned_grid.md`. In `middle+middle.2`, the missing left supports
are `{L0,L3}`, `{L0,L4}` and the missing right supports are `{R0,R1}`,
`{R0,R2}`. They are two disjoint pairs of noncross labels, distinguished
by shore. With shores kept, a simultaneous label permutation must
preserve both pairs setwise, giving `2!·2! = 4` actions. With shores
exchanged it must swap the two pairs, again giving `2!·2! = 4` actions.
All fix the unordered crossing and preserve the off-diagonal grid and
the four required noncross diagonal witnesses. They act bijectively on
the set of legal matchings of the allowed left and right double pairs.
The action on an individual double is the image of all four of its
anchors; it is not just a permutation of the hole names.

For an oriented transport from a checked pattern to another alignment,
take the induced injection on retained sites given by their full
supports. The twenty private grid sites map bijectively to the twenty
grid sites, and a grid site cannot map to a double. All double sites
have distinct supports. The injection preserves site/anchor incidence
and the sole wing edge. Thus pairs sharing an anchor, exterior triangles,
and every retained witnessed independent-ten block map to necessary
clauses: the moved anchors still have no crossing, avoid all moved
exterior sites in the block, and the vertex count stays ten. A purported
completion of the destination consequently pulls back to an assignment
satisfying the source CNF, contradicting a checked LRAT. The argument
does not require a graph automorphism or a syntactic permutation of the
LRAT trace. It also applies to a previously certified smaller set of
doubles whenever its literal image is contained in the destination;
such a transport need not preserve the original proof's *full* scheme.

The only new implication used here is local: if every labelled
matching for the named holes inherits a checked contradiction, then
no target has this marked hole scheme at `h=8`. This says nothing about
nonaligned doubles or about other marked schemes or whole degree cases.
