"""Guards against deprecated SSZ formulas.

Detects and blocks use of non-canonical formulas that are
explicitly banned in ssz-complete-documentation.
"""

import re
from typing import List, Dict, Optional


class DeprecatedFormulaError(Exception):
    """Raised when deprecated formula is detected."""
    
    def __init__(self, formula: str, reason: str, suggestion: str):
        self.formula = formula
        self.reason = reason
        self.suggestion = suggestion
        super().__init__(f"Deprecated formula '{formula}': {reason}. {suggestion}")


# Deprecated patterns with reasons and suggestions
DEPRECATED_PATTERNS: Dict[str, Dict] = {
    # HARD FAIL - Never use
    '(r_s/r)^2 * exp': {
        'pattern': r'\(r_s/r\)\^?2.*exp',
        'reason': 'This formula is explicitly banned in canonical SSZ',
        'suggestion': 'Use xi_weak=r_s/(2r) or xi_strong=1-exp(-phi*r_s/r)',
        'severity': 'HARD_FAIL',
    },
    'r_s/r normalized as canonical': {
        'pattern': r'Xi\s*=\s*r_s/r\s+as\s+canonical',
        'reason': 'Xi = r_s/r is toy normalization, not canonical SSZ',
        'suggestion': 'Use xi_canonical(r, r_s) for proper branch selection',
        'severity': 'HARD_FAIL',
    },
    'PHI = 0.208987 as toy': {
        'pattern': r'PHI\s*=\s*0\.208987.*toy',
        'reason': 'PHI is canonical SSZ constant, not toy parameter',
        'suggestion': 'Use PHI from canonical module as fundamental constant',
        'severity': 'HARD_FAIL',
    },
    # WARNINGS - Toy only with explicit disclaimer
    'Xi = r_s/r without disclaimer': {
        'pattern': r'Xi\s*=\s*r_s/r(?!.*toy|!.*legacy)',
        'reason': 'Xi = r_s/r appears without explicit toy/legacy disclaimer',
        'suggestion': 'Add "# TOY NORMALIZATION - NOT CANONICAL" or use xi_canonical()',
        'severity': 'WARNING',
    },
    'Xi(r_s) = 1 as canonical': {
        'pattern': r'Xi\(r_s\)\s*=\s*1',
        'reason': 'Xi(r_s) = 1 is incorrect; canonical value is 0.801711847',
        'suggestion': 'Use XI_HORIZON from canonical.xi module',
        'severity': 'HARD_FAIL',
    },
}


def detect_deprecated_formula(code_or_text: str, 
                                raise_on_hard_fail: bool = True) -> List[Dict]:
    """Detect deprecated formulas in code or text.
    
    Args:
        code_or_text: String to check
        raise_on_hard_fail: If True, raise DeprecatedFormulaError for hard fails
        
    Returns:
        List of detected issues
        
    Raises:
        DeprecatedFormulaError: If hard fail detected and raise_on_hard_fail=True
    """
    issues = []
    
    for name, info in DEPRECATED_PATTERNS.items():
        pattern = info['pattern']
        
        if re.search(pattern, code_or_text, re.IGNORECASE):
            issue = {
                'formula_name': name,
                'pattern': pattern,
                'reason': info['reason'],
                'suggestion': info['suggestion'],
                'severity': info['severity'],
            }
            issues.append(issue)
            
            if info['severity'] == 'HARD_FAIL' and raise_on_hard_fail:
                raise DeprecatedFormulaError(
                    formula=name,
                    reason=info['reason'],
                    suggestion=info['suggestion'],
                )
    
    return issues


def validate_formula_canonical(formula_code: str) -> Dict:
    """Validate that formula code uses only canonical SSZ.
    
    Args:
        formula_code: Code string to validate
        
    Returns:
        Validation report
    """
    try:
        issues = detect_deprecated_formula(formula_code, raise_on_hard_fail=False)
        
        hard_fails = [i for i in issues if i['severity'] == 'HARD_FAIL']
        warnings = [i for i in issues if i['severity'] == 'WARNING']
        
        return {
            'is_canonical': len(hard_fails) == 0,
            'hard_fails': hard_fails,
            'warnings': warnings,
            'message': 'Canonical' if len(hard_fails) == 0 else f'{len(hard_fails)} hard fails',
        }
    except Exception as e:
        return {
            'is_canonical': False,
            'error': str(e),
            'message': f'Validation error: {e}',
        }


def assert_canonical_xi_usage(xi_computation_code: str):
    """Assert that Xi computation uses canonical formulas.
    
    Args:
        xi_computation_code: Code computing Xi
        
    Raises:
        DeprecatedFormulaError: If non-canonical formula detected
    """
    # Check for toy normalization without disclaimer
    if re.search(r'Xi\s*=\s*r_s/r', xi_computation_code):
        if not re.search(r'toy|legacy|normalized.*only', xi_computation_code, re.I):
            raise DeprecatedFormulaError(
                formula='Xi = r_s/r without disclaimer',
                reason='Xi = r_s/r is toy normalization, not canonical',
                suggestion='Use xi_canonical(r, r_s) or add explicit toy disclaimer',
            )
    
    # Check for incorrect horizon value
    if re.search(r'Xi\(r_s\)\s*=\s*1', xi_computation_code):
        raise DeprecatedFormulaError(
            formula='Xi(r_s) = 1',
            reason='Canonical Xi(r_s) = 0.801711847, not 1',
            suggestion='Use XI_HORIZON from canonical.xi module',
        )


def print_deprecated_formula_guide():
    """Print guide for deprecated formulas."""
    print("=" * 70)
    print("DEPRECATED FORMULA GUIDE - CANONICAL SSZ")
    print("=" * 70)
    print()
    print("❌ HARD FAIL (Never use):")
    print("-" * 40)
    for name, info in DEPRECATED_PATTERNS.items():
        if info['severity'] == 'HARD_FAIL':
            print(f"  {name}")
            print(f"    Reason: {info['reason']}")
            print(f"    Fix: {info['suggestion']}")
            print()
    
    print("⚠️  WARNINGS (Toy only with disclaimer):")
    print("-" * 40)
    for name, info in DEPRECATED_PATTERNS.items():
        if info['severity'] == 'WARNING':
            print(f"  {name}")
            print(f"    Reason: {info['reason']}")
            print(f"    Fix: {info['suggestion']}")
            print()
    
    print("=" * 70)
