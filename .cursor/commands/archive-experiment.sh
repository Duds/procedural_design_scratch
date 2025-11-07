#!/bin/bash
# Archive a completed experiment

set -e

if [ -z "$1" ]; then
    echo "Usage: archive-experiment.sh <notebook-name>"
    echo "Example: archive-experiment.sh gray_scott_vase_experiment"
    exit 1
fi

NOTEBOOK_NAME="$1"
SOURCE="procedural-design/notebooks/experiments/${NOTEBOOK_NAME}.ipynb"
DEST="procedural-design/notebooks/archived_experiments/${NOTEBOOK_NAME}.ipynb"

# Check if source exists
if [ ! -f "$SOURCE" ]; then
    echo "Error: Experiment not found: $SOURCE"
    exit 1
fi

# Check if already archived
if [ -f "$DEST" ]; then
    echo "Error: Experiment already archived: $DEST"
    echo "Use a different name or remove the archived version first"
    exit 1
fi

# Move to archive
echo "Archiving experiment: $NOTEBOOK_NAME"
mv "$SOURCE" "$DEST"

# Create archive note
DATE=$(date +"%d/%m/%Y")
echo "Archived on: $DATE" >> procedural-design/notebooks/archived_experiments/ARCHIVE_LOG.txt
echo "  - $NOTEBOOK_NAME" >> procedural-design/notebooks/archived_experiments/ARCHIVE_LOG.txt

echo "✓ Experiment archived successfully!"
echo ""
echo "Location: $DEST"

