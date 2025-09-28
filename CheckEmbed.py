import sys
import numpy as np
import trimesh
eps = 1e-8

def read_stl(filename):
    triangles, verts = [], []
    for line in open(filename):
        if line.strip().startswith('vertex'):
            verts.append([float(x) for x in line.strip().split()[1:]])
            if len(verts) == 3:
                triangles.append(np.array(verts))
                verts = []
    return triangles

def tri_tri_intersect(tri1, tri2):
    # Return False if triangles just share an edge (and are not coplanar)
    def share_edge(t1, t2):
        # Check all pairs of edges
        for i in range(3):
            a1, a2 = t1[i], t1[(i+1)%3]
            for j in range(3):
                b1, b2 = t2[j], t2[(j+1)%3]
                if (np.linalg.norm(a1-b1)<eps and np.linalg.norm(a2-b2)<eps) or (np.linalg.norm(a1-b2)<eps and np.linalg.norm(a2-b1)<eps):
                    return True
        return False
    # Check coplanarity
    def is_coplanar(t1, t2):
        n1 = np.cross(t1[1]-t1[0], t1[2]-t1[0])
        n2 = np.cross(t2[1]-t2[0], t2[2]-t2[0])
        n1 = n1 / np.linalg.norm(n1)
        n2 = n2 / np.linalg.norm(n2)
        return np.linalg.norm(n1-n2) < eps or np.linalg.norm(n1+n2) < eps
    if share_edge(tri1, tri2) and not is_coplanar(tri1, tri2):
        return False
    # Return False if triangles are exactly the same (all vertices match within eps)
    def triangles_equal(t1, t2):
        # Check all permutations
        for perm in [(0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)]:
            if all(np.linalg.norm(t1[i]-t2[perm[i]]) < eps for i in range(3)):
                return True
        return False
    if triangles_equal(tri1, tri2):
        return False
    # Return False if triangles are exactly the same (all vertices match within eps)
    def triangles_equal(t1, t2):
        for perm in [(0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)]:
            if all(np.linalg.norm(t1[i]-t2[perm[i]]) < eps for i in range(3)):
                return True
        return False
    if triangles_equal(tri1, tri2):
        return False

    # Return False if triangles just share an edge (and are not coplanar)
    def share_edge(t1, t2):
        for i in range(3):
            a1, a2 = t1[i], t1[(i+1)%3]
            for j in range(3):
                b1, b2 = t2[j], t2[(j+1)%3]
                if (np.linalg.norm(a1-b1)<eps and np.linalg.norm(a2-b2)<eps) or (np.linalg.norm(a1-b2)<eps and np.linalg.norm(a2-b1)<eps):
                    return True
        return False
    def is_coplanar(t1, t2):
        n1 = np.cross(t1[1]-t1[0], t1[2]-t1[0])
        n2 = np.cross(t2[1]-t2[0], t2[2]-t2[0])
        n1 = n1 / np.linalg.norm(n1)
        n2 = n2 / np.linalg.norm(n2)
        return np.linalg.norm(n1-n2) < eps or np.linalg.norm(n1+n2) < eps
    if share_edge(tri1, tri2) and not is_coplanar(tri1, tri2):
        return False

    # Use trimesh for intersection
    mesh1 = trimesh.Trimesh(vertices=tri1, faces=[[0,1,2]], process=False)
    mesh2 = trimesh.Trimesh(vertices=tri2, faces=[[0,1,2]], process=False)
    inter = mesh1.intersection(mesh2)
    # If intersection mesh has faces, triangles intersect
    return inter.faces.shape[0] > 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python CheckEmbed.py file.stl")
        sys.exit(1)
    triangles = read_stl(sys.argv[1])
    n = len(triangles)
    for i in range(n):
        for j in range(i+1, n):
            if tri_tri_intersect(triangles[i], triangles[j]):
                print("false")
                print("Triangle 1:", triangles[i])
                print("Triangle 2:", triangles[j])
                return
    print("true")

if __name__ == "__main__":
    main()