import sys
import numpy as np
eps = 1e-3

def read_stl(filename):
    triangles, verts = [], []
    for line in open(filename):
        if line.strip().startswith('vertex'):
            verts.append([float(x) for x in line.strip().split()[1:]])
            if len(verts) == 3:
                triangles.append(np.array(verts))
                verts = []
    return triangles

def tri_tri_intersect(tri1, tri2):
    """
    Check if two triangles have intersecting interiors (excluding shared edges/vertices).
    Returns True if triangles intersect in their interiors, False otherwise.
    """
    def bounding_boxes_intersect(t1, t2):
        """Quick bounding box intersection test"""
        # Get min/max for each triangle
        min1 = np.min(t1, axis=0)
        max1 = np.max(t1, axis=0)
        min2 = np.min(t2, axis=0)
        max2 = np.max(t2, axis=0)
        
        # Check if bounding boxes overlap in all 3 dimensions
        return (max1[0] >= min2[0] and min1[0] <= max2[0] and
                max1[1] >= min2[1] and min1[1] <= max2[1] and
                max1[2] >= min2[2] and min1[2] <= max2[2])
    
    # Quick bounding box test - early exit if no overlap
    if not bounding_boxes_intersect(tri1, tri2):
        return False
    
    def triangles_share_vertex(t1, t2):
        """Check if triangles share any vertices"""
        for v1 in t1:
            for v2 in t2:
                if np.linalg.norm(v1 - v2) < eps:
                    return True
        return False
    
    def triangles_share_edge(t1, t2):
        """Check if triangles share an edge"""
        edges1 = [(t1[i], t1[(i+1)%3]) for i in range(3)]
        edges2 = [(t2[i], t2[(i+1)%3]) for i in range(3)]
        
        for e1 in edges1:
            for e2 in edges2:
                # Check if edges are the same (in either direction)
                if ((np.linalg.norm(e1[0] - e2[0]) < eps and np.linalg.norm(e1[1] - e2[1]) < eps) or
                    (np.linalg.norm(e1[0] - e2[1]) < eps and np.linalg.norm(e1[1] - e2[0]) < eps)):
                    return True
        return False
    
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    def point_in_triangle_2d(pt, v0, v1, v2):
        d1 = sign(pt, v0, v1)
        d2 = sign(pt, v1, v2)
        d3 = sign(pt, v2, v0)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def point_in_triangle_interior_2d(pt, v0, v1, v2):
        """Check if point is strictly inside triangle (not on boundary)"""
        d1 = sign(pt, v0, v1)
        d2 = sign(pt, v1, v2)
        d3 = sign(pt, v2, v0)
        
        # All signs must be same and non-zero for strict interior
        return (d1 > eps and d2 > eps and d3 > eps) or (d1 < -eps and d2 < -eps and d3 < -eps)
    
    def get_plane_equation(triangle):
        v0, v1, v2 = triangle
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        if np.linalg.norm(normal) < eps:
            return None
        normal = normal / np.linalg.norm(normal)
        d = -np.dot(normal, v0)
        return normal, d
    
    def line_plane_intersect(line_start, line_dir, plane_normal, plane_d):
        denom = np.dot(plane_normal, line_dir)
        if abs(denom) < eps:
            return None  # Line parallel to plane
        t = -(np.dot(plane_normal, line_start) + plane_d) / denom
        return line_start + t * line_dir, t
    
    def point_in_triangle_interior_3d(point, triangle):
        """Check if point is strictly inside triangle interior"""
        v0, v1, v2 = triangle
        # Project to 2D by finding the dominant axis of the normal
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        abs_normal = np.abs(normal)
        
        # Choose projection plane based on largest normal component
        if abs_normal[0] >= abs_normal[1] and abs_normal[0] >= abs_normal[2]:
            # Project to yz plane
            pt_2d = point[[1, 2]]
            v0_2d = v0[[1, 2]]
            v1_2d = v1[[1, 2]]
            v2_2d = v2[[1, 2]]
        elif abs_normal[1] >= abs_normal[2]:
            # Project to xz plane
            pt_2d = point[[0, 2]]
            v0_2d = v0[[0, 2]]
            v1_2d = v1[[0, 2]]
            v2_2d = v2[[0, 2]]
        else:
            # Project to xy plane
            pt_2d = point[[0, 1]]
            v0_2d = v0[[0, 1]]
            v1_2d = v1[[0, 1]]
            v2_2d = v2[[0, 1]]
        
        return point_in_triangle_interior_2d(pt_2d, v0_2d, v1_2d, v2_2d)
    
    def coplanar_triangles_overlap(t1, t2, normal):
        """Check if two coplanar triangles overlap (excluding identical triangles)"""
        # First check if triangles are identical
        vertices_match = 0
        for v1 in t1:
            for v2 in t2:
                if np.linalg.norm(v1 - v2) < eps:
                    vertices_match += 1
                    break
        if vertices_match == 3:
            return False  # Identical triangles, not intersecting
        
        # Project both triangles to 2D for overlap test
        abs_normal = np.abs(normal)
        if abs_normal[0] >= abs_normal[1] and abs_normal[0] >= abs_normal[2]:
            # Project to yz plane
            t1_2d = t1[:, [1, 2]]
            t2_2d = t2[:, [1, 2]]
        elif abs_normal[1] >= abs_normal[2]:
            # Project to xz plane
            t1_2d = t1[:, [0, 2]]
            t2_2d = t2[:, [0, 2]]
        else:
            # Project to xy plane
            t1_2d = t1[:, [0, 1]]
            t2_2d = t2[:, [0, 1]]
        
        # Check if any vertex of t1 is inside t2 or vice versa
        for vertex in t1_2d:
            if point_in_triangle_interior_2d(vertex, t2_2d[0], t2_2d[1], t2_2d[2]):
                return True
        
        for vertex in t2_2d:
            if point_in_triangle_interior_2d(vertex, t1_2d[0], t1_2d[1], t1_2d[2]):
                return True
        
        # Check edge-edge intersections in 2D
        def line_segments_intersect_2d(p1, q1, p2, q2):
            """Check if two 2D line segments intersect"""
            def on_segment(p, q, r):
                return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                        q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
            
            def orientation(p, q, r):
                val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
                if abs(val) < eps:
                    return 0  # collinear
                return 1 if val > 0 else 2  # clockwise or counterclockwise
            
            o1 = orientation(p1, q1, p2)
            o2 = orientation(p1, q1, q2)
            o3 = orientation(p2, q2, p1)
            o4 = orientation(p2, q2, q1)
            
            # General case
            if o1 != o2 and o3 != o4:
                return True
            
            # Special cases for collinear points
            if (o1 == 0 and on_segment(p1, p2, q1)) or \
               (o2 == 0 and on_segment(p1, q2, q1)) or \
               (o3 == 0 and on_segment(p2, p1, q2)) or \
               (o4 == 0 and on_segment(p2, q1, q2)):
                return True
            
            return False
        
        # Check all edge pairs for intersection
        for i in range(3):
            edge1 = (t1_2d[i], t1_2d[(i+1)%3])
            for j in range(3):
                edge2 = (t2_2d[j], t2_2d[(j+1)%3])
                if line_segments_intersect_2d(edge1[0], edge1[1], edge2[0], edge2[1]):
                    return True
        
        return False
    
    # Early exit: if triangles share vertices or edges, they don't have intersecting interiors
    if triangles_share_vertex(tri1, tri2) or triangles_share_edge(tri1, tri2):
        return False
    
    # Get plane equations for both triangles
    plane1 = get_plane_equation(tri1)
    plane2 = get_plane_equation(tri2)
    
    if plane1 is None or plane2 is None:
        return False  # Degenerate triangle
    
    normal1, d1 = plane1
    normal2, d2 = plane2
    
    # Check if triangles are coplanar
    if abs(np.dot(normal1, normal2)) > 1 - eps:
        # Check if they're actually on the same plane
        dist_to_plane2 = abs(np.dot(normal2, tri1[0]) + d2)
        if dist_to_plane2 < eps:
            # Coplanar - check for overlap
            return coplanar_triangles_overlap(tri1, tri2, normal1)
        else:
            return False  # Parallel but different planes
    
    # Check each edge of tri1 against tri2's plane for interior intersections
    for i in range(3):
        v1 = tri1[i]
        v2 = tri1[(i + 1) % 3]
        edge_dir = v2 - v1
        
        # Find intersection with tri2's plane
        intersection = line_plane_intersect(v1, edge_dir, normal2, d2)
        if intersection is not None:
            point, t = intersection
            # Check if intersection point is strictly inside the edge (not at endpoints)
            if eps < t < 1 - eps:
                # Check if intersection point is in tri2's interior
                if point_in_triangle_interior_3d(point, tri2):
                    return True
    
    # Check each edge of tri2 against tri1's plane for interior intersections
    for i in range(3):
        v1 = tri2[i]
        v2 = tri2[(i + 1) % 3]
        edge_dir = v2 - v1
        
        # Find intersection with tri1's plane
        intersection = line_plane_intersect(v1, edge_dir, normal1, d1)
        if intersection is not None:
            point, t = intersection
            # Check if intersection point is strictly inside the edge (not at endpoints)
            if eps < t < 1 - eps:
                # Check if intersection point is in tri1's interior
                if point_in_triangle_interior_3d(point, tri1):
                    return True
    
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
                print("Triangle 1:", triangles[i])
                print("Triangle 2:", triangles[j])
                return
    print("true")

if __name__ == "__main__":
    main()