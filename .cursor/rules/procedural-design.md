---
description: Domain-specific rules for procedural design and generative algorithms
globs: ["src/**/*.py", "**/*.ipynb"]
alwaysApply: true
---

# Procedural Design Guidelines

## Algorithmic Design Principles

1. **Parametric Control**
   - Expose meaningful parameters
   - Use normalised ranges (0-1) where appropriate
   - Provide sensible defaults
   - Document parameter effects with examples

2. **Deterministic by Default**
   - Use seeded random number generators
   - Document random seed usage
   - Allow reproducibility
   - Save seed with outputs

3. **Scale Independence**
   - Work in normalised coordinates
   - Scale as final step
   - Document expected scale
   - Provide unit conversion utilities

## Reaction-Diffusion Systems

1. **Gray-Scott Parameters**
   - Feed rate (f): typical range 0.01-0.08
   - Kill rate (k): typical range 0.045-0.065
   - Diffusion rates: Du = 2e-5, Dv = 1e-5
   - Document pattern regime chosen

2. **Stability**
   - Verify stability criteria
   - Use appropriate timesteps
   - Check for numerical issues
   - Monitor conservation

3. **Initial Conditions**
   - Document perturbation strategy
   - Use consistent random seeds
   - Consider boundary conditions
   - Test multiple initialisations

## Space Colonisation Algorithms

1. **Attraction Points**
   - Document distribution method
   - Specify attraction radius
   - Define kill distance
   - Consider point density

2. **Growth Parameters**
   - Step size (branch segments)
   - Influence radius
   - Branch thickness rules
   - Termination criteria

3. **Structure Validation**
   - Check connectivity
   - Verify no orphan branches
   - Test structural integrity
   - Validate growth bounds

## Mesh Generation

1. **Topology**
   - Ensure manifold meshes
   - Check for holes
   - Verify normals consistency
   - Remove duplicate vertices

2. **Quality**
   - Avoid degenerate triangles
   - Maintain reasonable aspect ratios
   - Check edge lengths
   - Verify volume closure

3. **Resolution**
   - Balance detail vs file size
   - Document polygon count
   - Consider target application (3D print, render)
   - Provide decimation options

## Field-Based Generation

1. **Field Setup**
   - Define field dimensions
   - Choose appropriate resolution
   - Consider boundary conditions
   - Document memory requirements

2. **Marching Cubes**
   - Choose appropriate isovalue
   - Smooth before extraction
   - Handle boundary cases
   - Verify mesh closure

3. **Performance**
   - Use appropriate field size
   - Consider GPU acceleration
   - Profile bottlenecks
   - Document computation time

## Organic Forms

1. **Natural Patterns**
   - Reference biological systems
   - Understand growth mechanisms
   - Use appropriate noise functions
   - Consider scaling laws

2. **Structural Integrity**
   - Ensure printability (if applicable)
   - Maintain wall thickness
   - Check for overhangs
   - Consider support structures

3. **Aesthetics**
   - Balance order and chaos
   - Consider visual weight
   - Test at different scales
   - Iterate on feedback

## Optimisation

1. **Computational Efficiency**
   - Use vectorised operations
   - Leverage Taichi JIT compilation
   - Minimise Python loops
   - Profile before optimising

2. **Memory Efficiency**
   - Use appropriate data types
   - Release unused fields
   - Stream large data
   - Consider sparse representations

3. **Parameter Space**
   - Use grid search for exploration
   - Document interesting regions
   - Automate batch generation
   - Version control parameters

## Validation

1. **Mathematical Correctness**
   - Verify algorithm implementation
   - Check against references
   - Test edge cases
   - Validate assumptions

2. **Physical Constraints**
   - Check real-world dimensions
   - Verify material requirements
   - Consider manufacturing limits
   - Test structural analysis

3. **Visual Quality**
   - Render from multiple angles
   - Check at different scales
   - Verify pattern continuity
   - Test lighting conditions

## Documentation

1. **Algorithm Description**
   - Cite original papers
   - Explain modifications
   - Document parameters
   - Provide examples

2. **Usage Examples**
   - Show basic usage
   - Demonstrate parameter effects
   - Include visualisations
   - Provide benchmark results

3. **Experiment Notes**
   - Record what worked
   - Document failures
   - Note interesting discoveries
   - Link related experiments

