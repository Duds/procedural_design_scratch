"""Pipeline for generating perforated moss poles using space colonization."""

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import numpy as np
import trimesh

from ..algorithms.space_colonization import SpaceColonizationAlgorithm, SpaceColonizationConfig
from ..geometry.primitives import create_cylinder, create_hollow_cylinder
from ..geometry.tube_sweep import sweep_tube
from ..geometry.mesh_operations import validate_mesh


@dataclass
class MossPoleConfig:
    """Configuration for moss pole generation.
    
    Attributes:
        outer_diameter: Outer diameter in mm
        wall_thickness: Wall thickness in mm
        height: Pole height in mm
        tunnel_radius: Radius of perforation tubes in mm
        attractor_count: Number of space colonization attractors
        influence_radius: Attractor influence radius in mm
        kill_radius: Attractor kill radius in mm
        step_size: Branch growth step size in mm
        n_ribs: Number of structural ribs (no-cut zones)
        rib_width_degrees: Angular width of ribs in degrees
        random_seed: Random seed for reproducibility
    """
    outer_diameter: float = 50.0
    wall_thickness: float = 2.0
    height: float = 200.0
    tunnel_radius: float = 1.5
    attractor_count: int = 2000
    influence_radius: float = 16.0
    kill_radius: float = 3.5
    step_size: float = 1.8
    n_ribs: int = 4
    rib_width_degrees: float = 10.0
    random_seed: Optional[int] = 42


