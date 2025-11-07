"""Tests for Gray-Scott reaction-diffusion algorithm."""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from algorithms.gray_scott import GrayScottSimulator, GrayScottConfig

try:
    import taichi as ti
    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False


class TestGrayScottConfig:
    """Tests for GrayScottConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = GrayScottConfig()
        assert config.feed_rate > 0
        assert config.kill_rate > 0
        assert config.Du > 0
        assert config.Dv > 0
        assert config.dt > 0
    
    def test_pattern_presets(self):
        """Test pattern type presets."""
        config_spots = GrayScottConfig(pattern_type='spots')
        config_stripes = GrayScottConfig(pattern_type='stripes')
        
        # Should have different parameters
        assert config_spots.feed_rate != config_stripes.feed_rate
    
    def test_custom_pattern(self):
        """Test custom pattern parameters."""
        config = GrayScottConfig(
            pattern_type='custom',
            feed_rate=0.03,
            kill_rate=0.06
        )
        assert config.feed_rate == 0.03
        assert config.kill_rate == 0.06


class TestGrayScottSimulator:
    """Tests for GrayScottSimulator."""
    
    def test_initialization(self):
        """Test simulator initialization."""
        sim = GrayScottSimulator(resolution=64)
        
        assert sim.U.shape == (64, 64)
        assert sim.V.shape == (64, 64)
        assert np.allclose(sim.U, 1.0)
        assert np.allclose(sim.V, 0.0)
    
    def test_random_initialization(self):
        """Test random seed initialization."""
        sim = GrayScottSimulator(resolution=64)
        sim.initialize_random(n_seeds=3, seed=42)
        
        # Should have perturbations
        assert not np.allclose(sim.U, 1.0)
        assert not np.allclose(sim.V, 0.0)
        
        # Should be reproducible
        sim2 = GrayScottSimulator(resolution=64)
        sim2.initialize_random(n_seeds=3, seed=42)
        
        assert np.allclose(sim.U, sim2.U)
        assert np.allclose(sim.V, sim2.V)
    
    def test_custom_initialization(self):
        """Test custom initial conditions."""
        sim = GrayScottSimulator(resolution=64)
        
        U_init = np.random.rand(64, 64).astype(np.float32)
        V_init = np.random.rand(64, 64).astype(np.float32)
        
        sim.initialize_custom(U_init, V_init)
        
        assert np.allclose(sim.U, U_init)
        assert np.allclose(sim.V, V_init)
    
    def test_custom_initialization_wrong_shape(self):
        """Test error on wrong shape."""
        sim = GrayScottSimulator(resolution=64)
        
        U_init = np.random.rand(32, 32).astype(np.float32)
        V_init = np.random.rand(32, 32).astype(np.float32)
        
        with pytest.raises(ValueError):
            sim.initialize_custom(U_init, V_init)
    
    def test_single_step_cpu(self):
        """Test single simulation step on CPU."""
        sim = GrayScottSimulator(resolution=64, use_gpu=False)
        sim.initialize_random(n_seeds=1, seed=42)
        
        U_before = sim.U.copy()
        V_before = sim.V.copy()
        
        sim.step()
        
        # State should change
        assert not np.allclose(sim.U, U_before)
        assert not np.allclose(sim.V, V_before)
        
        # Values should stay in bounds
        assert np.all(sim.U >= 0.0)
        assert np.all(sim.U <= 1.0)
        assert np.all(sim.V >= 0.0)
        assert np.all(sim.V <= 1.0)
    
    @pytest.mark.skipif(not TAICHI_AVAILABLE, reason="Taichi not available")
    def test_single_step_gpu(self):
        """Test single simulation step on GPU."""
        sim = GrayScottSimulator(resolution=64, use_gpu=True)
        sim.initialize_random(n_seeds=1, seed=42)
        
        sim.step()
        
        U, V = sim.get_state()
        
        # Values should stay in bounds
        assert np.all(U >= 0.0)
        assert np.all(U <= 1.0)
        assert np.all(V >= 0.0)
        assert np.all(V <= 1.0)
    
    @pytest.mark.skipif(not TAICHI_AVAILABLE, reason="Taichi not available")
    def test_cpu_gpu_consistency(self):
        """Test that CPU and GPU give similar results."""
        resolution = 64
        steps = 100
        seed = 42
        
        # CPU simulation
        sim_cpu = GrayScottSimulator(resolution=resolution, use_gpu=False)
        sim_cpu.initialize_random(n_seeds=3, seed=seed)
        field_cpu = sim_cpu.run(steps)
        
        # GPU simulation
        sim_gpu = GrayScottSimulator(resolution=resolution, use_gpu=True)
        sim_gpu.initialize_random(n_seeds=3, seed=seed)
        field_gpu = sim_gpu.run(steps)
        
        # Results should be close (allowing for numerical differences)
        assert np.allclose(field_cpu, field_gpu, atol=1e-4)
    
    def test_run_simulation(self):
        """Test running multiple steps."""
        sim = GrayScottSimulator(resolution=32, use_gpu=False)
        sim.initialize_random(n_seeds=2, seed=42)
        
        field = sim.run(steps=100)
        
        assert field.shape == (32, 32)
        assert np.all(field >= 0.0)
        assert np.all(field <= 1.0)
    
    def test_callback(self):
        """Test callback functionality."""
        sim = GrayScottSimulator(resolution=32, use_gpu=False)
        sim.initialize_random(n_seeds=1, seed=42)
        
        callback_steps = []
        
        def callback(step, field):
            callback_steps.append(step)
        
        sim.run(steps=50, callback=callback, callback_interval=10)
        
        assert callback_steps == [10, 20, 30, 40, 50]
    
    def test_conservation_approximate(self):
        """Test approximate mass conservation."""
        sim = GrayScottSimulator(resolution=64, use_gpu=False)
        sim.initialize_random(n_seeds=1, seed=42)
        
        # Total "mass" at start
        mass_start = sim.U.sum() + sim.V.sum()
        
        sim.run(steps=100)
        
        # Total "mass" at end
        mass_end = sim.U.sum() + sim.V.sum()
        
        # Should be roughly conserved (within 20% for this test)
        # Note: Gray-Scott doesn't strictly conserve mass due to feed/kill terms
        assert abs(mass_end - mass_start) / mass_start < 0.2
    
    def test_pattern_convergence(self):
        """Test that patterns stabilise over time."""
        sim = GrayScottSimulator(resolution=64, use_gpu=False)
        sim.initialize_random(n_seeds=3, seed=42)
        
        # Run to quasi-steady state
        sim.run(steps=5000)
        V_mid = sim.V.copy()
        
        # Run more steps
        sim.run(steps=1000)
        V_end = sim.V.copy()
        
        # Changes should be small (pattern stabilised)
        change = np.abs(V_end - V_mid).mean()
        assert change < 0.01


class TestTaichiKernels:
    """Taichi-specific tests."""
    
    @pytest.mark.skipif(not TAICHI_AVAILABLE, reason="Taichi not available")
    def test_taichi_initialization(self):
        """Test Taichi field initialization."""
        sim = GrayScottSimulator(resolution=64, use_gpu=True)
        
        assert sim.U_ti is not None
        assert sim.V_ti is not None
        assert sim._update_kernel is not None
    
    @pytest.mark.skipif(not TAICHI_AVAILABLE, reason="Taichi not available")
    def test_taichi_boundary_conditions(self):
        """Test periodic boundary conditions in Taichi kernel."""
        sim = GrayScottSimulator(resolution=32, use_gpu=True)
        
        # Create a simple pattern at the edge
        U = np.ones((32, 32), dtype=np.float32)
        V = np.zeros((32, 32), dtype=np.float32)
        
        # Put perturbation at edge
        V[0, 0] = 0.5
        V[31, 31] = 0.5
        
        sim.initialize_custom(U, V)
        sim.step()
        
        U_out, V_out = sim.get_state()
        
        # Perturbation should have diffused across boundary
        assert V_out[31, 0] > 0.0  # Wrapped from (0,0)
        assert V_out[0, 31] > 0.0  # Wrapped from (31,31)
    
    @pytest.mark.skipif(not TAICHI_AVAILABLE, reason="Taichi not available")
    def test_taichi_performance(self):
        """Test Taichi GPU performance advantage."""
        import time
        
        resolution = 256
        steps = 100
        
        # CPU
        sim_cpu = GrayScottSimulator(resolution=resolution, use_gpu=False)
        sim_cpu.initialize_random(seed=42)
        
        start = time.time()
        sim_cpu.run(steps)
        cpu_time = time.time() - start
        
        # GPU
        sim_gpu = GrayScottSimulator(resolution=resolution, use_gpu=True)
        sim_gpu.initialize_random(seed=42)
        
        # Warmup
        sim_gpu.step()
        
        start = time.time()
        sim_gpu.run(steps)
        gpu_time = time.time() - start
        
        # GPU should be faster (or at least not much slower)
        # Note: For small problems, GPU might be slower due to overhead
        print(f"CPU: {cpu_time:.3f}s, GPU: {gpu_time:.3f}s")
        assert gpu_time < cpu_time * 2  # Allow 2x margin


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
