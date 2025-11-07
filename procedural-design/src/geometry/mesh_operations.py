"""Mesh operations for procedural generation."""

from typing import Optional, Tuple, Dict
import numpy as np
import trimesh
from skimage import measure


def extract_isosurface(
    field: np.ndarray,
    isovalue: float = 0.5,
    spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    smooth: bool = True,
    smooth_iterations: int = 3
) -> trimesh.Trimesh:
    """Extract isosurface from 3D scalar field using marching cubes.
    
    Args:
        field: 3D scalar field
        isovalue: Isosurface threshold value
        spacing: Voxel spacing in (x, y, z)
        smooth: Apply Laplacian smoothing
        smooth_iterations: Number of smoothing iterations
        
    Returns:
        Extracted mesh
        
    Raises:
        ValueError: If field is not 3D
    """
    if field.ndim != 3:
        raise ValueError(f"Field must be 3D, got shape {field.shape}")
    
    # Extract surface using marching cubes
    vertices, faces, normals, values = measure.marching_cubes(
        field,
        level=isovalue,
        spacing=spacing
    )
    
    # Create mesh
    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        vertex_normals=normals,
        process=True
    )
    
    # Optional smoothing
    if smooth:
        mesh = smooth_mesh(mesh, iterations=smooth_iterations)
    
    return mesh


def apply_displacement(
    mesh: trimesh.Trimesh,
    displacement_field: np.ndarray,
    amplitude: float = 1.0,
    along_normal: bool = True
) -> trimesh.Trimesh:
    """Apply displacement to mesh vertices.
    
    Args:
        mesh: Input mesh
        displacement_field: Displacement values (one per vertex or interpolated)
        amplitude: Displacement amplitude scaling
        along_normal: Displace along vertex normals (vs. displacement vectors)
        
    Returns:
        Displaced mesh
        
    Raises:
        ValueError: If displacement_field shape doesn't match vertices
    """
    mesh_copy = mesh.copy()
    
    if along_normal:
        # Displace along normals
        if displacement_field.shape[0] != len(mesh.vertices):
            raise ValueError(
                f"Displacement field length {displacement_field.shape[0]} "
                f"doesn't match vertex count {len(mesh.vertices)}"
            )
        
        displacement = mesh.vertex_normals * displacement_field[:, np.newaxis]
        mesh_copy.vertices += amplitude * displacement
    else:
        # Direct displacement vectors
        if displacement_field.shape != mesh.vertices.shape:
            raise ValueError(
                f"Displacement field shape {displacement_field.shape} "
                f"doesn't match vertices shape {mesh.vertices.shape}"
            )
        
        mesh_copy.vertices += amplitude * displacement_field
    
    return mesh_copy


def smooth_mesh(
    mesh: trimesh.Trimesh,
    iterations: int = 3,
    lambda_factor: float = 0.5
) -> trimesh.Trimesh:
    """Apply Laplacian smoothing to mesh.
    
    Args:
        mesh: Input mesh
        iterations: Number of smoothing iterations
        lambda_factor: Smoothing strength (0-1)
        
    Returns:
        Smoothed mesh
    """
    mesh_copy = mesh.copy()
    
    for _ in range(iterations):
        # Compute vertex neighbors
        vertex_neighbors = mesh_copy.vertex_neighbors
        
        # Laplacian smoothing
        new_vertices = mesh_copy.vertices.copy()
        for i, neighbors in enumerate(vertex_neighbors):
            if len(neighbors) > 0:
                neighbor_mean = mesh_copy.vertices[neighbors].mean(axis=0)
                new_vertices[i] = (
                    (1 - lambda_factor) * mesh_copy.vertices[i] +
                    lambda_factor * neighbor_mean
                )
        
        mesh_copy.vertices = new_vertices
    
    return mesh_copy


def validate_mesh(mesh: trimesh.Trimesh) -> Dict[str, bool]:
    """Validate mesh for 3D printing and quality.
    
    Args:
        mesh: Mesh to validate
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'is_watertight': mesh.is_watertight,
        'is_winding_consistent': mesh.is_winding_consistent,
        'has_degenerate_faces': False,
        'has_duplicate_vertices': False,
        'is_volume': mesh.is_volume,
    }
    
    # Check for degenerate faces
    if hasattr(mesh, 'area_faces'):
        results['has_degenerate_faces'] = np.isclose(mesh.area_faces, 0).any()
    
    # Check for duplicate vertices
    unique_verts = np.unique(mesh.vertices, axis=0)
    results['has_duplicate_vertices'] = len(unique_verts) < len(mesh.vertices)
    
    # Overall validity
    results['is_valid'] = (
        results['is_watertight'] and
        results['is_winding_consistent'] and
        not results['has_degenerate_faces']
    )
    
    return results


def create_field_from_pattern(
    pattern_2d: np.ndarray,
    height_samples: int,
    extrude_height: float = 1.0
) -> np.ndarray:
    """Create 3D field by extruding 2D pattern.
    
    Args:
        pattern_2d: 2D pattern array
        height_samples: Number of samples in height dimension
        extrude_height: Physical height of extrusion
        
    Returns:
        3D field array
    """
    h, w = pattern_2d.shape
    field_3d = np.zeros((h, w, height_samples), dtype=pattern_2d.dtype)
    
    # Simple extrusion
    for i in range(height_samples):
        field_3d[:, :, i] = pattern_2d
    
    return field_3d


def remesh_uniform(
    mesh: trimesh.Trimesh,
    target_edge_length: Optional[float] = None,
    target_faces: Optional[int] = None
) -> trimesh.Trimesh:
    """Remesh to uniform edge length or target face count.
    
    Args:
        mesh: Input mesh
        target_edge_length: Desired edge length
        target_faces: Desired number of faces
        
    Returns:
        Remeshed mesh
        
    Note:
        Uses trimesh's subdivision/decimation. For advanced remeshing,
        consider using PyMeshLab or other external tools.
    """
    mesh_copy = mesh.copy()
    
    if target_faces:
        # Decimate or subdivide to reach target
        current_faces = len(mesh_copy.faces)
        
        if current_faces > target_faces:
            # Decimate
            ratio = target_faces / current_faces
            mesh_copy = mesh_copy.simplify_quadric_decimation(target_faces)
        else:
            # Subdivide
            while len(mesh_copy.faces) < target_faces:
                mesh_copy = mesh_copy.subdivide()
                if len(mesh_copy.faces) > target_faces * 1.5:
                    # Overshoot, decimate back
                    mesh_copy = mesh_copy.simplify_quadric_decimation(target_faces)
                    break
    
    return mesh_copy

