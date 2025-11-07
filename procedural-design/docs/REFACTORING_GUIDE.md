# Refactoring Guide

This guide explains the refactored structure of the procedural design project.

## Overview

The project has been refactored from notebook-only code into a professional, modular structure with:

1. **Reusable algorithm modules** (`src/algorithms/`)
2. **Geometry utilities** (`src/geometry/`)
3. **End-to-end pipelines** (`src/pipelines/`)
4. **CLI tools** for batch processing (`src/cli/`)
5. **Interactive Streamlit app** (`src/app/`)
6. **Comprehensive tests** (`tests/`)

## Project Structure

```
procedural-design/
├── src/
│   ├── algorithms/          # Core generative algorithms
│   │   ├── gray_scott.py    # Reaction-diffusion simulator
│   │   └── space_colonization.py  # Branch growth algorithm
│   ├── geometry/            # Mesh operations
│   │   ├── primitives.py    # Basic shapes
│   │   ├── mesh_operations.py  # Mesh processing
│   │   └── tube_sweep.py    # Tube sweeping
│   ├── pipelines/           # End-to-end workflows
│   │   ├── vase.py          # Vase generation pipeline
│   │   └── moss_pole.py     # Moss pole pipeline
│   ├── cli/                 # Command-line tools
│   │   ├── generate_vase.py
│   │   └── generate_moss_pole.py
│   └── app/                 # Web applications
│       └── streamlit_app.py
├── tests/                   # Comprehensive test suite
│   ├── test_gray_scott.py
│   ├── test_space_colonization.py
│   └── test_pipelines.py
├── notebooks/               # Jupyter notebooks for experimentation
│   ├── 01_refactored_example.ipynb
│   └── experiments/
└── outputs/                 # Generated meshes and renders
    └── meshes/stl/
```

## Key Design Principles

### 1. Separation of Concerns

- **Algorithms** (`src/algorithms/`): Pure algorithm implementations
- **Geometry** (`src/geometry/`): Mesh generation and operations
- **Pipelines** (`src/pipelines/`): Combine algorithms + geometry
- **Interfaces** (`src/cli/`, `src/app/`): User-facing tools

### 2. Configuration Objects

All pipelines use dataclasses for configuration:

```python
from pipelines.vase import VaseConfig, VasePipeline

config = VaseConfig(
    height=150.0,
    pattern_type='spots'
)
pipeline = VasePipeline(config)
```

### 3. CPU/GPU Agnostic

Algorithms support both CPU and GPU:

```python
# CPU
sim = GrayScottSimulator(use_gpu=False)

# GPU (requires Taichi)
sim = GrayScottSimulator(use_gpu=True)
```

### 4. Testability

All components have comprehensive unit tests:

```bash
pytest tests/ -v
```

## Migration Guide

### From Notebook to Module

**Before (in notebook):**

```python
def gray_scott_multi(size=256, steps=20000, ...):
    U = np.ones((size, size))
    V = np.zeros((size, size))
    # ... implementation
    return V

field = gray_scott_multi(size=256, steps=10000)
```

**After (using module):**

```python
from algorithms.gray_scott import GrayScottSimulator, GrayScottConfig

config = GrayScottConfig(pattern_type='spots')
sim = GrayScottSimulator(resolution=256, config=config)
sim.initialize_random(n_seeds=5)
field = sim.run(steps=10000)
```

### From Inline Mesh Code to Pipeline

**Before:**

```python
# 100 lines of mesh generation code in notebook
vertices = []
faces = []
for i in range(h):
    # Complex mesh building logic...
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
mesh.export('output.stl')
```

**After:**

```python
from pipelines.vase import VasePipeline, VaseConfig

config = VaseConfig(height=150.0)
pipeline = VasePipeline(config)
mesh = pipeline.generate()
pipeline.export('output.stl')
```

## Usage Patterns

### 1. Jupyter Notebook Experimentation

Use notebooks for parameter exploration:

