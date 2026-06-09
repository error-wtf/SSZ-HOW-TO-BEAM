"""Energy budget estimation for SSZ effective sources.

Computes integrated energy requirements and localization properties.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum, auto


class LocalizationStatus(Enum):
    """Status of source localization."""
    UNDEFINED = auto()
    LOCALIZED = auto()  # Concentrated in finite region
    EXTENDED = auto()  # Spread over large region
    DIVERGENT = auto()  # Infinite extent or energy


@dataclass
class SourceLocalization:
    """Localization properties of effective source."""
    localization_radius: float  # Characteristic radius containing 90% energy
    total_extent: float  # Full extent of non-negligible source
    peak_position: float  # u coordinate of peak energy density
    concentration_factor: float  # Ratio of peak to average energy
    
    def to_dict(self) -> Dict:
        return {
            'localization_radius': float(self.localization_radius),
            'total_extent': float(self.total_extent),
            'peak_position': float(self.peak_position),
            'concentration_factor': float(self.concentration_factor),
        }


@dataclass
class EnergyBudgetResult:
    """Result of energy budget computation.
    
    Provides estimates of total energy required, without claiming
    such energy can be physically supplied or manipulated.
    """
    # Energy estimates
    total_effective_energy: float  # Integrated T_00 over volume
    energy_density_peak: float  # Maximum energy density
    energy_density_average: float  # Average over bridge region
    
    # Comparison metrics
    schwarzs_mass_equivalent: float  # M = E / c^2
    solar_masses: float  # In units of M_sun
    
    # Localization
    localization: SourceLocalization
    localization_status: LocalizationStatus
    
    # Feasibility proxy (not a claim)
    # Compare to known energy scales
    vs_solar_output: float  # Ratio to solar luminosity * 1 year
    vs_kinetic_energy: float  # Ratio to kinetic energy of moving mass
    
    def to_dict(self) -> Dict:
        return {
            'total_effective_energy': float(self.total_effective_energy),
            'energy_density_peak': float(self.energy_density_peak),
            'energy_density_average': float(self.energy_density_average),
            'schwarzs_mass_equivalent': float(self.schwarzs_mass_equivalent),
            'solar_masses': float(self.solar_masses),
            'localization': self.localization.to_dict(),
            'localization_status': self.localization_status.name,
            'vs_solar_output': float(self.vs_solar_output),
            'vs_kinetic_energy': float(self.vs_kinetic_energy),
        }


def compute_energy_budget(
    bridge,
    n_points: int = 100,
    c: float = 3e8,  # Speed of light m/s
    G: float = 6.674e-11,  # Gravitational constant
) -> EnergyBudgetResult:
    """Compute energy budget for SSZ bridge effective source.
    
    Integrates effective energy density along bridge to estimate
    total energy requirements.
    
    Args:
        bridge: SSZBridgeMetric instance
        n_points: Integration resolution
        c: Speed of light (SI units)
        G: Gravitational constant (SI units)
        
    Returns:
        EnergyBudgetResult with estimates
        
    Note:
        This computes what energy would be required geometrically,
        not whether such energy can be physically concentrated
        or manipulated.
    """
    from .effective_source import compute_effective_source
    
    # Scan along bridge
    u_values = np.linspace(-1, 1, n_points)
    du = 2.0 / n_points
    
    energy_densities = []
    positions = []
    
    for u in u_values:
        result = compute_effective_source(bridge, u)
        
        if result.diagnostics.is_finite:
            # Extract energy density
            rho = result.energy_density
            energy_densities.append(rho)
            positions.append(u)
        else:
            energy_densities.append(0.0)
            positions.append(u)
    
    # Convert to numpy arrays
    energy_densities = np.array(energy_densities)
    positions = np.array(positions)
    
    # Find peak
    peak_idx = np.argmax(np.abs(energy_densities))
    peak_position = positions[peak_idx]
    peak_density = energy_densities[peak_idx]
    
    # Compute average
    avg_density = np.mean(energy_densities)
    
    # Integration: E = ∫ ρ dV
    # For 1D bridge: dV ≈ (throat area) * du * ell0
    # Throat area ≈ π * R_throat^2
    throat_area = np.pi * bridge.throat_radius**2
    
    # Convert from geometrized to SI if needed
    # In geometrized units, energy density has units of 1/length^2
    # To convert to J/m^3: multiply by c^4 / G
    conversion_factor = c**4 / G  # ~ 1.21e44 J/m per unit geometrized energy
    
    # Integrate
    # E = ∫ ρ(u) * A * du * ell0
    # Use np.trapezoid for NumPy 2.0+ compatibility
    if hasattr(np, 'trapezoid'):
        total_energy_geom = np.trapezoid(energy_densities, positions) * throat_area * bridge.ell0
    else:
        total_energy_geom = np.trapz(energy_densities, positions) * throat_area * bridge.ell0
    total_energy_si = total_energy_geom * conversion_factor
    
    # Localization analysis
    # Find where energy density drops to 10% of peak
    threshold = 0.1 * abs(peak_density)
    significant_points = positions[np.abs(energy_densities) > threshold]
    
    if len(significant_points) > 0:
        extent = significant_points[-1] - significant_points[0]
        
        # Find 90% containment radius
        sorted_indices = np.argsort(np.abs(energy_densities))[::-1]
        cumulative = np.cumsum(np.abs(energy_densities[sorted_indices]))
        total = cumulative[-1]
        
        if total > 0:
            containment_idx = np.where(cumulative > 0.9 * total)[0][0]
            containment_radius = abs(positions[sorted_indices[containment_idx]] - peak_position)
        else:
            containment_radius = extent
        
        # Concentration factor
        concentration = abs(peak_density / avg_density) if avg_density != 0 else 1.0
        
        if extent < 2.0:  # Finite region
            loc_status = LocalizationStatus.LOCALIZED
        else:
            loc_status = LocalizationStatus.EXTENDED
    else:
        extent = 0.0
        containment_radius = 0.0
        concentration = 1.0
        loc_status = LocalizationStatus.UNDEFINED
    
    localization = SourceLocalization(
        localization_radius=float(containment_radius * bridge.ell0),  # In meters
        total_extent=float(extent * bridge.ell0),
        peak_position=float(peak_position),
        concentration_factor=float(concentration),
    )
    
    # Schwarzschild mass equivalent
    M_sun = 1.989e30  # kg
    mass_equiv = total_energy_si / c**2
    solar_masses = mass_equiv / M_sun
    
    # Comparisons
    solar_output_1year = 3.828e26 * 365.25 * 24 * 3600  # J
    vs_solar = total_energy_si / solar_output_1year if solar_output_1year > 0 else np.inf
    
    # Kinetic energy comparison: 1 kg at 0.1c
    kinetic_ref = 0.5 * 1.0 * (0.1 * c)**2
    vs_kinetic = total_energy_si / kinetic_ref
    
    return EnergyBudgetResult(
        total_effective_energy=float(total_energy_si),
        energy_density_peak=float(peak_density * conversion_factor),
        energy_density_average=float(avg_density * conversion_factor),
        schwarzs_mass_equivalent=float(mass_equiv),
        solar_masses=float(solar_masses),
        localization=localization,
        localization_status=loc_status,
        vs_solar_output=float(vs_solar),
        vs_kinetic_energy=float(vs_kinetic),
    )


def energy_budget_sensitivity_analysis(
    xi_left_range: Tuple[float, float] = (0.0, 1.0),
    xi_right_range: Tuple[float, float] = (0.0, 1.0),
    lambda_range: Tuple[float, float] = (0.0, 0.5),
    ell0_range: Tuple[float, float] = (1.0, 1000.0),
    n_samples: int = 10,
) -> Dict:
    """Parameter sensitivity analysis for energy budgets.
    
    Scans parameter space to find configurations with minimal
    energy requirements.
    
    Args:
        xi_left_range: Range for left segment density
        xi_right_range: Range for right segment density
        lambda_range: Range for bridge coupling
        ell0_range: Range for bridge scale (meters)
        n_samples: Samples per parameter
        
    Returns:
        Dictionary with sensitivity results
    """
    from ..bridge_metric import SSZBridgeMetric
    
    results = []
    
    # Sample parameter space
    for xi_left in np.linspace(xi_left_range[0], xi_left_range[1], n_samples):
        for xi_right in np.linspace(xi_right_range[0], xi_right_range[1], n_samples):
            for lambda_bridge in np.linspace(lambda_range[0], lambda_range[1], n_samples):
                for ell0 in np.linspace(ell0_range[0], ell0_range[1], n_samples):
                    try:
                        bridge = SSZBridgeMetric(
                            xi_left=float(xi_left),
                            xi_right=float(xi_right),
                            lambda_bridge=float(lambda_bridge),
                            ell0=float(ell0),
                        )
                        
                        budget = compute_energy_budget(bridge)
                        
                        results.append({
                            'xi_left': float(xi_left),
                            'xi_right': float(xi_right),
                            'lambda_bridge': float(lambda_bridge),
                            'ell0': float(ell0),
                            'total_energy': budget.total_effective_energy,
                            'solar_masses': budget.solar_masses,
                            'localization_radius': budget.localization.localization_radius,
                        })
                    except Exception:
                        continue
    
    if not results:
        return {
            'status': 'NO_VALID_CONFIGURATIONS',
            'min_energy_config': None,
            'max_energy_config': None,
        }
    
    # Find extremes
    energies = [r['total_energy'] for r in results]
    min_idx = np.argmin(energies)
    max_idx = np.argmax(energies)
    
    return {
        'status': 'ANALYSIS_COMPLETE',
        'n_configurations_tested': len(results),
        'min_energy_config': results[min_idx],
        'max_energy_config': results[max_idx],
        'energy_range': (float(min(energies)), float(max(energies))),
    }
