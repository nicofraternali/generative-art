"""
Tiling squares — a Truchet-style tiling sketch.

Each cell of a 2^L by 2^L grid contains a diagonal line in one of two
orientations, chosen randomly. Where a 2x2 neighborhood matches the
"1001" pattern (top-left and bottom-right are 1, top-right and bottom-left
are 0), a diamond is drawn over the intersection.

Interactive keys (when run without --seed):
    r       New random structure (new seed), keep current theme.
    space   New random theme, keep current structure.
    s       Save the current piece. Prints the seed and theme used,
            then logs the saved filepath.

Deterministic mode (when run with --seed and --theme):
    The sketch loads with the specified seed and theme, renders once,
    saves automatically, and exits.

Usage:
    uv run python projects/tiling_squares/sketch.py
    uv run python projects/tiling_squares/sketch.py --seed 4823 --theme JAPAN
    uv run python projects/tiling_squares/sketch.py --seed 4823 --theme JAPAN --L 5
"""

from __future__ import annotations

import argparse
import random
import sys

import py5

from genart.io import save_artwork
from genart.palettes import TILING_THEMES, list_tiling_themes
from genart.seeds import init_seed


# ---------------------------------------------------------------------------
# Configuration (defaults — can be overridden by CLI flags).
# ---------------------------------------------------------------------------

DEFAULT_L = 4
DEFAULT_THEME = "ORIGINAL"
HI_RES_SIZE = 2400
PREVIEW_SIZE = 600
MARGIN_RATIO = 0.08

PROJECT_NAME = "tiling_squares"


# ---------------------------------------------------------------------------
# Module-level state. py5 requires top-level functions, so we keep state
# in module-level variables. These are populated in setup() from CLI args.
# ---------------------------------------------------------------------------

L: int = DEFAULT_L
seed: int = 0
theme_name: str = DEFAULT_THEME
palette: dict = {}
grid: list[list[int]] = []
pg = None  # py5 graphics buffer

# Mode flags driven by CLI:
auto_save_and_exit: bool = False  # True when --seed is given


# ---------------------------------------------------------------------------
# CLI parsing.
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tiling squares generative art.")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for deterministic reproduction. If omitted, a random seed is used "
             "and the sketch runs interactively.",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default=DEFAULT_THEME,
        choices=list_tiling_themes(),
        help=f"Theme name. Default: {DEFAULT_THEME}.",
    )
    parser.add_argument(
        "--L",
        type=int,
        default=DEFAULT_L,
        help=f"Grid resolution exponent (grid is 2^L by 2^L). Default: {DEFAULT_L}.",
    )
    parser.add_argument(
        "--save-and-exit",
        action="store_true",
        help="With --seed, render once, save, and exit without opening "
             "an interactive window. Useful for batch rendering.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Composition logic.
# ---------------------------------------------------------------------------

def generate_grid() -> None:
    """Generate a fresh 2^L by 2^L grid of random 0/1 values."""
    global grid
    cols = 2**L
    rows = 2**L
    grid = [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]


def render_art() -> None:
    """Paint the current grid into the high-res buffer using the current palette."""
    if not grid:
        return

    pg.begin_draw()
    pg.background(palette["bg"])

    cols = len(grid[0])
    rows = len(grid)

    margin = HI_RES_SIZE * MARGIN_RATIO
    active_width = HI_RES_SIZE - (margin * 2)
    s = active_width / cols

    pg.push_matrix()
    pg.translate(margin, margin)

    # Phase A: diamonds where 2x2 neighborhood matches "1001".
    pg.no_stroke()
    pg.fill(palette["accent"])
    for r in range(rows - 1):
        for c in range(cols - 1):
            tl = grid[r][c]
            tr = grid[r][c + 1]
            bl = grid[r + 1][c]
            br = grid[r + 1][c + 1]
            if tl == 1 and tr == 0 and bl == 0 and br == 1:
                cx = (c + 1) * s
                cy = (r + 1) * s
                pg.quad(cx, cy - s, cx + s, cy, cx, cy + s, cx - s, cy)

    # Phase B: diagonal lines in every cell.
    pg.stroke(palette["line"])
    pg.stroke_weight(HI_RES_SIZE * 0.005)
    pg.stroke_cap(py5.ROUND)

    for r in range(rows):
        for c in range(cols):
            x = c * s
            y = r * s
            if grid[r][c] == 0:
                pg.line(x, y, x + s, y + s)
            else:
                pg.line(x, y + s, x + s, y)

    pg.pop_matrix()
    pg.end_draw()


def new_composition(use_seed: int | None = None) -> None:
    """Reseed RNG, generate a new grid. Does not change the theme."""
    global seed
    seed = init_seed(use_seed)
    generate_grid()
    render_art()
    print(f"Composition: seed={seed}, theme={theme_name}, L={L}")


def cycle_theme() -> None:
    """Pick a new random theme and re-render the existing grid."""
    global theme_name, palette
    theme_name = random.choice(list_tiling_themes())
    palette = TILING_THEMES[theme_name]
    render_art()
    print(f"Theme: {theme_name}")


def save_current() -> None:
    """Save the current piece with full metadata."""
    params = {
        "L": L,
        "margin_ratio": MARGIN_RATIO,
        "hi_res_size": HI_RES_SIZE,
    }
    path = save_artwork(
        pg,
        project_name=PROJECT_NAME,
        seed=seed,
        theme_name=theme_name,
        params=params,
    )
    print(f"Saved: {path}")
    print(f"  seed={seed}  theme={theme_name}  L={L}")


# ---------------------------------------------------------------------------
# py5 lifecycle.
# ---------------------------------------------------------------------------

def setup() -> None:
    global pg, palette
    py5.size(PREVIEW_SIZE, PREVIEW_SIZE)
    pg = py5.create_graphics(HI_RES_SIZE, HI_RES_SIZE)

    palette = TILING_THEMES[theme_name]
    new_composition(use_seed=seed if seed != 0 else None)
    # Note: if --save-and-exit was passed, the actual save happens in
    # draw() after the first frame is rendered, so the user sees what
    # got saved before the window closes.


def draw() -> None:
    py5.image(pg, 0, 0, py5.width, py5.height)
    if auto_save_and_exit and py5.frame_count == 1:
        save_current()
        py5.exit_sketch()


def draw() -> None:
    py5.image(pg, 0, 0, py5.width, py5.height)


def key_pressed() -> None:
    if py5.key == "s":
        save_current()
    elif py5.key == "r":
        new_composition()
    elif py5.key == " ":
        cycle_theme()


# ---------------------------------------------------------------------------
# Entry point. Logic runs at module level so py5 can find setup(), draw(),
# and key_pressed() in the module's global namespace.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args()
    L = args.L
    theme_name = args.theme
    auto_save_and_exit = args.save_and_exit

    if args.seed is not None:
        seed = args.seed
    else:
        seed = 0  # placeholder; real seed assigned by init_seed() in setup()

    py5.run_sketch()