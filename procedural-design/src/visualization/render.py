import trimesh
import numpy as np
import matplotlib.pyplot as plt

def render_mesh(mesh_path, output_path):
    """
    Renders a 3D mesh and saves the visualization as an image.

    Parameters:
    - mesh_path: str, path to the mesh file (e.g., STL, OBJ).
    - output_path: str, path to save the rendered image.
    """
    mesh = trimesh.load(mesh_path)
    scene = mesh.scene()
    scene.show()

    # Save a screenshot of the rendered scene
    plt.savefig(output_path)
    plt.close()

def visualize_pattern(pattern, title='Pattern Visualization'):
    """
    Visualizes a 2D pattern using matplotlib.

    Parameters:
    - pattern: 2D numpy array representing the pattern.
    - title: str, title of the visualization.
    """
    plt.imshow(pattern, cmap='viridis')
    plt.colorbar()
    plt.title(title)
    plt.axis('off')
    plt.show()