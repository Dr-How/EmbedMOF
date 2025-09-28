import json
import numpy as np
import sys

if len(sys.argv) < 2:
    print("Usage: python ExportSTL.py <network_name>")
    sys.exit(1)

network_name = sys.argv[1]
modelfile = f"models/{network_name}.stl"

with open("surface_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]
    faces = data["faces"]

def find_dup(verts, tol=1e-6):
    n = len(verts)
    for length in range(2, n//2+1):
        for i in range(n):
            sub = [verts[(i+k)%n] for k in range(length)]
            for j in range(n):
                if j == i:
                    continue
                match = True
                for k in range(length):
                    if not np.allclose(verts[(j+k)%n], sub[-(k+1)], atol=tol):
                        match = False
                        break
                if match:
                    i1 = i
                    j1 = (i+length-1)%n
                    i2 = j
                    j2 = (j+length-1)%n
                    return i1, j1, i2, j2
    return None

triangles = []

def draw_polygon(vlist):
    center = np.mean(vlist, axis=0)
    n = len(vlist)
    for i in range(n):
        triangles.append([center, vlist[i], vlist[(i+1)%n]])

def draw_band(face):
    cell = [0, 0, 0]
    verts = []
    for h_idx in face:
        h = halfedges[h_idx]
        v_idx = h[0]
        v = np.array(vertices[v_idx]) + np.dot(cell, periods)
        verts.append(v)
        cell = [c + d for c, d in zip(cell, h[2])]
    verts_list = list(verts)
    dir = np.dot(cell, periods)
    dir = np.array(dir)
    dir = dir / np.linalg.norm(dir)
    # Project all verts_list onto the line through the center with direction dir
    center = np.mean(verts_list, axis=0)
    projected_verts = []
    for i, v in enumerate(verts_list):
        v = np.array(v)
        t = np.dot(v - center, dir)
        projected_verts.append(center + t * dir)
    for i in range(len(verts_list)-1):
        draw_polygon([verts_list[i], verts_list[i+1], projected_verts[i+1], projected_verts[i]])

def draw_face(face):
    cell = [0, 0, 0]
    verts = []
    for h_idx in face:
        h = halfedges[h_idx]
        v_idx = h[0]
        v = np.array(vertices[v_idx]) + np.dot(cell, periods)
        verts.append(v)
        cell = [c + d for c, d in zip(cell, h[2])]
    verts_list = list(verts)
    while True:
        dup = find_dup(verts_list)
        if not dup:
            break
        i1, j1, i2, j2 = dup
        n = len(verts_list)
        # Rotate verts_list so that i1 == 1
        shift = (i1 - 1) % n
        verts_list = verts_list[shift:] + verts_list[:shift]
        # Update indices after rotation
        i1 = 1
        j1 = (j1 - shift) % n
        i2 = (i2 - shift) % n
        j2 = (j2 - shift) % n
        # Ensure i1 < j1 < i2 < j2
        if i2 < j1:
            i1, j1, i2, j2 = i2, j2, i1, j1
        # Triangulate polygons for the two duplicate sublists
        poly1 = [verts_list[(k)%len(verts_list)] for k in range(i1-1, j1+2)]
        draw_polygon(poly1)
        poly2 = [verts_list[(k)%len(verts_list)] for k in range(i2-1, j2+2)]
        draw_polygon(poly2)
        # Remove the duplicate sublists (second occurrence first)
        for _ in range(i2, j2+1):
            verts_list.pop(i2 % len(verts_list))
        for _ in range(i1, j1+1):
            verts_list.pop(i1 % len(verts_list))
    # Triangulate polygon for remaining vertices
    if len(verts_list) > 2:
        draw_polygon(verts_list)

for face in faces:
    cell = [0, 0, 0]
    for h_idx in face:
        h = halfedges[h_idx]
        cell = [c + d for c, d in zip(cell, h[2])]
    if all(c == 0 for c in cell):
        draw_face(face)
    else:
        draw_band(face)

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
