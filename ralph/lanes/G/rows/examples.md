# Two short closure checks (hand; conditional on the report's gluing)

## (n6,n7,n8,n9) = (0,18,0,22), e = 162

Let `h(v)` count degree-7 neighbours. The degree-7 edge floor
`e(H_v)>=104` gives `Z(v)=63-2h(v)<=58`, hence `h(v)>=3`.
The degree-9 gluing floor `e(H_v)>=88` gives `Z(v)=81-2h(v)<=74`,
hence `h(v)>=4`. Counting degree-7 to degree-9 edges from their 7-end
gives at most `18*4=72`; counting from their 9-end gives at least `22*4=88`.

## (n6,n7,n8,n9) = (8,0,0,32), e = 168

Here let `h(v)` count degree-6 neighbours. The degree-6 edge floor
`e(H_v)>=118` gives `Z(v)=54-3h(v)<=50`, hence `h(v)>=2`.
The degree-9 gluing floor `e(H_v)>=88` gives `Z(v)=81-3h(v)<=80`, hence
`h(v)>=1`. Counting degree-6 to degree-9 edges from the 6-end gives at most
`8*4=32`, and from the 9-end at least `32*1=32`. Equality forces every
degree-6 vertex to have exactly two degree-6 neighbours and every degree-9
vertex to have exactly one. Thus there are eight degree-6 to degree-6 edges
and only eight wedges whose endpoints both have degree 6 (one at each 6-vertex).
But each of the `binom(8,2)-8=20` nonedges between degree-6 vertices needs
a wedge by maximality. This contradicts the count.
