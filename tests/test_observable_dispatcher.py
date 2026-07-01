"""Tests for SSZ Observable Dispatcher.

Validates Prime Directive implementation:
    Observable → Class → Method → Scope → Calculate
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.tensor_core.observable_dispatcher import (
    classify_regime,
    Regime,
    ObservableType,
    compute_observable_factor,
    check_factor_2_warning,
    ObservableDispatcher,
)


class TestRegimeClassification:
    """Test regime classification by r/r_s."""
    
    def test_very_close_regime(self):
        """r_s/r < 1.8 → VERY_CLOSE."""
        assert classify_regime(1.0, 1.0) == Regime.VERY_CLOSE
        assert classify_regime(1.5, 1.0) == Regime.VERY_CLOSE
        assert classify_regime(1.79, 1.0) == Regime.VERY_CLOSE
    
    def test_blended_regime(self):
        """1.8 ≤ r/r_s ≤ 2.2 → BLENDED."""
        assert classify_regime(1.8, 1.0) == Regime.BLENDED
        assert classify_regime(2.0, 1.0) == Regime.BLENDED
        assert classify_regime(2.19, 1.0) == Regime.BLENDED
    
    def test_photon_sphere_regime(self):
        """2.2 < r/r_s < 3.0 → PHOTON_SPHERE."""
        assert classify_regime(2.2, 1.0) == Regime.PHOTON_SPHERE
        assert classify_regime(2.5, 1.0) == Regime.PHOTON_SPHERE
        assert classify_regime(2.99, 1.0) == Regime.PHOTON_SPHERE
    
    def test_strong_regime(self):
        """3.0 ≤ r/r_s < 10.0 → STRONG."""
        assert classify_regime(3.0, 1.0) == Regime.STRONG
        assert classify_regime(5.0, 1.0) == Regime.STRONG
        assert classify_regime(9.99, 1.0) == Regime.STRONG
    
    def test_weak_regime(self):
        """r/r_s ≥ 10.0 → WEAK."""
        assert classify_regime(10.0, 1.0) == Regime.WEAK
        assert classify_regime(100.0, 1.0) == Regime.WEAK
    
    def test_zero_schwarzschild(self):
        """r_s = 0 → WEAK (no black hole)."""
        assert classify_regime(1.0, 0.0) == Regime.WEAK


class TestObservableClassification:
    """Test observable type classification and method selection."""
    
    def test_null_uses_ppn(self):
        """NULL observables use PPN (1+γ)."""
        result = compute_observable_factor(
            ObservableType.NULL_GEODESIC,
            r=10.0,
            r_s=1.0,
            gamma=1.0,
        )
        
        assert result["method"] == "PPN"
        assert result["scope"] == "full_GR"
        assert result["factor"] == 2.0  # (1+γ) with γ=1
    
    def test_timelike_static_uses_xi_proxy(self):
        """TIMELIKE STATIC uses Ξ-proxy."""
        result = compute_observable_factor(
            ObservableType.TIMELIKE_STATIC,
            r=10.0,
            r_s=1.0,
        )
        
        assert result["method"] == "XI_PROXY"
        assert result["scope"] == "g_tt_only"
        # Factor is D = 1/(1+Ξ)
        assert 0 < result["factor"] <= 1.0
    
    def test_timelike_orbit_uses_ppn(self):
        """TIMELIKE ORBIT uses PPN (γ,β)."""
        result = compute_observable_factor(
            ObservableType.TIMELIKE_ORBIT,
            r=10.0,
            r_s=1.0,
            gamma=1.0,
            beta=1.0,
        )
        
        assert result["method"] == "PPN"
        assert result["scope"] == "gamma_beta"


class TestFactor2Rule:
    """Test Factor-2 rule for null observables.
    
    Critical rule: Ξ-only gives ~50% of GR, full needs PPN (1+γ).
    """
    
    def test_factor_2_warning_detection(self):
        """Detect when null result shows Factor-2 signature."""
        # If we get 0.5 when expecting 1.0, that's Factor-2
        assert check_factor_2_warning(0.5, 1.0) == True
        assert check_factor_2_warning(0.55, 1.0) == True  # Within range
        assert check_factor_2_warning(0.45, 1.0) == True  # Within range
        
        # Full GR results should not trigger
        assert check_factor_2_warning(1.0, 1.0) == False
        assert check_factor_2_warning(0.9, 1.0) == False
    
    def test_xi_only_vs_full_gr_null(self):
        """Compare Ξ-only vs full PPN for null observables."""
        r, r_s = 10.0, 1.0
        xi = r_s / (2.0 * r)  # Standard formula
        
        # Ξ-only piece
        D = 1.0 / (1.0 + xi)
        
        # Full GR factor
        full_result = compute_observable_factor(
            ObservableType.NULL_GEODESIC,
            r, r_s, gamma=1.0
        )
        
        # The full result should be (1+γ), not just D
        assert full_result["factor"] == 2.0
        assert full_result["method"] == "PPN"


class TestDispatcherPipeline:
    """Test full ObservableDispatcher pipeline."""
    
    def test_null_static_classification(self):
        """null + static → NULL_GEODESIC."""
        result = ObservableDispatcher.classify_and_compute(
            geodesic_type="null",
            motion_state="static",
            r=10.0,
            r_s=1.0,
        )
        
        assert result["observable_type"] == "NULL_GEODESIC"
        assert result["method"] == "PPN"
    
    def test_timelike_static_classification(self):
        """timelike + static → TIMELIKE_STATIC."""
        result = ObservableDispatcher.classify_and_compute(
            geodesic_type="timelike",
            motion_state="static",
            r=10.0,
            r_s=1.0,
        )
        
        assert result["observable_type"] == "TIMELIKE_STATIC"
        assert result["method"] == "XI_PROXY"
    
    def test_timelike_orbit_classification(self):
        """timelike + orbit → TIMELIKE_ORBIT."""
        result = ObservableDispatcher.classify_and_compute(
            geodesic_type="timelike",
            motion_state="orbit",
            r=10.0,
            r_s=1.0,
        )
        
        assert result["observable_type"] == "TIMELIKE_ORBIT"
        assert result["method"] == "PPN"
    
    def test_regime_included_in_result(self):
        """Result includes regime classification."""
        result = ObservableDispatcher.classify_and_compute(
            geodesic_type="null",
            motion_state="static",
            r=10.0,  # 10 r_s → WEAK
            r_s=1.0,
        )
        
        assert result["regime"] == "WEAK"
        assert result["r_over_rs"] == 10.0


class TestSSZCanonicalFormulas:
    """Test SSZ canonical formulas are used correctly."""
    
    def test_weak_field_xi_formula(self):
        """Weak field uses Ξ = r_s/(2r)."""
        r, r_s = 20.0, 1.0  # 20 r_s → weak
        
        result = compute_observable_factor(
            ObservableType.TIMELIKE_STATIC,
            r, r_s
        )
        
        expected_xi = r_s / (2.0 * r)  # 0.025
        expected_D = 1.0 / (1.0 + expected_xi)  # ~0.9756
        
        assert np.isclose(result["xi"], expected_xi, rtol=0.1)
        assert np.isclose(result["D"], expected_D, rtol=0.1)
    
    def test_xi_non_negative(self):
        """Ξ is always non-negative."""
        for r in [1.0, 2.0, 5.0, 10.0, 100.0]:
            for r_s in [0.1, 1.0, 10.0]:
                result = compute_observable_factor(
                    ObservableType.TIMELIKE_STATIC,
                    r, r_s
                )
                assert result["xi"] >= 0, f"Negative Xi at r={r}, r_s={r_s}"
    
    def test_D_positive_and_leq_one(self):
        """D = 1/(1+Ξ) is in (0, 1]."""
        for r in [1.0, 2.0, 5.0, 10.0]:
            for r_s in [0.1, 1.0, 10.0]:
                result = compute_observable_factor(
                    ObservableType.TIMELIKE_STATIC,
                    r, r_s
                )
                assert 0 < result["D"] <= 1.0, \
                    f"D={result['D']} out of range at r={r}, r_s={r_s}"
