"""Tests for A* pathfinding and dynamic maze validation."""

from py_warcraft_td.config import GOAL_CELL, GRID_COLS, GRID_ROWS, SPAWN_CELL
from py_warcraft_td.pathfinding import PathFinder, grid_to_pixel, pixel_to_grid


def test_clear_grid_path():
    """Verify that a path exists on an empty grid from spawn to goal."""
    pf = PathFinder(GRID_COLS, GRID_ROWS)
    path = pf.astar(SPAWN_CELL, GOAL_CELL, set())
    assert path is not None
    assert path[0] == SPAWN_CELL
    assert path[-1] == GOAL_CELL
    assert len(path) == (GOAL_CELL[0] - SPAWN_CELL[0]) + abs(GOAL_CELL[1] - SPAWN_CELL[1]) + 1


def test_maze_corridor_path():
    """Verify A* navigates around placed obstacles/towers."""
    pf = PathFinder(GRID_COLS, GRID_ROWS)
    # Block column 5 except for row 0
    blocked = {(5, r) for r in range(1, GRID_ROWS)}
    path = pf.astar(SPAWN_CELL, GOAL_CELL, blocked)
    assert path is not None
    # Must pass through (5, 0)
    assert (5, 0) in path


def test_can_place_tower_blocks_wall():
    """Verify player cannot completely seal off the maze."""
    pf = PathFinder(GRID_COLS, GRID_ROWS)
    # Block column 5 except row 0
    blocked = {(5, r) for r in range(1, GRID_ROWS)}

    # Attempting to place a tower at (5, 0) would seal off the maze!
    assert not pf.can_place_tower(5, 0, SPAWN_CELL, GOAL_CELL, blocked)

    # Placing anywhere else that keeps a path open should be valid
    assert pf.can_place_tower(2, 2, SPAWN_CELL, GOAL_CELL, blocked)


def test_cannot_build_on_spawn_or_goal():
    pf = PathFinder(GRID_COLS, GRID_ROWS)
    assert not pf.can_place_tower(SPAWN_CELL[0], SPAWN_CELL[1], SPAWN_CELL, GOAL_CELL, set())
    assert not pf.can_place_tower(GOAL_CELL[0], GOAL_CELL[1], SPAWN_CELL, GOAL_CELL, set())


def test_grid_pixel_conversions():
    px = grid_to_pixel((0, 0))
    grid = pixel_to_grid(px)
    assert grid == (0, 0)
