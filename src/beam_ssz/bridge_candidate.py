"""Bridge candidate data structures."""
from __future__ import annotations

from dataclasses import dataclass

from .energy_conditions import EnergyConditionReport
from .worldline import WorldlineSegment


@dataclass(frozen=True)
class BridgeCandidate:
    candidate_id: str = "test_candidate"
    effective_distance: float = 1.0
    normal_distance: float = 1.0
    max_tidal_delta_a: float = 0.0
    tidal_limit: float = 1.0
    worldline: WorldlineSegment = None
    energy: EnergyConditionReport = None
    singularity_flag: bool = False

    @property
    def compression_ratio(self) -> float:
        if self.normal_distance <= 0:
            raise ValueError("normal_distance must be positive")
        return self.effective_distance / self.normal_distance
