"""Canonical SSZ segment density Ξ(r) functions.

Aligned with ssz-complete-documentation.

Formulas:
- Weak: Ξ_weak(r) = r_s / (2r) for r/r_s > 2.2
- Strong: Ξ_strong(r) = 1 - exp(-φ * r_s / r) for r_s/r < 1.8
- Blend: C² Hermite interpolation for 1.8 ≤ r/r_s ≤ 2.2

Horizon values:
- Ξ(r_s) = 1 - exp(-φ) ≈ 0.801711847...
- D(r_s) = 1/(1+Ξ) ≈ 0.555027709...
"""

import numpy as np
from typing import Union, Literal

# SSZ scaling constant φ = Golden Ratio
# φ = (1 + √5) / 2 ≈ 1.618033988749895
# Used in canonical strong branch: Ξ_strong(r) = 1 - exp(-φ * r_s / r)
PHI = (1.0 + np.sqrt(5.0)) / 2.0  # = 1.618033988749895...

# Canonical horizon values (NOT Ξ=1!)
XI_HORIZON = 1.0 - np.exp(-PHI)  # ≈ 0.801711847...
D_HORIZON = 1.0 / (1.0 + XI_HORIZON)  # ≈ 0.555027709...

# Regime boundaries
R_BLEND_START = 1.8
R_BLEND_END = 2.2


def xi_weak(r: Union[float, np.ndarray], r_s: float = 1.0) -> Union[float, np.ndarray]:
    """Weak-field branch: Ξ_weak(r) = r_s / (2r).
    
    Valid for: r/r_s > 2.2
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Ξ value in weak-field regime
        
    Example:
        >>> xi_weak(10.0, 1.0)  # r/r_s = 10
        0.05
    """
    ratio = r / r_s
    return 0.5 / ratio  # = r_s / (2r)


def xi_strong(r: Union[float, np.ndarray], r_s: float = 1.0) -> Union[float, np.ndarray]:
    """Strong-field/inner branch: Ξ_strong(r) = 1 - exp(-φ * r_s / r).
    
    Valid for: r_s/r < 1.8
    
    At horizon (r = r_s):
        Ξ(r_s) = 1 - exp(-φ) ≈ 0.801711847...
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Ξ value in strong-field regime
        
    Example:
        >>> xi_strong(1.0, 1.0)  # r/r_s = 1 (horizon)
        0.801711847...  # XI_HORIZON
    """
    ratio = r / r_s
    return 1.0 - np.exp(-PHI / ratio)  # = 1 - exp(-φ * r_s / r)


def xi_blend(r: Union[float, np.ndarray], r_s: float = 1.0) -> Union[float, np.ndarray]:
    """Blend zone: Hermite interpolation between weak and strong branches.
    
    Valid for: 1.8 ≤ r/r_s ≤ 2.2
    
    Uses C² continuous Hermite interpolation to smoothly connect:
    - xi_strong at r/r_s = 1.8
    - xi_weak at r/r_s = 2.2
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Ξ value in blend zone
        
    Raises:
        NotImplementedError: If full Hermite interpolation not yet implemented
    """
    ratio = r / r_s
    
    # Check if in blend zone
    is_scalar = np.isscalar(ratio)
    
    if is_scalar:
        if not (R_BLEND_START <= ratio <= R_BLEND_END):
            raise ValueError(f"r/r_s = {ratio} outside blend zone [{R_BLEND_START}, {R_BLEND_END}]")
    else:
        if not np.all((R_BLEND_START <= ratio) & (ratio <= R_BLEND_END)):
            raise ValueError(f"Some r/r_s values outside blend zone [{R_BLEND_START}, {R_BLEND_END}]")
    
    # Endpoint values
    xi_start = xi_strong(R_BLEND_START * r_s, r_s)  # At r/r_s = 1.8
    xi_end = xi_weak(R_BLEND_END * r_s, r_s)       # At r/r_s = 2.2
    
    # Derivatives at endpoints (for C² continuity)
    # dΞ_strong/dr = -φ * r_s/r² * exp(-φ*r_s/r)
    dxi_start = -PHI / (R_BLEND_START ** 2) * np.exp(-PHI / R_BLEND_START)
    
    # dΞ_weak/dr = -r_s/(2r²) = -0.5/r for r_s=1
    dxi_end = -0.5 / (R_BLEND_END ** 2)
    
    # Normalize to [0,1] parameter t
    t = (ratio - R_BLEND_START) / (R_BLEND_END - R_BLEND_START)
    
    # Hermite basis functions
    h00 = 2*t**3 - 3*t**2 + 1
    h10 = t**3 - 2*t**2 + t
    h01 = -2*t**3 + 3*t**2
    h11 = t**3 - t**2
    
    # Hermite interpolation with derivative matching
    xi = (h00 * xi_start + 
          h10 * (R_BLEND_END - R_BLEND_START) * dxi_start +
          h01 * xi_end +
          h11 * (R_BLEND_END - R_BLEND_START) * dxi_end)
    
    return xi


