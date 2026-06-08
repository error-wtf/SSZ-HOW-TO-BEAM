"""Bridge candidate data structures."""
from __future__ import annotations

from dataclasses import dataclass

from .energy_conditions import EnergyConditionReport
from .worldline import WorldlineSegment


@dataclass(frozen=True)
class BridgeCandidate:
    candidate_id: str
    effective_distance: float
    normal_distance: float
    max_tidal_delta_a: float
    tidal_limit: float
    worldline: WorldlineSegment
    energy: EnergyConditionReport
    singularity_flag: bool = False

    @property
    def compression_ratio(self) -> float:
        if self.normal_distance <= 0:
            raise ValueError("normal_distance must be positive")
        return self.effective_distance / self.normal_distance
