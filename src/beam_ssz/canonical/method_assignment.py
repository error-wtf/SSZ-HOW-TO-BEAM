"""Prime Directive: Observable → Class → Method → Scope → Then calculate.

Observable method assignment aligned with ssz-complete-documentation.

Observable Classes:
- NULL_LIGHT_PATH: PPN completion with (1+γ)
- TIMELIKE_STATIC_CLOCK: Ξ direct via D(r)
- TIMELIKE_ORBIT: PPN orbit machinery
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional, List


class ObservableClass(Enum):
    """Classification of SSZ observables."""
    NULL_LIGHT_PATH = auto()       # Light/photon paths
    TIMELIKE_STATIC_CLOCK = auto() # Static clocks, redshift
    TIMELIKE_ORBIT = auto()        # Orbital dynamics
    UNKNOWN = auto()               # Not classified


class Method(Enum):
    """Calculation methods for observables."""
    PPN_COMPLETION = auto()        # NULL: result = Ξ-only × (1+γ)
    XI_DIRECT = auto()             # TIMELIKE STATIC: D(r) = 1/(1+Ξ)
    PPN_ORBIT = auto()             # TIMELIKE ORBIT: full PPN machinery
    BLOCKED_UNKNOWN = auto()       # Unknown: must classify first


# Observable type to class mapping
OBSERVABLE_CLASS_MAP: Dict[str, ObservableClass] = {
    # NULL / light-path observables
    'lensing': ObservableClass.NULL_LIGHT_PATH,
    'shapiro_delay': ObservableClass.NULL_LIGHT_PATH,
    'vlbi': ObservableClass.NULL_LIGHT_PATH,
    'group_delay': ObservableClass.NULL_LIGHT_PATH,
    'light_time_delay': ObservableClass.NULL_LIGHT_PATH,
    'interferometry': ObservableClass.NULL_LIGHT_PATH,
    'phase_shift': ObservableClass.NULL_LIGHT_PATH,
    'photon_delay': ObservableClass.NULL_LIGHT_PATH,
    
    # TIMELIKE STATIC / clock observables
    'redshift': ObservableClass.TIMELIKE_STATIC_CLOCK,
    'time_dilation': ObservableClass.TIMELIKE_STATIC_CLOCK,
    'gps': ObservableClass.TIMELIKE_STATIC_CLOCK,
    'pound_rebka': ObservableClass.TIMELIKE_STATIC_CLOCK,
    'clock': ObservableClass.TIMELIKE_STATIC_CLOCK,
    'gravitational_redshift': ObservableClass.TIMELIKE_STATIC_CLOCK,
    
    # TIMELIKE ORBIT observables
    'perihelion': ObservableClass.TIMELIKE_ORBIT,
    'perihelion_advance': ObservableClass.TIMELIKE_ORBIT,
    'precession': ObservableClass.TIMELIKE_ORBIT,
    'frame_dragging': ObservableClass.TIMELIKE_ORBIT,
    'orbit': ObservableClass.TIMELIKE_ORBIT,
}


# Class to method mapping
CLASS_METHOD_MAP: Dict[ObservableClass, Method] = {
    ObservableClass.NULL_LIGHT_PATH: Method.PPN_COMPLETION,
    ObservableClass.TIMELIKE_STATIC_CLOCK: Method.XI_DIRECT,
    ObservableClass.TIMELIKE_ORBIT: Method.PPN_ORBIT,
    ObservableClass.UNKNOWN: Method.BLOCKED_UNKNOWN,
}


@dataclass
class MethodAssignment:
    """Complete method assignment for an observable."""
    observable_type: str
    observable_class: ObservableClass
    method: Method
    formula_hint: str
    ppn_gamma_factor: Optional[float]  # 2.0 for GR-equivalent
    description: str


def assign_method(observable_type: str) -> MethodAssignment:
    """Assign calculation method to observable type.
    
    Args:
        observable_type: Type of observable (e.g., 'lensing', 'redshift')
        
    Returns:
        MethodAssignment with complete method specification
        
    Raises:
        ValueError: If observable type not recognized
    """
    observable_type_lower = observable_type.lower().replace(' ', '_')
    
    # Get class
    observable_class = OBSERVABLE_CLASS_MAP.get(observable_type_lower, ObservableClass.UNKNOWN)
    
    # Get method
    method = CLASS_METHOD_MAP.get(observable_class, Method.BLOCKED_UNKNOWN)
    
    # Build assignment
    if observable_class == ObservableClass.NULL_LIGHT_PATH:
        return MethodAssignment(
            observable_type=observable_type,
            observable_class=observable_class,
            method=method,
            formula_hint="result = Xi_only × (1+γ)",
            ppn_gamma_factor=2.0,  # GR-equivalent
            description="NULL observable: Use PPN completion with gamma factor",
        )
    
    elif observable_class == ObservableClass.TIMELIKE_STATIC_CLOCK:
        return MethodAssignment(
            observable_type=observable_type,
            observable_class=observable_class,
            method=method,
            formula_hint="D(r) = 1/(1+Ξ(r))",
            ppn_gamma_factor=None,  # Direct Xi, no PPN
            description="TIMELIKE STATIC: Use Ξ directly via D(r)",
        )
    
    elif observable_class == ObservableClass.TIMELIKE_ORBIT:
        return MethodAssignment(
            observable_type=observable_type,
            observable_class=observable_class,
            method=method,
            formula_hint="PPN orbit machinery",
            ppn_gamma_factor=None,
            description="TIMELIKE ORBIT: Use full PPN orbit equations",
        )
    
    else:
        return MethodAssignment(
            observable_type=observable_type,
            observable_class=observable_class,
            method=method,
            formula_hint="UNKNOWN - must classify",
            ppn_gamma_factor=None,
            description="Observable type not classified - BLOCKED",
        )


def validate_observable_method(observable_type: str, 
                                xi_only_result: float,
                                expected_method: Method) -> dict:
    """Validate that observable result matches assigned method.
    
    Args:
        observable_type: Type of observable
        xi_only_result: Result using only Xi (no PPN)
        expected_method: Expected calculation method
        
    Returns:
        Validation report
    """
    assignment = assign_method(observable_type)
    
    is_correct = (assignment.method == expected_method)
    
    # If NULL but Xi-only used without PPN, this is wrong
    if assignment.method == Method.PPN_COMPLETION:
        correct_result = xi_only_result * 2.0  # (1+γ) with γ=1
        warning = "Xi-only result is HALF of correct PPN-completed result"
    else:
        correct_result = xi_only_result
        warning = None
    
    return {
        'observable_type': observable_type,
        'assigned_class': assignment.observable_class.name,
        'assigned_method': assignment.method.name,
        'expected_method': expected_method.name,
        'method_correct': is_correct,
        'xi_only_result': xi_only_result,
        'correct_result': correct_result,
        'warning': warning,
    }


def list_observable_types() -> Dict[ObservableClass, List[str]]:
    """List all classified observable types by class.
    
    Returns:
        Dictionary mapping classes to observable type lists
    """
    result = {
        ObservableClass.NULL_LIGHT_PATH: [],
        ObservableClass.TIMELIKE_STATIC_CLOCK: [],
        ObservableClass.TIMELIKE_ORBIT: [],
        ObservableClass.UNKNOWN: [],
    }
    
    for obs_type, obs_class in OBSERVABLE_CLASS_MAP.items():
        result[obs_class].append(obs_type)
    
    # Convert to regular dict with class names as keys
    return {
        'NULL_LIGHT_PATH': result[ObservableClass.NULL_LIGHT_PATH],
        'TIMELIKE_STATIC_CLOCK': result[ObservableClass.TIMELIKE_STATIC_CLOCK],
        'TIMELIKE_ORBIT': result[ObservableClass.TIMELIKE_ORBIT],
    }


def print_method_catalog():
    """Print human-readable method assignment catalog."""
    catalog = list_observable_types()
    
    print("=" * 70)
    print("SSZ PRIME DIRECTIVE: OBSERVABLE METHOD ASSIGNMENT")
    print("=" * 70)
    print()
    
    print("NULL / LIGHT-PATH OBSERVABLES (PPN Completion):")
    print("-" * 40)
    for obs in catalog['NULL_LIGHT_PATH']:
        print(f"  • {obs}")
    print()
    
    print("TIMELIKE STATIC / CLOCK OBSERVABLES (Ξ Direct):")
    print("-" * 40)
    for obs in catalog['TIMELIKE_STATIC_CLOCK']:
        print(f"  • {obs}")
    print()
    
    print("TIMELIKE ORBIT OBSERVABLES (PPN Orbit):")
    print("-" * 40)
    for obs in catalog['TIMELIKE_ORBIT']:
        print(f"  • {obs}")
    print()
    
    print("=" * 70)
    print("FORMULA SUMMARY:")
    print("-" * 40)
    print("NULL: result = Xi_only × (1+γ)")
    print("      For GR: γ=1, factor = 2")
    print()
    print("TIMELIKE STATIC: D(r) = 1/(1+Ξ(r))")
    print("                 Use Xi directly")
    print()
    print("TIMELIKE ORBIT: Full PPN orbit machinery")
    print("=" * 70)
