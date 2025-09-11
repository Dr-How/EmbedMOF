import json
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

with open("surface_data.json") as f:
    data = json.load(f)
    periods = data["periods"]
    vertices = data["vertices"]
    halfedges = data["halfedges"]
    faces = data["faces"]

for f in faces:
    print(f)

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

def draw_face(face, color=(0.5, 0.8, 1.0, 0.5)):
    glColor4fv(color)
    # Compute the vertices of the face
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
    # Draw triangles from center to each edge
    glBegin(GL_TRIANGLES)
    n = len(verts)
    for i in range(n):
        glVertex3fv(center)
        glVertex3fv(verts[i])
        glVertex3fv(verts[(i+1)%n])
    glEnd()
    # Draw triangle edges
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(n):
        glVertex3fv(verts[(i+1)%n])
        glVertex3fv(center)
        glVertex3fv(verts[i])
        glVertex3fv(center)
    glEnd()
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(n):
        glVertex3fv(verts[(i+1)%n])
        glVertex3fv(verts[i])
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
    for ff in faces:
        draw_face(ff)

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

    window = glfw.create_window(800, 800, "2D Networks", None, None)
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