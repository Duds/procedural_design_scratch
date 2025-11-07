# Template Meshes

This directory contains seed/template meshes that can be processed with procedural algorithms.

## Directory Structure

```
templates/
├── stl/              # STL format templates
├── obj/              # OBJ format templates
└── README.md         # This file
```

## Workflow

### 1. Create Template in Fusion360 (or other CAD)

Design your base geometry and export as STL:
- File → Export → STL
- Save to `data/templates/stl/`
- Recommended settings:
  - Format: Binary
  - Refinement: High
  - Send to 3D Print Utility: No

### 2. Process with Gray-Scott Algorithm

**Using Python/Jupyter:**

```python
from pipelines.mesh_processor import MeshProcessorPipeline, MeshProcessorConfig
from pathlib import Path

config = MeshProcessorConfig(
    template_path=Path("data/templates/stl/your_template.stl"),
    pattern_type='spots',  # 'spots', 'stripes', 'waves', 'holes'
    displacement_amplitude=8.0,  # Displacement in mm
    simulation_steps=10000,
    random_seed=42
)

pipeline = MeshProcessorPipeline(config)
mesh = pipeline.generate()
pipeline.export('outputs/meshes/stl/processed_result.stl')
```

**Using CLI:**

```bash
python src/cli/process_template.py \
    data/templates/stl/your_template.stl \
    --output outputs/meshes/stl/processed_result.stl \
    --pattern waves \
    --displacement 10 \
    --steps 10000 \
    --stats \
    --visualize
```

### 3. Batch Process Multiple Templates

```bash
# Process all templates in stl/ directory
for template in data/templates/stl/*.stl; do
    filename=$(basename "$template" .stl)
    python src/cli/process_template.py "$template" \
        --output "outputs/meshes/stl/${filename}_processed.stl" \
        --pattern spots \
        --stats
done
```

## Available Pattern Types

- **spots**: Classic spot patterns (cellular)
- **stripes**: Stripe/wave patterns
- **waves**: Larger wavelike structures
- **holes**: Reverse spots (holes instead of bumps)

## Parameters Guide

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `displacement_amplitude` | 8.0 | 1-20 mm | Max displacement from surface |
| `field_resolution` | 256 | 64-512 | Pattern resolution (higher = finer) |
| `simulation_steps` | 10000 | 1000-20000 | Simulation iterations (more = developed) |
| `n_seeds` | 7 | 1-20 | Initial pattern seeds |
| `taper_top` | 0.3 | 0-1 | Reduce effect at top (0=none, 1=full) |
| `taper_bottom` | 0.15 | 0-1 | Reduce effect at bottom |
| `random_seed` | 42 | Any int | For reproducibility |

## Tips

### For Best Results

1. **Template Quality**
   - Ensure mesh is watertight
   - Use high polygon count for smooth displacement
   - Avoid very thin walls (< 2mm)

2. **Pattern Settings**
   - Start with low resolution (128) for testing
   - Increase steps for more developed patterns
   - Use taper to maintain structural integrity at edges

3. **Displacement Amount**
   - Keep displacement < wall thickness/2
   - Test with small values first (2-5mm)
   - Consider support structures if needed

### Troubleshooting

**Pattern looks too chaotic:**
- Reduce `n_seeds` to 3-5
- Increase `simulation_steps` to 15000+
- Try 'stripes' pattern type

**Not enough detail:**
- Increase `field_resolution` to 512
- Increase `displacement_amplitude`
- Ensure template has enough polygons

**Mesh not watertight after processing:**
- Check template is watertight first
- Reduce `displacement_amplitude`
- Avoid very thin template walls

## Example Templates

### Current Templates

- `Gray-Scott Vase v1.stl` - Vase template from Fusion360

### Recommended Template Types

- **Vases/Vessels**: Cylindrical forms work great
- **Planters**: Good for organic textures
- **Lamp Shades**: Patterns create interesting light effects
- **Decorative Objects**: Any surface that benefits from texture

## Advanced Usage

### Custom Pattern Parameters

```python
config = MeshProcessorConfig(
    template_path=Path("data/templates/stl/my_template.stl"),
    pattern_type='custom'  # Use custom feed/kill rates
)

# Access the Gray-Scott config
config.simulator.config.feed_rate = 0.035
config.simulator.config.kill_rate = 0.060
```

### Different Mapping Strategies

The default uses cylindrical coordinate unwrapping. For non-cylindrical objects, you might need to modify `_sample_field_for_vertices()` in `mesh_processor.py`.

## Next Steps

1. Create template in CAD software
2. Export to `data/templates/stl/`
3. Run processing pipeline (notebook or CLI)
4. Export result to `outputs/meshes/stl/`
5. Validate for 3D printing
6. Print and iterate!

