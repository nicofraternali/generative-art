# Workflow

This document describes the day-to-day operations of the `generative-art` project.
It grows as new stages are implemented. Each section is dated so you can see when
the workflow changed.

---

## Stage 1 — Foundation (May 2026)

### What exists now

- `pyproject.toml` declares dependencies; `uv.lock` pins exact versions.
- `src/genart/palettes.py` is the single source of truth for color themes.
- `.gitignore` excludes virtual envs, caches, and per-project `output/` folders.
- The `genart` package is importable from any sketch via `from genart.palettes import ...`.

### Daily commands

**Activate the environment when starting a session:**

The environment is automatic — `uv run <command>` always uses the project's
virtual environment. There is no `activate` step.

**Add a new dependency:**

```powershell
uv add               # runtime dependency
uv add --group dev   # dev-only (Jupyter, linters, etc.)
```

This updates `pyproject.toml` and `uv.lock` together.

**Run any Python file inside the project's environment:**

```powershell
uv run python 
```

**Verify the shared package is importable:**

```powershell
uv run python -c "from genart.palettes import TILING_THEMES; print(len(TILING_THEMES))"
```

### What does NOT yet exist

- No sketches have been migrated to use `genart.palettes` yet.
- No save/IO utilities (`genart.io`) — sketches still save manually.
- No seed-management utility (`genart.seeds`) — pendulum still doesn't seed RNG.
- No `curated/` workflow or scripts.
- No blog integration.

These come in subsequent stages.

---

## Stage 2 — Core utilities (May 2026)

### What was added

- `src/genart/seeds.py` — `init_seed(seed=None)` deterministically seeds
  both Python's `random` and `numpy.random`. Returns the seed used.
- `src/genart/io.py` — `save_artwork(pg, project_name, seed, theme_name, params)`
  saves a py5 graphics buffer with metadata embedded as PNG text chunks
  AND written to a JSON sidecar.

### How sketches will use these (from stage 3 onward)

Every sketch follows this pattern:

```python
from genart.seeds import init_seed
from genart.io import save_artwork
from genart.palettes import TILING_THEMES

def reset():
    global seed, theme_name, palette
    seed = init_seed()                  # generates and seeds RNG
    theme_name = "ORIGINAL"
    palette = TILING_THEMES[theme_name]
    # ... reset composition state ...

def on_save_key():
    save_artwork(
        pg,
        project_name="tiling_squares",
        seed=seed,
        theme_name=theme_name,
        params={"L": L, "margin_ratio": MARGIN_RATIO},
    )
```

### What gets saved

For a piece saved with seed=4823, theme="JAPAN", on 2026-05-01, you get:

    projects/pendulum/output/pendulum_4823_20260501_143211.png
    projects/pendulum/output/pendulum_4823_20260501_143211.json

The PNG has metadata embedded as text chunks. The JSON sidecar contains:

    {
      "project": "pendulum",
      "seed": 4823,
      "theme": "JAPAN",
      "timestamp_utc": "2026-05-01T14:32:11.123456+00:00",
      "git_commit": "a3f7d2e",
      "git_dirty": false,
      "library_versions": {"python": "3.12.3", "py5": "0.10.4a2", ...},
      "params": { /* project-specific */ }
    }

### Reading metadata back

```powershell
uv run python -c "from genart.io import read_artwork_metadata; import json; print(json.dumps(read_artwork_metadata('path/to/piece.png'), indent=2))"
```

## Stage 3 — First sketch migrated (May 2026)

### What was added

- `projects/tiling_squares/sketch.py` — the original tiling sketch refactored
  to use the shared package. Imports themes from `genart.palettes`, seeds
  RNG via `genart.seeds.init_seed`, and saves via `genart.io.save_artwork`.
- Command-line interface: `--seed`, `--theme`, `--L`.
- Per-project README at `projects/tiling_squares/README.md`.

### How to run a sketch

Interactive session:

```powershell
uv run python projects//sketch.py
```

View a specific piece (interactive — window stays open):

```powershell
uv run python projects//sketch.py --seed  --theme 
```

Reproduce and save without interaction (batch mode):

```powershell
uv run python projects//sketch.py --seed  --theme  --save-and-exit
```

### Where outputs go

All saves land in `projects/<project>/output/`, which is gitignored.
Pieces only enter version control when explicitly curated (stage 5).

---

## Stage 4 (partial) — tilings unified (May 2026)

### What was added

- `src/genart/tiling.py` — shared primitives for Truchet-style tilings:
  `generate_grid(L)`, `find_diamonds(grid)`, `GridGeometry` dataclass.
- `projects/tiling_squares/sketch.py` — refactored to use the shared module.
- `projects/tiling_holes/sketch.py` — new sketch using the shared module
  with V-cut trench rendering.

### Architectural note

Both tiling sketches share their combinatorial substrate (the 0/1 grid
and the 1001 diamond detection) but differ in rendering. The shared
substrate lives in `genart.tiling`; rendering stays per-sketch. This
keeps `genart.tiling` py5-free and lets each sketch express its style
without negotiating a common rendering interface.

### Pending in Stage 4 — completed (May 2026)

- `projects/pendulum/sketch.py` — migrated, with proper RNG seeding,
  scipy-based topology solver, vectorized adjacency detection, and
  quality metrics in the metadata.
- Saves produce two files per piece: `_trace` (raw simulation) and
  `_art` (painted topology), each with its own sidecar.
- New CLI flag `--max-points` for varying trace duration.

Stage 4 complete. Next: Stage 5 — curation and blog bridge.

## Stage 5 — Blog bridge (planned)

`scripts/curate.py` to promote outputs into `curated/`, and
`scripts/build_gallery.py` to emit Jekyll posts and assets into the blog repo.