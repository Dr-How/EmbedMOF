import sys
import subprocess
import math
import numpy as np
import json

if len(sys.argv) < 2:
    print("Usage: python RotationSystem3D.py <network_name>")
    sys.exit(1)

network_name = sys.argv[1]
command = ["sh", "run_systre.sh", network_name]
result = subprocess.run(command, capture_output=True, text=True)
systre_output = result.stdout

lines = [line.strip() for line in systre_output.splitlines()]
keywords = ["Relaxed cell parameters:", "Barycentric positions:", "Edges:", "Edge centers:"]
# keywords = ["Relaxed cell parameters:", "Relaxed positions:", "Edges:", "Edge centers:"]
key_lines = [i for i, line in enumerate(lines) if any(keyword in line for keyword in keywords)]

#extract systre symbol
str_symbol = lines[2]
split_symbol = str_symbol.split('"')
symbol = split_symbol[1] if len(split_symbol) > 1 else None
print("Symbol:", symbol)

#extract dimension
str_dim = lines[4]
split_dim = str_dim.split()
split_last = split_dim[-1].split("-")
dimension = int(split_last[0])
if dimension != 3:
    raise SystemExit("Aborted: Dimension is not 3.")

#extract basis
str_basis = lines[key_lines[0]+1 : key_lines[0]+3]
str_basis_split = [item for sublist in (s.split(",") for s in str_basis) for item in sublist]
shape = [float(x.split()[-1]) for x in str_basis_split]
shape[3:6] = [np.radians(angle) for angle in shape[3:6]]
angleA = np.arccos((np.cos(shape[3]) - np.cos(shape[4]) * np.cos(shape[5])) /
                   (np.sin(shape[4]) * np.sin(shape[5])))
period3 = [
    np.cos(shape[4]),
    np.sin(shape[4]) * np.cos(angleA),
    np.sin(shape[4]) * np.sin(angleA)
]
periods = np.array([
    [shape[0], 0, 0],
    [shape[1] * np.cos(shape[-1]), shape[1] * np.sin(shape[-1]), 0],
    [shape[2] * period3[0], shape[2] * period3[1], shape[2] * period3[2]]
])
norms = [float(np.linalg.norm(period)) for period in periods]
angle_12 = np.degrees(np.arccos(np.dot(periods[0], periods[1]) / (norms[0] * norms[1])))
angle_23 = np.degrees(np.arccos(np.dot(periods[1], periods[2]) / (norms[1] * norms[2])))
angle_31 = np.degrees(np.arccos(np.dot(periods[2], periods[0]) / (norms[2] * norms[0])))
print("Norms:", norms)
print("Angle between periods 1 and 2 (degrees):", angle_12)
print("Angle between periods 2 and 3 (degrees):", angle_23)
print("Angle between periods 3 and 1 (degrees):", angle_31)

#extract positions
str_vertices = lines[key_lines[1] + 1 : key_lines[2]]
split_vertices = [line.split() for line in str_vertices]
vertices = [list(map(float, vert[2:])) for vert in split_vertices]
for v, vert in enumerate(vertices):
    vertices[v] = [vv if vv < 1.0 else 0.0 for vv in vert]
print("Vertices", vertices)

# compute halfedges and inversions
str_edges = lines[key_lines[2] + 1 : key_lines[3]]
split_edges = [edge.split() for edge in str_edges]
edges = [[list(map(float, edge[:3])), list(map(float, edge[4:7]))] for edge in split_edges]
edges = [[tuple(edge_part) for edge_part in edge] for edge in edges]
for edge in edges:
    print(edge)
halfedges = []
inversions = []

vertices = np.array(vertices)

def find_vertex_index(target, vertices, tol=1e-3):
    for i, v in enumerate(vertices):
        if np.allclose(v, target, atol=tol):
            return i
    return None

print(len(edges))

for e, edge in enumerate(edges):
    try:
        cell1 = [math.floor(x) for x in edge[0]]
        vertex1 = [x - c for x, c in zip(edge[0], cell1)]
        v1 = find_vertex_index(vertex1, vertices)
        cell2 = [math.floor(x) for x in edge[1]]
        vertex2 = [x - c for x, c in zip(edge[1], cell2)]
        v2 = find_vertex_index(vertex2, vertices)
        cell = [c2 - c1 for c2, c1 in zip(cell2, cell1)]
        nonzero = any(c != 0 for c in cell)
        if v1 is None or v2 is None:
            raise ValueError(f"Edge {edge}: vertex not found for {vertex1} or {vertex2}")
        if v1 < v2 or (v1 == v2 and nonzero):
            halfedges.append([v1, v2, cell])
            halfedges.append([v2, v1, [-c for c in cell]])
            inversions.extend([len(halfedges)-1, len(halfedges) - 2])
    except Exception as ex:
        print(ex)
print("Halfedges:", halfedges)
print("Inversions:", inversions)

vertices = np.array(vertices)
periods = np.array(periods)
vertices = np.dot(vertices, periods)
print("Transformed vertices:", vertices)

output_data = {
    "periods": periods.tolist(),
    "vertices": vertices.tolist(),
    "halfedges": halfedges,
    "inversions": inversions,
    "normals": []
}

with open("network_data.json", "w") as f:
    json.dump(output_data, f, indent=2)