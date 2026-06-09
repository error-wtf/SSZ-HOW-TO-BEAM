"""Finite difference operators for tensor derivatives.

Provides numerical differentiation with convergence diagnostics.
"""

import numpy as np
from typing import Callable


def central_diff(
    f: Callable[[np.ndarray], float],
    x: np.ndarray,
    i: int,
    h: float = 1e-5,
) -> float:
    """Central difference for scalar function.
    
    df/dx_i ≈ (f(x + h*e_i) - f(x - h*e_i)) / (2h)
    
    Args:
        f: Scalar function f(x)
        x: Position array [t, r, theta, phi]
        i: Coordinate index to differentiate (0=t, 1=r, 2=theta, 3=phi)
        h: Step size
    
    Returns:
        df/dx_i at position x
    """
    x_plus = x.copy()
    x_minus = x.copy()
    x_plus[i] += h
    x_minus[i] -= h
    return (f(x_plus) - f(x_minus)) / (2.0 * h)


def second_diff(
    f: Callable[[np.ndarray], float],
    x: np.ndarray,
    i: int,
    j: int,
    h: float = 1e-4,
) -> float:
    """Second partial derivative.
    
    d²f/(dx_i dx_j) using central differences.
    
    Args:
        f: Scalar function f(x)
        x: Position array
        i: First coordinate index
        j: Second coordinate index
        h: Step size
    
    Returns:
        d²f/(dx_i dx_j) at position x
    """
    if i == j:
        # Pure second derivative
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[i] += h
        x_minus[i] -= h
        return (f(x_plus) - 2*f(x) + f(x_minus)) / (h**2)
    else:
        # Mixed derivative
        x_pp = x.copy()
        x_pm = x.copy()
        x_mp = x.copy()
        x_mm = x.copy()
        
        x_pp[i] += h; x_pp[j] += h
        x_pm[i] += h; x_pm[j] -= h
        x_mp[i] -= h; x_mp[j] += h
        x_mm[i] -= h; x_mm[j] -= h
        
        return (f(x_pp) - f(x_pm) - f(x_mp) + f(x_mm)) / (4.0 * h**2)


def metric_derivative(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    i: int,
    h: float = 1e-5,
) -> np.ndarray:
    """Derivative of metric tensor g[mu,nu].
    
    Args:
        g_func: Function returning g[mu,nu] at position x
        x: Position array
        i: Coordinate index
        h: Step size
    
    Returns:
        dg/dx_i as array [mu, nu]
    """
    x_plus = x.copy()
    x_minus = x.copy()
    x_plus[i] += h
    x_minus[i] -= h
    
    g_plus = g_func(x_plus)
    g_minus = g_func(x_minus)
    
    return (g_plus - g_minus) / (2.0 * h)


def test_convergence(
    f: Callable[[np.ndarray], float],
    x: np.ndarray,
    i: int,
    analytic_derivative: float,
    h_values: list = None,
) -> dict:
    """Test convergence of finite differences.
    
    Args:
        f: Function to test
        x: Position
        i: Coordinate index
        analytic_derivative: Known exact derivative for comparison
        h_values: List of step sizes (default: [1e-3, 1e-4, 1e-5, 1e-6])
    
    Returns:
        Dict with errors and convergence rate estimate
    """
    if h_values is None:
        h_values = [1e-3, 1e-4, 1e-5, 1e-6]
    
    errors = []
    for h in h_values:
        approx = central_diff(f, x, i, h)
        error = abs(approx - analytic_derivative)
        errors.append(error)
    
    # Estimate convergence rate (should be ~2 for central differences)
    rates = []
    for i in range(len(errors)-1):
        if errors[i+1] > 0 and errors[i] > 0:
            rate = np.log(errors[i] / errors[i+1]) / np.log(h_values[i] / h_values[i+1])
            rates.append(rate)
    
    avg_rate = np.mean(rates) if rates else None
    
    return {
        'h_values': h_values,
        'errors': errors,
        'convergence_rates': rates,
        'average_rate': avg_rate,
        'is_second_order': avg_rate is not None and 1.5 < avg_rate < 2.5,
    }
