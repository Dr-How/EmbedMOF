import json
import numpy as np
import sys

network_name = sys.argv[1]
modelfile = f"models/{network_name}.stl"

if len(sys.argv) < 2:
    print("Usage: python RotationSystem3D.py <network_name>")
    sys.exit(1)

with open("surface_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]
    faces = data["faces"]

triangles = []
for face in faces:
    cell = [0, 0, 0]
    verts = []
    for h_idx in face:
        h = halfedges[h_idx]
        v_idx = h[0]
        v = np.array(vertices[v_idx]) + np.dot(cell, periods)
        verts.append(v)
        cell = [c + d for c, d in zip(cell, h[2])]
    verts = np.array(verts)
    center = np.mean(verts, axis=0)
    n = len(verts)
    for i in range(n):
        triangles.append([center, verts[i], verts[(i+1)%n]])

def write_stl(triangles, filename):
    with open(filename, "w") as f:
        f.write("solid surface_model\n")
        for tri in triangles:
            v1, v2, v3 = tri
            normal = np.cross(v2-v1, v3-v1)
            if np.linalg.norm(normal) > 0:
                normal = normal / np.linalg.norm(normal)
            else:
                normal = np.array([0.0, 0.0, 0.0])
            f.write(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n")
            f.write("    outer loop\n")
            for v in [v1, v2, v3]:
                f.write(f"      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid surface_model\n")

write_stl(triangles, modelfile)
print("STL file written: surface_model.stl")
