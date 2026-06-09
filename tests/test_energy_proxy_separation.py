"""Test separation of heuristic proxy vs tensor-derived energy diagnostics.

CRITICAL: Proxy energy CANNOT claim NEC pass.
Only tensor-derived T_mu_nu can claim energy condition status.
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.energy_proxy import (
    EnergyProxyStatus,
    EnergyProxyDiagnostic,
    validate_no_linear_energy_addition,
)
from beam_ssz.tensor_core import (
    EnergyConditionStatus,
    check_nec,
)


class TestProxyVsTensorSeparation:
    """Test that proxy and tensor statuses are strictly separated."""
    
    def test_proxy_cannot_claim_nec_pass(self):
        """Proxy energy diagnostic CANNOT claim NEC_PASS_NUMERIC."""
        diagnostic = EnergyProxyDiagnostic()
        
        # Even with "positive" heuristic energy
        status, details = diagnostic.check_heuristic_nec(
            energy_proxy=1.0,  # "Positive"
            threshold=0.0,
        )
        
        # Status must be HEURISTIC_*, never NEC_PASS_NUMERIC
        assert status != EnergyProxyStatus.NOT_RUN
        assert status in [
            EnergyProxyStatus.HEURISTIC_PASS,
            EnergyProxyStatus.HEURISTIC_WARNING,
            EnergyProxyStatus.PROXY_ONLY,
        ]
        
        # Explicitly NOT NEC pass
        assert status != EnergyConditionStatus.NEC_PASS_NUMERIC
        assert "NEC" not in status.value or "HEURISTIC" in status.value
    
    def test_proxy_always_has_warning(self):
        """Proxy results always carry WARNING label."""
        diagnostic = EnergyProxyDiagnostic()
        
        result = diagnostic.estimate_energy_density_proxy(
            D=0.5,
            s=2.0,
            method="naive"
        )
        
        assert "WARNING" in result
        assert "HEURISTIC" in result["WARNING"] or "PROXY" in result["WARNING"]
        assert result["CANNOT_CLAIM_NEC"] == True
    
    def test_proxy_includes_forbidden_claims(self):
        """Proxy result lists claims it CANNOT make."""
        diagnostic = EnergyProxyDiagnostic()
        
        status, details = diagnostic.check_heuristic_nec(
            energy_proxy=1.0,
            threshold=0.0,
        )
        
        assert "FORBIDDEN_CLAIMS" in details
        forbidden = details["FORBIDDEN_CLAIMS"]
        
        assert "NEC satisfied" in forbidden
        assert "Energy conditions proven" in forbidden
        assert "No exotic matter required" in forbidden


class TestMultiplicativeEnergyBookkeeping:
    """Test multiplicative vs linear energy accounting."""
    
    def test_multiplicative_not_additive(self):
        """Energy transforms are multiplicative, not additive."""
        diagnostic = EnergyProxyDiagnostic()
        
        E_rest = 100.0
        factors = {
            "time_dilation": 0.5,  # D factor
            "redshift": 0.8,
        }
        
        result = diagnostic.multiplicative_energy_bookkeeping(E_rest, factors)
        
        # E_obs = 100 × 0.5 × 0.8 = 40
        expected = 100.0 * 0.5 * 0.8
        assert np.isclose(result["E_obs"], expected)
        
        # NOT: 100 + 0.5 + 0.8 (that would be wrong!)
        wrong_additive = E_rest + 0.5 + 0.8
        assert result["E_obs"] != wrong_additive
    
    def test_linear_addition_detected_as_suspicious(self):
        """Linear addition pattern is detected."""
        # Suspicious pattern: SR + GR + extra
        suspicious_components = {
            "SR_contribution": 10.0,
            "GR_contribution": 20.0,
            "extra_term": 5.0,
        }
        
        is_ok = validate_no_linear_energy_addition(suspicious_components)
        assert is_ok == False  # Suspicious!
    
    def test_multiplicative_pattern_accepted(self):
        """Multiplicative pattern is accepted."""
        # OK pattern: factors to multiply
        ok_components = {
            "D_factor": 0.5,
            "s_factor": 2.0,
            "redshift": 0.9,
        }
        
        is_ok = validate_no_linear_energy_addition(ok_components)
        assert is_ok == True


class TestHeuristicVsTensorStatusValues:
    """Test that heuristic and tensor status values don't overlap inappropriately."""
    
    def test_proxy_status_values(self):
        """Proxy statuses are distinct from tensor statuses."""
        proxy_statuses = [
            EnergyProxyStatus.NOT_RUN,
            EnergyProxyStatus.PROXY_ONLY,
            EnergyProxyStatus.HEURISTIC_PASS,
            EnergyProxyStatus.HEURISTIC_WARNING,
            EnergyProxyStatus.HEURISTIC_FAIL,
            EnergyProxyStatus.TENSOR_REQUIRED,
        ]
        
        # None of these claim actual NEC pass
        for status in proxy_statuses:
            assert "NEC_PASS" not in status.value
            assert "PASS_NUMERIC" not in status.value
    
    def test_tensor_status_requires_tensor(self):
        """Tensor statuses (NEC_PASS_NUMERIC, etc.) require T_mu_nu."""
        tensor_statuses = [
            EnergyConditionStatus.NEC_PASS_NUMERIC,
            EnergyConditionStatus.NEC_FAIL_NUMERIC,
            EnergyConditionStatus.WEC_PASS_NUMERIC,
            EnergyConditionStatus.WEC_FAIL_NUMERIC,
        ]
        
        for status in tensor_statuses:
            assert "NUMERIC" in status.value
            assert status != EnergyProxyStatus.HEURISTIC_PASS


class TestEnergyProxyDocumentation:
    """Test that proxy results are properly documented as such."""
    
    def test_proxy_energy_is_not_physical_t00(self):
        """Proxy energy is explicitly NOT T_00."""
        diagnostic = EnergyProxyDiagnostic()
        
        result = diagnostic.estimate_energy_density_proxy(D=0.5, s=2.0)
        
        assert result["WARNING"] == "HEURISTIC ONLY - NOT T_mu_nu"
        assert "NOT T_mu_nu" in result["WARNING"]
    
    def test_real_nec_requires_tensor(self):
        """Documentation: real NEC needs tensor T_mu_nu."""
        diagnostic = EnergyProxyDiagnostic()
        
        _, details = diagnostic.check_heuristic_nec(energy_proxy=1.0)
        
        assert "REAL_NEC_REQUIRES" in details
        assert details["REAL_NEC_REQUIRES"] == "tensor-derived T_mu_nu"
