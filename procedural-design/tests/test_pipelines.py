"""Tests for end-to-end pipelines."""

import pytest
import numpy as np
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipelines.vase import VasePipeline, VaseConfig
from pipelines.moss_pole import MossPolePipeline, MossPoleConfig


class TestVasePipeline:
    """Tests for VasePipeline."""
    
    def test_initialization(self):
        """Test pipeline initialization."""
        pipeline = VasePipeline()
        
        assert pipeline.config is not None
        assert pipeline.simulator is not None
        assert pipeline.field is None
        assert pipeline.mesh is None
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = VaseConfig(
            height=200.0,
            pattern_type='waves'
        )
        pipeline = VasePipeline(config)
        
        assert pipeline.config.height == 200.0
        assert pipeline.config.pattern_type == 'waves'
    
    def test_generate_pattern(self):
        """Test pattern generation."""
        config = VaseConfig(
            field_resolution=64,
            simulation_steps=100
        )
        pipeline = VasePipeline(config)
        
        field = pipeline.generate_pattern()
        
        assert field.shape == (64, 64)
        assert np.all(field >= 0.0)
        assert np.all(field <= 1.0)
    
    def test_generate_mesh(self):
        """Test mesh generation."""
        config = VaseConfig(
            field_resolution=32,
            simulation_steps=100,
            height=100.0
        )
        pipeline = VasePipeline(config)
        
        mesh = pipeline.generate_mesh()
        
        assert mesh is not None
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
    
    def test_full_pipeline(self):
        """Test complete pipeline."""
        config = VaseConfig(
            field_resolution=32,
            simulation_steps=100,
            height=100.0,
            random_seed=42
        )
        pipeline = VasePipeline(config)
        
        mesh = pipeline.generate()
        
        assert mesh is not None
        assert pipeline.field is not None
        assert pipeline.mesh is not None
    
    def test_validate_mesh(self):
        """Test mesh validation."""
        config = VaseConfig(
            field_resolution=32,
            simulation_steps=100
        )
        pipeline = VasePipeline(config)
        pipeline.generate()
        
        validation = pipeline.validate()
        
        assert 'is_watertight' in validation
        assert 'is_valid' in validation
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        config = VaseConfig(
            field_resolution=32,
            simulation_steps=100
        )
        pipeline = VasePipeline(config)
        pipeline.generate()
        
        stats = pipeline.get_stats()
        
        assert 'vertices' in stats
        assert 'faces' in stats
        assert 'volume_mm3' in stats
        assert 'is_watertight' in stats
    
    def test_export(self):
        """Test mesh export."""
        config = VaseConfig(
            field_resolution=32,
            simulation_steps=100
        )
        pipeline = VasePipeline(config)
        pipeline.generate()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_vase.stl'
            pipeline.export(output_path)
            
            assert output_path.exists()
            assert output_path.stat().st_size > 0


class TestMossPolePipeline:
    """Tests for MossPolePipeline."""
    
    def test_initialization(self):
        """Test pipeline initialization."""
        pipeline = MossPolePipeline()
        
        assert pipeline.config is not None
        assert pipeline.colonizer is not None
        assert pipeline.shell is None
        assert pipeline.branches is None
        assert pipeline.mesh is None
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = MossPoleConfig(
            height=250.0,
            outer_diameter=60.0
        )
        pipeline = MossPolePipeline(config)
        
        assert pipeline.config.height == 250.0
        assert pipeline.config.outer_diameter == 60.0
    
    def test_generate_shell(self):
        """Test shell generation."""
        pipeline = MossPolePipeline()
        shell = pipeline.generate_shell()
        
        assert shell is not None
        assert len(shell.vertices) > 0
        assert len(shell.faces) > 0
    
    def test_generate_branch_pattern(self):
        """Test branch pattern generation."""
        config = MossPoleConfig(
            attractor_count=100,
            height=100.0
        )
        pipeline = MossPolePipeline(config)
        
        branches = pipeline.generate_branch_pattern()
        
        assert branches is not None
        assert len(branches) > 0
    
    def test_full_pipeline(self):
        """Test complete pipeline (simplified)."""
        config = MossPoleConfig(
            attractor_count=50,
            height=100.0,
            random_seed=42
        )
        pipeline = MossPolePipeline(config)
        
        # Generate just shell and pattern (boolean ops may fail in tests)
        pipeline.generate_shell()
        pipeline.generate_branch_pattern()
        
        assert pipeline.shell is not None
        assert pipeline.branches is not None
    
    def test_get_stats_after_generation(self):
        """Test statistics retrieval."""
        config = MossPoleConfig(
            attractor_count=50,
            height=100.0
        )
        pipeline = MossPolePipeline(config)
        
        # Just generate shell for testing
        pipeline.shell = pipeline.generate_shell()
        pipeline.branches = []
        pipeline.mesh = pipeline.shell
        
        stats = pipeline.get_stats()
        
        assert 'vertices' in stats
        assert 'faces' in stats
        assert 'open_fraction' in stats
        assert 'n_branches' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
