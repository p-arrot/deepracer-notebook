# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AWS DeepRacer racing line and speed profile optimizer. Computes optimal racing lines with safety distance constraints and speed profiles based on a friction circle model.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_core.py -v

# Run a single test
pytest tests/test_core.py::TestMengerCurvature::test_straight_line_returns_zero -v

# Open notebook
jupyter notebook DeepRacer_Workflow.ipynb
```

## Architecture

**3-Stage Optimization Pipeline:**
1. **Path optimization** (`core.py:optimize_race_line`) — Gradient descent with binary search adjusts each point to smooth curvature while enforcing `safety_distance` from track boundaries (hard constraint via shapely)
2. **Speed profile** (`DeepRacer_Workflow.ipynb` Step 4) — Friction circle model: `a_lat = v² × κ ≤ μ × g`. Forward pass for acceleration limits, backward pass for braking limits
3. **Outer iteration** — Couples path and speed; if curvature-limited speed is too low, increase curvature weight to shorten path

**Core abstraction in `core.py`:**
- `compute_racing_line(track_path, ...)` — Main entry, loads npy, returns racing line + waypoints dict
- `load_track_waypoints(track_path)` — Handles multiple npy formats (see below)
- `improve_race_line(...)` — Single gradient descent sweep
- `menger_curvature(pt1, pt2, pt3)` — 1/r curvature via triangle geometry

**npy format support** (`core.py:load_track_waypoints`):
- Dict/object: `center_line`/`waypoints`, `inner_border`/`left_border`, `outer_border`/`right_border`
- Array (N,6): interleaved `[cx,cy, ix,iy, ox,oy]`
- Array (N,4): `[inner_x, inner_y, outer_x, outer_y]`
- Array (N,2): center line only (requires boundary data for optimization)

## Key Parameters

| Parameter | Default | Effect |
|-----------|--------|--------|
| `safety_distance` | 0.2 m | Hard constraint — minimum distance from track boundary |
| `line_iterations` | 2000 | Path optimization convergence |
| `xi_iterations` | 4 | Binary search depth per point |
| `min_speed` / `max_speed` | 1.0 / 3.0 m/s | Speed limits |
| `look_ahead_points` | 1 | Forward look for speed calculation |

## Notebook Workflow (DeepRacer_Workflow.ipynb)

1. Export track npy → CSV (`waypoints.csv`)
2. Compute optimal racing line (calls `core.py`)
3. Speed profile & timing (in-notebook calculation)
4. 4D racing line data `[x, y, speed, time]` for `visualize.html`
5. Reward function for AWS DeepRacer console

## Test Data

Default track: `map/reinvent_base.npy` — first center point approx `(3.0, 0.68)`, closed loop.
