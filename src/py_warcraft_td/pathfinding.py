"""A* pathfinding and maze validation for ground and flying creeps."""

import heapq
from typing import Dict, List, Optional, Set, Tuple
from py_warcraft_td.config import GRID_COLS, GRID_ROWS, CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y


GridCoord = Tuple[int, int]
PixelCoord = Tuple[float, float]


def grid_to_pixel(coord: GridCoord) -> PixelCoord:
    """Convert grid cell (col, row) to world pixel center (x, y)."""
    col, row = coord
    x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE / 2.0
    y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE / 2.0
    return (x, y)


def pixel_to_grid(pixel: PixelCoord) -> Optional[GridCoord]:
    """Convert screen pixel coordinates to grid cell (col, row). Returns None if out of bounds."""
    x, y = pixel
    rel_x = x - GRID_OFFSET_X
    rel_y = y - GRID_OFFSET_Y
    if rel_x < 0 or rel_y < 0:
        return None
    col = int(rel_x // CELL_SIZE)
    row = int(rel_y // CELL_SIZE)
    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
        return (col, row)
    return None


class PathFinder:
    """A* Pathfinding engine for the dynamic mazing grid."""

    def __init__(self, cols: int = GRID_COLS, rows: int = GRID_ROWS):
        self.cols = cols
        self.rows = rows
        # Orthogonal neighbors (prevents diagonal clipping through adjacent towers)
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def astar(
        self,
        start: GridCoord,
        goal: GridCoord,
        blocked: Set[GridCoord],
    ) -> Optional[List[GridCoord]]:
        """Find the shortest path from start to goal avoiding blocked cells using A*."""
        if start == goal:
            return [start]
        if start in blocked or goal in blocked:
            return None

        # Priority queue stores tuples of (f_score, h_score, current_node)
        open_set: List[Tuple[float, float, GridCoord]] = []
        heapq.heappush(open_set, (self._heuristic(start, goal), 0.0, start))

        came_from: Dict[GridCoord, GridCoord] = {}
        g_score: Dict[GridCoord, float] = {start: 0.0}

        visited: Set[GridCoord] = set()

        while open_set:
            _, current_g, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            if current in visited:
                continue
            visited.add(current)

            for dx, dy in self.directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if not (0 <= neighbor[0] < self.cols and 0 <= neighbor[1] < self.rows):
                    continue
                if neighbor in blocked and neighbor != goal:
                    continue

                tentative_g = current_g + 1.0

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = self._heuristic(neighbor, goal)
                    f = tentative_g + h
                    heapq.heappush(open_set, (f, tentative_g, neighbor))

        return None

    def _heuristic(self, a: GridCoord, b: GridCoord) -> float:
        """Manhattan distance heuristic."""
        return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def can_place_tower(
        self,
        col: int,
        row: int,
        spawn: GridCoord,
        goal: GridCoord,
        occupied_cells: Set[GridCoord],
        active_ground_creeps: Optional[List[GridCoord]] = None,
    ) -> bool:
        """Verify whether placing a tower at (col, row) is valid and does NOT trap creeps or block the goal."""
        target = (col, row)
        # Cannot build on spawn, goal, or already occupied cells
        if target == spawn or target == goal or target in occupied_cells:
            return False

        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False

        # Hypothetically place the tower
        test_blocked = occupied_cells | {target}

        # Check path from spawn to goal
        if self.astar(spawn, goal, test_blocked) is None:
            return False

        # Check paths for all active ground creeps
        if active_ground_creeps:
            for creep_cell in active_ground_creeps:
                if creep_cell == target:
                    return False
                if self.astar(creep_cell, goal, test_blocked) is None:
                    return False

        return True
