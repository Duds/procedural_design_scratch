"""Tube sweeping operations for creating tubular meshes along paths."""

from typing import Optional, List
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation


def create_profile(
    radius: float = 1.0,
    sides: int = 16,
    shape: str = 'circle'
) -> np.ndarray:
    """Create a 2D profile for tube sweeping.
    
    Args:
        radius: Profile radius
        sides: Number of sides
        shape: Profile shape ('circle', 'square', 'hexagon')
        
    Returns:
        Array of shape (sides, 2) with profile points
    """
    if shape == 'circle':
        theta = np.linspace(0, 2 * np.pi, sides, endpoint=False)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        return np.column_stack([x, y])
    
    elif shape == 'square':
        # Create square profile
        side_len = radius * 2
        points_per_side = sides // 4
        points = []
        
        # Bottom
        x = np.linspace(-radius, radius, points_per_side)
        y = np.full_like(x, -radius)
        points.append(np.column_stack([x, y]))
        
        # Right
        y = np.linspace(-radius, radius, points_per_side)
        x = np.full_like(y, radius)
        points.append(np.column_stack([x, y]))
        
        # Top
        x = np.linspace(radius, -radius, points_per_side)
        y = np.full_like(x, radius)
        points.append(np.column_stack([x, y]))
        
        # Left
        y = np.linspace(radius, -radius, points_per_side)
        x = np.full_like(y, -radius)
        points.append(np.column_stack([x, y]))
        
        return np.vstack(points)
    
    elif shape == 'hexagon':
        theta = np.linspace(0, 2 * np.pi, 7, endpoint=True)[:6]
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        return np.column_stack([x, y])
    
    else:
        raise ValueError(f"Unknown profile shape: {shape}")


def sweep_tube(
    path: np.ndarray,
    radius: float = 1.0,
    sides: int = 16,
    cap_ends: bool = False,
    profile_shape: str = 'circle'
) -> trimesh.Trimesh:
    """Sweep a circular profile along a 3D path to create a tube.
    
    Uses parallel transport frame to avoid twisting.
    
    Args:
        path: Array of shape (N, 3) defining the centerline
        radius: Tube radius
        sides: Number of radial sides
        cap_ends: Add caps to tube ends
        profile_shape: Shape of profile ('circle', 'square', 'hexagon')
        
    Returns:
        Tube mesh
        
    Raises:
        ValueError: If path has fewer than 2 points
    """
    if len(path) < 2:
        raise ValueError("Path must have at least 2 points")
    
    # Create profile
    profile = create_profile(radius, sides, profile_shape)
    
    # Compute frames along path using parallel transport
    frames = _compute_parallel_transport_frames(path)
    
    # Generate vertices by transforming profile at each frame
    vertices = []
    for i, (point, normal, binormal) in enumerate(frames):
        # Transform profile points
        transformed = (
            point[np.newaxis, :] +
            profile[:, 0:1] * normal +
            profile[:, 1:2] * binormal
        )
        vertices.append(transformed)
    
    vertices = np.vstack(vertices)
    
    # Generate faces
    faces = []
    n_points = len(path)
    
    for i in range(n_points - 1):
        for j in range(sides):
            j_next = (j + 1) % sides
            
            # Quad vertices
            v0 = i * sides + j
            v1 = i * sides + j_next
            v2 = (i + 1) * sides + j_next
            v3 = (i + 1) * sides + j
            
            # Two triangles
            faces.append([v0, v1, v2])
            faces.append([v2, v3, v0])
    
    # Add end caps if requested
    if cap_ends:
        # Start cap
        start_center_idx = len(vertices)
        vertices = np.vstack([vertices, [path[0]]])
        for j in range(sides):
            j_next = (j + 1) % sides
            faces.append([start_center_idx, j_next, j])
        
        # End cap
        end_center_idx = len(vertices)
        vertices = np.vstack([vertices, [path[-1]]])
        last_ring_start = (n_points - 1) * sides
        for j in range(sides):
            j_next = (j + 1) % sides
            faces.append([end_center_idx, last_ring_start + j, last_ring_start + j_next])
    
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)


def _compute_parallel_transport_frames(
    path: np.ndarray
) -> List[tuple]:
    """Compute parallel transport frames along a 3D curve.
    
    Args:
        path: Array of shape (N, 3) with path points
        
    Returns:
        List of (position, normal, binormal) tuples
    """
    frames = []
    
    # Compute tangent at first point
    t = path[1] - path[0]
    t = t / np.linalg.norm(t)
    
    # Initialize first frame
    # Choose normal perpendicular to tangent
    if abs(np.dot(t, [0, 0, 1])) > 0.999:
        n = np.array([1.0, 0.0, 0.0])
    else:
        n = np.cross([0, 0, 1], t)
        n = n / np.linalg.norm(n)
    
    b = np.cross(t, n)
    frames.append((path[0], n, b))
    
    # Parallel transport frame along curve
    for i in range(1, len(path) - 1):
        # Previous tangent
        t_prev = t
        
        # New tangent
        t = path[i + 1] - path[i]
        t = t / np.linalg.norm(t)
        
        # Rotate frame
        angle = np.arccos(np.clip(np.dot(t_prev, t), -1.0, 1.0))
        if angle > 1e-6:
            axis = np.cross(t_prev, t)
            axis_norm = np.linalg.norm(axis)
            if axis_norm > 1e-8:
                axis = axis / axis_norm
                rotation = Rotation.from_rotvec(angle * axis)
                n = rotation.apply(n)
                b = rotation.apply(b)
        
        frames.append((path[i], n, b))
    
    # Last frame
    frames.append((path[-1], n, b))
    
    return frames


def sweep_variable_radius(
    path: np.ndarray,
    radii: np.ndarray,
    sides: int = 16
) -> trimesh.Trimesh:
    """Sweep with variable radius along path.
    
    Args:
        path: Array of shape (N, 3) with path points
        radii: Array of shape (N,) with radius at each path point
        sides: Number of radial sides
        
    Returns:
        Variable-radius tube mesh
        
    Raises:
        ValueError: If radii length doesn't match path length
    """
    if len(radii) != len(path):
        raise ValueError(
            f"Radii length {len(radii)} must match path length {len(path)}"
        )
    
    # Compute frames
    frames = _compute_parallel_transport_frames(path)
    
    # Base profile (unit circle)
    theta = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    profile_x = np.cos(theta)
    profile_y = np.sin(theta)
    
    # Generate vertices with variable radius
    vertices = []
    for i, ((point, normal, binormal), r) in enumerate(zip(frames, radii)):
        # Scale profile by radius
        transformed = (
            point[np.newaxis, :] +
            r * profile_x[:, np.newaxis] * normal +
            r * profile_y[:, np.newaxis] * binormal
        )
        vertices.append(transformed)
    
    vertices = np.vstack(vertices)
    
    # Generate faces (same as constant radius)
    faces = []
    n_points = len(path)
    
    for i in range(n_points - 1):
        for j in range(sides):
            j_next = (j + 1) % sides
            
            v0 = i * sides + j
            v1 = i * sides + j_next
            v2 = (i + 1) * sides + j_next
            v3 = (i + 1) * sides + j
            
            faces.append([v0, v1, v2])
            faces.append([v2, v3, v0])
    
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)

