File list

* rcsr3d.{cgd, arc}: Data base of 3D networks from RCSR.
* extract_symbols.sh: Extract symbols of networks from the .cgd database, and redirect the output into symbols.dat.
* run_systre.sh: Take a network symbol as parameter, out a temporary file containing the cgd description of the network, and run systre on it.
* Halfedges.py: run systre, read the result, and generate the half-edge set and the inversions (no rotations yet).
* DrawNetwork.py: draw the network (Only vertices and edges).
* Coplanar.py: tell if all vertices are locally planar, i.e. the adjacent edges are coplanar.
* filter_coplanar.sh: for all networks in symbols.dat, filter out those whose vertices are locally planar.
* Orthogonal.py: tell if for all edges, the normal vectors at its vertices are orthogonal.
* filter_orthogonal.sh: for all networks in coplanar-*.dat, filter out those NONE of whose edges is orthogonal.
* coplanar-*.dat: list of locally planar networks.  * could be barycentric or relaxed, depending on the embedding method.
* orthogonal-*.dat: list of locally planar networks none of whose edges is orthogonal.
