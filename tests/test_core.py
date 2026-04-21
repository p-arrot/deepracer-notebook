"""
Tests for core.py — racing line optimization functions.
"""

import numpy as np
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core import (
    menger_curvature,
    load_track_waypoints,
    improve_race_line,
    npy_to_csv,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test data
# ─────────────────────────────────────────────────────────────────────────────

TRACK_PATH = Path(__file__).parent.parent / "map" / "reinvent_base.npy"


# ─────────────────────────────────────────────────────────────────────────────
# Test: menger_curvature
# ─────────────────────────────────────────────────────────────────────────────

class TestMengerCurvature:
    def test_straight_line_returns_zero(self):
        """Three collinear points should give zero curvature."""
        p1 = (0.0, 0.0)
        p2 = (1.0, 0.0)
        p3 = (2.0, 0.0)
        assert menger_curvature(p1, p2, p3) == 0.0

    def test_known_curvature(self):
        """Semicircle of radius 1 should give curvature = 1."""
        # Points on a unit circle at 0, 90, 180 degrees
        p1 = (1.0, 0.0)
        p2 = (0.0, 1.0)
        p3 = (-1.0, 0.0)
        kappa = menger_curvature(p1, p2, p3)
        assert abs(kappa - 1.0) < 0.01

    def test_atol_prevents_division_by_zero(self):
        """Identical points should return 0, not raise."""
        p = (0.5, 0.5)
        assert menger_curvature(p, p, p) == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Test: load_track_waypoints
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadTrackWaypoints:
    def test_loads_npy_file(self):
        """Should load the bundled track without error."""
        center, inner, outer = load_track_waypoints(str(TRACK_PATH))
        assert len(center) > 0
        assert len(inner) > 0
        assert len(outer) > 0
        assert len(center) == len(inner) == len(outer)

    def test_arrays_are_numpy(self):
        """Returned arrays should be numpy arrays."""
        center, inner, outer = load_track_waypoints(str(TRACK_PATH))
        assert isinstance(center, np.ndarray)
        assert isinstance(inner, np.ndarray)
        assert isinstance(outer, np.ndarray)

    def test_center_matches_expected_approx(self):
        """Center line first point should be close to (3, 0.68)."""
        center, _, _ = load_track_waypoints(str(TRACK_PATH))
        assert abs(center[0][0] - 3.0) < 0.1
        assert abs(center[0][1] - 0.68) < 0.1

    def test_closed_loop_approximation(self):
        """First and last center points should be nearly identical (closed track)."""
        center, _, _ = load_track_waypoints(str(TRACK_PATH))
        dist = np.linalg.norm(center[0] - center[-1])
        assert dist < 0.5, "Track should be closed (first ≈ last point)"


# ─────────────────────────────────────────────────────────────────────────────
# Test: improve_race_line (single iteration)
# ─────────────────────────────────────────────────────────────────────────────

class TestImproveRaceLine:
    def test_does_not_crash(self):
        """Should run without raising on the default track."""
        center, inner, outer = load_track_waypoints(str(TRACK_PATH))
        # Use a small subset for speed
        init_line = center[:10]
        result = improve_race_line(init_line, inner, outer, safety_distance=0.2)
        assert len(result) == len(init_line)

    def test_output_length_unchanged(self):
        """Output should have same number of points as input."""
        center, inner, outer = load_track_waypoints(str(TRACK_PATH))
        init_line = center[:20]
        result = improve_race_line(init_line, inner, outer, safety_distance=0.2)
        assert len(result) == len(init_line)

    def test_respects_safety_distance(self):
        """Optimized points should stay at least safety_distance from boundaries."""
        center, inner, outer = load_track_waypoints(str(TRACK_PATH))
        from shapely.geometry import Point, LineString

        init_line = center[:30]
        safety = 0.2
        result = improve_race_line(init_line, inner, outer, safety_distance=safety)

        ls_inner = LineString(inner)
        ls_outer = LineString(outer)

        for pt in result:
            p = Point(pt)
            assert p.distance(ls_inner) >= safety - 1e-6, "Too close to inner boundary"
            assert p.distance(ls_outer) >= safety - 1e-6, "Too close to outer boundary"
