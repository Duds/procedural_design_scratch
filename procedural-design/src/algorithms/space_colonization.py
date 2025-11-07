"""Space colonization algorithm for generating branch-like structures.

Based on the algorithm described in:
    Runions, A., Fuhrer, M., Lane, B., Federl, P., Rolland-Lagan, A. G., & Prusinkiewicz, P. (2005).
    Modeling and visualization of leaf venation patterns. ACM Transactions on Graphics, 24(3), 702-711.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np


@dataclass
class SpaceColonizationConfig:
    """Configuration for space colonization algorithm.
    
    Attributes:
        influence_radius: Radius within which attractors influence nodes
        kill_radius: Radius within which attractors are removed
        step_size: Growth step size per iteration
        min_node_spacing: Minimum distance between nodes
        max_iterations: Maximum number of growth iterations
    """
    influence_radius: float = 16.0
    kill_radius: float = 3.5
    step_size: float = 1.8
    min_node_spacing: float = 1.6
    max_iterations: int = 2000


class SpaceColonizationAlgorithm:
    """Space colonization algorithm for organic branching patterns.
    
    This algorithm simulates the growth of plant-like vein structures by
    iteratively growing nodes toward attractor points.
    
    Example:
        >>> config = SpaceColonizationConfig()
        >>> algo = SpaceColonizationAlgorithm(config)
        >>> algo.add_attractors(attractors)
        >>> algo.add_initial_nodes(initial_nodes)
        >>> algo.grow()
        >>> nodes, edges = algo.get_structure()
    """
    
    def __init__(self, config: Optional[SpaceColonizationConfig] = None):
        """Initialize algorithm.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or SpaceColonizationConfig()
        self.nodes: List[np.ndarray] = []
        self.parents: List[int] = []
        self.attractors: np.ndarray = np.array([])
        self.active_attractors: np.ndarray = np.array([])
    
    def add_attractors(self, attractors: np.ndarray) -> None:
        """Add attractor points.
        
        Args:
            attractors: Array of shape (N, 2) or (N, 3) with attractor positions
        """
        self.attractors = attractors.copy()
        self.active_attractors = np.ones(len(attractors), dtype=bool)
    
    def add_initial_nodes(self, nodes: List[np.ndarray]) -> None:
        """Add initial seed nodes.
        
        Args:
            nodes: List of node positions
        """
        self.nodes = [node.copy() for node in nodes]
        self.parents = [-1] * len(nodes)  # -1 indicates root
    
    def _distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        """Calculate distance between two points.
        
        Args:
            p1: First point
            p2: Second point
            
        Returns:
            Euclidean distance
        """
        return np.linalg.norm(p1 - p2)
    
    def _find_closest_node(self, point: np.ndarray) -> Tuple[int, float]:
        """Find closest node to a point.
        
        Args:
            point: Query point
            
        Returns:
            Tuple of (node_index, distance)
        """
        if not self.nodes:
            return -1, float('inf')
        
        distances = [self._distance(point, node) for node in self.nodes]
        min_idx = int(np.argmin(distances))
        return min_idx, distances[min_idx]
    
    def grow_step(self) -> bool:
        """Perform single growth iteration.
        
        Returns:
            True if growth occurred, False otherwise
        """
        if not self.active_attractors.any():
            return False
        
        # Get active attractor indices
        active_idx = np.where(self.active_attractors)[0]
        
        # Accumulate growth directions for each node
        growth_dirs = [np.zeros_like(self.nodes[0]) for _ in self.nodes]
        influence_count = [0] * len(self.nodes)
        
        # Kill attractors that are too close
        attractors_to_remove = set()
        
        for ai in active_idx:
            attractor = self.attractors[ai]
            
            # Find closest node
            closest_idx, dist = self._find_closest_node(attractor)
            
            if closest_idx == -1:
                continue
            
            # Kill if too close
            if dist < self.config.kill_radius:
                attractors_to_remove.add(ai)
                continue
            
            # Influence if within range
            if dist <= self.config.influence_radius:
                direction = attractor - self.nodes[closest_idx]
                direction = direction / (np.linalg.norm(direction) + 1e-8)
                growth_dirs[closest_idx] += direction
                influence_count[closest_idx] += 1
        
        # Remove killed attractors
        for ai in attractors_to_remove:
            self.active_attractors[ai] = False
        
        # Grow new nodes
        new_nodes = []
        new_parents = []
        
        for node_idx, count in enumerate(influence_count):
            if count == 0:
                continue
            
            # Normalize growth direction
            direction = growth_dirs[node_idx] / (np.linalg.norm(growth_dirs[node_idx]) + 1e-8)
            
            # Calculate new node position
            new_pos = self.nodes[node_idx] + direction * self.config.step_size
            
            # Check spacing constraint
            _, min_dist = self._find_closest_node(new_pos)
            if min_dist >= self.config.min_node_spacing * 0.8:
                new_nodes.append(new_pos)
                new_parents.append(node_idx)
        
        # Add new nodes
        if new_nodes:
            self.nodes.extend(new_nodes)
            self.parents.extend(new_parents)
            return True
        
        return False
    
    def grow(self, progress_callback: Optional[callable] = None) -> int:
        """Grow structure until completion or max iterations.
        
        Args:
            progress_callback: Optional callback(iteration, nodes_count)
            
        Returns:
            Number of iterations performed
        """
        for i in range(self.config.max_iterations):
            if not self.grow_step():
                return i + 1
            
            if progress_callback:
                progress_callback(i + 1, len(self.nodes))
        
        return self.config.max_iterations
    
    def get_structure(self) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """Get final node structure.
        
        Returns:
            Tuple of:
                - nodes: Array of shape (N, D) with node positions
                - edges: List of (parent_idx, child_idx) tuples
        """
        nodes = np.array(self.nodes)
        edges = [
            (parent, i)
            for i, parent in enumerate(self.parents)
            if parent >= 0
        ]
        return nodes, edges
    
    def get_polylines(self) -> List[List[np.ndarray]]:
        """Extract continuous polylines from the structure.
        
        Returns:
            List of polylines, where each polyline is a list of points
        """
        # Build adjacency list
        children = [[] for _ in self.nodes]
        for i, parent in enumerate(self.parents):
            if parent >= 0:
                children[parent].append(i)
        
        polylines = []
        
        def trace_branch(start_idx: int) -> List[np.ndarray]:
            """Trace a branch from a node."""
            line = [self.nodes[start_idx]]
            current = start_idx
            
            # Follow chain until branching or leaf
            while len(children[current]) == 1:
                current = children[current][0]
                line.append(self.nodes[current])
            
            # Recurse for branches
            if len(children[current]) > 1:
                for child in children[current]:
                    polylines.extend(trace_branch(child))
            
            return line
        
        # Start from roots
        for i, parent in enumerate(self.parents):
            if parent == -1:
                polylines.append(trace_branch(i))
        
        return polylines
    
    def get_statistics(self) -> dict:
        """Get algorithm statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_nodes': len(self.nodes),
            'active_attractors': int(self.active_attractors.sum()),
            'total_attractors': len(self.attractors),
            'branches': sum(1 for p in self.parents if p == -1),
        }
