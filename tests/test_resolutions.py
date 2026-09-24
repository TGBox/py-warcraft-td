"""Tests for dynamic resolution scaling and LayoutConfig metrics."""

from py_warcraft_td.config import create_layout_config
from py_warcraft_td.game import Game


def test_layout_fullhd_1080p():
    """Verify 1920x1080 Full HD layout metrics."""
    layout = create_layout_config(1920, 1080)
    assert layout.screen_width == 1920
    assert layout.screen_height == 1080
    assert layout.grid_cols == 26
    assert layout.grid_rows == 17
    assert layout.cell_size == 48
    assert layout.grid_width == 26 * 48
    assert layout.spawn_cell == (0, 8)
    assert layout.goal_cell == (25, 8)
    assert layout.sidebar_width >= 500


def test_layout_ultrawide_21_9():
    """Verify 2560x1080 Ultrawide layout metrics."""
    layout = create_layout_config(2560, 1080)
    assert layout.screen_width == 2560
    assert layout.screen_height == 1080
    assert layout.grid_cols == 34
    assert layout.grid_rows == 17
    assert layout.cell_size == 48
    assert layout.grid_width == 34 * 48
    assert layout.spawn_cell == (0, 8)
    assert layout.goal_cell == (33, 8)
    assert layout.sidebar_width >= 800  # Wide sidebar for dual-column tower display


def test_game_resolution_switching():
    """Verify dynamic resolution switching on Game instance."""
    game = Game(width=1920, height=1080, headless=True)
    assert game.layout.screen_width == 1920
    assert game.layout.grid_cols == 26

    # Switch to 2560x1080
    game.set_resolution(2560, 1080)
    assert game.layout.screen_width == 2560
    assert game.layout.grid_cols == 34

    # Run simulation frames in Ultrawide
    game.start_game(mode_waves=20, difficulty="Normal")
    for _ in range(30):
        game.update(1.0 / 60.0)
        game.draw()

    assert game.game_state == "PLAYING"
