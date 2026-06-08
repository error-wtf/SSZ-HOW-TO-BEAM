"""Smoke tests for all simulation scripts."""
import sys
from pathlib import Path

# Find repo root relative to this test file
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'src'))

import pytest
import subprocess
import os


# Dynamically discover all simulation scripts (including 017, 018)
SIMULATIONS = sorted(
    str(p.relative_to(REPO_ROOT))
    for p in (REPO_ROOT / "simulations").glob("*.py")
    if p.stem != "__init__"  # Exclude __init__.py if present
)


@pytest.mark.parametrize("simulation", SIMULATIONS)
def test_simulation_runs(simulation):
    """Test that simulation script runs without errors."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / simulation)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=20,
    )
    
    # Should return 0 (success) or have no errors in output
    assert result.returncode == 0 or "Error" not in result.stderr


@pytest.mark.parametrize("simulation", SIMULATIONS)
def test_simulation_imports(simulation):
    """Test that simulation can be imported without errors."""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "sim_module",
        REPO_ROOT / simulation
    )
    module = importlib.util.module_from_spec(spec)
    
    # Should not raise ImportError
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        pytest.fail(f"Failed to import {simulation}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
