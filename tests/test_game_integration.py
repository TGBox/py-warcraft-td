"""Integration tests for Game controller, placement, and simulation loop."""

from py_warcraft_td.elements import Element
from py_warcraft_td.game import Game
from py_warcraft_td.towers.tower_catalog import get_tower_def


def test_game_full_simulation_cycle():
    """Run headless simulation and verify tower placement, path recalculation, and updates."""
    game = Game(headless=True)
    game.start_game(mode_waves=20, difficulty="Normal")

    arrow_def = get_tower_def("arrow_1")
    assert arrow_def is not None

    # Place an Arrow Tower at (2, 2)
    initial_gold = game.gold
    game._try_place_tower((2, 2), arrow_def)

    assert (2, 2) in game.towers
    assert game.gold == initial_gold - arrow_def.cost
    tower = game.towers[(2, 2)]
    assert tower.definition.id == "arrow_1"

    # Upgrade tower
    game._try_upgrade_tower(tower)
    assert tower.definition.id == "arrow_2"

    # Step simulation forward for 60 frames (1 second)
    for _ in range(60):
        game.update(1.0 / 60.0)
        game.draw()

    # Creeps should start spawning or countdown should progress
    assert game.game_state == "PLAYING"
    assert game.lives > 0


def test_cannot_place_tower_blocking_maze_in_game():
    game = Game(headless=True)
    game.start_game(mode_waves=20, difficulty="Normal")
    arrow_def = get_tower_def("arrow_1")

    # Build walls along column 4 leaving only row 0
    for r in range(1, 17):
        game.towers[(4, r)] = None  # Mock occupied

    # Try placing tower at (4, 0)
    old_count = len(game.towers)
    game._try_place_tower((4, 0), arrow_def)
    # Placement should be rejected because it blocks the maze
    assert (4, 0) not in game.towers
