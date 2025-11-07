# Quick Start Guide

## Installation

```bash
cd procedural-design
pip install -r requirements.txt
```

## Generate Your First Vase (5 minutes)

### Option 1: Using Python

```python
from pipelines.vase import VasePipeline, VaseConfig

# Create configuration
config = VaseConfig(
    height=150.0,
    pattern_type='spots',
    random_seed=42
)

# Generate
pipeline = VasePipeline(config)
mesh = pipeline.generate()

# Export
pipeline.export('my_first_vase.stl')
```

### Option 2: Using CLI

```bash
python src/cli/generate_vase.py \
    --height 150 \
    --pattern spots \
    --output my_first_vase.stl \
    --stats \
    --validate
```

### Option 3: Using Streamlit (Interactive)

```bash
streamlit run src/app/streamlit_app.py
```

Then:
1. Adjust parameters in sidebar
2. Click "Generate Vase"
3. Download STL file

## Generate Your First Moss Pole (5 minutes)

### Using Python

```python
from pipelines.moss_pole import MossPolePipeline, MossPoleConfig

config = MossPoleConfig(
    height=200.0,
    attractor_count=2000
)

pipeline = MossPolePipeline(config)
mesh = pipeline.generate()
pipeline.export('my_first_pole.stl')
```

### Using CLI

```bash
python src/cli/generate_moss_pole.py \
    --height 200 \
    --attractors 2000 \
    --output my_first_pole.stl \
    --stats
```

## Experiment in Jupyter (10 minutes)

1. Start Jupyter Lab:

```bash
jupyter lab
```

1. Open `notebooks/01_refactored_example.ipynb`

2. Run all cells to see both vase and moss pole generation

3. Experiment with parameters!

## Run Tests

```bash
pytest tests/ -v
```

## Next Steps

- Read [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) for detailed architecture
- Explore `notebooks/experiments/` for more examples
- Check `.cursor/rules/` for coding guidelines
- Try different pattern presets: 'spots', 'stripes', 'waves', 'holes'

## Common Parameters

### Vase Generator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| height | float | 150.0 | Vase height in mm |
| base_size | float | 80.0 | Base dimension in mm |
| profile_type | str | 'square' | 'circle', 'square', 'hexagon' |
| pattern_type | str | 'spots' | 'spots', 'stripes', 'waves', 'holes' |
| displacement_amplitude | float | 6.0 | Displacement in mm |
| simulation_steps | int | 10000 | More = finer patterns |

### Moss Pole Generator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| outer_diameter | float | 50.0 | Diameter in mm |
| height | float | 200.0 | Height in mm |
| tunnel_radius | float | 1.5 | Perforation size in mm |
| attractor_count | int | 2000 | Branch density |
| n_ribs | int | 4 | Structural ribs |

## Tips

1. **Start small**: Use low resolution (64-128) and fewer steps (1000-5000) for testing
2. **GPU acceleration**: Set `use_gpu=True` if you have Taichi GPU support
3. **Reproducibility**: Set `random_seed` for consistent results
4. **Validation**: Always run `pipeline.validate()` before 3D printing
5. **Batch processing**: Use CLI tools for generating multiple variants

## Troubleshooting

**Q: Generation is slow**
- Lower `field_resolution` and `simulation_steps`
- Enable GPU with `use_gpu=True`

**Q: Mesh has holes**
- Increase `simulation_steps` for better patterns
- Check `mesh.is_watertight` property
- Run with `--validate` flag in CLI

**Q: Pattern looks wrong**
- Try different `pattern_type` presets
- Adjust `feed_rate` and `kill_rate` manually
- Increase `simulation_steps`

**Q: Import errors**
- Make sure you're in the `procedural-design/` directory
- Check Python path includes `src/`

## Getting Help

- Check [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)
- Look at test files in `tests/` for examples
- Read docstrings in source code
- Check `.cursor/rules/` for coding standards

