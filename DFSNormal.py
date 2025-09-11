import json
from unittest import result
import numpy as np
import sys

sys.setrecursionlimit(10000)

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

visited = [False] * len(vertices)

success = True

def dfs(v):
    visited[v] = True
    v_normal = normals[v]
    for u, _ in adj[v]:
        u_normal = normals[u]
        dot = np.dot(v_normal, u_normal)
        if dot <= 0:
            if visited[u]:
                success = False
                return
            normals[u] = -u_normal
        if not visited[u]:
            dfs(u)

dfs(0)

if success:
    print("true")
    # Save new normals to network_data.json
    data["normals"] = [normal.tolist() for normal in normals]
    with open("network_data.json", "w") as f:
        json.dump(data, f)
else:
    print("false")

