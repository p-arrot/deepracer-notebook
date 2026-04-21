# DeepRacer Racing Line Optimization — Notebook Workflow

A standalone Jupyter Notebook workflow for optimizing racing lines and speed profiles for AWS DeepRacer tracks.

## Overview

This project provides a complete 5-step workflow for computing optimal racing lines with safety distance constraints, speed profiles based on a friction circle model, and a reward function for AWS DeepRacer.

## Project Structure

```
deepracer-notebook/
├── DeepRacer_Workflow.ipynb   # Main notebook (5-step workflow)
├── core.py                    # Core functions: compute_racing_line(), npy_to_csv()
├── visualize.html             # Browser-based track & racing line viewer
├── requirements.txt           # Python dependencies
├── map/
│   └── reinvent_base.npy      # Default track file
└── waypoints.csv              # Exported track waypoints (auto-generated)
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Open the notebook:**
   ```bash
   jupyter notebook DeepRacer_Workflow.ipynb
   ```

3. **Run all cells** from top to bottom.

## Workflow Steps

| Step | Description | Output |
|------|-------------|--------|
| 1 | Export track npy → CSV | `waypoints.csv` for visualize.html |
| 2 | Compute optimal racing line | Racing line coordinates |
| 3 | Speed profile & timing | Velocity & arrival time per point |
| 4 | 4D racing line data | [x, y, speed, time] for visualize.html |
| 5 | Reward function | AWS DeepRacer reward function code |

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `safety_distance` | 0.2 m | Minimum distance from track boundary |
| `line_iterations` | 2000 | Racing line optimization iterations |
| `xi_iterations` | 4 | Binary search depth per point |
| `min_speed` / `max_speed` | 1.0 / 3.0 m/s | Speed limits |
| `look_ahead_points` | 1 | Forward look for speed calculation |

## visualize.html

Open `visualize.html` in a browser to:
- Import `waypoints.csv` to view track boundaries
- Paste 4D racing line data to visualize speed profile (red=low, green=high)

## Algorithm

The racing line optimization uses a gradient descent approach with binary search:
1. Start from center line
2. Adjust each point to smooth curvature while maintaining safety distance from boundaries
3. Iterate 2000 times for convergence

Speed profile is computed using the **friction circle model**:
- Lateral acceleration: a_lat = v² × κ ≤ μ × g
- Forward pass for acceleration limits, backward pass for braking limits

## Track Data Format

Supported npy structures:
- **Dict/object:** keys include `center_line`/`waypoints`, `left_border`/`inner_border`, `right_border`/`outer_border`
- **Array (N,6):** interleaved [cx,cy, ix,iy, ox,oy]
- **Array (N,4):** [inner_x, inner_y, outer_x, outer_y]
- **Array (N,2):** center line only (requires boundary data for optimization)

## License

MIT
