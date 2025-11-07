"""Pipeline for processing existing mesh templates with procedural algorithms."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import numpy as np
import trimesh
import matplotlib.pyplot as plt

from ..algorithms.gray_scott import GrayScottSimulator, GrayScottConfig
from ..geometry.mesh_operations import validate_mesh


@dataclass
class MeshProcessorConfig:
    """Configuration for mesh processing pipeline.
    
    Attributes:
        template_path: Path to seed STL file
        displacement_amplitude: Maximum displacement in mm
        field_resolution: Resolution of reaction-diffusion field
        simulation_steps: Number of simulation steps
        n_seeds: Number of initial seed patches
        pattern_type: Gray-Scott pattern preset
        random_seed: Random seed for reproducibility
        taper_top: Reduce displacement at top (0.0-1.0)
        taper_bottom: Reduce displacement at bottom (0.0-1.0)
    """
    template_path: Path
    displacement_amplitude: float = 8.0
    field_resolution: int = 256
    simulation_steps: int = 10000
    n_seeds: int = 7
    pattern_type: str = 'spots'
    random_seed: Optional[int] = 42
    taper_top: float = 0.3
    taper_bottom: float = 0.15


class MeshProcessorPipeline:
    """Pipeline for applying procedural patterns to existing meshes.
    
    Example:
        >>> config = MeshProcessorConfig(
        ...     template_path='data/templates/stl/my_vase.stl',
        ...     pattern_type='waves'
        ... )
        >>> pipeline = MeshProcessorPipeline(config)
        >>> mesh = pipeline.generate()
        >>> mesh.export('processed_vase.stl')
    """
    
    def __init__(self, config: MeshProcessorConfig):
        """Initialize pipeline."""
        self.config = config
        self.template_mesh: Optional[trimesh.Trimesh] = None
        self.field: Optional[np.ndarray] = None
        self.mesh: Optional[trimesh.Trimesh] = None
        
        # Initialize Gray-Scott simulator
        gs_config = GrayScottConfig(pattern_type=self.config.pattern_type)
        self.simulator = GrayScottSimulator(
            resolution=self.config.field_resolution,
            config=gs_config
        )
    
    def load_template(self) -> trimesh.Trimesh:
        """Load template mesh from file."""
        print(f"Loading template: {self.config.template_path}")
        self.template_mesh = trimesh.load(str(self.config.template_path))
        
        print(f"  Vertices: {len(self.template_mesh.vertices):,}")
        print(f"  Faces: {len(self.template_mesh.faces):,}")
        
        if not self.template_mesh.is_watertight:
            print("  ⚠️  Warning: Template mesh is not watertight!")
        else:
            print("  ✓ Template is watertight")
        
        return self.template_mesh
    
    def generate_pattern(self) -> np.ndarray:
        """Generate reaction-diffusion pattern."""
        print(f"\nGenerating pattern ({self.config.simulation_steps} steps)...")
        
        self.simulator.initialize_random(
            n_seeds=self.config.n_seeds,
            seed=self.config.random_seed
        )
        
        self.field = self.simulator.run(self.config.simulation_steps)
        print("  ✓ Pattern generated")
        
        return self.field
    
    def apply_to_mesh(self) -> trimesh.Trimesh:
        """Apply pattern to template mesh."""
        if self.template_mesh is None:
            self.load_template()
        
        if self.field is None:
            self.generate_pattern()
        
        print("\nApplying pattern to mesh...")
        
        # Get mesh properties
        vertices = self.template_mesh.vertices
        normals = self.template_mesh.vertex_normals
        
        # Get mesh bounds
        bounds = self.template_mesh.bounds
        z_coords = vertices[:, 2]
        z_min, z_max = bounds[0, 2], bounds[1, 2]
        z_range = z_max - z_min
        
        # Normalize Z to [0, 1]
        z_norm = (z_coords - z_min) / (z_range + 1e-8)
        
        # Sample field based on vertex positions
        field_values = self._sample_field_for_vertices(vertices, z_norm)
        
        # Apply vertical taper
        taper = self._compute_taper(z_norm)
        
        # Compute displacement
        displacement = self.config.displacement_amplitude * taper * (field_values - 0.5)
        
        # Apply along normals
        new_vertices = vertices + normals * displacement[:, np.newaxis]
        
        # Create new mesh
        self.mesh = trimesh.Trimesh(
            vertices=new_vertices,
            faces=self.template_mesh.faces,
            process=True
        )
        
        print(f"  ✓ Pattern applied (displacement range: {displacement.min():.2f} to {displacement.max():.2f} mm)")
        
        return self.mesh
    
    def _sample_field_for_vertices(
        self,
        vertices: np.ndarray,
        z_norm: np.ndarray
    ) -> np.ndarray:
        """Sample field values for each vertex.
        
        Uses cylindrical unwrapping for better pattern mapping.
        """
        # Convert to cylindrical coordinates
        x, y = vertices[:, 0], vertices[:, 1]
        theta = np.arctan2(y, x)
        theta_norm = (theta + np.pi) / (2 * np.pi)  # Normalize to [0, 1]
        
        # Map to field indices
        h, w = self.field.shape
        row_idx = np.clip((z_norm * (h - 1)).astype(int), 0, h - 1)
        col_idx = np.clip((theta_norm * (w - 1)).astype(int), 0, w - 1)
        
        # Sample field
        return self.field[row_idx, col_idx]
    
    def _compute_taper(self, z_norm: np.ndarray) -> np.ndarray:
        """Compute vertical taper to reduce displacement at top/bottom."""
        taper = np.ones_like(z_norm)
        
        # Bottom taper
        if self.config.taper_bottom > 0:
            bottom_mask = z_norm < self.config.taper_bottom
            taper[bottom_mask] = z_norm[bottom_mask] / self.config.taper_bottom
        
        # Top taper
        if self.config.taper_top > 0:
            top_threshold = 1.0 - self.config.taper_top
            top_mask = z_norm > top_threshold
            taper[top_mask] = (1.0 - z_norm[top_mask]) / self.config.taper_top
        
        return taper
    
    def generate(self) -> trimesh.Trimesh:
        """Complete pipeline: load template, generate pattern, apply."""
        self.load_template()
        self.generate_pattern()
        return self.apply_to_mesh()
    
    def visualize_field(self, save_path: Optional[Path] = None):
        """Visualize the generated pattern."""
        if self.field is None:
            self.generate_pattern()
        
        fig, ax = plt.subplots(figsize=(10, 10))
        im = ax.imshow(self.field, cmap='viridis', origin='lower')
        ax.set_title(f'Gray-Scott Pattern ({self.config.pattern_type})')
        ax.axis('off')
        plt.colorbar(im, ax=ax)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  ✓ Visualization saved to {save_path}")
        
        plt.show()
    
    def validate(self) -> dict:
        """Validate processed mesh."""
        if self.mesh is None:
            raise ValueError("No mesh generated yet. Call generate() first.")
        
        return validate_mesh(self.mesh)
    
    def export(self, path: Path, file_format: str = 'stl') -> None:
        """Export processed mesh."""
        if self.mesh is None:
            raise ValueError("No mesh generated yet. Call generate() first.")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        self.mesh.export(str(path), file_type=file_format)
        print(f"  ✓ Exported to {path}")
    
    def get_stats(self) -> dict:
        """Get mesh statistics."""
        if self.mesh is None:
            raise ValueError("No mesh generated yet. Call generate() first.")
        
        return {
            'template_vertices': len(self.template_mesh.vertices),
            'template_faces': len(self.template_mesh.faces),
            'output_vertices': len(self.mesh.vertices),
            'output_faces': len(self.mesh.faces),
            'volume_mm3': self.mesh.volume,
            'surface_area_mm2': self.mesh.area,
            'is_watertight': self.mesh.is_watertight,
            'template_watertight': self.template_mesh.is_watertight,
        }

