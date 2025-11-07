---
description: Project structure and organisation rules for procedural design project
globs: ["**/*"]
alwaysApply: true
---

# Project Structure Rules

## Directory Organisation

1. **Main Project Location**
   - All project code lives in `procedural-design/`
   - Keep the root directory clean and minimal
   - No loose files in root except README.md

2. **Notebooks Organisation**
   - Active experiments: `procedural-design/notebooks/experiments/`
   - Archived/completed work: `procedural-design/notebooks/archived_experiments/`
   - Test notebooks: `procedural-design/notebooks/` (root level)
   - Name format: `{technique}_{object}_experiment.ipynb`

3. **Source Code Structure**
   ```
   src/
   ├── utils/          # Mesh operations, pattern generation
   ├── visualization/  # Rendering and display utilities
   └── models/         # Procedural generation algorithms
   ```

4. **Outputs Organisation**
   ```
   outputs/
   ├── meshes/
   │   └── stl/        # Final STL exports
   ├── renders/        # Images and visualisations
   └── data/           # Intermediate data files
   ```

5. **Documentation**
   - API docs: `docs/api/`
   - Examples: `docs/examples/`
   - Experiment notes: Include in notebook markdown cells

## File Naming Conventions

1. **Notebooks**
   - Use lowercase with underscores
   - Include experiment type and object
   - Example: `gray_scott_vase_experiment.ipynb`

2. **Python Modules**
   - Lowercase with underscores for modules
   - PascalCase for classes
   - snake_case for functions

3. **Output Files**
   - Include date stamp: `YYYYMMDD_description.stl`
   - Use descriptive names: `moss_pole_pattern_v2.stl`

## Import Organisation

1. **Standard Library** (first)
2. **Third-party Libraries** (numpy, taichi, trimesh, etc.)
3. **Local Modules** (from src/)

## Code Location Rules

1. **Keep in Notebooks (During Experimentation)**
   - Quick prototypes and iterations
   - Visual experimentation
   - Parameter tuning

2. **Move to src/ (When Stable)**
   - Reusable functions
   - Core algorithms
   - Utilities used across experiments

3. **Never Duplicate**
   - Don't copy-paste between notebooks
   - Extract to src/ and import instead
   - Use relative imports from src/

