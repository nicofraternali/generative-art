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

## Stage 2 — Core utilities (planned)

Will add `genart.seeds` for deterministic RNG initialization and `genart.io` for
saving artwork with embedded metadata and JSON sidecars.

## Stage 3 — Migrate first sketch (planned)

Refactor `tiling_squares` to use the shared package. Establishes the template
for migrating the others.

## Stage 4 — Migrate remaining sketches (planned)

`tiling_holes` and `pendulum`. The pendulum gets the actual RNG seeding fix
and optionally the `scipy.ndimage.label` optimization.

## Stage 5 — Blog bridge (planned)

`scripts/curate.py` to promote outputs into `curated/`, and
`scripts/build_gallery.py` to emit Jekyll posts and assets into the blog repo.