class MossPolePipeline:
    """End-to-end pipeline for generating perforated moss poles.
    
    Example:
        >>> config = MossPoleConfig(height=250)
        >>> pipeline = MossPolePipeline(config)
        >>> mesh = pipeline.generate()
        >>> mesh.export('moss_pole.stl')
    """
    
    def __init__(self, config: Optional[MossPoleConfig] = None):
        """Initialize pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or MossPoleConfig()
        self.shell: Optional[trimesh.Trimesh] = None
        self.branches: Optional[List[np.ndarray]] = None
        self.mesh: Optional[trimesh.Trimesh] = None
        
        # Initialize space colonization
        sc_config = SpaceColonizationConfig(
            influence_radius=self.config.influence_radius,
            kill_radius=self.config.kill_radius,
            step_size=self.config.step_size
        )
        self.colonizer = SpaceColonizationAlgorithm(sc_config)
    
    def generate_shell(self) -> trimesh.Trimesh:
        """Generate hollow cylindrical shell.
        
        Returns:
            Shell mesh
        """
        print("Generating shell...")
        
        outer_r = self.config.outer_diameter / 2
        inner_r = outer_r - self.config.wall_thickness
        
        # Create hollow cylinder
        outer = create_cylinder(
            radius=outer_r,
            height=self.config.height,
            sections=64
        )
        inner = create_cylinder(
            radius=inner_r,
            height=self.config.height,
            sections=64
        )
        
        # Boolean difference
        self.shell = outer.difference(inner)
        
        return self.shell
    
    def generate_branch_pattern(self) -> List[np.ndarray]:
        """Generate branch pattern using space colonization.
        
        Returns:
            List of polylines representing branches
        """
        print("Generating branch pattern...")
        
        # Generate attractors in cylindrical coordinates
        rng = np.random.default_rng(self.config.random_seed)
        r = self.config.outer_diameter / 2
        
        # Create rib mask
        rib_angles = np.linspace(0, 2*np.pi, self.config.n_ribs, endpoint=False)
        half_width = np.radians(self.config.rib_width_degrees / 2)
        
        attractors_2d = []
        attempts = 0
        max_attempts = self.config.attractor_count * 10
        
        while len(attractors_2d) < self.config.attractor_count and attempts < max_attempts:
            attempts += 1
            
            # Random cylindrical coordinates
            theta = rng.uniform(0, 2*np.pi)
            z = rng.uniform(-self.config.height/2, self.config.height/2)
            
            # Check if in rib zone
            in_rib = False
            for rib_angle in rib_angles:
                angle_diff = abs(np.arctan2(
                    np.sin(theta - rib_angle),
                    np.cos(theta - rib_angle)
                ))
                if angle_diff < half_width:
                    in_rib = True
                    break
            
            if not in_rib:
                attractors_2d.append([theta, z])
        
        attractors_2d = np.array(attractors_2d)
        
        # Add attractors to colonizer
        self.colonizer.add_attractors(attractors_2d)
        
        # Initialize with seed nodes around the cylinder
        n_seeds = 8
        seed_thetas = np.linspace(0, 2*np.pi, n_seeds, endpoint=False)
        seed_nodes = []
        
        # Add seeds at top and bottom
        for theta in seed_thetas:
            seed_nodes.append(np.array([theta, -self.config.height/2 + 5]))
            seed_nodes.append(np.array([theta, self.config.height/2 - 5]))
        
        self.colonizer.add_initial_nodes(seed_nodes)
        
        # Grow
        iterations = self.colonizer.grow(
            progress_callback=lambda i, n: print(f"  Iteration {i}: {n} nodes")
            if i % 100 == 0 else None
        )
        
        print(f"Growth completed in {iterations} iterations")
        
        # Get structure and convert to 3D polylines
        nodes, edges = self.colonizer.get_structure()
        
        # Convert from (theta, z) to (x, y, z)
        branches_3d = []
        for parent_idx, child_idx in edges:
            parent = nodes[parent_idx]
            child = nodes[child_idx]
            
            # Convert to 3D
            p_theta, p_z = parent
            c_theta, c_z = child
            
            p_3d = np.array([
                r * np.cos(p_theta),
                r * np.sin(p_theta),
                p_z
            ])
            
            c_3d = np.array([
                r * np.cos(c_theta),
                r * np.sin(c_theta),
                c_z
            ])
            
            branches_3d.append(np.array([p_3d, c_3d]))
        
        self.branches = branches_3d
        
        return self.branches
    
    def generate_perforation_tubes(self) -> List[trimesh.Trimesh]:
        """Generate tube meshes for perforations.
        
        Returns:
            List of tube meshes
        """
        if self.branches is None:
            self.generate_branch_pattern()
        
        print(f"Generating {len(self.branches)} perforation tubes...")
        
        tubes = []
        for branch in self.branches:
            tube = sweep_tube(
                path=branch,
                radius=self.config.tunnel_radius,
                sides=12,
                cap_ends=True
            )
            tubes.append(tube)
        
        return tubes
    
    def generate(self) -> trimesh.Trimesh:
        """Generate complete moss pole.
        
        Returns:
            Final perforated mesh
        """
        # Generate shell
        self.generate_shell()
        
        # Generate branch pattern
        self.generate_branch_pattern()
        
        # Generate tubes
        tubes = self.generate_perforation_tubes()
        
        print("Applying boolean operations...")
        
        # Union all tubes
        if tubes:
            combined_tubes = tubes[0]
            for tube in tubes[1:]:
                try:
                    combined_tubes = combined_tubes.union(tube)
                except:
                    # If union fails, skip this tube
                    pass
            
            # Subtract from shell
            try:
                self.mesh = self.shell.difference(combined_tubes)
            except:
                print("Boolean operation failed, returning shell only")
                self.mesh = self.shell
        else:
            self.mesh = self.shell
        
        return self.mesh
    
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
        """Export moss pole to file.
        
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
        
        stats = {
            'vertices': len(self.mesh.vertices),
            'faces': len(self.mesh.faces),
            'volume_mm3': self.mesh.volume,
            'surface_area_mm2': self.mesh.area,
            'bounds_mm': self.mesh.bounds.tolist(),
            'is_watertight': self.mesh.is_watertight,
        }
        
        # Calculate open fraction
        shell_volume = np.pi * (
            (self.config.outer_diameter/2)**2 -
            (self.config.outer_diameter/2 - self.config.wall_thickness)**2
        ) * self.config.height
        
        stats['open_fraction'] = 1 - (self.mesh.volume / shell_volume)
        stats['n_branches'] = len(self.branches) if self.branches else 0
        
        return stats
