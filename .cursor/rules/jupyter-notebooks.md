---
description: Best practices for Jupyter notebooks in procedural design experiments
globs: ["**/*.ipynb"]
alwaysApply: true
---

# Jupyter Notebook Best Practices

## Notebook Structure

1. **Standard Sections**
   ```
   # Experiment Title
   ## Overview
   ## Setup & Imports
   ## Parameters
   ## Implementation
   ## Visualisation
   ## Export
   ## Results & Notes
   ```

2. **Header Cell Requirements**
   - Title with clear description
   - Date of experiment
   - Dependencies and versions
   - Expected outputs

3. **Import Cell**
   - Always first code cell
   - One cell for all imports
   - Group by: stdlib, third-party, local

## Code Quality in Notebooks

1. **Cell Organisation**
   - One logical operation per cell
   - Keep cells under 50 lines
   - Use markdown to separate sections
   - Clear cell execution order

2. **Variable Naming**
   - Descriptive names (not `x`, `y`, `z`)
   - Use `params_` prefix for parameters
   - Use `mesh_` prefix for mesh objects
   - Use `pattern_` prefix for generated patterns

3. **Comments**
   - Explain algorithm choices
   - Document parameter effects
   - Note performance considerations
   - Link to research papers or resources

## Taichi-Specific Rules

1. **Kernel Definition**
   - Define all kernels early in notebook
   - Document kernel parameters
   - Specify field dimensions clearly
   - Add performance notes

2. **Field Initialisation**
   - Clearly state field sizes
   - Document memory usage for large fields
   - Use appropriate data types (ti.f32, ti.i32)

3. **GPU/CPU Selection**
   - Explicitly specify architecture
   - Document why GPU or CPU chosen
   - Note performance differences

## Visualisation

1. **Plot Configuration**
   - Set figure size explicitly
   - Use clear titles and labels
   - Include colour bars for heatmaps
   - Save high-resolution versions

2. **3D Visualisation**
   - Use consistent camera angles
   - Include scale references
   - Show multiple views if needed
   - Export render settings

3. **Animation**
   - Document frame rate
   - Keep file sizes reasonable
   - Use appropriate formats (mp4, gif)

## Parameters and Configuration

1. **Parameter Cells**
   - Group all parameters in one cell
   - Use clear variable names
   - Include units in comments
   - Document valid ranges

2. **Documentation**
   - Explain parameter effects
   - Reference research papers
   - Note interaction between parameters

## Export and Output

1. **Mesh Export**
   - Check mesh validity before export
   - Use consistent file naming
   - Save metadata with meshes
   - Document units (mm, cm, etc.)

2. **Data Persistence**
   - Save intermediate results
   - Version control parameters
   - Export visualisations
   - Keep experiment logs

## Notebook Maintenance

1. **Before Archiving**
   - Run all cells fresh
   - Clear unnecessary outputs
   - Add final notes section
   - Document what worked/didn't work

2. **Git Practices**
   - Clear outputs before commit (optional)
   - Don't commit large binary outputs
   - Use .gitignore for data files
   - Commit parameter changes separately

## Performance Considerations

1. **Memory Management**
   - Document memory requirements
   - Release large fields when done
   - Use appropriate field sizes
   - Monitor memory usage

2. **Computation Time**
   - Add timing for expensive operations
   - Document expected runtime
   - Use progress bars for long operations
   - Cache expensive computations

## Testing in Notebooks

1. **Validation**
   - Test with small parameters first
   - Verify mesh topology
   - Check for degenerate cases
   - Validate outputs before export

2. **Debugging**
   - Use small test cases
   - Visualise intermediate steps
   - Print field statistics
   - Check array shapes

