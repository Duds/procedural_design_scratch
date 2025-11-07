#!/bin/bash
# Run a Jupyter notebook experiment and export results

set -e

if [ -z "$1" ]; then
    echo "Usage: run-experiment.sh <notebook-path> [--no-export]"
    echo "Example: run-experiment.sh procedural-design/notebooks/experiments/gray_scott_vase_experiment.ipynb"
    exit 1
fi

NOTEBOOK="$1"
EXPORT_FLAG="${2:-}"

# Check if notebook exists
if [ ! -f "$NOTEBOOK" ]; then
    echo "Error: Notebook not found: $NOTEBOOK"
    exit 1
fi

# Check if jupyter is installed
if ! command -v jupyter &> /dev/null; then
    echo "Error: Jupyter not found. Install with: pip install jupyter"
    exit 1
fi

echo "Running experiment: $NOTEBOOK"
echo "================================"
echo ""

# Run the notebook
jupyter nbconvert --to notebook --execute --inplace "$NOTEBOOK"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Experiment completed successfully!"
    
    if [ "$EXPORT_FLAG" != "--no-export" ]; then
        # Export to HTML for viewing
        HTML_OUTPUT="${NOTEBOOK%.ipynb}.html"
        jupyter nbconvert --to html "$NOTEBOOK" --output "$HTML_OUTPUT"
        echo "✓ Exported results to: $HTML_OUTPUT"
    fi
else
    echo ""
    echo "✗ Experiment failed!"
    exit 1
fi

