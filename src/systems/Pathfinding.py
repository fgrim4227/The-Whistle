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
import random 
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

def _open_start_area(
    grid: List[List[bool]],
    cols: int,
    rows: int,
    start_cell: Tuple[int, int],
    obstacles: List[pygame.Rect],
    radius: int = 2,
) -> None:
    """
    Around where the entity already stands, decide which cells are walkable
    from the obstacles' real footprint instead of their padded one. The
    padding keeps a route from hugging furniture, but an entity standing
    close to a piece of it is already inside that padding -- judged by the
    padded grid it would be boxed in with nowhere to step, and no route
    would exist at all. Its own body is proof those cells are passable, so
    near the start reality wins and it can walk back out to the padded
    route further along.
    """
    sx, sy = start_cell
    for gy in range(max(0, sy - radius), min(rows, sy + radius + 1)):
        for gx in range(max(0, sx - radius), min(cols, sx + radius + 1)):
            if grid[gy][gx]:
                continue
            cell_rect = pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if not any(cell_rect.colliderect(obs) for obs in obstacles):
                grid[gy][gx] = True


def _nearest_walkable_cell(
    grid: List[List[bool]], cols: int, rows: int, cell: Tuple[int, int], max_radius: int = 6
) -> Optional[Tuple[int, int]]:
    """
    If `cell` itself isn't walkable (e.g. it fell inside an obstacle's
    safety margin), looks outward ring by ring for the closest cell
    that is -- so a goal right next to furniture still gets a real
    path instead of find_path giving up entirely.
    """
    if grid[cell[1]][cell[0]]:
        return cell

    cx, cy = cell
    for radius in range(1, max_radius + 1):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if max(abs(dx), abs(dy)) != radius:
                    continue
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx]:
                    return (nx, ny)
    return None


def find_path(
    room,
    start: Tuple[float, float],
    goal: Tuple[float, float],
    entity_width: float = 24.0,
    min_entity_width: Optional[float] = None,
) -> List[Tuple[float, float]]:
    """
    A list of (x, y) points in world space traversed in order to get
    from the start to the destination while avoiding obstacles returned
    by `room.get_obstacles()`.

    The list is never empty. When the destination sits inside furniture
    (or inside the safety margin around it), the route ends at the
    closest spot a body that wide can actually stand on instead of at
    the destination itself -- walking at a point no one could ever reach
    means shoving against the furniture forever, since the caller's
    "am I there yet" check can never come out true. When no route exists
    at all, the answer is a single point: the destination, to be walked
    at in a straight line for lack of anything better.
    """
    if min_entity_width is None:
        min_entity_width = entity_width

    raw_obstacles = room.get_obstacles()

    width = entity_width
    while True:
        grid, cols, rows = _build_walkable_grid(room, width)

        def to_cell(point: Tuple[float, float]) -> Tuple[int, int]:
            cx = max(0, min(cols - 1, int(point[0] // CELL_SIZE)))
            cy = max(0, min(rows - 1, int(point[1] // CELL_SIZE)))
            return cx, cy

        start_cell = to_cell(start)
        goal_cell = to_cell(goal)

        goal_is_standable = grid[goal_cell[1]][goal_cell[0]]
        if not goal_is_standable:
            nearest = _nearest_walkable_cell(grid, cols, rows, goal_cell)
            if nearest is None:
                return [goal]
            goal_cell = nearest

        _open_start_area(grid, cols, rows, start_cell, raw_obstacles)
        grid[start_cell[1]][start_cell[0]] = True

        cell_path = _search(grid, cols, rows, start_cell, goal_cell)
        if cell_path is not None:
            break

        if width <= min_entity_width:
            return [goal]
        width = max(min_entity_width, width - 8)

    cell_path = _smooth(grid, cols, rows, cell_path)

    waypoints = [
        (gx * CELL_SIZE + CELL_SIZE / 2.0, gy * CELL_SIZE + CELL_SIZE / 2.0) for gx, gy in cell_path
    ]
    if goal_is_standable and waypoints:
        waypoints[-1] = goal

    # If the first waypoint is where the entity already stands, advance past it
    # so path consumers don't cycle in place on their own current position.
    while waypoints and math.hypot(waypoints[0][0] - start[0], waypoints[0][1] - start[1]) < 10.0:
        waypoints.pop(0)

    return waypoints


def nearest_standable(room, position: Tuple[float, float], entity_width: float = 24.0) -> Tuple[float, float]:
    """
    The closest point to `position` where a body that wide fits without
    overlapping anything solid. Returns `position` untouched when the
    whole area around it is blocked.
    """
    grid, cols, rows = _build_walkable_grid(room, entity_width)
    cx = max(0, min(cols - 1, int(position[0] // CELL_SIZE)))
    cy = max(0, min(rows - 1, int(position[1] // CELL_SIZE)))

    cell = _nearest_walkable_cell(grid, cols, rows, (cx, cy))
    if cell is None:
        return position
    return (cell[0] * CELL_SIZE + CELL_SIZE / 2.0, cell[1] * CELL_SIZE + CELL_SIZE / 2.0)


def sample_walkable_points(
    room, count: int = 4, min_spacing: float = 120.0, entity_width: float = 24.0
) -> List[Tuple[float, float]]:
    """
    create random points on the walkable floor, each separated from
    the others by at least 'min_spacing' px—so they don't all end up
    clustered in a corner. If the room is too small to find that many
    points with that spacing, it returns the ones it managed to find
    instead of failing
    """
    grid, cols, rows = _build_walkable_grid(room, entity_width)
    candidates = [
        (gx * CELL_SIZE + CELL_SIZE / 2.0, gy * CELL_SIZE + CELL_SIZE / 2.0)
        for gy in range(rows)
        for gx in range(cols)
        if grid[gy][gx]
    ]
    random.shuffle(candidates)

    points: List[Tuple[float, float]] = []
    for point in candidates:
        if len(points) >= count:
            break
        if all(math.hypot(point[0] - p[0], point[1] - p[1]) >= min_spacing for p in points):
            points.append(point)

    if not points and candidates:
        points.append(candidates[0])

    return points
