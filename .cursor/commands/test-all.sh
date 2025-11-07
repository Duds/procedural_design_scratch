#!/bin/bash
# Run all tests for the procedural design project

set -e

cd procedural-design

echo "🧪 Running all tests..."
echo "======================"
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest pytest-cov
fi

# Run tests with coverage
python3 -m pytest tests/ -v --cov=src --cov-report=term-missing

echo ""
echo "✓ All tests completed!"

