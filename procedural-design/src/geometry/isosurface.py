"""Isosurface extraction from scalar fields."""

from typing import Optional, Tuple
import numpy as np
from skimage import measure
import trimesh


def extract_isosurface(
    field: np.ndarray,
    isovalue: float = 0.5,
    spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    smooth: bool = True
) -> trimesh.Trimesh:
    """Extract isosurface from 3D scalar field using marching cubes.
    
    Args:
        field: 3D numpy array of scalar values
        isovalue: Value at which to extract surface
        spacing: Voxel spacing in (z, y, x) order
        smooth: Whether to apply Laplacian smoothing
        
    Returns:
        Extracted mesh
        
    Raises:
        ValueError: If field is not 3D
        
    Example:
        >>> field = np.random.rand(100, 100, 100)
        >>> mesh = extract_isosurface(field, isovalue=0.5)
        >>> mesh.export('surface.stl')
    """
    if field.ndim != 3:
        raise ValueError(f"Field must be 3D, got {field.ndim}D array")
    
    # Use marching cubes to extract surface
    verts, faces, normals, _ = measure.marching_cubes(
        field.astype(np.float32),
        level=isovalue,
        spacing=spacing
    )
    
    # Create mesh
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    
    # Optional smoothing
    if smooth:
        mesh = smooth_mesh_laplacian(mesh, iterations=3)
    
    return mesh


def marching_cubes_field(
    field: np.ndarray,
    threshold: float = 0.5
) -> np.ndarray:
    """Convert continuous field to binary via thresholding.
    
    Args:
        field: Scalar field
        threshold: Threshold value
        
    Returns:
        Binary field (True where field > threshold)
    """
    return field > threshold


def smooth_mesh_laplacian(
    mesh: trimesh.Trimesh,
    iterations: int = 3,
    lambda_factor: float = 0.5
) -> trimesh.Trimesh:
    """Apply Laplacian smoothing to mesh.
    
    Args:
        mesh: Input mesh
        iterations: Number of smoothing iterations
        lambda_factor: Smoothing factor (0-1, higher = more smoothing)
        
    Returns:
        Smoothed mesh
    """
    vertices = mesh.vertices.copy()
    
    for _ in range(iterations):
        # Compute vertex neighbors
        vertex_neighbors = [set() for _ in range(len(vertices))]
        for face in mesh.faces:
            for i in range(3):
                vertex_neighbors[face[i]].update([face[(i+1)%3], face[(i+2)%3]])
        
        # Laplacian smoothing
        new_vertices = vertices.copy()
        for i, neighbors in enumerate(vertex_neighbors):
            if len(neighbors) > 0:
                neighbor_positions = vertices[list(neighbors)]
                laplacian = neighbor_positions.mean(axis=0) - vertices[i]
                new_vertices[i] = vertices[i] + lambda_factor * laplacian
        
        vertices = new_vertices
    
    return trimesh.Trimesh(vertices=vertices, faces=mesh.faces)


def field_from_function(
    bounds: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
    resolution: Tuple[int, int, int],
    func
) -> Tuple[np.ndarray, Tuple[float, float, float]]:
    """Create scalar field by evaluating a function over a grid.
    
    Args:
        bounds: ((xmin, xmax), (ymin, ymax), (zmin, zmax))
        resolution: (nx, ny, nz) grid resolution
        func: Function taking (x, y, z) and returning scalar value
        
    Returns:
        Tuple of (field array, spacing)
        
    Example:
        >>> # Create a sphere
        >>> def sphere(x, y, z):
        ...     return x**2 + y**2 + z**2 - 25
        >>> field, spacing = field_from_function(
        ...     ((-10, 10), (-10, 10), (-10, 10)),
        ...     (50, 50, 50),
        ...     sphere
        ... )
        >>> mesh = extract_isosurface(field, isovalue=0)
    """
    (xmin, xmax), (ymin, ymax), (zmin, zmax) = bounds
    nx, ny, nz = resolution
    
    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    z = np.linspace(zmin, zmax, nz)
    
    spacing = (
        (zmax - zmin) / (nz - 1),
        (ymax - ymin) / (ny - 1),
        (xmax - xmin) / (nx - 1)
    )
    
    # Create grid
    Z, Y, X = np.meshgrid(z, y, x, indexing='ij')
    
    # Evaluate function
    field = func(X, Y, Z)
    
    return field, spacing