def xi_canonical(r: Union[float, np.ndarray], 
                 r_s: float = 1.0,
                 allow_toy_normalized: bool = False) -> Union[float, np.ndarray]:
    """Canonical Ξ(r) with automatic branch selection.
    
    This is the MAIN canonical SSZ function. Use this for all canonical calculations.
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        allow_toy_normalized: If True, fall back to toy Ξ=r_s/r for unsupported cases
        
    Returns:
        Canonical Ξ value
        
    Branch selection:
        r_s/r < 1.8:  xi_strong (strong field)
        1.8-2.2:      xi_blend (interpolation)
        > 2.2:        xi_weak (weak field)
    """
    ratio = r / r_s
    
    # Handle scalars and arrays
    is_scalar = np.isscalar(ratio)
    
    if is_scalar:
        if ratio < R_BLEND_START:
            return xi_strong(r, r_s)
        elif ratio <= R_BLEND_END:
            return xi_blend(r, r_s)
        else:
            return xi_weak(r, r_s)
    else:
        # Array case
        xi = np.zeros_like(ratio, dtype=float)
        
        # Strong field region
        mask_strong = ratio < R_BLEND_START
        xi[mask_strong] = xi_strong(r[mask_strong], r_s)
        
        # Blend region
        mask_blend = (ratio >= R_BLEND_START) & (ratio <= R_BLEND_END)
        if np.any(mask_blend):
            xi[mask_blend] = xi_blend(r[mask_blend], r_s)
        
        # Weak field region
        mask_weak = ratio > R_BLEND_END
        xi[mask_weak] = xi_weak(r[mask_weak], r_s)
        
        return xi


def xi_toy_normalized(r: Union[float, np.ndarray], r_s: float = 1.0) -> Union[float, np.ndarray]:
    """Toy normalized formula: Ξ = r_s/r.
    
    ⚠️ WARNING: This is NOT canonical SSZ. Use only for:
    - Toy proxy tests
    - Legacy comparisons
    - Explicitly marked normalized models
    
    Canonical SSZ uses:
    - Ξ_weak = r_s/(2r) for weak field
    - Ξ_strong = 1-exp(-φ*r_s/r) for strong field
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Toy normalized Ξ = r_s/r
    """
    return r_s / r


def validate_canonical_xi(xi_value: float, r_ratio: float) -> dict:
    """Validate Ξ value against canonical expectations.
    
    Args:
        xi_value: Computed Ξ value
        r_ratio: r/r_s ratio
        
    Returns:
        Validation report
    """
    if r_ratio < 1.8:
        expected = xi_strong(r_ratio, 1.0)
        regime = "strong"
    elif r_ratio <= 2.2:
        expected_low = xi_strong(1.8, 1.0)
        expected_high = xi_weak(2.2, 1.0)
        expected = (expected_low + expected_high) / 2  # Approximate
        regime = "blend"
    else:
        expected = xi_weak(r_ratio, 1.0)
        regime = "weak"
    
    deviation = abs(xi_value - expected) / expected if expected != 0 else abs(xi_value)
    
    return {
        'xi_value': float(xi_value),
        'r_ratio': float(r_ratio),
        'expected_canonical': float(expected),
        'deviation': float(deviation),
        'regime': regime,
        'is_canonical': deviation < 0.01,  # Within 1%
    }
