"""SSZ metric utilities."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sin

from .constants import C
from .xi import evaluate_d_s_x


@dataclass(frozen=True)
class SSZMetric:
    """Diagonal SSZ metric in spherical coordinates for x=r/r_s.

    Components follow ds²=-D² c²dt²+s²dr²+r²dΩ². The metric tensor below uses
    coordinates (ct, r, theta, phi) when c_scaled=True, so g_tt=-D². If
    c_scaled=False, g_tt=-D² c².
    """

    x: float
    r_s: float = 1.0
    theta: float = 1.5707963267948966
    c_scaled: bool = True

    @property
    def r(self) -> float:
        return self.x * self.r_s

    @property
    def xi(self) -> float:
        return evaluate_d_s_x(self.x)[2].xi

    @property
    def D(self) -> float:
        return evaluate_d_s_x(self.x)[0]

    @property
    def s(self) -> float:
        return evaluate_d_s_x(self.x)[1]

    def components(self) -> dict[str, float]:
        g_tt = -(self.D ** 2) if self.c_scaled else -(self.D ** 2) * C * C
        return {
            "tt": g_tt,
            "rr": self.s ** 2,
            "theta_theta": self.r ** 2,
            "phi_phi": (self.r ** 2) * (sin(self.theta) ** 2),
        }

    def inverse_components(self) -> dict[str, float]:
        comps = self.components()
        return {name: 1.0 / value for name, value in comps.items()}

    def determinant(self) -> float:
        comps = self.components()
        det = 1.0
        for value in comps.values():
            det *= value
        return det

    def is_finite(self) -> bool:
        values = list(self.components().values()) + list(self.inverse_components().values()) + [self.determinant()]
        return all(isfinite(v) for v in values) and self.determinant() != 0.0
