#!/bin/bash
# Create a new experiment notebook with standard structure

set -e

# Check if name provided
if [ -z "$1" ]; then
    echo "Usage: new-experiment.sh <experiment-name>"
    echo "Example: new-experiment.sh turing_pattern_bowl"
    exit 1
fi

EXPERIMENT_NAME="$1"
NOTEBOOK_PATH="procedural-design/notebooks/experiments/${EXPERIMENT_NAME}.ipynb"
DATE=$(date +"%d/%m/%Y")

# Check if file already exists
if [ -f "$NOTEBOOK_PATH" ]; then
    echo "Error: Experiment '$EXPERIMENT_NAME' already exists!"
    exit 1
fi

# Create notebook with standard structure
cat > "$NOTEBOOK_PATH" << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# EXPERIMENT_NAME_TITLE\n",
    "\n",
    "**Date:** DATE_PLACEHOLDER\n",
    "\n",
    "## Overview\n",
    "\n",
    "Description of the experiment, goals, and expected outcomes.\n",
    "\n",
    "## Dependencies\n",
    "\n",
    "- Taichi >= 1.7.0\n",
    "- NumPy >= 1.21.0\n",
    "- Trimesh >= 3.9.0\n",
    "- Matplotlib >= 3.4.0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Standard library\n",
    "import os\n",
    "from pathlib import Path\n",
    "\n",
    "# Third-party\n",
    "import numpy as np\n",
    "import taichi as ti\n",
    "import trimesh\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# Local (if needed)\n",
    "# from src.utils import mesh, patterns\n",
    "\n",
    "# Initialise Taichi\n",
    "ti.init(arch=ti.cpu)  # Use ti.gpu for GPU acceleration"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Parameters\n",
    "\n",
    "Configure all experiment parameters here."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Simulation parameters\n",
    "params_resolution = 128\n",
    "params_steps = 1000\n",
    "params_dt = 1.0\n",
    "\n",
    "# Algorithm-specific parameters\n",
    "# TODO: Add your parameters here\n",
    "\n",
    "# Output settings\n",
    "params_output_dir = Path('../outputs/meshes/stl')\n",
    "params_random_seed = 42\n",
    "\n",
    "# Set random seed for reproducibility\n",
    "np.random.seed(params_random_seed)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Implementation\n",
    "\n",
    "Core algorithm implementation."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# TODO: Implement your algorithm here"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Visualisation\n",
    "\n",
    "Visualise results and intermediate steps."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# TODO: Add visualisation code"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Export\n",
    "\n",
    "Generate and export mesh."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# TODO: Add mesh generation and export code"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Results & Notes\n",
    "\n",
    "Document findings, interesting parameter combinations, and future directions.\n",
    "\n",
    "### What Worked\n",
    "- \n",
    "\n",
    "### What Didn't Work\n",
    "- \n",
    "\n",
    "### Next Steps\n",
    "- "
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.12.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

# Replace placeholders
TITLE=$(echo "$EXPERIMENT_NAME" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
sed -i.bak "s/EXPERIMENT_NAME_TITLE/$TITLE/" "$NOTEBOOK_PATH"
sed -i.bak "s/DATE_PLACEHOLDER/$DATE/" "$NOTEBOOK_PATH"
rm "${NOTEBOOK_PATH}.bak"

echo "✓ Created new experiment: $NOTEBOOK_PATH"
echo ""
echo "Next steps:"
echo "  1. Open the notebook in Jupyter Lab"
echo "  2. Fill in the experiment description"
echo "  3. Add your parameters and implementation"
echo ""
echo "To open: jupyter lab $NOTEBOOK_PATH"

