# Cursor Configuration

This directory contains project-specific rules and commands for the procedural design workspace.

## Rules

The `rules/` directory contains coding standards and guidelines that Cursor AI will follow when assisting with this project:

### 📁 `project-structure.md`
- Directory organisation standards
- File naming conventions
- Import organisation
- Code location guidelines

### 📓 `jupyter-notebooks.md`
- Notebook structure and sections
- Cell organisation best practices
- Taichi-specific guidelines
- Visualisation standards
- Export and archiving procedures

### 🎨 `procedural-design.md`
- Algorithmic design principles
- Reaction-diffusion system guidelines
- Space colonisation algorithms
- Mesh generation standards
- Validation requirements

### 🐍 `python-code.md`
- Type hints and typing standards
- Function design principles
- NumPy and Taichi best practices
- Error handling patterns
- Documentation standards

## Commands

The `commands/` directory contains shell scripts to streamline common workflows:

### 🆕 `new-experiment.sh`
Create a new experiment notebook with standard structure.

```bash
.cursor/commands/new-experiment.sh <experiment-name>
```

Example:
```bash
.cursor/commands/new-experiment.sh turing_pattern_bowl
```

### 🚀 `run-experiment.sh`
Execute a notebook experiment and optionally export to HTML.

```bash
.cursor/commands/run-experiment.sh <notebook-path> [--no-export]
```

Example:
```bash
.cursor/commands/run-experiment.sh procedural-design/notebooks/experiments/gray_scott_vase_experiment.ipynb
```

### ✅ `validate-mesh.sh`
Validate exported STL meshes for quality and 3D printing readiness.

```bash
.cursor/commands/validate-mesh.sh <mesh-file.stl>
```

Example:
```bash
.cursor/commands/validate-mesh.sh procedural-design/outputs/meshes/stl/moss_pole_20241105.stl
```

Checks:
- Watertight status
- Face winding consistency
- Degenerate faces
- Duplicate vertices
- Overhang analysis
- Dimensions and volume

### 🧪 `test-all.sh`
Run all unit tests with coverage reporting.

```bash
.cursor/commands/test-all.sh
```

### 🔧 `setup-dev.sh`
Set up complete development environment.

```bash
.cursor/commands/setup-dev.sh
```

This script:
- Creates virtual environment
- Installs all dependencies
- Sets up Jupyter kernel
- Creates output directories
- Installs development tools

### 📦 `archive-experiment.sh`
Move completed experiments to archive folder.

```bash
.cursor/commands/archive-experiment.sh <notebook-name>
```

Example:
```bash
.cursor/commands/archive-experiment.sh gray_scott_vase_experiment
```

## Usage with Cursor

### Applying Rules

Rules are automatically applied based on their glob patterns:
- Rules with `alwaysApply: true` apply to all files
- Specific globs target particular file types (e.g., `**/*.ipynb` for notebooks)

### Running Commands

From the project root, you can run commands directly:

```bash
# Make executable (already done)
chmod +x .cursor/commands/*.sh

# Run any command
./.cursor/commands/new-experiment.sh my_experiment
```

Or add to your shell PATH for easier access:

```bash
export PATH="$PATH:$(pwd)/.cursor/commands"
new-experiment.sh my_experiment
```

## Customisation

Feel free to:
- Add new rules for specific workflows
- Create additional commands for common tasks
- Modify existing rules to match your preferences
- Add project-specific linting rules

## Contributing

When adding new rules or commands:
1. Follow the existing format and structure
2. Include clear documentation
3. Test commands thoroughly
4. Use Australian English spelling
5. Add examples where helpful

