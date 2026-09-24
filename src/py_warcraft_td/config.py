"""Configuration, constants, and dynamic resolution layout metrics for py-warcraft-td."""

from dataclasses import dataclass
from typing import Dict, Tuple

# Default Dimensions (Windowed fallback)
DEFAULT_WIDTH = 1360
DEFAULT_HEIGHT = 768
FPS = 60

# Static Defaults for backward compatibility
GRID_COLS = 24
GRID_ROWS = 17
CELL_SIZE = 36
GRID_OFFSET_X = 24
GRID_OFFSET_Y = 80
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
SPAWN_CELL = (0, 8)
GOAL_CELL = (GRID_COLS - 1, 8)
SIDEBAR_X = GRID_OFFSET_X + GRID_WIDTH + 20
SIDEBAR_Y = GRID_OFFSET_Y
SIDEBAR_WIDTH = DEFAULT_WIDTH - SIDEBAR_X - 24
SIDEBAR_HEIGHT = GRID_HEIGHT


@dataclass
class LayoutConfig:
    """Dynamic resolution metrics for 1360x768, 1920x1080 (16:9), and 2560x1080 (21:9 Ultrawide)."""
    screen_width: int
    screen_height: int
    grid_cols: int
    grid_rows: int
    cell_size: int
    grid_offset_x: int
    grid_offset_y: int
    grid_width: int
    grid_height: int
    spawn_cell: Tuple[int, int]
    goal_cell: Tuple[int, int]
    sidebar_x: int
    sidebar_y: int
    sidebar_width: int
    sidebar_height: int
    top_bar_height: int = 70
    bottom_bar_height: int = 42

    def grid_to_pixel(self, coord: Tuple[int, int]) -> Tuple[float, float]:
        col, row = coord
        x = self.grid_offset_x + col * self.cell_size + self.cell_size / 2.0
        y = self.grid_offset_y + row * self.cell_size + self.cell_size / 2.0
        return (x, y)

    def pixel_to_grid(self, pixel: Tuple[float, float]) -> Tuple[int, int] | None:
        x, y = pixel
        rel_x = x - self.grid_offset_x
        rel_y = y - self.grid_offset_y
        if rel_x < 0 or rel_y < 0:
            return None
        col = int(rel_x // self.cell_size)
        row = int(rel_y // self.cell_size)
        if 0 <= col < self.grid_cols and 0 <= row < self.grid_rows:
            return (col, row)
        return None


def create_layout_config(width: int, height: int) -> LayoutConfig:
    """Create optimal layout metrics for the specified screen resolution."""
    if width >= 2500:
        # 21:9 Ultrawide (e.g. 2560x1080)
        cols = 34
        rows = 17
        cell_size = 48
        gw = cols * cell_size   # 1632 px
        gh = rows * cell_size   # 816 px
        gx = 36
        gy = 86
        sx = gx + gw + 28       # 1696 px
        sy = gy
        sw = width - sx - 36    # ~828 px
        sh = gh
        spawn = (0, 8)
        goal = (cols - 1, 8)

    elif width >= 1800:
        # 16:9 Full HD (e.g. 1920x1080)
        cols = 26
        rows = 17
        cell_size = 48
        gw = cols * cell_size   # 1248 px
        gh = rows * cell_size   # 816 px
        gx = 32
        gy = 86
        sx = gx + gw + 24       # 1304 px
        sy = gy
        sw = width - sx - 28    # ~588 px
        sh = gh
        spawn = (0, 8)
        goal = (cols - 1, 8)

    else:
        # Compact / Windowed (e.g. 1360x768)
        cols = 24
        rows = 17
        cell_size = 36
        gw = cols * cell_size   # 864 px
        gh = rows * cell_size   # 612 px
        gx = 24
        gy = 80
        sx = gx + gw + 20       # 908 px
        sy = gy
        sw = width - sx - 24    # ~428 px
        sh = gh
        spawn = (0, 8)
        goal = (cols - 1, 8)

    return LayoutConfig(
        screen_width=width,
        screen_height=height,
        grid_cols=cols,
        grid_rows=rows,
        cell_size=cell_size,
        grid_offset_x=gx,
        grid_offset_y=gy,
        grid_width=gw,
        grid_height=gh,
        spawn_cell=spawn,
        goal_cell=goal,
        sidebar_x=sx,
        sidebar_y=sy,
        sidebar_width=sw,
        sidebar_height=sh,
    )


# Palette (Warcraft 3 Dark Fantasy & Elemental Accents)
BG_DARK = (14, 16, 22)
BG_PANEL = (22, 26, 36)
BG_PANEL_ALT = (30, 36, 50)
BG_PANEL_BORDER = (52, 64, 88)
BG_GRID_A = (26, 30, 40)
BG_GRID_B = (30, 35, 46)
GRID_LINE_COLOR = (40, 48, 64)

TEXT_COLOR = (235, 240, 245)
TEXT_MUTED = (150, 162, 178)
TEXT_GOLD = (255, 215, 55)
TEXT_GREEN = (80, 230, 120)
TEXT_RED = (255, 80, 80)
TEXT_BLUE = (80, 180, 255)
TEXT_PURPLE = (200, 120, 255)

# Element Colors: (Primary / Bright, Secondary / Deep)
ELEMENT_COLORS = {
    "NONE": ((180, 190, 200), (120, 130, 140)),
    "LIGHT": ((255, 245, 140), (220, 190, 60)),
    "DARKNESS": ((185, 95, 255), (110, 35, 175)),
    "WATER": ((60, 185, 255), (20, 110, 210)),
    "FIRE": ((255, 95, 35), (200, 40, 15)),
    "NATURE": ((65, 225, 95), (25, 150, 50)),
    "EARTH": ((210, 150, 80), (145, 95, 45)),
}

# Economy & Gameplay Defaults
STARTING_LIVES = 50
DEFAULT_INTEREST_RATE = 0.02  # 2.0%
INTEREST_INTERVAL = 15.0      # 15 seconds
TOWER_SELL_RATIO = 0.80       # 80% refund on sell

# Difficulty Modifiers (Gold, Creep HP multiplier, Creep Speed multiplier)
DIFFICULTY_SETTINGS = {
    "Normal": {
        "starting_gold": 120,
        "hp_mult": 1.0,
        "speed_mult": 1.0,
        "gold_mult": 1.0,
        "lives": 50,
    },
    "Hard": {
        "starting_gold": 90,
        "hp_mult": 1.35,
        "speed_mult": 1.1,
        "gold_mult": 0.9,
        "lives": 35,
    },
    "Chaos": {
        "starting_gold": 75,
        "hp_mult": 1.8,
        "speed_mult": 1.2,
        "gold_mult": 0.8,
        "lives": 20,
    },
}
