"""Configuration and constants for py-warcraft-td (Element TD)."""

from typing import Tuple

# Screen & Window Dimensions
SCREEN_WIDTH = 1360
SCREEN_HEIGHT = 768
FPS = 60

# Grid Geometry
GRID_COLS = 24
GRID_ROWS = 17
CELL_SIZE = 36
GRID_OFFSET_X = 24
GRID_OFFSET_Y = 80
GRID_WIDTH = GRID_COLS * CELL_SIZE   # 864 px
GRID_HEIGHT = GRID_ROWS * CELL_SIZE  # 612 px

# Spawn & Exit Coordinates (in grid coordinates)
SPAWN_CELL = (0, 8)
GOAL_CELL = (GRID_COLS - 1, 8)

# Sidebar UI Geometry
SIDEBAR_X = GRID_OFFSET_X + GRID_WIDTH + 20  # 908 px
SIDEBAR_Y = GRID_OFFSET_Y
SIDEBAR_WIDTH = SCREEN_WIDTH - SIDEBAR_X - 24 # ~428 px
SIDEBAR_HEIGHT = GRID_HEIGHT

# Palette (Warcraft 3 Dark Fantasy & Elemental Accents)
BG_DARK = (16, 18, 24)
BG_PANEL = (24, 28, 38)
BG_PANEL_ALT = (32, 38, 52)
BG_PANEL_BORDER = (55, 68, 92)
BG_GRID_A = (28, 32, 42)
BG_GRID_B = (32, 37, 48)
GRID_LINE_COLOR = (42, 50, 68)

TEXT_COLOR = (235, 240, 245)
TEXT_MUTED = (150, 162, 178)
TEXT_GOLD = (255, 210, 60)
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
