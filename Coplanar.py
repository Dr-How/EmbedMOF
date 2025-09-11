import json
import numpy as np

with open("network_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]


adj = [[] for _ in range(len(vertices))]
for h in halfedges:
    adj[h[0]].append((h[1], h[-1]))

coplanar = True
tol = 1e-3  # tolerance for numerical errors
for v in range(len(vertices)):
    neighbors = []
    v1 = vertices[v]
    for u, cell in adj[v]:
        v2 = np.array(vertices[u]) + np.dot(cell, periods)
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