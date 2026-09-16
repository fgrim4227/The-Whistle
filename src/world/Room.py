"""
Room class representing an individual physical room in the cabin.
"""

from typing import List, Optional, Tuple
import pygame
import settings
from src.world.Door import Door
from src.world.GameObject import GameObject
from src.world.HidingSpot import HidingSpot


class Room:
    def __init__(
        self,
        name: str,
        display_name: str,
        cols: int = settings.GRID_COLS,
        rows: int = settings.GRID_ROWS,
        build_walls: bool = True,
        tile_size: int = settings.TILE_SIZE,
    ) -> None:
        self.name = name
        self.display_name = display_name
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size
        self.width = cols * self.tile_size
        self.height = rows * self.tile_size

        self.solid_tiles: List[pygame.Rect] = []
        self.doors: List[Door] = []
        self.items: List[GameObject] = []
        self.hiding_spots: List[HidingSpot] = []
        self.patrol_waypoints: List[Tuple[float, float]] = []
        self.player_spawn: Optional[Tuple[float, float]] = None
        self.background_surface: Optional[pygame.Surface] = None

        # Weathered dark wood floor color (fallback for procedural rooms)
        self.floor_color = (42, 32, 25)
        self.wall_color = (25, 20, 18)

        if build_walls:
            self._build_perimeter_walls()

        self.boss = None

    def _build_perimeter_walls(self) -> None:
        """Generates outer boundary walls with openings for doorways."""
        ts = self.tile_size
        # Top wall
        self.solid_tiles.append(pygame.Rect(0, 0, self.width, ts))
        # Bottom wall
        self.solid_tiles.append(pygame.Rect(0, self.height - ts, self.width, ts))
        # Left wall
        self.solid_tiles.append(pygame.Rect(0, 0, ts, self.height))
        # Right wall
        self.solid_tiles.append(pygame.Rect(self.width - ts, 0, ts, self.height))

    def get_obstacles(self) -> List[pygame.Rect]:
        """Returns all solid obstacles that entities collide against."""
        obs = list(self.solid_tiles)
        # Add locked or barred doors as solid obstacles
        for door in self.doors:
            if door.is_locked or door.is_barred:
                obs.append(door.get_rect())
        # Add furniture and hiding spots that are marked as solid
        for spot in self.hiding_spots:
            if getattr(spot, "is_solid", True):
                obs.append(spot.get_rect())
        return obs

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        ox, oy = camera_offset
        if self.background_surface:
            # Render pre-baked Tiled graphic layers (Floors, Walls, Decors)
            surface.blit(self.background_surface, (-ox, -oy))
        else:
            # Fallback procedural floor rendering
            surface.fill(self.floor_color)
            for y in range(0, self.height, self.tile_size):
                pygame.draw.line(surface, (35, 26, 20), (-ox, y - oy), (self.width - ox, y - oy), 1)

            for wall in self.solid_tiles:
                w_rect = wall.move(-ox, -oy)
                pygame.draw.rect(surface, self.wall_color, w_rect)
                pygame.draw.rect(surface, (15, 12, 10), w_rect, width=1)

        # Draw doors
        house_ref = getattr(self, "house", None)
        for door in self.doors:
            door.render(surface, camera_offset, house=house_ref)

        # Draw hiding spots
        for spot in self.hiding_spots:
            spot.render(surface, camera_offset)

        # Draw floor items
        for item in self.items:
            item.render(surface, camera_offset, house=house_ref)
