import json
import numpy as np

with open("network_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]

coplanar = True
tol = 1e-3  # tolerance for numerical errors
for v in range(len(vertices)):
    neighbors = []
    v1 = vertices[v]
    for h in halfedges:
        if h[0] == v:
            v2 = np.array(vertices[h[1]]) + np.dot(h[-1], periods)
            edge_vector = np.array(v2) - np.array(v1)
            neighbors.append(edge_vector)
    neighbors = np.array(neighbors)
    if len(neighbors) <= 3:
        continue
    else:
        _, s, _ = np.linalg.svd(neighbors)
        if s[-1] > tol:
            coplanar = False
            print(v, neighbors, s)
            break

print("true" if coplanar else "false")