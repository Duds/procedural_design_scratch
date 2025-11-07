"""Gray-Scott reaction-diffusion algorithm implementation.

This module provides both CPU (NumPy) and GPU (Taichi) implementations
of the Gray-Scott reaction-diffusion system.

References:
    - Gray, P., & Scott, S. K. (1983). Autocatalytic reactions in the isothermal,
      continuous stirred tank reactor: Isolas and other forms of multistability.
      Chemical Engineering Science, 38(1), 29-43.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

try:
    import taichi as ti
    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False


@dataclass
class GrayScottConfig:
    """Configuration for Gray-Scott simulation.
    
    Attributes:
        feed_rate: Feed rate (F), typical range 0.01-0.08
        kill_rate: Kill rate (k), typical range 0.045-0.065
        Du: Diffusion rate of U chemical, default 2e-5
        Dv: Diffusion rate of V chemical, default 1e-5
        dt: Timestep, default 1.0
        pattern_type: Preset pattern ('spots', 'stripes', 'waves', 'custom')
    """
    feed_rate: float = 0.055
    kill_rate: float = 0.062
    Du: float = 2e-5
    Dv: float = 1e-5
    dt: float = 1.0
    pattern_type: str = 'spots'
    
    def __post_init__(self):
        """Apply pattern presets if specified."""
        presets = {
            'spots': (0.055, 0.062),
            'stripes': (0.035, 0.060),
            'waves': (0.014, 0.054),
            'holes': (0.039, 0.058),
        }
        
        if self.pattern_type in presets:
            self.feed_rate, self.kill_rate = presets[self.pattern_type]


class GrayScottSimulator:
    """Gray-Scott reaction-diffusion simulator.
    
    Supports both CPU and GPU backends for flexibility and performance.
    
    Example:
        >>> config = GrayScottConfig(pattern_type='spots')
        >>> sim = GrayScottSimulator(resolution=256, config=config)
        >>> sim.initialize_random(n_seeds=5)
        >>> field = sim.run(steps=10000)
        >>> plt.imshow(field)
    """
    
    def __init__(
        self,
        resolution: int = 256,
        config: Optional[GrayScottConfig] = None,
        use_gpu: bool = False,
        dtype: type = np.float32
    ):
        """Initialize simulator.
        
        Args:
            resolution: Grid resolution (square grid)
            config: Simulation configuration
            use_gpu: Use Taichi GPU backend if available
            dtype: Data type for arrays
            
        Raises:
            RuntimeError: If GPU requested but Taichi not available
        """
        self.resolution = resolution
        self.config = config or GrayScottConfig()
        self.dtype = dtype
        self.use_gpu = use_gpu and TAICHI_AVAILABLE
        
        if use_gpu and not TAICHI_AVAILABLE:
            raise RuntimeError(
                "GPU backend requested but Taichi not installed. "
                "Install with: pip install taichi"
            )
        
        # Initialize fields
        self.U = np.ones((resolution, resolution), dtype=dtype)
        self.V = np.zeros((resolution, resolution), dtype=dtype)
        
        # Initialize Taichi if using GPU
        if self.use_gpu:
            self._init_taichi()
    
    def _init_taichi(self):
        """Initialize Taichi fields and kernels."""
        ti.init(arch=ti.gpu)
        
        # Create Taichi fields
        self.U_ti = ti.field(dtype=ti.f32, shape=(self.resolution, self.resolution))
        self.V_ti = ti.field(dtype=ti.f32, shape=(self.resolution, self.resolution))
        
        # Define update kernel
        @ti.kernel
        def update_kernel(
            U: ti.template(),
            V: ti.template(),
            Du: float,
            Dv: float,
            F: float,
            k: float,
            dt: float
        ):
            """Taichi kernel for Gray-Scott update."""
            n = U.shape[0]
            for i, j in U:
                # Compute Laplacian with periodic boundary
                im = (i - 1) % n
                ip = (i + 1) % n
                jm = (j - 1) % n
                jp = (j + 1) % n
                
                Lu = (U[im, j] + U[ip, j] + U[i, jm] + U[i, jp] - 4.0 * U[i, j])
                Lv = (V[im, j] + V[ip, j] + V[i, jm] + V[i, jp] - 4.0 * V[i, j])
                
                uvv = U[i, j] * V[i, j] * V[i, j]
                
                U[i, j] += (Du * Lu - uvv + F * (1.0 - U[i, j])) * dt
                V[i, j] += (Dv * Lv + uvv - (F + k) * V[i, j]) * dt
                
                # Clamp values
                U[i, j] = ti.max(0.0, ti.min(1.0, U[i, j]))
                V[i, j] = ti.max(0.0, ti.min(1.0, V[i, j]))
        
        self._update_kernel = update_kernel
    
    def initialize_random(
        self,
        n_seeds: int = 5,
        seed: Optional[int] = None
    ) -> None:
        """Initialize with random seed patches.
        
        Args:
            n_seeds: Number of random perturbation patches
            seed: Random seed for reproducibility
        """
        rng = np.random.default_rng(seed)
        
        for _ in range(n_seeds):
            cx = rng.integers(self.resolution // 4, 3 * self.resolution // 4)
            cy = rng.integers(self.resolution // 4, 3 * self.resolution // 4)
            r = max(2, self.resolution // 20)
            
            self.U[cx-r:cx+r, cy-r:cy+r] = 0.5
            self.V[cx-r:cx+r, cy-r:cy+r] = 0.25
        
        # Copy to GPU if needed
        if self.use_gpu:
            self.U_ti.from_numpy(self.U)
            self.V_ti.from_numpy(self.V)
    
    def initialize_custom(
        self,
        U_init: np.ndarray,
        V_init: np.ndarray
    ) -> None:
        """Initialize with custom initial conditions.
        
        Args:
            U_init: Initial U field
            V_init: Initial V field
            
        Raises:
            ValueError: If shapes don't match resolution
        """
        if U_init.shape != (self.resolution, self.resolution):
            raise ValueError(
                f"U_init shape {U_init.shape} doesn't match "
                f"resolution ({self.resolution}, {self.resolution})"
            )
        if V_init.shape != (self.resolution, self.resolution):
            raise ValueError(
                f"V_init shape {V_init.shape} doesn't match "
                f"resolution ({self.resolution}, {self.resolution})"
            )
        
        self.U = U_init.astype(self.dtype)
        self.V = V_init.astype(self.dtype)
        
        if self.use_gpu:
            self.U_ti.from_numpy(self.U)
            self.V_ti.from_numpy(self.V)
    
    def step(self) -> None:
        """Perform single simulation step."""
        if self.use_gpu:
            self._step_gpu()
        else:
            self._step_cpu()
    
    def _step_cpu(self) -> None:
        """CPU implementation of single step."""
        # Compute Laplacian with periodic boundaries
        Lu = (
            np.roll(self.U, 1, axis=0) +
            np.roll(self.U, -1, axis=0) +
            np.roll(self.U, 1, axis=1) +
            np.roll(self.U, -1, axis=1) -
            4.0 * self.U
        )
        Lv = (
            np.roll(self.V, 1, axis=0) +
            np.roll(self.V, -1, axis=0) +
            np.roll(self.V, 1, axis=1) +
            np.roll(self.V, -1, axis=1) -
            4.0 * self.V
        )
        
        uvv = self.U * self.V * self.V
        
        self.U += (
            self.config.Du * Lu -
            uvv +
            self.config.feed_rate * (1.0 - self.U)
        ) * self.config.dt
        
        self.V += (
            self.config.Dv * Lv +
            uvv -
            (self.config.feed_rate + self.config.kill_rate) * self.V
        ) * self.config.dt
        
        # Clamp values
        np.clip(self.U, 0.0, 1.0, out=self.U)
        np.clip(self.V, 0.0, 1.0, out=self.V)
    
    def _step_gpu(self) -> None:
        """GPU implementation of single step."""
        self._update_kernel(
            self.U_ti,
            self.V_ti,
            self.config.Du,
            self.config.Dv,
            self.config.feed_rate,
            self.config.kill_rate,
            self.config.dt
        )
    
    def run(
        self,
        steps: int,
        callback: Optional[callable] = None,
        callback_interval: int = 100
    ) -> np.ndarray:
        """Run simulation for specified steps.
        
        Args:
            steps: Number of simulation steps
            callback: Optional callback function called every callback_interval steps
            callback_interval: Steps between callback calls
            
        Returns:
            Final V field as numpy array
        """
        for i in range(steps):
            self.step()
            
            if callback and (i + 1) % callback_interval == 0:
                if self.use_gpu:
                    # Copy from GPU for callback
                    V_cpu = self.V_ti.to_numpy()
                    callback(i + 1, V_cpu)
                else:
                    callback(i + 1, self.V)
        
        # Return final V field
        if self.use_gpu:
            return self.V_ti.to_numpy()
        else:
            return self.V.copy()
    
    def get_state(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get current U and V fields.
        
        Returns:
            Tuple of (U, V) numpy arrays
        """
        if self.use_gpu:
            return self.U_ti.to_numpy(), self.V_ti.to_numpy()
        else:
            return self.U.copy(), self.V.copy()
