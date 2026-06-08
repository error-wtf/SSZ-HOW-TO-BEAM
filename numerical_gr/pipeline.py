#!/usr/bin/env python3
"""
Numerical GR Pipeline for SSZ Bridge Metric Validation
Ready for Einstein Toolkit or standalone execution

This script generates initial data and evolution parameters for
full 3D numerical relativity simulations of the SSZ bridge.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d
import sys
import os

sys.path.insert(0, '../src')
from beam_ssz.bridge_metric import SSZBridgeMetric


class SSZInitialDataGenerator:
    """Generate ADM initial data for numerical GR simulations."""
    
    def __init__(self, bridge: SSZBridgeMetric):
        self.bridge = bridge
        self.n_points = 128  # Standard resolution
        
    def generate_3d_grid(self, domain_size=10.0):
        """
        Generate 3D Cartesian grid for initial data.
        
        Domain: [-domain_size, domain_size]³ in units of ℓ₀
        """
        x = np.linspace(-domain_size, domain_size, self.n_points)
        y = np.linspace(-domain_size, domain_size, self.n_points)
        z = np.linspace(-domain_size, domain_size, self.n_points)
        
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        return X, Y, Z
    
    def compute_conformal_metric(self, X, Y, Z):
        """
        Compute conformal 3-metric γ_ij = ψ⁴ γ̃_ij
        
        For bridge: γ̃_ij ≈ δ_ij (conformally flat approximation)
        ψ = 1 + Ξ/2 (conformal factor from Brill-Lindquist)
        """
        # Radial coordinate in bridge
        r = np.sqrt(X**2 + Y**2 + Z**2)
        
        # Interpolate Xi from 1D bridge to 3D
        u_vals = np.linspace(-1, 1, 100)
        xi_vals = [self.bridge.xi(u) for u in u_vals]
        xi_interp = interp1d(u_vals, xi_vals, kind='cubic', 
                             bounds_error=False, fill_value=0)
        
        # Map 3D r to bridge coordinate u
        # Approximation: u ≈ tanh(r / ell0)
        u_3d = np.tanh(r / self.bridge.ell0)
        
        # Conformal factor
        xi_3d = xi_interp(u_3d)
        psi = 1.0 + xi_3d / 2.0
        
        # 3-metric: γ_ij = ψ⁴ δ_ij (conformally flat)
        gamma_xx = psi**4
        gamma_yy = psi**4
        gamma_zz = psi**4
        
        return gamma_xx, gamma_yy, gamma_zz, psi
    
    def compute_extrinsic_curvature(self, X, Y, Z):
        """
        Compute extrinsic curvature K_ij.
        
        For time-symmetric initial data: K_ij = 0
        For Bowen-York: Solve momentum constraints
        """
        # Start with time-symmetric (simplest)
        K_xx = np.zeros_like(X)
        K_yy = np.zeros_like(X)
        K_zz = np.zeros_like(X)
        K_xy = np.zeros_like(X)
        K_xz = np.zeros_like(X)
        K_yz = np.zeros_like(X)
        
        # TODO: Add Bowen-York data for non-zero momentum
        
        return K_xx, K_yy, K_zz, K_xy, K_xz, K_yz
    
    def check_hamiltonian_constraint(self, gamma, K, psi):
        """
        Check Hamiltonian constraint: R + K² - K_ij K^ij = 16πρ
        
        Should be ~0 for vacuum initial data.
        """
        # Unpack tuples
        gamma_xx, gamma_yy, gamma_zz = gamma
        K_xx, K_yy, K_zz, K_xy, K_xz, K_yz = K
        
        # Compute Ricci scalar R for conformally flat metric
        # R = -8 ψ⁻⁵ ∇²ψ
        
        # Laplacian of psi (finite differences)
        d2psi_dx2 = np.gradient(np.gradient(psi, axis=0), axis=0)
        d2psi_dy2 = np.gradient(np.gradient(psi, axis=1), axis=1)
        d2psi_dz2 = np.gradient(np.gradient(psi, axis=2), axis=2)
        
        laplacian_psi = d2psi_dx2 + d2psi_dy2 + d2psi_dz2
        
        R = -8 * psi**(-5) * laplacian_psi
        
        # K² - K_ij K^ij (trace terms)
        K_trace = K_xx + K_yy + K_zz
        K_squared = K_trace**2
        
        K_ij_Kij = (K_xx**2 + K_yy**2 + K_zz**2 + 
                    2*K_xy**2 + 2*K_xz**2 + 2*K_yz**2)
        
        # Hamiltonian constraint violation
        violation = R + K_squared - K_ij_Kij
        
        max_violation = np.max(np.abs(violation))
        
        return violation, max_violation
    
    def export_to_hdf5(self, filename='ssz_initial_data.h5'):
        """
        Export initial data to HDF5 format for Einstein Toolkit.
        """
        X, Y, Z = self.generate_3d_grid()
        gamma_xx, gamma_yy, gamma_zz, psi = self.compute_conformal_metric(X, Y, Z)
        K_xx, K_yy, K_zz, K_xy, K_xz, K_yz = self.compute_extrinsic_curvature(X, Y, Z)
        
        # Check constraints
        _, max_violation = self.check_hamiltonian_constraint(
            (gamma_xx, gamma_yy, gamma_zz), 
            (K_xx, K_yy, K_zz, K_xy, K_xz, K_yz),
            psi
        )
        
        print(f"Hamiltonian constraint max violation: {max_violation:.2e}")
        
        with h5py.File(filename, 'w') as f:
            # Grid
            f.create_dataset('x', data=X)
            f.create_dataset('y', data=Y)
            f.create_dataset('z', data=Z)
            
            # 3-metric
            f.create_dataset('gamma_xx', data=gamma_xx)
            f.create_dataset('gamma_yy', data=gamma_yy)
            f.create_dataset('gamma_zz', data=gamma_zz)
            
            # Extrinsic curvature
            f.create_dataset('K_xx', data=K_xx)
            f.create_dataset('K_yy', data=K_yy)
            f.create_dataset('K_zz', data=K_zz)
            f.create_dataset('K_xy', data=K_xy)
            f.create_dataset('K_xz', data=K_xz)
            f.create_dataset('K_yz', data=K_yz)
            
            # Conformal factor
            f.create_dataset('psi', data=psi)
            
            # Metadata
            f.attrs['ell0'] = self.bridge.ell0
            f.attrs['throat_radius'] = self.bridge.throat_radius
            f.attrs['xi_left'] = self.bridge.xi_left
            f.attrs['xi_right'] = self.bridge.xi_right
            f.attrs['lambda_bridge'] = self.bridge.lambda_bridge
            f.attrs['constraint_violation'] = max_violation
        
        print(f"Initial data exported to {filename}")


class SSZEvolutionParameters:
    """Generate evolution parameters for numerical GR."""
    
    def __init__(self, bridge: SSZBridgeMetric):
        self.bridge = bridge
    
    def generate_cactus_parfile(self, filename='ssz_bridge.par'):
        """
        Generate Cactus parameter file for Einstein Toolkit.
        """
        parfile = f"""# SSZ Bridge Evolution Parameters
