#!/bin/bash
#
# SSZ-HOW-TO-BEAM v1.0.0 Installation Script
# For Linux/macOS
#

set -e

echo "=================================="
echo "SSZ-HOW-TO-BEAM v1.0.0 Installer"
echo "=================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "Error: Python 3.10 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python version check passed ($PYTHON_VERSION)"
echo ""

# Detect if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Note: Not in a virtual environment."
    echo "Recommended: Create a venv first:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Installation mode
if [ "$1" == "--dev" ]; then
    echo "Installing in DEVELOPMENT mode..."
    pip install -r requirements-dev.txt
    pip install -e .
    echo ""
    echo "✓ Development installation complete"
    echo "  Includes: pytest, black, ruff, mypy, sphinx"
elif [ "$1" == "--all" ]; then
    echo "Installing with ALL optional dependencies..."
    pip install -r requirements.txt
    pip install h5py sympy matplotlib
    pip install -e .
    echo ""
    echo "✓ Full installation complete"
    echo "  Includes: h5py, sympy, matplotlib"
else
    echo "Installing CORE dependencies only..."
    pip install -r requirements.txt
    pip install -e .
    echo ""
    echo "✓ Core installation complete"
    echo "  For full features, run: ./install.sh --all"
fi

echo ""
echo "=================================="
echo "Testing installation..."
echo "=================================="
echo ""

# Test import
python3 -c "import beam_ssz; print(f'Version: {beam_ssz.__version__}')"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation successful!"
    echo ""
    echo "Quick start:"
    echo "  python3 -c \"import beam_ssz; print(beam_ssz.__version__)\""
    echo "  python3 -m pytest tests/ -q"
    echo ""
else
    echo ""
    echo "✗ Installation test failed"
    exit 1
fi
