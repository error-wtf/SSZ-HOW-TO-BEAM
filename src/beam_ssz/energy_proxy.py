"""Energy proxy diagnostics - SEPARATE from tensor-derived T_mu_nu.

CRITICAL: These are HEURISTIC/PROXY only.
They CANNOT claim PASS status for energy conditions.
Only tensor-derived T_mu_nu can yield NEC_PASS_NUMERIC, etc.

From ssz-complete-documentation:
- Energy rules concern observed transformation factors (multiplicative)
- NOT statements about global GR energy conservation
- NEVER add SR + GR + "extra" energies linearly (triple counting)
- USE: E_obs = E_rest × (transform factors)
"""

from enum import Enum, auto
from typing import Dict, Any, Tuple
import numpy as np


class EnergyProxyStatus(Enum):
    """Status for HEURISTIC energy diagnostics ONLY.
    
    These are NOT tensor-derived energy conditions.
    They CANNOT auto-claim NEC/WEC/SEC/DEC pass.
    """
    NOT_RUN = "NOT_RUN"
    PROXY_ONLY = "PROXY_ONLY"
    HEURISTIC_PASS = "HEURISTIC_PASS"  # Proxy only, not NEC!
    HEURISTIC_WARNING = "HEURISTIC_WARNING"
    HEURISTIC_FAIL = "HEURISTIC_FAIL"
    TENSOR_REQUIRED = "TENSOR_REQUIRED"  # Need real T_mu_nu


class EnergyProxyDiagnostic:
    """Heuristic energy diagnostic using SSZ proxy methods.
    
    WARNING: This is NOT a substitute for tensor-derived T_mu_nu.
    Any claim like "NEC satisfied" requires genuine tensor calculation.
    """
    
    @staticmethod
    def estimate_energy_density_proxy(
        D: float,
        s: float,
        method: str = "naive"
    ) -> Dict[str, Any]:
        """Estimate energy density via SSZ proxy.
        
        This is a HEURISTIC only.
        It uses D = 1/(1+Xi) as proxy indicator, NOT physical T_00.
        
        Args:
            D: Time dilation factor
            s: Spatial scaling factor
            method: Proxy method name
        
        Returns:
            Dict with proxy estimate and warnings
        """
        # Naive proxy: energy density ∝ (1 - D^2) or similar
        # This is NOT the real T_00 from Einstein tensor!
        
        if method == "naive":
            # Simple proxy: deviation from flat = "energy indicator"
            proxy_energy = abs(1.0 - D**2)
        elif method == "gradient":
            # Would need spatial gradient of D
            proxy_energy = abs(1.0 - D**2)  # Placeholder
        else:
            raise ValueError(f"Unknown proxy method: {method}")
        
        return {
            "proxy_energy_density": proxy_energy,
            "method": method,
            "D": D,
            "s": s,
            "WARNING": "HEURISTIC ONLY - NOT T_mu_nu",
            "CANNOT_CLAIM_NEC": True,
            "status": EnergyProxyStatus.PROXY_ONLY,
        }
    
    @staticmethod
    def check_heuristic_nec(
        energy_proxy: float,
        threshold: float = 0.0,
    ) -> Tuple[EnergyProxyStatus, Dict]:
        """Heuristic "NEC" check - PROXY ONLY.
        
        CRITICAL: This is NOT the real Null Energy Condition.
        Real NEC requires: T_mu_nu k^mu k^nu >= 0 for ALL null k.
        
        This proxy CANNOT claim:
        - "NEC satisfied"
        - "Energy conditions proven"
        - "No exotic matter required"
        
        Args:
            energy_proxy: Heuristic energy density proxy
            threshold: Threshold for warning
        
        Returns:
            Tuple of (status, details)
            
        Status will ALWAYS be PROXY_ONLY or HEURISTIC_*,
        NEVER NEC_PASS_NUMERIC (that requires tensor T_mu_nu).
        """
        details = {
            "energy_proxy": energy_proxy,
            "threshold": threshold,
            "WARNING": "PROXY ONLY - NOT REAL NEC",
            "REAL_NEC_REQUIRES": "tensor-derived T_mu_nu",
        }
        
        if energy_proxy < threshold:
            # Negative proxy energy = heuristic warning
            # But this is NOT a real NEC violation!
            status = EnergyProxyStatus.HEURISTIC_WARNING
            details["interpretation"] = "Heuristic negative - may indicate exotic, but NOT proven"
        else:
            status = EnergyProxyStatus.HEURISTIC_PASS
            details["interpretation"] = "Heuristic positive - but CANNOT claim NEC pass"
        
        # ALWAYS add this warning
        details["FORBIDDEN_CLAIMS"] = [
            "NEC satisfied",
            "Energy conditions proven", 
            "No exotic matter required",
        ]
        
        return status, details
    
    @staticmethod
    def multiplicative_energy_bookkeeping(
        E_rest: float,
        transform_factors: Dict[str, float],
    ) -> Dict[str, Any]:
        """Compute observed energy via multiplicative factors.
        
        From ssz-complete-documentation:
            E_obs = E_rest × (transform factors)
            NOT: SR + GR + "extra" linear addition (triple counting!)
        
        Args:
            E_rest: Rest frame energy
            transform_factors: Dict of transformation factors
        
        Returns:
            Energy with bookkeeping metadata
        """
        # Multiplicative, not additive
        E_obs = E_rest
        factor_product = 1.0
        
        for name, factor in transform_factors.items():
            E_obs *= factor
            factor_product *= factor
        
        return {
            "E_rest": E_rest,
            "E_obs": E_obs,
            "transform_factors": transform_factors,
            "factor_product": factor_product,
            "method": "multiplicative_bookkeeping",
            "WARNING_linear_addition_forbidden": True,
        }


def validate_no_linear_energy_addition(energy_components: Dict[str, float]) -> bool:
    """Check that energies are NOT being added linearly.
    
    From ssz-complete-documentation:
        NEVER add SR + GR + "extra" energies linearly.
    
    This is a validation helper, not a computation.
    
    Args:
        energy_components: Dict of energy contributions
    
    Returns:
        True if multiplicative bookkeeping detected
    """
    # If we see keys like "SR_contribution", "GR_contribution", "extra_contribution"
    # and they look like they're meant to be added, that's suspicious
    
    suspicious_keys = ['sr', 'gr', 'special_relativity', 'general_relativity', 'extra']
    
    has_suspicious = any(
        any(s in k.lower() for s in suspicious_keys)
        for k in energy_components.keys()
    )
    
    if has_suspicious and len(energy_components) > 1:
        # This looks like linear addition pattern
        return False  # Suspicious
    
    return True  # Probably OK
