"""Search space definition for metric bridge candidates.

This module defines the parameter space for searching for viable
metric bridge candidates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import numpy as np

from .metric_bridge import BridgeParameters, evaluate_bridge_candidate


@dataclass(frozen=True)
class SearchSpaceBounds:
    """Bounds for search space parameters."""
    alpha_min: float
    alpha_max: float
    lambda_min: float
    lambda_max: float
    k_min: float
    k_max: float


@dataclass(frozen=True)
class SearchGrid:
    """Grid definition for parameter search."""
    alpha_values: np.ndarray
    lambda_values: np.ndarray
    k_values: np.ndarray


@dataclass(frozen=True)
class SearchPoint:
    """A single point in the search space."""
    alpha: float
    lambda_segment: float
    k: float


class SearchSpace:
    """Search space for metric bridge parameters."""
    
    DEFAULT_BOUNDS = SearchSpaceBounds(
        alpha_min=0.1,
        alpha_max=10.0,
        lambda_min=0.0,
        lambda_max=5.0,
        k_min=0.01,
        k_max=1.0,
    )
    
    def __init__(self, bounds: SearchSpaceBounds | None = None):
        """Initialize search space.
        
        Args:
            bounds: Parameter bounds (uses DEFAULT_BOUNDS if None)
        """
        self.bounds = bounds or SearchSpace.DEFAULT_BOUNDS
    
    def create_linear_grid(
        self,
        alpha_points: int = 10,
        lambda_points: int = 10,
        k_points: int = 10,
    ) -> SearchGrid:
        """Create a linear grid over the search space.
        
        Args:
            alpha_points: Number of alpha grid points
            lambda_points: Number of lambda grid points
            k_points: Number of k grid points
            
        Returns:
            SearchGrid with linear spacing
        """
        alpha_values = np.linspace(self.bounds.alpha_min, self.bounds.alpha_max, alpha_points)
        lambda_values = np.linspace(self.bounds.lambda_min, self.bounds.lambda_max, lambda_points)
        k_values = np.linspace(self.bounds.k_min, self.bounds.k_max, k_points)
        
        return SearchGrid(
            alpha_values=alpha_values,
            lambda_values=lambda_values,
            k_values=k_values,
        )
    
    def create_log_grid(
        self,
        alpha_points: int = 10,
        lambda_points: int = 10,
        k_points: int = 10,
    ) -> SearchGrid:
        """Create a logarithmic grid over the search space.
        
        Args:
            alpha_points: Number of alpha grid points
            lambda_points: Number of lambda grid points
            k_points: Number of k grid points
            
        Returns:
            SearchGrid with logarithmic spacing
        """
        alpha_values = np.logspace(
            np.log10(self.bounds.alpha_min),
            np.log10(self.bounds.alpha_max),
            alpha_points,
        )
        lambda_values = np.logspace(
            np.log10(max(self.bounds.lambda_min, 1e-6)),
            np.log10(self.bounds.lambda_max),
            lambda_points,
        )
        k_values = np.logspace(
            np.log10(self.bounds.k_min),
            np.log10(self.bounds.k_max),
            k_points,
        )
        
        return SearchGrid(
            alpha_values=alpha_values,
            lambda_values=lambda_values,
            k_values=k_values,
        )
    
    def iterate_grid(self, grid: SearchGrid) -> Iterator[SearchPoint]:
        """Iterate over all points in a grid.
        
        Args:
            grid: SearchGrid to iterate over
            
        Yields:
            SearchPoint for each combination
        """
        for alpha in grid.alpha_values:
            for lam in grid.lambda_values:
                for k in grid.k_values:
                    yield SearchPoint(
                        alpha=alpha,
                        lambda_segment=lam,
                        k=k,
                    )
    
    def random_sample(
        self,
        n_samples: int,
        seed: int | None = None,
    ) -> list[SearchPoint]:
        """Generate random samples from the search space.
        
        Args:
            n_samples: Number of samples to generate
            seed: Random seed for reproducibility
            
        Returns:
            List of SearchPoint objects
        """
        rng = np.random.default_rng(seed)
        
        points = []
        for _ in range(n_samples):
            alpha = rng.uniform(self.bounds.alpha_min, self.bounds.alpha_max)
            lam = rng.uniform(self.bounds.lambda_min, self.bounds.lambda_max)
            k = rng.uniform(self.bounds.k_min, self.bounds.k_max)
            points.append(SearchPoint(alpha=alpha, lambda_segment=lam, k=k))
        
        return points
    
    def point_to_parameters(self, point: SearchPoint) -> BridgeParameters:
        """Convert a SearchPoint to BridgeParameters.
        
        Args:
            point: SearchPoint to convert
            
        Returns:
            BridgeParameters object
        """
        return BridgeParameters(
            alpha=point.alpha,
            lambda_segment=point.lambda_segment,
            k_min=self.bounds.k_min,
            k_max=self.bounds.k_max,
        )
    
    def search_candidates(
        self,
        A: float,
        B: float,
        rs: float,
        grid: SearchGrid | None = None,
        max_candidates: int | None = None,
    ) -> list[tuple[SearchPoint, BridgeParameters]]:
        """Search for bridge candidates over the parameter space.
        
        Args:
            A: Start radius (meters)
            B: End radius (meters)
            rs: Schwarzschild radius (meters)
            grid: Search grid (uses linear grid if None)
            max_candidates: Maximum number of candidates to return
            
        Returns:
            List of (SearchPoint, BridgeParameters) tuples
        """
        if grid is None:
            grid = self.create_linear_grid(alpha_points=5, lambda_points=5, k_points=5)
        
        candidates = []
        count = 0
        
        for point in self.iterate_grid(grid):
            params = self.point_to_parameters(point)
            candidates.append((point, params))
            count += 1
            
            if max_candidates is not None and count >= max_candidates:
                break
        
        return candidates
    
    def evaluate_search_point(
        self,
        point: SearchPoint,
        A: float,
        B: float,
        rs: float,
    ) -> BridgeParameters:
        """Evaluate a single search point.
        
        Args:
            point: SearchPoint to evaluate
            A: Start radius (meters)
            B: End radius (meters)
            rs: Schwarzschild radius (meters)
            
        Returns:
            BridgeParameters object
        """
        params = self.point_to_parameters(point)
        return params
