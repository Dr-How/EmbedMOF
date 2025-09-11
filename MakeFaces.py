import json
import numpy as np

with open("network_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]
    inversions = data["inversions"]
    normals = data["normals"]

adj = [[] for _ in range(len(vertices))]
for h_idx, h in enumerate(halfedges):
    adj[h[0]].append(h_idx)

def angle(vec, normal, ref_dir):
    proj = vec - np.dot(vec, normal) * normal / np.linalg.norm(normal)**2
    proj = proj / np.linalg.norm(proj)
    ang = np.arctan2(np.dot(np.cross(ref_dir, proj), normal), np.dot(ref_dir, proj))
    return ang

rotations = [None] * len(halfedges)
for v in range(len(vertices)):
    neighbors = []
    halfedge_indices = []
    v1 = vertices[v]
    for h_idx in adj[v]:
        h = halfedges[h_idx]
        u, cell = h[1], h[-1]
        v2 = np.array(vertices[u]) + np.dot(cell, periods)
        edge_vector = np.array(v2) - np.array(v1)
        neighbors.append(edge_vector)
        halfedge_indices.append(h_idx)
    neighbors = np.array(neighbors)
    normal = np.array(normals[v])
    ref_dir = neighbors[0] - np.dot(neighbors[0], normal) * normal / np.linalg.norm(normal)**2
    ref_dir = ref_dir / np.linalg.norm(ref_dir)
    order = sorted(range(len(neighbors)), key=lambda i: angle(neighbors[i], normal, ref_dir))
    for i in range(len(order)):
        h_idx = halfedge_indices[order[i]]
        next_h_idx = halfedge_indices[order[(i+1)%len(order)]]
        rotations[h_idx] = next_h_idx
    
# Construct faces
visited = [False] * len(halfedges)
faces = []
for h_start in range(len(halfedges)):
    if not visited[h_start]:
        f = [h_start]
        cell = [0, 0, 0]
        while True:
            h = f[-1]
            if all(c == 0 for c in cell):
                visited[h] = True
            next_h = rotations[inversions[h]]
            if next_h == f[0]:
                break
            f.append(next_h)
            cell = [c + dc for c, dc in zip(cell, halfedges[h][2])]
        faces.append(f)

trivial_faces = True

for f in faces:
    cell = [0, 0, 0]
    for h_idx in f:
        cell = [c + dc for c, dc in zip(cell, halfedges[h_idx][2])]
    if any(c != 0 for c in cell):
        trivial_faces = False
        break

if trivial_faces:
    data.pop("normals", None)
    data["faces"] = faces
    with open("surface_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("true")
else:
    print("false")