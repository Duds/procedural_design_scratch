# Procedural Design - Refactored

A professional, modular system for generating procedural 3D designs using reaction-diffusion and space colonisation algorithms.

## 🎨 Features

- **Gray-Scott Reaction-Diffusion**: Generate organic patterns for vases and vessels
- **Space Colonisation**: Create perforated structures with branch-like patterns
- **CPU/GPU Support**: Taichi-powered GPU acceleration for fast simulations
- **Multiple Interfaces**: Jupyter notebooks, CLI tools, and interactive Streamlit app
- **Production Ready**: Comprehensive tests, type hints, and documentation
- **3D Print Optimised**: Mesh validation and export to STL/OBJ/PLY formats

## 🚀 Quick Start

### Installation

```bash
cd procedural-design
pip install -r requirements.txt
```

### Generate Your First Vase

**Python:**
```python
from pipelines.vase import VasePipeline, VaseConfig

config = VaseConfig(pattern_type='spots')
pipeline = VasePipeline(config)
mesh = pipeline.generate()
pipeline.export('vase.stl')
```

**CLI:**
```bash
python src/cli/generate_vase.py \
    --pattern spots \
    --output vase.stl \
    --stats
```

**Interactive:**
```bash
streamlit run src/app/streamlit_app.py
```

See [docs/QUICK_START.md](docs/QUICK_START.md) for more examples.

## 📁 Project Structure

```
procedural-design/
├── src/
│   ├── algorithms/          # Core generative algorithms
│   │   ├── gray_scott.py           # Reaction-diffusion (CPU/GPU)
│   │   └── space_colonization.py  # Branch growth
│   ├── geometry/            # Mesh operations
│   │   ├── primitives.py           # Basic shapes
│   │   ├── mesh_operations.py      # Processing & validation
│   │   └── tube_sweep.py           # Tube generation
│   ├── pipelines/           # End-to-end workflows
│   │   ├── vase.py                 # Vase generation
│   │   └── moss_pole.py            # Perforated structures
│   ├── cli/                 # Command-line tools
│   └── app/                 # Streamlit web app
├── tests/                   # Comprehensive test suite
├── notebooks/               # Jupyter notebooks
│   ├── 01_refactored_example.ipynb
│   └── experiments/
└── docs/                    # Documentation
    ├── QUICK_START.md
    └── REFACTORING_GUIDE.md
```

## 🎯 Usage Examples

### 1. Jupyter Notebook Experimentation

```python
# notebooks/experiments/my_experiment.ipynb
from pipelines.vase import VasePipeline, VaseConfig

# Iterate through patterns
for pattern in ['spots', 'stripes', 'waves']:
    config = VaseConfig(pattern_type=pattern)
    pipeline = VasePipeline(config)
    mesh = pipeline.generate()
    pipeline.export(f'vase_{pattern}.stl')
```

### 2. CLI Batch Processing

```bash
# Generate 10 variants with different seeds
for seed in {1..10}; do
    python src/cli/generate_vase.py \
        --random-seed $seed \
        --output "vase_$seed.stl"
done
```

### 3. Python Script Automation

```python
from pipelines.moss_pole import MossPolePipeline, MossPoleConfig

# Generate multiple pole heights
for height in [150, 200, 250]:
    config = MossPoleConfig(height=height)
    pipeline = MossPolePipeline(config)
    mesh = pipeline.generate()
    pipeline.export(f'pole_{height}mm.stl')
```

### 4. Interactive Streamlit App

```bash
streamlit run src/app/streamlit_app.py
```

Provides real-time parameter adjustment with instant preview.

## 🧪 Testing

Run comprehensive test suite:

```bash
# All tests
pytest tests/ -v

# Specific tests
pytest tests/test_gray_scott.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

Tests include:
- Algorithm correctness
- CPU/GPU consistency (Taichi)
- Mesh validation
- Pipeline integration
- Edge cases and performance

## 🛠️ Technology Stack

- **NumPy/SciPy**: Numerical computing
- **Taichi**: GPU acceleration
- **Trimesh**: 3D mesh operations
- **scikit-image**: Marching cubes
- **Matplotlib**: Visualisation
- **Streamlit**: Interactive web app
- **pytest**: Testing framework

## 📖 Documentation

- [QUICK_START.md](docs/QUICK_START.md) - Get started in 5 minutes
- [REFACTORING_GUIDE.md](docs/REFACTORING_GUIDE.md) - Detailed architecture guide
- `.cursor/rules/` - Coding standards and guidelines
- Docstrings - Inline documentation in all modules

## 🎨 Algorithms

### Gray-Scott Reaction-Diffusion

Simulates chemical reactions that produce organic patterns. Parameters:
- **Pattern presets**: spots, stripes, waves, holes
- **Feed rate (F)**: 0.01-0.08
- **Kill rate (k)**: 0.045-0.065
- **Resolution**: 64-512
- **Steps**: 1000-20000

### Space Colonisation

Grows branch-like structures toward attractor points. Parameters:
- **Attractor count**: 500-5000
- **Influence radius**: 5-30 mm
- **Kill radius**: 1-10 mm
- **Step size**: 0.5-5 mm

## 🔧 Development

### Adding New Algorithms

1. Create algorithm in `src/algorithms/`
2. Add config dataclass
3. Write comprehensive tests
4. Create pipeline in `src/pipelines/`
5. Add CLI tool and Streamlit interface

See [REFACTORING_GUIDE.md](docs/REFACTORING_GUIDE.md) for details.

### Code Quality

- Type hints throughout
- Comprehensive docstrings
- Australian English spelling
- Pytest test coverage
- Follows `.cursor/rules/` standards

## 📊 Performance

- **CPU**: NumPy vectorised operations
- **GPU**: Taichi JIT compilation (10-100x speedup)
- **Memory**: Efficient field representations
- **Batch**: CLI tools for parallel processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Follow coding standards in `.cursor/rules/`
5. Submit a pull request

## 📝 License

MIT License

## 🙏 Acknowledgements

- **Gray-Scott Model**: P. Gray & S. K. Scott (1983)
- **Space Colonisation**: Runions et al. (2005)
- **Trimesh**: Michael Dawson-Haggerty
- **Taichi**: Taichi Graphics

## 📞 Support

- Documentation: See `docs/` directory
- Examples: Check `notebooks/` and `tests/`
- Issues: Open a GitHub issue
- Questions: See [QUICK_START.md](docs/QUICK_START.md) and [REFACTORING_GUIDE.md](docs/REFACTORING_GUIDE.md)