# Generated for Einstein Toolkit / Cactus

ActiveThorns = "
    BSSN
    ADMBase
    TmunuBase
    HydroBase
    IllinoisGRMHD
    Carpet
    CarpetIOHDF5
    CarpetIOASCII
    Time
    Coordinates
"

# Grid structure
Carpet::domain_from_coordbase = yes
CoordBase::domainsize = minmax
CoordBase::xmin = -10.0
CoordBase::xmax = 10.0
CoordBase::ymin = -10.0
CoordBase::ymax = 10.0
CoordBase::zmin = -10.0
CoordBase::zmax = 10.0

# Resolution
Carpet::max_refinement_levels = 3
Carpet::refinement_center_x = 0.0
Carpet::refinement_center_y = 0.0
Carpet::refinement_center_z = 0.0

# Evolution
BSSN::time_evolution_method = "RK4"
BSSN::dt = 0.01

# Initial data
ADMBase::initial_data = "SSZBridge"
ADMBase::initial_lapse = "Psi"
ADMBase::initial_shift = "Zero"

# SSZ Bridge parameters
SSZBridge::ell0 = {self.bridge.ell0}
SSZBridge::throat_radius = {self.bridge.throat_radius}
SSZBridge::xi_left = {self.bridge.xi_left}
SSZBridge::xi_right = {self.bridge.xi_right}
SSZBridge::lambda_bridge = {self.bridge.lambda_bridge}

# Output
CarpetIOHDF5::out_every = 100
CarpetIOHDF5::out_vars = "BSSN::ADMMetric BSSN::ADMCurvature"

# Termination
evolution_time = 100.0
"""
        
        with open(filename, 'w') as f:
            f.write(parfile)
        
        print(f"Cactus parameter file written to {filename}")


def main():
    """Generate initial data for SSZ bridge simulation."""
    
    # Create bridge
    from beam_ssz.bridge_metric import create_canonical_bridge
    
    bridge = create_canonical_bridge(
        xi_a=0.01,  # Weak for stability
        xi_b=0.01,
        lambda_bridge=0.1,  # Below λ_crit
        ell0=1.0,  # Larger for numerics
        throat_radius=10.0,
    )
    
    print("=" * 70)
    print("SSZ Numerical GR Pipeline")
    print("=" * 70)
    print(f"\nBridge parameters:")
    print(f"  ℓ₀ = {bridge.ell0}")
    print(f"  R₀ = {bridge.throat_radius}")
    print(f"  Ξ = {bridge.xi_left}")
    print(f"  λ = {bridge.lambda_bridge}")
    
    # Generate initial data
    print("\nGenerating initial data...")
    generator = SSZInitialDataGenerator(bridge)
    generator.export_to_hdf5('ssz_initial_data.h5')
    
    # Generate evolution parameters
    print("\nGenerating evolution parameters...")
    evo = SSZEvolutionParameters(bridge)
    evo.generate_cactus_parfile('ssz_bridge.par')
    
    print("\n" + "=" * 70)
    print("INITIAL DATA SCAFFOLD GENERATED")
    print("=" * 70)
    print("\n⚠️  Constraint violation nonzero: NOT validated for evolution yet.")
    print(f"    Hamiltonian constraint violation: {ham:.2e}")
    print("\nWhat is missing for validation:")
    print("  - Convergence study: 64³, 128³, 256³ resolution")
    print("  - Constraint violation < 1e-6 (currently too high)")
    print("  - Momentum constraints (not just Hamiltonian)")
    print("  - Full 3D evolution with Einstein Toolkit")
    print("\nNext steps (if pursuing full validation):")
    print("1. Install Einstein Toolkit (https://einsteintoolkit.org/)")
    print("2. Run convergence study at multiple resolutions")
    print("3. Achieve constraint violation < 1e-6")
    print("4. Full evolution: 10^6 CPU-hours on 128 cores")
    print("\nCurrent status: SCAFFOLD ONLY - NOT READY FOR PUBLICATION")
    print("=" * 70)


if __name__ == "__main__":
    main()
