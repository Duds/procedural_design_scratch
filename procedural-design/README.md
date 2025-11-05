# Project Overview

This project implements a procedural design for generating a decorative moss pole using the Gray-Scott reaction-diffusion model. The goal is to create a hollow, perforated structure that mimics natural moss growth patterns.

## Features

- **Gray-Scott Reaction-Diffusion Model**: Utilizes a mathematical model to simulate the growth patterns.
- **Mesh Generation**: Exports the generated patterns as 3D meshes in STL format.
- **Visualization**: Renders the generated patterns for better understanding and presentation.
- **Modular Structure**: Organized into notebooks, source code, outputs, documentation, and tests for ease of use and maintenance.

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd procedural-design
pip install -r requirements.txt
```

## Usage

1. **Run the Jupyter Notebook**: Open the `notebooks/experiments/gray-scott-decorative-moss-pole.ipynb` to experiment with the Gray-Scott model.
2. **Generate Meshes**: The notebook includes code to generate and export the mesh.
3. **Visualize Patterns**: Use the visualization functions in `src/visualization/render.py` to create visual representations of the patterns.

## Directory Structure

```
procedural-design
├── notebooks
│   └── experiments
│       └── gray-scott-decorative-moss-pole.ipynb
├── src
│   ├── utils
│   │   ├── __init__.py
│   │   ├── mesh.py
│   │   └── patterns.py
│   └── visualization
│       ├── __init__.py
│       └── render.py
├── outputs
│   ├── meshes
│   │   └── stl
│   └── renders
├── docs
│   ├── examples
│   └── api
├── data
│   └── parameters
├── tests
│   ├── __init__.py
│   ├── test_mesh.py
│   └── test_patterns.py
├── requirements.txt
├── setup.py
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.