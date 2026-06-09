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

# ALWAYS create and use virtual environment (required for externally-managed systems)
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Try: sudo apt install python3-venv"
        exit 1
    fi
    echo "✓ Virtual environment created in .venv/"
    echo ""
fi

# Verify venv exists and has pip
if [ ! -f ".venv/bin/python" ]; then
    echo "ERROR: Virtual environment is incomplete (no python)"
    echo "Please remove .venv/ and try again"
    exit 1
fi

if [ ! -f ".venv/bin/pip" ]; then
    echo "WARNING: pip not found in venv, ensuring pip is available..."
    .venv/bin/python -m ensurepip --upgrade 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install pip in virtual environment"
        exit 1
    fi
fi

# Activate venv if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to activate virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment activated"
    echo ""
fi

# ALWAYS use venv pip - never system pip
VENV_PIP=".venv/bin/pip"
VENV_PYTHON=".venv/bin/python"

# Upgrade pip in venv
echo "Upgrading pip..."
$VENV_PIP install --upgrade pip

# Installation mode
if [ "$1" == "--dev" ]; then
    echo ""
    echo "Installing in DEVELOPMENT mode..."
    $VENV_PIP install -r requirements-dev.txt
    $VENV_PIP install -e .
    echo ""
    echo "✓ Development installation complete"
    echo "  Includes: pytest, black, ruff, mypy, sphinx"
elif [ "$1" == "--all" ]; then
    echo ""
    echo "Installing with ALL optional dependencies..."
    $VENV_PIP install -r requirements.txt
    $VENV_PIP install h5py sympy matplotlib
    $VENV_PIP install -e .
    echo ""
    echo "✓ Full installation complete"
    echo "  Includes: h5py, sympy, matplotlib"
else
    echo ""
    echo "Installing CORE dependencies only..."
    $VENV_PIP install -r requirements.txt
    $VENV_PIP install -e .
    echo ""
    echo "✓ Core installation complete"
    echo "  For full features, run: ./install.sh --all"
fi

echo ""
echo "=================================="
echo "Testing installation..."
echo "=================================="
echo ""

# Test import using venv python
$VENV_PYTHON -c "import beam_ssz; print(f'Version: {beam_ssz.__version__}')"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation successful!"
    echo ""
    echo "Quick start:"
    echo "  source .venv/bin/activate"
    echo "  $VENV_PYTHON -c \"import beam_ssz; print(beam_ssz.__version__)\""
    echo "  $VENV_PYTHON run_all_modules_test.py           # Quick test (58 modules)"
    echo "  $VENV_PYTHON run_58_modules_complete_verbose.py # Full detail test"
    echo ""
else
    echo ""
    echo "✗ Installation test failed"
    exit 1
fi
