import sys
import numpy as np
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

def edge_edge(V0, V1, U0, U1):
    v, u = V1-V0, U1-U0
    a, b, c = np.dot(v,v), np.dot(v,u), np.dot(u,u)
    w0 = V0-U0
    d, e = np.dot(v,w0), np.dot(u,w0)
    denom = a*c - b*b
    if abs(denom) < eps:
        return False
    s, t = (b*e-c*d)/denom, (a*e-b*d)/denom
    if not (eps < s < 1-eps and eps < t < 1-eps):
        return False
    return np.linalg.norm((V0+s*v)-(U0+t*u)) < eps

def point_in_tri(p, tri):
    v0, v1, v2 = tri[1]-tri[0], tri[2]-tri[0], p-tri[0]
    d00, d01, d11 = np.dot(v0,v0), np.dot(v0,v1), np.dot(v1,v1)
    d20, d21 = np.dot(v2,v0), np.dot(v2,v1)
    denom = d00*d11 - d01*d01
    if abs(denom) < eps:
        return False
    v = (d11*d20 - d01*d21)/denom
    w = (d00*d21 - d01*d20)/denom
    u = 1-v-w
    return (u > eps) and (v > eps) and (w > eps)

def share_vertex_or_edge(A, B):
    return any(np.linalg.norm(a-b)<eps for a in A for b in B)

def tri_tri_intersect(a, b):
    # Fast bounding box check
    min_a = np.min(a, axis=0)
    max_a = np.max(a, axis=0)
    min_b = np.min(b, axis=0)
    max_b = np.max(b, axis=0)
    if np.any(max_a < min_b) or np.any(max_b < min_a):
        return False
    V, U = a, b
    N1, N2 = np.cross(V[1]-V[0], V[2]-V[0]), np.cross(U[1]-U[0], U[2]-U[0])
    d1, d2 = -np.dot(N1, V[0]), -np.dot(N2, U[0])
    du = [np.dot(N1, u)+d1 for u in U]
    dv = [np.dot(N2, v)+d2 for v in V]
    du = [0.0 if abs(x)<eps else x for x in du]
    dv = [0.0 if abs(x)<eps else x for x in dv]
    if all(x*y>0 for x,y in [(du[0],du[1]),(du[0],du[2])]): return False
    if all(x*y>0 for x,y in [(dv[0],dv[1]),(dv[0],dv[2])]): return False
    found = any(edge_edge(*ea,*eb) for ea in [(V[0],V[1]),(V[1],V[2]),(V[2],V[0])] for eb in [(U[0],U[1]),(U[1],U[2]),(U[2],U[0])])
    found |= any(point_in_tri(p, U) for p in V)
    found |= any(point_in_tri(p, V) for p in U)
    if found and not share_vertex_or_edge(V, U): return True
    return False

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
                # print("Triangle 1:", triangles[i])
                # print("Triangle 2:", triangles[j])
                return
    print("true")

if __name__ == "__main__":
    main()