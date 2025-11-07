"""Mesh operations and validation utilities."""

from typing import Tuple, Dict
import numpy as np
import trimesh


def validate_mesh(mesh: trimesh.Trimesh) -> Dict[str, any]:
    """Validate mesh for 3D printing and general quality.
    
    Args:
        mesh: Mesh to validate
        
    Returns:
        Dictionary with validation results
        
    Example:
        >>> mesh = trimesh.load('model.stl')
        >>> results = validate_mesh(mesh)
        >>> if results['is_valid']:
        ...     print("Mesh is ready for printing!")
    """
    results = {
        'is_valid': True,
        'is_watertight': mesh.is_watertight,
        'is_winding_consistent': mesh.is_winding_consistent,
        'num_vertices': len(mesh.vertices),
        'num_faces': len(mesh.faces),
        'volume': mesh.volume if mesh.is_volume else None,
        'surface_area': mesh.area,
        'bounds': mesh.bounds,
        'warnings': [],
        'errors': []
    }
    
    # Check watertight
    if not mesh.is_watertight:
        results['is_valid'] = False
        results['errors'].append("Mesh is not watertight (has holes)")
    
    # Check winding
    if not mesh.is_winding_consistent:
        results['warnings'].append("Face winding is inconsistent")
    
    # Check for degenerate faces
    degenerate = np.isclose(mesh.area_faces, 0).sum()
    if degenerate > 0:
        results['is_valid'] = False
        results['errors'].append(f"Found {degenerate} degenerate faces (zero area)")
        results['degenerate_faces'] = int(degenerate)
    
    # Check for duplicate vertices
    unique_verts = len(np.unique(mesh.vertices, axis=0))
    duplicates = len(mesh.vertices) - unique_verts
    if duplicates > 0:
        results['warnings'].append(f"Found {duplicates} duplicate vertices")
        results['duplicate_vertices'] = int(duplicates)
    
    # Check for self-intersections (expensive, skip for large meshes)
    if len(mesh.faces) < 50000:
        if not mesh.is_volume:
            results['warnings'].append("Mesh may have self-intersections or is not a volume")
    
    # Compute bounding box dimensions
    bounds = mesh.bounds
    size = bounds[1] - bounds[0]
    results['dimensions'] = {
        'x': float(size[0]),
        'y': float(size[1]),
        'z': float(size[2])
    }
    
    return results


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
    from .isosurface import smooth_mesh_laplacian
    return smooth_mesh_laplacian(mesh, iterations, lambda_factor)


def decimate_mesh(
    mesh: trimesh.Trimesh,
    target_faces: int
) -> trimesh.Trimesh:
    """Reduce number of faces in mesh.
    
    Args:
        mesh: Input mesh
        target_faces: Target number of faces
        
    Returns:
        Decimated mesh
    """
    if len(mesh.faces) <= target_faces:
        return mesh
    
    # Use trimesh simplification
    simplified = mesh.simplify_quadric_decimation(target_faces)
    
    return simplified


def repair_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Attempt to repair common mesh issues.
    
    Args:
        mesh: Input mesh
        
    Returns:
        Repaired mesh
    """
    # Remove duplicate vertices
    mesh.merge_vertices()
    
    # Remove degenerate faces
    mesh.remove_degenerate_faces()
    
    # Remove duplicate faces
    mesh.remove_duplicate_faces()
    
    # Fill holes (if applicable)
    if not mesh.is_watertight:
        try:
            mesh.fill_holes()
        except Exception:
            pass  # Hole filling can fail on complex geometry
    
    # Fix normals
    if not mesh.is_winding_consistent:
        mesh.fix_normals()
    
    return mesh


def compute_overhang_analysis(
    mesh: trimesh.Trimesh,
    overhang_angle: float = 45.0
) -> Dict[str, any]:
    """Analyse mesh for 3D printing overhangs.
    
    Args:
        mesh: Mesh to analyse
        overhang_angle: Angle in degrees beyond which support is needed
        
    Returns:
        Dictionary with overhang analysis
    """
    # Compute face normals
    normals = mesh.face_normals
    
    # Check how many faces point downward beyond threshold
    z_component = normals[:, 2]
    threshold = -np.cos(np.deg2rad(overhang_angle))
    
    downward_facing = z_component < threshold
    overhang_percentage = (downward_facing.sum() / len(normals)) * 100
    
    return {
        'overhang_percentage': float(overhang_percentage),
        'num_overhang_faces': int(downward_facing.sum()),
        'total_faces': len(normals),
        'needs_supports': overhang_percentage > 20.0
    }


def slice_mesh_horizontal(
    mesh: trimesh.Trimesh,
    z_height: float
) -> np.ndarray:
    """Slice mesh at a given height and return 2D contour.
    
    Args:
        mesh: Mesh to slice
        z_height: Z height at which to slice
        
    Returns:
        Array of 2D contour points
    """
    # Use trimesh's section method
    section = mesh.section(plane_origin=[0, 0, z_height],
                          plane_normal=[0, 0, 1])
    
    if section is None:
        return np.array([])
    
    # Get 2D coordinates
    coords, _ = section.to_planar()
    
    return coords.vertices

