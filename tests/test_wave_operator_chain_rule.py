from beam_ssz.wave_operator import naive_missing_chain_term, wave_operator_1d_radial


def test_chain_rule_operator_differs_from_naive_for_nonzero_gradient():
    x = 3.0
    # E(x)=x^2 => E'=2x, E''=2. Since s'(x)!=0, the extra chain-rule term matters.
    correct = wave_operator_1d_radial(x, dE_dx=2*x, d2E_dx2=2.0, r_s=1.0)
    naive = naive_missing_chain_term(x, d2E_dx2=2.0, r_s=1.0)
    assert abs(correct - naive) > 1e-4


def test_chain_rule_equals_naive_when_gradient_zero():
    x = 3.0
    correct = wave_operator_1d_radial(x, dE_dx=0.0, d2E_dx2=2.0, r_s=1.0)
    naive = naive_missing_chain_term(x, d2E_dx2=2.0, r_s=1.0)
    assert abs(correct - naive) < 1e-12
