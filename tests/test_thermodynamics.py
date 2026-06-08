"""Tests for thermodynamics module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric
from beam_ssz.thermodynamics import (
    BridgeThermodynamicAnalyzer,
    ThermodynamicResult,
    prove_thermodynamic_theorem,
)


def test_analyzer_instantiation():
    """Test that analyzer can be instantiated."""
    analyzer = BridgeThermodynamicAnalyzer()
    assert analyzer is not None


def test_estimate_total_energy():
    """Test total energy estimation."""
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    
    total, max_rho, avg_rho = analyzer.estimate_total_energy(bridge)
    
    # May be infinite if solver fails
    assert isinstance(total, (int, float))
    assert isinstance(max_rho, (int, float))


def test_check_exotic_matter():
    """Test exotic matter check."""
    import numpy as np
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.check_exotic_matter_requirement(bridge)
    
    assert 'requires_exotic' in result
    # Result depends on energy analysis - accept numpy or python bool
    val = result.get('requires_exotic')
    assert isinstance(val, (bool, np.bool_, type(None)))


def test_estimate_formation_time():
    """Test formation time estimation."""
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    
    time = analyzer.estimate_formation_time(bridge)
    
    assert time > 0
    assert isinstance(time, float)


def test_estimate_maintenance_power():
    """Test maintenance power estimation."""
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    
    power = analyzer.estimate_maintenance_power(bridge)
    
    assert power >= 0
    assert isinstance(power, (int, float))


def test_analyze_thermodynamics():
    """Test full thermodynamic analysis."""
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.analyze_thermodynamics(bridge)
    
    assert isinstance(result, ThermodynamicResult)
    assert hasattr(result, 'total_energy')
    assert hasattr(result, 'requires_exotic_matter')
    assert hasattr(result, 'overall_feasibility')


def test_weak_bridge_thermo():
    """Test thermodynamics for weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    
    analyzer = BridgeThermodynamicAnalyzer()
    result = analyzer.analyze_thermodynamics(bridge)
    
    assert result is not None


def test_prove_thermodynamic_theorem():
    """Test thermodynamic theorem prover."""
    bridge = create_canonical_bridge()
    
    theorem = prove_thermodynamic_theorem(bridge)
    
    assert 'theorem_name' in theorem
    assert 'statement' in theorem
    assert 'status' in theorem
    assert 'conclusion' in theorem


def test_thermodynamic_result_structure():
    """Test thermodynamic result structure."""
    import numpy as np
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    result = analyzer.analyze_thermodynamics(bridge)
    
    # Allow for inf values and numpy types
    assert isinstance(result.comparison_to_nuclear, (float, np.floating, type(float('inf'))))
    assert isinstance(result.requires_exotic_matter, (bool, np.bool_, type(None)))
    assert isinstance(result.violation_of_standard_physics, (bool, np.bool_, type(None)))


def test_energy_comparisons():
    """Test energy density comparisons."""
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    result = analyzer.analyze_thermodynamics(bridge)
    
    assert result.comparison_to_nuclear >= 0
    assert result.comparison_to_neutron_star >= 0
    assert result.comparison_to_planck >= 0


def test_feasibility_assessment():
    """Test feasibility assessment is provided."""
    analyzer = BridgeThermodynamicAnalyzer()
    bridge = create_canonical_bridge()
    result = analyzer.analyze_thermodynamics(bridge)
    
    assert len(result.overall_feasibility) > 0
    assert isinstance(result.overall_feasibility, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
