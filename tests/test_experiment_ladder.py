"""Tests for experiment ladder module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.experiment_ladder import (
    ExperimentLadder,
    ExperimentLevel,
)


def test_all_levels_defined():
    """Test that all 7 levels are defined."""
    levels = ExperimentLadder.get_all_levels()
    assert len(levels) == 7
    
    expected = [
        ExperimentLevel.LEVEL_0_FOUNDATIONAL,
        ExperimentLevel.LEVEL_1_PHOTON,
        ExperimentLevel.LEVEL_2_ATOMIC_CLOCK,
        ExperimentLevel.LEVEL_3_COLD_ATOM,
        ExperimentLevel.LEVEL_4_MESOSCOPIC,
        ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT,
        ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN,
    ]
    
    for level in expected:
        assert level in levels


def test_level_0_properties():
    """Test Level 0 (Foundational) properties."""
    stage = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_0_FOUNDATIONAL)
    
    assert stage.name == "Mathematical Consistency"
    assert "mathematical" in stage.description.lower()
    assert len(stage.required_observables) > 0
    assert "Mathematical models" in stage.allowed_test_systems


def test_level_6_is_forbidden():
    """Test Level 6 is explicitly forbidden."""
    stage = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN)
    
    assert "FORBIDDEN" in stage.name
    assert len(stage.allowed_test_systems) == 0
    assert len(stage.required_observables) == 0
    assert len(stage.pass_criteria) == 0
    assert len(stage.forbidden_claims) > 0


def test_progression_rules():
    """Test level progression rules."""
    # Can progress from 0 to 1
    assert ExperimentLadder.can_progress_to(
        ExperimentLevel.LEVEL_0_FOUNDATIONAL,
        ExperimentLevel.LEVEL_1_PHOTON,
    )
    
    # Cannot skip levels
    assert not ExperimentLadder.can_progress_to(
        ExperimentLevel.LEVEL_0_FOUNDATIONAL,
        ExperimentLevel.LEVEL_2_ATOMIC_CLOCK,
    )
    
    # Cannot progress to biological
    assert not ExperimentLadder.can_progress_to(
        ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT,
        ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN,
    )


def test_is_level_allowed():
    """Test level allowance check."""
    assert ExperimentLadder.is_level_allowed(ExperimentLevel.LEVEL_0_FOUNDATIONAL)
    assert ExperimentLadder.is_level_allowed(ExperimentLevel.LEVEL_1_PHOTON)
    assert ExperimentLadder.is_level_allowed(ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT)
    
    # Level 6 is NOT allowed
    assert not ExperimentLadder.is_level_allowed(ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN)


def test_each_level_has_required_observables():
    """Test that levels 0-5 have required observables."""
    levels_to_check = [
        ExperimentLevel.LEVEL_0_FOUNDATIONAL,
        ExperimentLevel.LEVEL_1_PHOTON,
        ExperimentLevel.LEVEL_2_ATOMIC_CLOCK,
        ExperimentLevel.LEVEL_3_COLD_ATOM,
        ExperimentLevel.LEVEL_4_MESOSCOPIC,
        ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT,
    ]
    
    for level in levels_to_check:
        stage = ExperimentLadder.get_stage(level)
        assert len(stage.required_observables) > 0


def test_photon_level_allowed_systems():
    """Test Level 1 allows photon systems."""
    stage = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_1_PHOTON)
    
    assert "Photons" in stage.allowed_test_systems
    assert "Laser systems" in stage.allowed_test_systems
    assert "Interferometers" in stage.allowed_test_systems


def test_cold_atom_level():
    """Test Level 3 (Cold Atom) properties."""
    stage = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_3_COLD_ATOM)
    
    assert "Cold atoms" in stage.allowed_test_systems
    assert "Bose-Einstein condensates" in stage.allowed_test_systems
    assert "quantum coherence" in [o.lower() for o in stage.required_observables]


def test_failure_criteria_exist():
    """Test that each level has failure criteria."""
    levels = ExperimentLadder.get_all_levels()
    
    for level in levels:
        stage = ExperimentLadder.get_stage(level)
        # All levels should have failure criteria defined
        assert len(stage.failure_criteria) > 0 or level == ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN


def test_no_human_claims_until_level_6():
    """Test that levels 0-5 explicitly forbid inappropriate claims."""
    # Level 0 forbids physical implementation claims
    stage_0 = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_0_FOUNDATIONAL)
    forbidden_0 = " ".join(stage_0.forbidden_claims).lower()
    assert "physical" in forbidden_0 or "implementation" in forbidden_0
    
    # Level 1 forbids matter transport and human applications
    stage_1 = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_1_PHOTON)
    forbidden_1 = " ".join(stage_1.forbidden_claims).lower()
    assert "matter" in forbidden_1 or "human" in forbidden_1
    
    # Level 6 forbids all biological
    stage_6 = ExperimentLadder.get_stage(ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN)
    forbidden_6 = " ".join(stage_6.forbidden_claims).lower()
    assert "human" in forbidden_6 or "biological" in forbidden_6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
