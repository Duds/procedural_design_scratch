"""Primitive geometric shapes for procedural generation."""

from typing import Tuple, Optional
import numpy as np
import trimesh


def create_cylinder(
    radius: float = 1.0,
    height: float = 2.0,
    sections: int = 32,
    closed: bool = True
) -> trimesh.Trimesh:
    """Create a cylindrical mesh.
    
    Args:
        radius: Cylinder radius
        height: Cylinder height (centered at origin)
        sections: Number of radial sections
        closed: Include top and bottom caps
        
    Returns:
        Trimesh cylinder
    """
    return trimesh.creation.cylinder(
        radius=radius,
        height=height,
        sections=sections,
        transform=None
    )


def create_sphere(
    radius: float = 1.0,
    subdivisions: int = 3
) -> trimesh.Trimesh:
    """Create a spherical mesh using icosphere subdivision.
    
    Args:
        radius: Sphere radius
        subdivisions: Number of subdivisions (higher = smoother)
        
    Returns:
        Trimesh sphere
    """
    return trimesh.creation.icosphere(
        subdivisions=subdivisions,
        radius=radius
    )


def create_torus(
    major_radius: float = 1.0,
    minor_radius: float = 0.3,
    major_sections: int = 32,
    minor_sections: int = 16
) -> trimesh.Trimesh:
    """Create a torus mesh.
    
    Args:
        major_radius: Radius from center to tube center
        minor_radius: Tube radius
        major_sections: Sections around major circle
        minor_sections: Sections around minor circle
        
    Returns:
        Trimesh torus
    """
    # Create profile circle
    theta = np.linspace(0, 2 * np.pi, minor_sections, endpoint=False)
    profile = np.column_stack([
        minor_radius * np.cos(theta),
        minor_radius * np.sin(theta)
    ])
    
    # Sweep around major circle
    phi = np.linspace(0, 2 * np.pi, major_sections, endpoint=False)
    vertices = []
    
    for p in phi:
        # Transform profile to current position
        r = major_radius + profile[:, 0]
        x = r * np.cos(p)
        y = r * np.sin(p)
        z = profile[:, 1]
        vertices.append(np.column_stack([x, y, z]))
    
    vertices = np.vstack(vertices)
    
    # Create faces
    faces = []
    for i in range(major_sections):
        for j in range(minor_sections):
            # Indices for quad
            i_next = (i + 1) % major_sections
            j_next = (j + 1) % minor_sections
            
            v0 = i * minor_sections + j
            v1 = i * minor_sections + j_next
            v2 = i_next * minor_sections + j_next
            v3 = i_next * minor_sections + j
            
            # Two triangles per quad
            faces.append([v0, v1, v2])
            faces.append([v2, v3, v0])
    
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)


def rounded_square_profile(
    side: float = 100.0,
    corner_radius: float = 20.0,
    points_per_edge: int = 64
) -> np.ndarray:
    """Create a rounded square profile path.
    
    This creates a 2D path of a square with rounded corners,
    useful for extruding or as a base shape.
    
    Args:
        side: Side length of the square
        corner_radius: Radius of corner rounds
        points_per_edge: Number of points per edge
        
    Returns:
        Array of shape (N, 2) with (x, y) coordinates
    """
    half = side / 2.0 - corner_radius
    points = []
    
    # Bottom edge
    x = np.linspace(-half, half, points_per_edge)
    y = np.full_like(x, -half - corner_radius)
    points.append(np.column_stack([x, y]))
    
    # Bottom-right corner
    angles = np.linspace(-np.pi/2, 0, points_per_edge // 4)
    x = half + corner_radius * np.cos(angles)
    y = -half + corner_radius * np.sin(angles)
    points.append(np.column_stack([x, y]))
    
    # Right edge
    y = np.linspace(-half, half, points_per_edge)
    x = np.full_like(y, half + corner_radius)
    points.append(np.column_stack([x, y]))
    
    # Top-right corner
    angles = np.linspace(0, np.pi/2, points_per_edge // 4)
    x = half + corner_radius * np.cos(angles)
    y = half + corner_radius * np.sin(angles)
    points.append(np.column_stack([x, y]))
    
    # Top edge
    x = np.linspace(half, -half, points_per_edge)
    y = np.full_like(x, half + corner_radius)
    points.append(np.column_stack([x, y]))
    
    # Top-left corner
    angles = np.linspace(np.pi/2, np.pi, points_per_edge // 4)
    x = -half + corner_radius * np.cos(angles)
    y = half + corner_radius * np.sin(angles)
    points.append(np.column_stack([x, y]))
    
    # Left edge
    y = np.linspace(half, -half, points_per_edge)
    x = np.full_like(y, -half - corner_radius)
    points.append(np.column_stack([x, y]))
    
    # Bottom-left corner
    angles = np.linspace(np.pi, 3*np.pi/2, points_per_edge // 4)
    x = -half + corner_radius * np.cos(angles)
    y = -half + corner_radius * np.sin(angles)
    points.append(np.column_stack([x, y]))
    
    return np.vstack(points)


def create_hollow_cylinder(
    outer_radius: float = 1.0,
    inner_radius: float = 0.8,
    height: float = 2.0,
    sections: int = 32
) -> trimesh.Trimesh:
    """Create a hollow cylindrical shell.
    
    Args:
        outer_radius: Outer radius
        inner_radius: Inner radius
        height: Height
        sections: Number of radial sections
        
    Returns:
        Trimesh of hollow cylinder
    """
    outer = create_cylinder(outer_radius, height, sections)
    inner = create_cylinder(inner_radius, height, sections)
    
    # Boolean difference
    result = outer.difference(inner)
    return result
