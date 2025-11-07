#!/bin/bash
# Set up development environment for procedural design project

set -e

echo "🔧 Setting up development environment..."
echo "========================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "procedural-design/requirements.txt" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

cd procedural-design

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov black flake8 mypy ipykernel

# Install package in development mode
if [ -f "setup.py" ]; then
    echo "Installing package in development mode..."
    pip install -e .
fi

# Set up Jupyter kernel
echo "Setting up Jupyter kernel..."
python3 -m ipykernel install --user --name=procedural-design --display-name="Procedural Design"

# Create output directories if they don't exist
echo "Creating output directories..."
mkdir -p outputs/meshes/stl
mkdir -p outputs/renders
mkdir -p data/parameters

echo ""
echo "✓ Development environment ready!"
echo ""
echo "To activate the environment, run:"
echo "  source procedural-design/venv/bin/activate"
echo ""
echo "To start Jupyter Lab:"
echo "  cd procedural-design && jupyter lab"