```python
# notebooks/experiments/my_experiment.ipynb
from pipelines.vase import VasePipeline, VaseConfig

# Quick iteration
for feed_rate in [0.03, 0.04, 0.05]:
    config = VaseConfig(pattern_type='custom')
    config.feed_rate = feed_rate
    
    pipeline = VasePipeline(config)
    mesh = pipeline.generate()
    pipeline.export(f'vase_f{feed_rate}.stl')
```

### 2. CLI for Production

Use CLI for batch processing:

```bash
# Generate multiple variants
for seed in {1..10}; do
    python src/cli/generate_vase.py \
        --pattern spots \
        --random-seed $seed \
        --output "outputs/vase_$seed.stl"
done
```

### 3. Streamlit for Exploration

Use Streamlit for interactive parameter tuning:

```bash
streamlit run src/app/streamlit_app.py
```

### 4. Python Scripts for Automation

Use modules directly in Python scripts:

```python
# generate_batch.py
from pipelines.vase import VasePipeline, VaseConfig

patterns = ['spots', 'stripes', 'waves']
for pattern in patterns:
    config = VaseConfig(pattern_type=pattern)
    pipeline = VasePipeline(config)
    mesh = pipeline.generate()
    pipeline.export(f'vase_{pattern}.stl')
```

## Testing

### Run All Tests

```bash
cd procedural-design
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Algorithm tests
pytest tests/test_gray_scott.py -v

# Pipeline tests
pytest tests/test_pipelines.py -v

# Taichi GPU tests only
pytest tests/test_gray_scott.py::TestTaichiKernels -v
```

### Skip Taichi Tests

If Taichi isn't installed:

```bash
pytest tests/ -v -m "not taichi"
```

## Best Practices

### 1. Keep Notebooks Clean

- Import from `src/` modules
- Keep notebooks under 100 lines
- Use notebooks for experimentation only
- Extract stable code to `src/`

### 2. Version Control

- Clear notebook outputs before committing
- Use `.gitignore` for generated meshes
- Keep parameter files in `data/parameters/`

### 3. Documentation

- Add docstrings to all functions
- Use type hints
- Include examples in docstrings
- Update README when adding features

### 4. Performance

- Profile before optimising
- Use GPU for large simulations
- Consider batch processing for multiple variants
- Cache expensive computations

## Extending the System

### Adding a New Algorithm

1. Create file in `src/algorithms/`
2. Implement config dataclass
3. Implement algorithm class
4. Add tests in `tests/`
5. Create pipeline in `src/pipelines/`

Example:

```python
# src/algorithms/turing_patterns.py
from dataclasses import dataclass

@dataclass
class TuringConfig:
    """Configuration for Turing pattern."""
    param1: float = 1.0

class TuringSimulator:
    """Turing pattern simulator."""
    def __init__(self, config: TuringConfig):
        self.config = config
    
    def run(self, steps: int):
        # Implementation
        pass
```

### Adding a New Pipeline

1. Create file in `src/pipelines/`
2. Define config with all parameters
3. Implement generation methods
4. Add validation and export
5. Create CLI tool in `src/cli/`

### Adding to Streamlit App

1. Add new page function to `src/app/streamlit_app.py`
2. Add sidebar controls
3. Add generation logic
4. Add visualization and export

## Troubleshooting

### Import Errors

Make sure `src/` is in your Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent / 'src'))
```

### Taichi GPU Issues

If GPU acceleration fails:

```python
# Fall back to CPU
sim = GrayScottSimulator(use_gpu=False)
```

### Mesh Boolean Operations Fail

Boolean operations can be unstable:

```python
# Try simplifying meshes first
mesh = mesh.simplify_quadric_decimation(1000)

# Or use alternative library
import pymeshlab
# ... use MeshLab booleans
```

## Additional Resources

- [Gray-Scott Paper](https://doi.org/10.1016/0009-2509(83)80132-8)
- [Space Colonization](http://algorithmicbotany.org/papers/venation.sig2005.html)
- [Trimesh Documentation](https://trimesh.org/)
- [Taichi Documentation](https://docs.taichi-lang.org/)

