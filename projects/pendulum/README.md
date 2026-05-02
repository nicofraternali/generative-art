# pendulum

A double pendulum runs under gravity and damping; its endpoint traces a
chaotic path. After `--max-points` samples, the trace is treated as a wall
structure, the enclosed regions are flood-filled (via `scipy.ndimage.label`),
adjacency is computed (via numpy roll operations), and regions are colored
with a greedy graph-coloring algorithm.

## A note on reproducibility and chaos

Double pendulums are paradigmatic chaotic systems — sensitivity to initial
conditions is the textbook property. But the *integrator* used here is
deterministic: same seed + same code + same NumPy version = bit-identical
output, every time. Reproducibility via `--seed` works perfectly.

The chaotic sensitivity only matters if you tried to reconstruct a piece
by typing initial angles back in from the metadata sidecar — at which point
floating-point precision loss would diverge the trajectory. The seed-based
contract avoids this entirely.

## Run

Interactive (random seed each session):

```powershell
uv run python projects/pendulum/sketch.py
```

Reproduce a specific piece:

```powershell
uv run python projects/pendulum/sketch.py --seed 4823 --theme JAPAN
```

Vary trace length:

```powershell
uv run python projects/pendulum/sketch.py --seed 4823 --max-points 1500
```

## Keys

- `r` — new random composition (new seed)
- `space` — new random theme + reset
- `s` — save current piece (saves both trace and art views)

## Each save produces two files

- `pendulum_<seed>_<timestamp>_trace.png` — the raw simulation view
- `pendulum_<seed>_<timestamp>_art.png` — the painted topology view

Plus matching `.json` sidecars for each.

## Quality metrics

Each saved piece records region statistics in its sidecar:
`n_components_total`, `n_regions_interior`, `n_regions_outside`,
`region_size_mean`, `region_size_std`, `region_size_min`, `region_size_max`.
Over time these can inform what `--max-points` value works for which
physical setups.