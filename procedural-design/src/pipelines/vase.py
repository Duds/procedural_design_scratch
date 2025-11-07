"""Pipeline for generating Gray-Scott patterned vases."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import numpy as np
import trimesh
import matplotlib.pyplot as plt

from ..algorithms.gray_scott import GrayScottSimulator, GrayScottConfig
from ..geometry.primitives import rounded_square_profile
from ..geometry.mesh_operations import validate_mesh


@dataclass
class VaseConfig:
    """Configuration for vase generation.
    
    Attributes:
        height: Vase height in mm
        base_size: Base dimension in mm
        profile_type: Base profile ('circle', 'square', 'hexagon')
        displacement_amplitude: Maximum displacement in mm
        field_resolution: Resolution of reaction-diffusion field
        simulation_steps: Number of simulation steps
        n_seeds: Number of initial seed patches
        pattern_type: Gray-Scott pattern preset
        random_seed: Random seed for reproducibility
        wall_thickness: Wall thickness (if hollow)
    """
    height: float = 150.0
    base_size: float = 80.0
    profile_type: str = 'square'
    displacement_amplitude: float = 6.0
    field_resolution: int = 256
    simulation_steps: int = 10000
    n_seeds: int = 5
    pattern_type: str = 'spots'
    random_seed: Optional[int] = 42
    wall_thickness: Optional[float] = None
    corner_radius: float = 20.0


class VasePipeline:
    """End-to-end pipeline for generating patterned vases.
    
    Example:
        >>> config = VaseConfig(height=200, pattern_type='waves')
        >>> pipeline = VasePipeline(config)
        >>> mesh = pipeline.generate()
        >>> mesh.export('vase.stl')
    """
    
    def __init__(self, config: Optional[VaseConfig] = None):
        """Initialize pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or VaseConfig()
        self.field: Optional[np.ndarray] = None
        self.mesh: Optional[trimesh.Trimesh] = None
        
        # Initialize Gray-Scott simulator
        gs_config = GrayScottConfig(pattern_type=self.config.pattern_type)
        self.simulator = GrayScottSimulator(
            resolution=self.config.field_resolution,
            config=gs_config
        )
    
    def generate_pattern(self) -> np.ndarray:
        """Generate reaction-diffusion pattern.
        
        Returns:
            2D pattern field
        """
        # Initialize with random seeds
        self.simulator.initialize_random(
            n_seeds=self.config.n_seeds,
            seed=self.config.random_seed
        )
        
        # Run simulation
        print(f"Simulating {self.config.simulation_steps} steps...")
        self.field = self.simulator.run(self.config.simulation_steps)
        
        return self.field
    
    def visualize_field(self, save_path: Optional[Path] = None):
        """Visualize the pattern field.
        
        Args:
            save_path: Optional path to save visualization
        """
        if self.field is None:
            self.generate_pattern()
        
        fig, ax = plt.subplots(figsize=(10, 10))
        im = ax.imshow(self.field, cmap='viridis', origin='lower')
        ax.set_title('Gray-Scott Pattern')
        ax.axis('off')
        plt.colorbar(im, ax=ax)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.show()
    
    def generate_mesh(self) -> trimesh.Trimesh:
        """Generate 3D mesh from pattern.
        
        Returns:
            Vase mesh
        """
        if self.field is None:
            self.generate_pattern()
        
        print("Building mesh...")
        
        # Get profile based on type
        if self.config.profile_type == 'square':
            profile = rounded_square_profile(
                side=self.config.base_size,
                corner_radius=self.config.corner_radius,
                points_per_edge=self.config.field_resolution // 4
            )
        elif self.config.profile_type == 'circle':
            theta = np.linspace(0, 2 * np.pi, self.config.field_resolution, endpoint=False)
            r = self.config.base_size / 2
            profile = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
        else:
            # Hexagon
            theta = np.linspace(0, 2 * np.pi, 7, endpoint=True)[:6]
            r = self.config.base_size / 2
            profile = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
            # Interpolate to match resolution
            from scipy.interpolate import interp1d
            t = np.linspace(0, 1, len(profile))
            t_new = np.linspace(0, 1, self.config.field_resolution)
            fx = interp1d(t, profile[:, 0], kind='linear')
            fy = interp1d(t, profile[:, 1], kind='linear')
            profile = np.column_stack([fx(t_new), fy(t_new)])
        
        # Vertical sampling
        h, w = self.field.shape
        z_vals = np.linspace(0, self.config.height, h)
        
        # Create taper (optional - could be configurable)
        taper = np.ones(h)
        top_taper_start = int(h * 2/3)
        bottom_taper_end = int(h * 1/6)
        
        for i in range(h):
            if i < bottom_taper_end:
                taper[i] = i / bottom_taper_end
            elif i > top_taper_start:
                taper[i] = 1 - (i - top_taper_start) / (h - top_taper_start)
        
        # Build vertices layer by layer
        vertices = []
        n_profile = len(profile)
        
        for i, zi in enumerate(z_vals):
            # Get displacement from field
            disp = self.config.displacement_amplitude * taper[i] * (self.field[i, :] - 0.5)
            
            # Resize displacement to match profile if needed
            if len(disp) != n_profile:
                from scipy.interpolate import interp1d
                x_old = np.linspace(0, 1, len(disp))
                x_new = np.linspace(0, 1, n_profile)
                f = interp1d(x_old, disp, kind='linear')
                disp = f(x_new)
            
            # Apply radial displacement
            scale = 1 + disp / (self.config.base_size / 2)
            layer = np.column_stack([
                profile[:, 0] * scale,
                profile[:, 1] * scale,
                np.full(n_profile, zi)
            ])
            vertices.append(layer)
        
        vertices = np.vstack(vertices)
        
        # Build faces
        faces = []
        for i in range(h - 1):
            for j in range(n_profile - 1):
                a = i * n_profile + j
                b = a + 1
                c = a + n_profile
                d = c + 1
                faces.extend([[a, b, c], [b, d, c]])
            
            # Close loop
            a = i * n_profile + (n_profile - 1)
            b = i * n_profile
            c = a + n_profile
            d = b + n_profile
            faces.extend([[a, b, c], [b, d, c]])
        
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
        
        return self.mesh
    
    def generate(self) -> trimesh.Trimesh:
        """Generate complete vase (pattern + mesh).
        
        Returns:
            Final vase mesh
        """
        self.generate_pattern()
        return self.generate_mesh()
    
    def validate(self) -> dict:
        """Validate generated mesh.
        
        Returns:
            Validation results dictionary
        """
        if self.mesh is None:
            raise ValueError("No mesh generated yet. Call generate() first.")
        
        return validate_mesh(self.mesh)
    
    def export(
        self,
        path: Path,
        file_format: str = 'stl'
    ) -> None:
        """Export vase to file.
        
        Args:
            path: Output file path
            file_format: File format ('stl', 'obj', 'ply', '3mf')
        """
        if self.mesh is None:
            raise ValueError("No mesh generated yet. Call generate() first.")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        self.mesh.export(str(path), file_type=file_format)
        print(f"Exported to {path}")
    
    def get_stats(self) -> dict:
        """Get mesh statistics.
        
        Returns:
            Statistics dictionary
        """
        if self.mesh is None:
            raise ValueError("No mesh generated yet. Call generate() first.")
        
        return {
            'vertices': len(self.mesh.vertices),
            'faces': len(self.mesh.faces),
            'volume_mm3': self.mesh.volume,
            'surface_area_mm2': self.mesh.area,
            'bounds_mm': self.mesh.bounds.tolist(),
            'is_watertight': self.mesh.is_watertight,
        }
