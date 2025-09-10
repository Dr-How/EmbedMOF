import json
import numpy as np

with open("network_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]

orthogonal = False
tol = 1e-3  # tolerance for numerical errors
normals = []
for v in range(len(vertices)):
    neighbors = []
    v1 = vertices[v]
    for h in halfedges:
        if h[0] == v:
            v2 = np.array(vertices[h[1]]) + np.dot(h[-1], periods)
            edge_vector = np.array(v2) - np.array(v1)
            neighbors.append(edge_vector)
    neighbors = np.array(neighbors)

    _, _, vh = np.linalg.svd(neighbors)
    normal = vh[-1]
    normal = normal / np.linalg.norm(normal)
    normals.append(normal)

for h in range(len(halfedges)):
    v1 = halfedges[h][0]
    n1 = normals[v1]
    v2 = halfedges[h][1]
    n2 = normals[v2]
    dot_product = np.dot(n1, n2)
    if np.isclose(dot_product, 0, atol=tol):
        print(f"for halfedge {h} are orthogonal: {n1}, {n2}, {dot_product}")
        orthogonal = True
        break

print("true" if orthogonal else "false")