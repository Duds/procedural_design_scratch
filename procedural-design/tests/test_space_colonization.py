"""Tests for space colonisation algorithm."""

import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from algorithms.space_colonization import (
    SpaceColonizationAlgorithm,
    SpaceColonizationConfig
)


class TestSpaceColonizationConfig:
    """Tests for SpaceColonizationConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SpaceColonizationConfig()
        
        assert config.influence_radius > 0
        assert config.kill_radius > 0
        assert config.kill_radius < config.influence_radius
        assert config.step_size > 0
        assert config.min_node_spacing > 0
        assert config.max_iterations > 0


class TestSpaceColonizationAlgorithm:
    """Tests for SpaceColonizationAlgorithm."""
    
    def test_initialization(self):
        """Test algorithm initialization."""
        algo = SpaceColonizationAlgorithm()
        
        assert len(algo.nodes) == 0
        assert len(algo.parents) == 0
        assert len(algo.attractors) == 0
    
    def test_add_attractors(self):
        """Test adding attractors."""
        algo = SpaceColonizationAlgorithm()
        
        attractors = np.random.rand(100, 2) * 100
        algo.add_attractors(attractors)
        
        assert len(algo.attractors) == 100
        assert algo.active_attractors.sum() == 100
    
    def test_add_initial_nodes(self):
        """Test adding initial nodes."""
        algo = SpaceColonizationAlgorithm()
        
        nodes = [
            np.array([0.0, 0.0]),
            np.array([10.0, 0.0]),
            np.array([0.0, 10.0])
        ]
        
        algo.add_initial_nodes(nodes)
        
        assert len(algo.nodes) == 3
        assert len(algo.parents) == 3
        assert all(p == -1 for p in algo.parents)  # All roots
    
    def test_grow_step_no_attractors(self):
        """Test that growth stops without attractors."""
        algo = SpaceColonizationAlgorithm()
        
        algo.add_initial_nodes([np.array([0.0, 0.0])])
        
        result = algo.grow_step()
        
        assert result is False
        assert len(algo.nodes) == 1  # No growth
    
    def test_grow_step_basic(self):
        """Test basic growth step."""
        config = SpaceColonizationConfig(
            influence_radius=20.0,
            kill_radius=5.0,
            step_size=2.0
        )
        algo = SpaceColonizationAlgorithm(config)
        
        # Add initial node
        algo.add_initial_nodes([np.array([0.0, 0.0])])
        
        # Add attractor in range
        algo.add_attractors(np.array([[10.0, 0.0]]))
        
        # Should grow
        result = algo.grow_step()
        
        assert result is True
        assert len(algo.nodes) > 1
    
    def test_grow_kills_close_attractors(self):
        """Test that close attractors are killed."""
        config = SpaceColonizationConfig(
            kill_radius=5.0,
            influence_radius=20.0
        )
        algo = SpaceColonizationAlgorithm(config)
        
        # Add initial node
        algo.add_initial_nodes([np.array([0.0, 0.0])])
        
        # Add close attractor
        algo.add_attractors(np.array([[2.0, 0.0]]))
        
        assert algo.active_attractors[0] is True
        
        # Growth step should kill it
        algo.grow_step()
        
        assert algo.active_attractors[0] is False
    
    def test_full_growth(self):
        """Test full growth until completion."""
        config = SpaceColonizationConfig(
            influence_radius=15.0,
            kill_radius=3.0,
            step_size=2.0,
            max_iterations=1000
        )
        algo = SpaceColonizationAlgorithm(config)
        
        # Add initial nodes
        algo.add_initial_nodes([
            np.array([0.0, 0.0]),
            np.array([100.0, 100.0])
        ])
        
        # Add random attractors
        np.random.seed(42)
        attractors = np.random.rand(50, 2) * 100
        algo.add_attractors(attractors)
        
        # Grow
        iterations = algo.grow()
        
        assert iterations > 0
        assert iterations <= config.max_iterations
        assert len(algo.nodes) > 2  # Should have grown
    
    def test_get_structure(self):
        """Test getting final structure."""
        algo = SpaceColonizationAlgorithm()
        
        algo.add_initial_nodes([
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
        ])
        
        # Manually add a child
        algo.nodes.append(np.array([2.0, 0.0]))
        algo.parents.append(1)
        
        nodes, edges = algo.get_structure()
        
        assert len(nodes) == 3
        assert len(edges) == 1
        assert edges[0] == (1, 2)
    
    def test_get_polylines(self):
        """Test extracting polylines."""
        algo = SpaceColonizationAlgorithm()
        
        # Create simple tree structure
        # Root: 0
        # Chain: 0 -> 1 -> 2 -> 3
        algo.nodes = [
            np.array([0.0, 0.0]),
            np.array([1.0, 0.0]),
            np.array([2.0, 0.0]),
            np.array([3.0, 0.0]),
        ]
        algo.parents = [-1, 0, 1, 2]
        
        polylines = algo.get_polylines()
        
        assert len(polylines) > 0
        assert all(isinstance(line, list) for line in polylines)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        algo = SpaceColonizationAlgorithm()
        
        algo.add_initial_nodes([np.array([0.0, 0.0])])
        algo.add_attractors(np.random.rand(10, 2) * 100)
        
        stats = algo.get_statistics()
        
        assert 'total_nodes' in stats
        assert 'active_attractors' in stats
        assert 'total_attractors' in stats
        assert 'branches' in stats
        
        assert stats['total_nodes'] == 1
        assert stats['total_attractors'] == 10
        assert stats['active_attractors'] == 10
        assert stats['branches'] == 1
    
    def test_min_node_spacing(self):
        """Test minimum node spacing constraint."""
        config = SpaceColonizationConfig(
            min_node_spacing=5.0,
            influence_radius=20.0,
            step_size=1.0
        )
        algo = SpaceColonizationAlgorithm(config)
        
        algo.add_initial_nodes([np.array([0.0, 0.0])])
        algo.add_attractors(np.array([[10.0, 0.0]]))
        
        # Grow multiple steps
        for _ in range(10):
            if not algo.grow_step():
                break
        
        # Check spacing between all nodes
        for i, node1 in enumerate(algo.nodes):
            for j, node2 in enumerate(algo.nodes):
                if i != j:
                    dist = np.linalg.norm(node1 - node2)
                    # Should respect spacing (with some tolerance for algorithm)
                    if dist > 0:
                        assert dist >= config.min_node_spacing * 0.7
    
    def test_reproducibility(self):
        """Test that results are reproducible."""
        config = SpaceColonizationConfig()
        
        def run_growth(seed):
            algo = SpaceColonizationAlgorithm(config)
            algo.add_initial_nodes([np.array([0.0, 0.0])])
            
            np.random.seed(seed)
            attractors = np.random.rand(20, 2) * 100
            algo.add_attractors(attractors)
            
            algo.grow()
            return algo.get_structure()
        
        nodes1, edges1 = run_growth(42)
        nodes2, edges2 = run_growth(42)
        
        assert np.allclose(nodes1, nodes2)
        assert edges1 == edges2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

