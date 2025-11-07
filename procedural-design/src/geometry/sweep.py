"""Path sweeping operations for creating tubular meshes."""

from typing import List, Tuple, Optional
import numpy as np
from scipy.spatial.transform import Rotation
import trimesh


def sweep_circle_along_path(
    path: np.ndarray,
    radius: float,
    n_sides: int = 16,
    closed: bool = False
) -> trimesh.Trimesh:
    """Sweep a circular cross-section along a 3D path.
    
    Creates a tubular mesh by sweeping a circle along the given path
    using parallel transport frames.
    
    Args:
        path: Nx3 array of 3D points defining the path
        radius: Radius of circular cross-section
        n_sides: Number of sides in circle (more = smoother)
        closed: Whether to close the tube ends
        
    Returns:
        Tubular mesh
        
    Example:
        >>> # Create a helical tube
        >>> t = np.linspace(0, 4*np.pi, 100)
        >>> path = np.column_stack([
        ...     10*np.cos(t),
        ...     10*np.sin(t),
        ...     t
        ... ])
        >>> tube = sweep_circle_along_path(path, radius=2.0)
    """
    if len(path) < 2:
        raise ValueError("Path must have at least 2 points")
    
    # Generate frames using parallel transport
    frames = compute_parallel_transport_frames(path)
    
    # Generate circle profile
    theta = np.linspace(0, 2*np.pi, n_sides, endpoint=False)
    circle = np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])
    
    # Sweep circle along path
    vertices = []
    for i, (centre, frame) in enumerate(zip(path, frames)):
        # Transform circle to frame
        for x, y in circle:
            point = centre + x * frame['normal'] + y * frame['binormal']
            vertices.append(point)
    
    vertices = np.array(vertices)
    
    # Generate faces between consecutive rings
    faces = []
    for i in range(len(path) - 1):
        for j in range(n_sides):
            j1 = (j + 1) % n_sides
            v0 = i * n_sides + j
            v1 = i * n_sides + j1
            v2 = (i + 1) * n_sides + j1
            v3 = (i + 1) * n_sides + j
            faces.extend([[v0, v1, v2], [v2, v3, v0]])
    
    # Optional end caps
    if closed and len(path) > 2:
        # Add centre vertices for caps
        start_centre = len(vertices)
        vertices = np.vstack([vertices, [path[0]]])
        end_centre = len(vertices)
        vertices = np.vstack([vertices, [path[-1]]])
        
        # Start cap
        for j in range(n_sides):
            j1 = (j + 1) % n_sides
            faces.append([start_centre, j1, j])
        
        # End cap
        last_ring_start = (len(path) - 1) * n_sides
        for j in range(n_sides):
            j1 = (j + 1) % n_sides
            faces.append([end_centre, last_ring_start + j, last_ring_start + j1])
    
    return trimesh.Trimesh(vertices=vertices, faces=np.array(faces))


def sweep_profile_along_path(
    path: np.ndarray,
    profile: np.ndarray,
    closed_profile: bool = True,
    closed_path: bool = False
) -> trimesh.Trimesh:
    """Sweep an arbitrary 2D profile along a 3D path.
    
    Args:
        path: Nx3 array of 3D path points
        profile: Mx2 array of 2D profile points (x, y)
        closed_profile: Whether profile forms a closed loop
        closed_path: Whether path forms a closed loop
        
    Returns:
        Swept mesh
    """
    if len(path) < 2:
        raise ValueError("Path must have at least 2 points")
    if len(profile) < 3:
        raise ValueError("Profile must have at least 3 points")
    
    # Compute frames
    frames = compute_parallel_transport_frames(path)
    
    # Sweep profile along path
    vertices = []
    for centre, frame in zip(path, frames):
        # Transform each profile point to 3D
        for x, y in profile:
            point = centre + x * frame['normal'] + y * frame['binormal']
            vertices.append(point)
    
    vertices = np.array(vertices)
    
    # Generate faces
    faces = []
    n_profile = len(profile)
    n_path = len(path)
    
    path_segments = n_path - 1 if not closed_path else n_path
    profile_segments = n_profile - 1 if not closed_profile else n_profile
    
    for i in range(path_segments):
        for j in range(profile_segments):
            j1 = (j + 1) % n_profile
            i1 = (i + 1) % n_path
            
            v0 = i * n_profile + j
            v1 = i * n_profile + j1
            v2 = i1 * n_profile + j1
            v3 = i1 * n_profile + j
            
            faces.extend([[v0, v1, v2], [v2, v3, v0]])
    
    return trimesh.Trimesh(vertices=vertices, faces=np.array(faces))


def compute_parallel_transport_frames(
    path: np.ndarray
) -> List[Dict[str, np.ndarray]]:
    """Compute parallel transport frames along a curve.
    
    Uses rotation minimising frames to avoid twisting.
    
    Args:
        path: Nx3 array of 3D points
        
    Returns:
        List of frames, each a dict with 'tangent', 'normal', 'binormal'
    """
    if len(path) < 2:
        raise ValueError("Path must have at least 2 points")
    
    frames = []
    
    # Initial frame
    t = path[1] - path[0]
    t = t / np.linalg.norm(t)
    
    # Choose initial normal (avoid parallel to tangent)
    if abs(np.dot(t, [0, 0, 1])) > 0.999:
        n = np.array([1.0, 0.0, 0.0])
    else:
        n = np.cross([0, 0, 1], t)
        n = n / np.linalg.norm(n)
    
    b = np.cross(t, n)
    b = b / np.linalg.norm(b)
    
    frames.append({'tangent': t, 'normal': n, 'binormal': b})
    
    # Transport frame along curve
    for i in range(1, len(path)):
        # Compute new tangent
        if i < len(path) - 1:
            t_new = path[i + 1] - path[i]
        else:
            t_new = t  # Keep previous tangent at end
        
        t_new = t_new / (np.linalg.norm(t_new) + 1e-10)
        
        # Rotate previous frame to new tangent
        angle = np.arccos(np.clip(np.dot(t, t_new), -1.0, 1.0))
        
        if angle > 1e-6:
            axis = np.cross(t, t_new)
            axis_norm = np.linalg.norm(axis)
            
            if axis_norm > 1e-6:
                axis = axis / axis_norm
                R = Rotation.from_rotvec(angle * axis)
                n = R.apply(n)
                b = R.apply(b)
        
        # Ensure orthonormality
        b = np.cross(t_new, n)
        b = b / (np.linalg.norm(b) + 1e-10)
        n = np.cross(b, t_new)
        n = n / (np.linalg.norm(n) + 1e-10)
        
        frames.append({'tangent': t_new, 'normal': n, 'binormal': b})
        t = t_new
    
    return frames


def create_tube_from_polyline(
    points: List[np.ndarray],
    radius: float,
    n_sides: int = 16
) -> trimesh.Trimesh:
    """Create tube from a list of 3D points.
    
    Convenience wrapper around sweep_circle_along_path.
    
    Args:
        points: List of [x, y, z] points or Nx3 array
        radius: Tube radius
        n_sides: Number of sides
        
    Returns:
        Tubular mesh
    """
    path = np.array(points)
    return sweep_circle_along_path(path, radius, n_sides, closed=False)

