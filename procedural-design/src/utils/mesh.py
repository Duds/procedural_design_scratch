import trimesh
import numpy as np

def create_mesh(vertices, faces):
    """
    Create a 3D mesh from vertices and faces.

    Parameters:
    vertices (np.ndarray): An array of shape (N, 3) containing the vertex coordinates.
    faces (np.ndarray): An array of shape (M, 3) containing the indices of the vertices that form each face.

    Returns:
    trimesh.Trimesh: A Trimesh object representing the 3D mesh.
    """
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def export_mesh(mesh, file_path, file_type='stl'):
    """
    Export the mesh to a specified file format.

    Parameters:
    mesh (trimesh.Trimesh): The mesh to export.
    file_path (str): The path where the mesh will be saved.
    file_type (str): The file format to export to ('stl', 'obj', etc.).

    Raises:
    ValueError: If the file type is not supported.
    """
    if file_type not in ['stl', 'obj', 'ply', '3mf']:
        raise ValueError(f"Unsupported file type: {file_type}")

    mesh.export(file_path, file_type=file_type)