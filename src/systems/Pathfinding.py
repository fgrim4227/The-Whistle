"""
Grid-based A* pathfinding for a Room, so a monster walking toward a
point can route around furniture instead of walking straight at it and
getting stuck. This module only answers "what points should I walk
through to get there without hitting anything" -- the actual walking
(Monster.move_towards) doesn't change at all; a caller just feeds it
find_path()'s waypoints one at a time instead of one raw target.
"""

import heapq
import math
from typing import Dict, List, Optional, Tuple

import pygame

# Size, in world pixels, of one pathfinding cell. Every room in this
# game is 512x288px and divides evenly into this (32x18 cells), whether
# it came from a 16px-tile Tiled map or a 32px-tile procedural one --
# this grid is its own thing, unrelated to either tile size.
CELL_SIZE = 16

_NEIGHBOR_STEPS: List[Tuple[int, int]] = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (1, -1), (-1, 1), (1, 1),
]


def _build_walkable_grid(room, entity_width: float) -> Tuple[List[List[bool]], int, int]:
    """
    A fresh True/False grid, cell [y][x] True meaning "clear to walk
    through". Every obstacle is padded outward by half the entity's
    width first, so a path is never planned through a gap the entity's
    own body couldn't actually fit through. Rebuilt from scratch every
    call rather than cached, since a room's obstacles can change (a
    door gets unlocked) and rooms here are small enough that rebuilding
    costs nothing worth worrying about.
    """
    cols = max(1, room.width // CELL_SIZE)
    rows = max(1, room.height // CELL_SIZE)
    margin = entity_width / 2.0
    padded_obstacles = [obs.inflate(margin * 2, margin * 2) for obs in room.get_obstacles()]

    grid = [[True] * cols for _ in range(rows)]
    for gy in range(rows):
        cell_top = gy * CELL_SIZE
        for gx in range(cols):
            cell_rect = pygame.Rect(gx * CELL_SIZE, cell_top, CELL_SIZE, CELL_SIZE)
            if any(cell_rect.colliderect(obs) for obs in padded_obstacles):
                grid[gy][gx] = False
    return grid, cols, rows


def _octile_distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)


def _search(
    grid: List[List[bool]], cols: int, rows: int, start: Tuple[int, int], goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """Standard A* over the grid; returns cell coordinates from start to goal, or None if unreachable."""
    if not grid[goal[1]][goal[0]]:
        return None

    open_heap: List[Tuple[float, Tuple[int, int]]] = [(0.0, start)]
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    best_cost: Dict[Tuple[int, int], float] = {start: 0.0}
    visited = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        cx, cy = current
        for dx, dy in _NEIGHBOR_STEPS:
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < cols and 0 <= ny < rows) or not grid[ny][nx]:
                continue
            if dx != 0 and dy != 0 and (not grid[cy][nx] or not grid[ny][cx]):
                # Blocks cutting the corner diagonally between two
                # obstacles that don't actually leave room to pass.
                continue

            step_cost = math.sqrt(2) if dx != 0 and dy != 0 else 1.0
            neighbor = (nx, ny)
            tentative = best_cost[current] + step_cost
            if tentative < best_cost.get(neighbor, math.inf):
                came_from[neighbor] = current
                best_cost[neighbor] = tentative
                priority = tentative + _octile_distance(neighbor, goal)
                heapq.heappush(open_heap, (priority, neighbor))

    return None


def _has_clear_line(grid: List[List[bool]], cols: int, rows: int, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    steps = max(abs(dx), abs(dy)) * 4
    if steps == 0:
        return True
    for i in range(steps + 1):
        t = i / steps
        x = round(a[0] + dx * t)
        y = round(a[1] + dy * t)
        if not (0 <= x < cols and 0 <= y < rows) or not grid[y][x]:
            return False
    return True


def _smooth(grid: List[List[bool]], cols: int, rows: int, cells: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Collapses the raw, staircase-y cell-by-cell route into just its
    corners: as long as there's a clear straight line between two
    points on the path, every cell between them is dropped. Without
    this, the monster would visibly turn every 16px instead of walking
    a natural-looking line toward each real turn.
    """
    if len(cells) <= 2:
        return cells

    smoothed = [cells[0]]
    i = 0
    while i < len(cells) - 1:
        j = len(cells) - 1
        while j > i + 1 and not _has_clear_line(grid, cols, rows, cells[i], cells[j]):
            j -= 1
        smoothed.append(cells[j])
        i = j
    return smoothed


def find_path(
    room, start: Tuple[float, float], goal: Tuple[float, float], entity_width: float = 24.0
) -> List[Tuple[float, float]]:
    """
    A list of world-space (x, y) points to walk through, in order, to
    get from start to goal while routing around room.get_obstacles()
    -- the real goal position is always the last entry. Returns an
    empty list if no route exists (the goal itself is unreachable).

    This rebuilds the room's walkable grid on every call, so it's fast
    enough for occasional use but callers driving a chase should ask
    for a fresh path every second or so, not every frame -- the target
    is usually still roughly where it was a moment ago anyway.
    """
    grid, cols, rows = _build_walkable_grid(room, entity_width)

    def to_cell(point: Tuple[float, float]) -> Tuple[int, int]:
        cx = max(0, min(cols - 1, int(point[0] // CELL_SIZE)))
        cy = max(0, min(rows - 1, int(point[1] // CELL_SIZE)))
        return cx, cy

    start_cell = to_cell(start)
    goal_cell = to_cell(goal)

    # An entity hugging a wall can have its own current cell padded
    # solid by _build_walkable_grid's margin -- always allow leaving
    # from wherever it actually already is.
    grid[start_cell[1]][start_cell[0]] = True

    cell_path = _search(grid, cols, rows, start_cell, goal_cell)
    if cell_path is None:
        return []

    cell_path = _smooth(grid, cols, rows, cell_path)

    waypoints = [
        (gx * CELL_SIZE + CELL_SIZE / 2.0, gy * CELL_SIZE + CELL_SIZE / 2.0) for gx, gy in cell_path
    ]
    waypoints[-1] = goal
    return waypoints
