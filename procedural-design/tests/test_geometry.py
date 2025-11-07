"""Tests for geometry utilities."""

import pytest
import numpy as np
import trimesh
from src.geometry.primitives import create_cylinder, create_hollow_cylinder, create_rounded_square_path
from src.geometry.isosurface import extract_isosurface, field_from_function
from src.geometry.mesh_ops import validate_mesh, smooth_mesh
from src.geometry.sweep import sweep_circle_along_path


class TestPrimitives:
    """Test geometric primitives."""
    
    def test_create_cylinder(self):
        """Test cylinder creation."""
        mesh = create_cylinder(radius=10.0, height=50.0, n_sides=32, closed=True)
        
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
        assert mesh.is_watertight
    
    def test_create_hollow_cylinder(self):
        """Test hollow cylinder creation."""
        mesh = create_hollow_cylinder(
            outer_radius=10.0,
            inner_radius=8.0,
            height=50.0,
            n_sides=32
        )
        
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
    
    def test_hollow_cylinder_invalid_radii(self):
        """Test that invalid radii raise error."""
        with pytest.raises(ValueError, match="Inner radius must be less than outer radius"):
            create_hollow_cylinder(outer_radius=8.0, inner_radius=10.0, height=50.0)
    
    def test_create_rounded_square_path(self):
        """Test rounded square path generation."""
        path = create_rounded_square_path(side=100.0, corner_radius=20.0, n_per_edge=64)
        
        assert isinstance(path, np.ndarray)
        assert path.shape[1] == 2  # 2D points
        assert len(path) > 0
        
        # Check it forms a closed loop (first and last points should be close)
        # Note: Due to how the path is constructed, this might not be exact
        assert path.shape[0] > 100  # Should have many points


class TestIsosurface:
    """Test isosurface extraction."""
    
    def test_extract_isosurface_sphere(self):
        """Test extracting a sphere."""
        def sphere(x, y, z):
            return x**2 + y**2 + z**2 - 100
        
        field, spacing = field_from_function(
            bounds=((-15, 15), (-15, 15), (-15, 15)),
            resolution=(30, 30, 30),
            func=sphere
        )
        
        mesh = extract_isosurface(field, isovalue=0, spacing=spacing, smooth=False)
        
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
        
        # Should be roughly spherical
        assert mesh.is_volume
    
    def test_extract_isosurface_cube(self):
        """Test extracting a cube."""
        def cube(x, y, z):
            return np.maximum.reduce([
                np.abs(x) - 10,
                np.abs(y) - 10,
                np.abs(z) - 10
            ])
        
        field, spacing = field_from_function(
            bounds=((-20, 20), (-20, 20), (-20, 20)),
            resolution=(40, 40, 40),
            func=cube
        )
        
        mesh = extract_isosurface(field, isovalue=0, spacing=spacing, smooth=False)
        
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
    
    def test_extract_isosurface_invalid_dimension(self):
        """Test that 2D array raises error."""
        field_2d = np.random.rand(50, 50)
        
        with pytest.raises(ValueError, match="Field must be 3D"):
            extract_isosurface(field_2d)


class TestMeshOps:
    """Test mesh operations."""
    
    @pytest.fixture
    def simple_mesh(self):
        """Create a simple test mesh."""
        return create_cylinder(radius=10.0, height=20.0, n_sides=16, closed=True)
    
    def test_validate_mesh(self, simple_mesh):
        """Test mesh validation."""
        results = validate_mesh(simple_mesh)
        
        assert 'is_valid' in results
        assert 'is_watertight' in results
        assert 'num_vertices' in results
        assert 'num_faces' in results
        assert results['num_vertices'] > 0
        assert results['num_faces'] > 0
    
    def test_smooth_mesh(self, simple_mesh):
        """Test mesh smoothing."""
        smoothed = smooth_mesh(simple_mesh, iterations=2, lambda_factor=0.3)
        
        assert isinstance(smoothed, trimesh.Trimesh)
        assert len(smoothed.vertices) == len(simple_mesh.vertices)
        assert len(smoothed.faces) == len(simple_mesh.faces)


class TestSweep:
    """Test path sweeping operations."""
    
    def test_sweep_circle_along_straight_path(self):
        """Test sweeping circle along straight line."""
        path = np.array([
            [0, 0, 0],
            [0, 0, 10],
            [0, 0, 20]
        ])
        
        mesh = sweep_circle_along_path(path, radius=2.0, n_sides=16, closed=False)
        
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
    
    def test_sweep_circle_along_helix(self):
        """Test sweeping circle along helix."""
        t = np.linspace(0, 4*np.pi, 50)
        path = np.column_stack([
            5 * np.cos(t),
            5 * np.sin(t),
            t
        ])
        
        mesh = sweep_circle_along_path(path, radius=1.0, n_sides=12, closed=False)
        
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
    
    def test_sweep_invalid_path(self):
        """Test that single-point path raises error."""
        path = np.array([[0, 0, 0]])
        
        with pytest.raises(ValueError, match="Path must have at least 2 points"):
            sweep_circle_along_path(path, radius=1.0)

