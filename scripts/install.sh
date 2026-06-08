#!/bin/bash
# Installation script for BEAM-SSZ v0.6

set -e

echo "BEAM-SSZ v0.6 Installation"
echo "=========================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install numpy scipy pytest

# Install package in development mode
echo "Installing BEAM-SSZ..."
pip install -e .

# Run tests
echo ""
echo "Running tests..."
python -m pytest tests/ --tb=no -q

echo ""
echo "=========================="
echo "Installation complete!"
echo "=========================="
echo ""
echo "To use BEAM-SSZ:"
echo "  source .venv/bin/activate"
echo "  python -c 'from beam_ssz import *'"
echo ""
echo "To run tests:"
echo "  python -m pytest tests/ -v"
echo ""
echo "To run analysis:"
echo "  python scripts/analyze_bridge.py --help"
