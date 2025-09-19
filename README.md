File list

* Python codes:
    - `Halfedges.py`: Run systre, read the result, and generate the half-edge set and the inversions (no rotations yet).
    - `DrawNetwork.py`: Draw the network (Only vertices and edges).
    - `Coplanar.py`: Tell if all vertices are locally planar, i.e. the adjacent edges are coplanar.
    - `Orthogonal.py`: Tell if for all edges, the normal vectors at its vertices are orthogonal.
    - `DFSNormal.py`: Use Depth-First search to assign normals vectors to all vertices, so that normal vectors at adjacent vertices always form an acute angle.
    - `MakeFaces.py`: Use the normal vectors and the right-hand rule to determine rotations, thereby generate a Rotation System and find the faces of the surface.
    - `DrawSuface.py`: Draw the surface (OpenGL).
    - `ExportSTL.py`: Export `.stl` file into the `models` directory.
    - `CheckEmbed.py`: Check if triangular mesh in an `.stl` file intersect itself.

* shellscripts:
    - `extract_symbols.sh`: Extract symbols of networks from the `.cgd` database, and redirect the output into `symbols.dat`.
    - `run_systre.sh`: Take a network symbol as parameter, out a temporary file containing the cgd description of the network, and run systre on it.
    - `filter_coplanar.sh`: For all networks in `symbols.dat`, filter out those whose vertices are locally planar.
    - `filter_orthogonal.sh`: For all networks in `coplanar-*.dat`, filter out those NONE of whose edges is orthogonal.
    - `filter_dfs.sh`: For all networks in `orthogonal-*.dat`, filter out those on which the DFS method fails.
    - `filter_trivial.sh`: For all networks in `orthogonal-*.dat` and not in `dfs-fail.dat`, filter out those with homologically non-trivial face-cycles.
    - `export_stl.sh`: Export a single STL.
    - `export_all_stl.sh`: Export STL for all networks in `trivial-faces.dat`.
    - `draw_surface.sh`: Draw a surface.
    - `check_all_models`: Check embeddedness for all STLs in the `models` directory.

* Data files:
    - `rcsr3d.{cgd, arc}`: Database of 3D networks from RCSR.
    - `symbols.dat`: list of network names in the `.cgd` database.
    - `symbols-large.dat`: list of a few networks that are too large (typically > 1.0Kb) to proceed.
    - `coplanar-*.dat`: list of locally planar networks.  * could be barycentric or relaxed, depending on the embedding method.
    - `orthogonal-*.dat`: list of locally planar networks none of whose edges is NON-orthogonal.
    - `dfs-fail.dat`: list of all locally planar and non-orthogonal networks on which the DFS assignment of normal vectors fails.
    - `trivial-faces.dat`: list of all networks in `dfs-fail.dat` that do not have non-trivial face-cycles.  This are the networks that are ready to be embedded!
    - `models`: Directory containing all STL models.
