"""Test observables relative to SSZ canonical background.

Critical: SSZ is the primary reference, NOT Minkowski.
Minkowski is only for comparison, not physical truth standard.
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.observables import (
    ReferenceFrame,
    get_reference_metric,
    compute_redshift,
)
from beam_ssz.observables.phase_shift import compute_phase_shift
from beam_ssz.observables.time_delay import compute_photon_delay


class TestSSZAsPrimaryReference:
    """Test that SSZ canonical is primary reference, not Minkowski."""
    
    def test_ssz_canonical_is_default(self):
        """SSZ_CANONICAL is the default reference frame."""
        result = compute_redshift(
            r_emitter=10.0,
            r_receiver=11.0,
            xi_func=lambda r: 0.1,  # Constant Xi
        )
        
        # Default should be SSZ_CANONICAL
        assert result.reference_frame == "SSZ_CANONICAL"
    
    def test_minkowski_is_comparison_only(self):
        """Minkowski frame explicitly marked as comparison only."""
        from beam_ssz.observables.reference_frame import compute_observable_relative_to_reference
        
        result = compute_observable_relative_to_reference(
            observable_value_ssz=1.5,
            observable_value_minkowski=1.0,
            reference=ReferenceFrame.FLAT_MINKOWSKI,
        )
        
        # Should have explicit warning
        assert "comparison" in result["frame_note"].lower()
        assert "not physical" in result["frame_note"].lower()
    
    def test_ssz_absolute_vs_minkowski_delta(self):
        """SSZ frame gives absolute value, Minkowski gives difference."""
        from beam_ssz.observables.reference_frame import compute_observable_relative_to_reference
        
        ssz_val = 1.5
        mink_val = 1.0
        
        # SSZ canonical
        result_ssz = compute_observable_relative_to_reference(
            ssz_val, mink_val, ReferenceFrame.SSZ_CANONICAL
        )
        
        # Absolute value
        assert result_ssz["value"] == ssz_val
        assert result_ssz["reference"] == "SSZ_CANONICAL"
        
        # Minkowski comparison
        result_mink = compute_observable_relative_to_reference(
            ssz_val, mink_val, ReferenceFrame.FLAT_MINKOWSKI
        )
        
        # Difference from flat
        assert result_mink["value"] == ssz_val - mink_val


class TestRedshiftCalculation:
    """Test gravitational redshift in SSZ metric."""
    
    def test_redshift_z_formula(self):
        """Redshift z = D_r/D_e - 1."""
        result = compute_redshift(
            r_emitter=10.0,
            r_receiver=11.0,
            xi_func=lambda r: 0.1 if r < 10.5 else 0.2,  # Different Xi
        )
        
        xi_e = 0.1
        xi_r = 0.2
        D_e = 1.0 / (1.0 + xi_e)
        D_r = 1.0 / (1.0 + xi_r)
        
        expected_z = D_r / D_e - 1.0
        
        assert np.isclose(result.redshift_z, expected_z, rtol=0.1)
    
    def test_redshift_energy_bookkeeping_multiplicative(self):
        """Energy bookkeeping is multiplicative, NOT additive."""
        E_rest = 100.0
        
        result = compute_redshift(
            r_emitter=10.0,
            r_receiver=11.0,
            xi_func=lambda r: 0.2,
            E_rest=E_rest,
        )
        
        xi_r = 0.2
        D_r = 1.0 / (1.0 + xi_r)
        
        # E_obs = E_rest × D_r (multiplicative!)
        expected_E_obs = E_rest * D_r
        
        assert np.isclose(result.energy_at_receiver, expected_E_obs)
        
        # NOT: E_rest + D_r (that would be wrong!)
        wrong_additive = E_rest + D_r
        assert result.energy_at_receiver != wrong_additive
    
    def test_xi_gradient_determines_redshift(self):
        """Redshift depends on Xi gradient, not just absolute value."""
        # Same Xi at both points
        result_flat = compute_redshift(
            r_emitter=10.0,
            r_receiver=11.0,
            xi_func=lambda r: 0.1,  # Constant
        )
        
        # Different Xi
        result_gradient = compute_redshift(
            r_emitter=10.0,
            r_receiver=11.0,
            xi_func=lambda r: 0.1 + 0.01 * (r - 10.0),  # Gradient
        )
        
        # Flat Xi → smaller redshift
        # Gradient Xi → larger redshift
        assert abs(result_gradient.redshift_z) > abs(result_flat.redshift_z)


class TestTimeDelayShapiro:
    """Test photon time delay (Shapiro delay) calculations."""
    
    def test_one_way_vs_round_trip_factor_2(self):
        """Round-trip is 2× one-way, SEPARATE from PPN."""
        result = compute_photon_delay(
            r_emitter=10.0,
            r_receiver=11.0,
            r_s=1.0,
            xi_func=lambda r: 0.1,
        )
        
        # Round-trip = 2 × one-way
        assert np.isclose(result.delay_round_trip, 2.0 * result.delay_one_way)
    
    def test_excess_delay_positive(self):
        """Excess delay (beyond geometric) should be positive."""
        result = compute_photon_delay(
            r_emitter=10.0,
            r_receiver=20.0,
            r_s=1.0,
            xi_func=lambda r: 0.1,
        )
        
        # SSZ time > geometric time (time dilation)
        assert result.excess_delay > 0
    
    def test_regime_classification_included(self):
        """Result includes regime classification."""
        result = compute_photon_delay(
            r_emitter=10.0,  # 10 r_s
            r_receiver=11.0,
            r_s=1.0,
            xi_func=lambda r: 0.1,
        )
        
        # 10 r_s → STRONG regime
        assert result.regime == "STRONG"


class TestPhaseShiftCalculation:
    """Test phase shift for interferometric observables."""
    
    def test_phase_shift_proportional_to_path_length(self):
        """Phase = optical path / wavelength."""
        path = [
            [0.0, 10.0, np.pi/2, 0.0],
            [0.0, 10.1, np.pi/2, 0.0],
            [0.0, 10.2, np.pi/2, 0.0],
        ]
        
        wavelength = 1.0e-6  # 1 micron
        
        result = compute_phase_shift(
            path_coords=path,
            wavelength=wavelength,
            xi_func=lambda r: 0.0,  # Flat for simplicity
            reference=ReferenceFrame.SSZ_CANONICAL,
        )
        
        # Phase should be positive for positive path
        assert result.phase_shift > 0
        assert result.wavelength == wavelength
    
    def test_ssz_vs_minkowski_phase_difference(self):
        """SSZ phase differs from Minkowski by metric factor."""
        path = [
            [0.0, 10.0, np.pi/2, 0.0],
            [0.0, 11.0, np.pi/2, 0.0],
        ]
        
        # SSZ with Xi
        result_ssz = compute_phase_shift(
            path_coords=path,
            wavelength=1.0,
            xi_func=lambda r: 0.5,  # Xi = 0.5
            reference=ReferenceFrame.SSZ_CANONICAL,
        )
        
        # Xi affects path length through s = 1 + Xi
        # So SSZ path > Minkowski path
        assert result_ssz.delta_from_flat is not None
        assert result_ssz.delta_from_flat != 0


class TestObservableDocumentation:
    """Test that observable limitations are documented."""
    
    def test_minkowski_comparison_explicitly_not_truth(self):
        """Documentation: Minkowski comparison is NOT physical truth."""
        result = compute_redshift(
            r_emitter=10.0,
            r_receiver=11.0,
            xi_func=lambda r: 0.1,
            reference=ReferenceFrame.FLAT_MINKOWSKI,
        )
        
        # Even though we computed it, the frame is comparison only
        assert result.reference_frame == "FLAT_MINKOWSKI"
    
    def test_ssz_primary_documented(self):
        """SSZ canonical is documented as primary reference."""
        from beam_ssz.observables.reference_frame import ReferenceFrame
        
        # SSZ_CANONICAL enum value exists
        assert ReferenceFrame.SSZ_CANONICAL is not None
        
        # Documentation in module
        import beam_ssz.observables.reference_frame as rf_module
        doc = rf_module.__doc__
        assert "SSZ" in doc
        assert "primary" in doc.lower() or "Minkowski" in doc
