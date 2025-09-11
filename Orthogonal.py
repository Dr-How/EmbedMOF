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

normals = []
for v in range(len(vertices)):
    neighbors = []
    v1 = vertices[v]
    for u, cell in adj[v]:
        v2 = np.array(vertices[u]) + np.dot(cell, periods)
        edge_vector = np.array(v2) - np.array(v1)
        neighbors.append(edge_vector)
    neighbors = np.array(neighbors)

    _, _, vh = np.linalg.svd(neighbors)
    normal = vh[-1]
    normal = normal / np.linalg.norm(normal)
    normals.append(normal)

orthogonal = False
tol = 1e-3  # tolerance for numerical errors

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