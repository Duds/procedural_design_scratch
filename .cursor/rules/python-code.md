---
description: Python coding standards for procedural design project
globs: ["src/**/*.py", "tests/**/*.py"]
alwaysApply: true
---

# Python Code Standards

## Type Hints

1. **Always Use Type Hints**
   ```python
   def generate_mesh(field: np.ndarray, isovalue: float = 0.5) -> trimesh.Trimesh:
       """Generate mesh from scalar field."""
       pass
   ```

2. **Import Types**
   ```python
   from typing import Optional, Tuple, List, Dict
   import numpy as np
   import trimesh
   ```

3. **Complex Types**
   ```python
   Coordinates = Tuple[float, float, float]
   MeshData = Dict[str, np.ndarray]
   ```

## Function Design

1. **Single Responsibility**
   - One function, one purpose
   - Keep functions under 50 lines
   - Extract complex logic
   - Name functions clearly

2. **Parameter Validation**
   ```python
   def apply_diffusion(field: np.ndarray, rate: float) -> np.ndarray:
       """Apply diffusion to field.
       
       Args:
           field: 2D or 3D scalar field
           rate: Diffusion rate (must be positive)
           
       Raises:
           ValueError: If rate is negative or field is invalid
       """
       if rate < 0:
           raise ValueError(f"Rate must be positive, got {rate}")
       if field.ndim not in [2, 3]:
           raise ValueError(f"Field must be 2D or 3D, got {field.ndim}D")
       # Implementation
   ```

3. **Return Types**
   - Be consistent
   - Avoid multiple return types
   - Document return values
   - Use type hints

## Numpy Best Practices

1. **Vectorisation**
   ```python
   # Good: Vectorised
   result = field * diffusion_rate + reaction_term
   
   # Bad: Python loop
   for i in range(len(field)):
       result[i] = field[i] * diffusion_rate + reaction_term[i]
   ```

2. **Array Operations**
   - Use in-place operations when appropriate
   - Avoid unnecessary copies
   - Use views where possible
   - Document array shapes

3. **Broadcasting**
   - Understand broadcasting rules
   - Document expected shapes
   - Add shape assertions
   - Use explicit reshaping

## Taichi Integration

1. **Kernel Definitions**
   ```python
   @ti.kernel
   def update_field(f: ti.template(), dt: float):
       """Update field using reaction-diffusion.
       
       Args:
           f: Taichi field to update
           dt: Timestep
       """
       for i, j in f:
           # Implementation
   ```

2. **Field Access**
   - Use ti.template() for field parameters
   - Document field shapes
   - Handle boundaries explicitly
   - Validate dimensions

3. **Performance**
   - Minimise kernel launches
   - Batch operations
   - Use appropriate data types
   - Profile hotspots

## Error Handling

1. **Specific Exceptions**
   ```python
   class MeshGenerationError(Exception):
       """Raised when mesh generation fails."""
       pass
   
   class InvalidParameterError(ValueError):
       """Raised when parameters are invalid."""
       pass
   ```

2. **Context**
   ```python
   try:
       mesh = generate_mesh(field)
   except Exception as e:
       raise MeshGenerationError(
           f"Failed to generate mesh from field of shape {field.shape}"
       ) from e
   ```

## Documentation

1. **Module Docstrings**
   ```python
   """Mesh generation utilities.
   
   This module provides functions for converting scalar fields to 3D meshes
   using marching cubes and other isosurface extraction algorithms.
   
   Example:
       >>> field = generate_field(128, 128, 128)
       >>> mesh = extract_isosurface(field, isovalue=0.5)
       >>> mesh.export('output.stl')
   """
   ```

2. **Function Docstrings**
   - Use Google or NumPy style
   - Document all parameters
   - Include examples
   - Note performance characteristics

3. **Inline Comments**
   - Explain why, not what
   - Document algorithm choices
   - Note performance implications
   - Reference papers/sources

## Testing

1. **Unit Tests**
   ```python
   def test_mesh_generation():
       """Test basic mesh generation."""
       field = np.random.rand(10, 10, 10)
       mesh = generate_mesh(field)
       
       assert mesh.is_watertight
       assert len(mesh.vertices) > 0
       assert len(mesh.faces) > 0
   ```

2. **Property Tests**
   - Test invariants
   - Verify mathematical properties
   - Check boundary conditions
   - Validate outputs

## Imports Organisation

1. **Standard Order**
   ```python
   # Standard library
   import os
   from pathlib import Path
   
   # Third-party
   import numpy as np
   import taichi as ti
   import trimesh
   
   # Local
   from ..utils import mesh
   from .patterns import gray_scott
   ```

2. **Avoid Star Imports**
   - Never use `from module import *`
   - Be explicit about imports
   - Avoid namespace pollution

## Configuration

1. **Constants**
   ```python
   # At module level
   DEFAULT_RESOLUTION = 128
   DEFAULT_ISOVALUE = 0.5
   MAX_FIELD_SIZE = 512
   ```

2. **Configuration Objects**
   ```python
   @dataclass
   class GrayScottConfig:
       """Configuration for Gray-Scott simulation."""
       feed_rate: float = 0.055
       kill_rate: float = 0.062
       Du: float = 2e-5
       Dv: float = 1e-5
       dt: float = 1.0
   ```

## Performance

1. **Profiling**
   - Use cProfile for bottlenecks
   - Document performance characteristics
   - Set performance targets
   - Benchmark improvements

2. **Memory**
   - Use generators for large datasets
   - Release resources explicitly
   - Monitor memory usage
   - Document memory requirements

3. **Optimisation**
   - Profile before optimising
   - Document optimisations
   - Maintain correctness
   - Benchmark results

