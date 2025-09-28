import json
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

with open("surface_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]
    faces = data["faces"]

angle_x, angle_y = 0, 0
mouse_x, mouse_y = 0, 0
is_dragging = False
zoom = -10  # initial zoom level

def setup_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)

def centering():
    all_vertices_array = np.array(vertices)
    min_x, min_y, min_z = np.min(all_vertices_array, axis=0)
    max_x, max_y, max_z = np.max(all_vertices_array, axis=0)
    plotcenter = np.array([(min_x + max_x)/2, (min_y + max_y)/2, (min_z + max_z)/2])
    for v, vert in enumerate(vertices):
        vertices[v] = vert - plotcenter
    
def draw_line(v1, v2, width=8.0, color=(0.0, 0.0, 0.0)):
    glColor3fv(color)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex3fv(v1)
    glVertex3fv(v2)
    glEnd()

def draw_vertex(v, size=0.1):
    glPushMatrix()
    glTranslatef(v[0], v[1], v[2])
    glColor3f(1.0, 0.0, 0.0)
    quadric = gluNewQuadric()
    gluSphere(quadric, size, 20, 20)
    gluDeleteQuadric(quadric)
    glPopMatrix()

def draw_triangle(v1, v2, v3, color=(0.5, 0.8, 1.0, 0.5)):
    glColor4fv(color)
    glBegin(GL_TRIANGLES)
    glVertex3fv(v1)
    glVertex3fv(v2)
    glVertex3fv(v3)
    glEnd()
    # Draw triangle edges in white
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    glVertex3fv(v1)
    glVertex3fv(v2)
    glVertex3fv(v2)
    glVertex3fv(v3)
    glVertex3fv(v3)
    glVertex3fv(v1)
    glEnd()

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

def draw_polygon(vlist, color=(0.5, 0.8, 1.0, 0.5)):
    center = np.mean(vlist, axis=0)
    n = len(vlist)
    for i in range(n):
        draw_triangle(center, vlist[i], vlist[(i+1)%n], color)

def draw_band(face, color=(0.8, 0.5, 1.0, 0.5)):
    glColor4fv(color)
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
        draw_polygon([verts_list[i], verts_list[i+1], projected_verts[i+1], projected_verts[i]], color = color)

def draw_face(face, color=(0.5, 0.8, 1.0, 0.5)):
    glColor4fv(color)
    cell = [0, 0, 0]
    verts = []
    for h_idx in face:
        h = halfedges[h_idx]
        v_idx = h[0]
        v = np.array(vertices[v_idx]) + np.dot(cell, periods)
        verts.append(v)
        cell = [c + d for c, d in zip(cell, h[2])]
    verts_list = list(verts)
    # print(verts_list)
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

        # Draw polygons for the two duplicate sublists
        poly1 = verts_list[i1-1:j1+2]
        draw_polygon(poly1, color)
        poly2 = verts_list[i2-1:j2+2]
        draw_polygon(poly2, color)
        # Remove the duplicate sublists (second occurrence first)
        for _ in range(i2, j2+1):
            verts_list.pop(i2 % len(verts_list))
        for _ in range(i1, j1+1):
            verts_list.pop(i1 % len(verts_list))
    # Draw polygon for remaining vertices
    if len(verts_list) > 2:
        draw_polygon(verts_list, color)
    # Draw boundary of the face
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(8.0)
    glBegin(GL_LINE_LOOP)
    for v in verts:
        glVertex3fv(v)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, zoom)
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)

    centering()
    for vv in vertices:
        draw_vertex(vv)
    for face in faces:
        cell = [0, 0, 0]
        for h_idx in face:
            h = halfedges[h_idx]
            cell = [c + d for c, d in zip(cell, h[2])]
        if all(c == 0 for c in cell):
            draw_face(face)
        else:
            draw_band(face)
    # draw_face(faces[0])
    # draw_face(faces[1], color=(1.0, 0.5, 0.5, 0.5))

    glfw.swap_buffers(window)

def init_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30, 800 / float(800), 1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def on_mouse_button(window, button, action, mods):
    global is_dragging, mouse_x, mouse_y
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            is_dragging = True
            mouse_x, mouse_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            is_dragging = False

def on_mouse_move(window, xpos, ypos):
    global angle_x, angle_y, mouse_x, mouse_y
    if is_dragging:
        dx = xpos - mouse_x
        dy = ypos - mouse_y
        angle_x += dy * 0.2
        angle_y += dx * 0.2
        mouse_x, mouse_y = xpos, ypos
        display()

def on_scroll(window, xoffset, yoffset):
    global zoom
    zoom += yoffset  # yoffset is positive for scroll up, negative for scroll down
    display()

def main():
    global window
    if not glfw.init():
        sys.exit(1)

    window = glfw.create_window(800, 800, "3D Surfaces", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, on_mouse_button)
    glfw.set_cursor_pos_callback(window, on_mouse_move)
    glfw.set_scroll_callback(window, on_scroll)
    
    init_gl()

    while not glfw.window_should_close(window):
        display()
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()