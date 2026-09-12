"""
Room class representing an individual physical room in the cabin.
"""

from typing import List, Optional, Tuple
import pygame
import settings
from src.world.Door import Door
from src.world.GameObject import GameObject
from src.world.HidingSpot import HidingSpot
from src.entities.NPC import NPC


class Room:
    def __init__(
        self,
        name: str,
        display_name: str,
        cols: int = settings.GRID_COLS,
        rows: int = settings.GRID_ROWS,
    ) -> None:
        self.name = name
        self.display_name = display_name
        self.cols = cols
        self.rows = rows
        self.tile_size = settings.TILE_SIZE
        self.width = cols * self.tile_size
        self.height = rows * self.tile_size

        self.solid_tiles: List[pygame.Rect] = []
        self.doors: List[Door] = []
        self.items: List[GameObject] = []
        self.hiding_spots: List[HidingSpot] = []
        self.npc: Optional[NPC] = None
        self.patrol_waypoints: List[Tuple[float, float]] = []

        # Weathered dark wood floor color
        self.floor_color = (42, 32, 25)
        self.wall_color = (25, 20, 18)

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
        # Add furniture and hiding spots
        for spot in self.hiding_spots:
            obs.append(spot.get_rect())
        return obs

    def render(self, surface: pygame.Surface) -> None:
        # Background / Cabin room floor
        surface.fill(self.floor_color)
        
        # Wood floor plank groove lines
        for y in range(0, self.height, self.tile_size):
            pygame.draw.line(surface, (35, 26, 20), (0, y), (self.width, y), 1)

        # Draw boundary walls
        for wall in self.solid_tiles:
            pygame.draw.rect(surface, self.wall_color, wall)
            pygame.draw.rect(surface, (15, 12, 10), wall, width=1)

        # Draw doors
        for door in self.doors:
            door.render(surface)

        # Draw hiding spots
        for spot in self.hiding_spots:
            spot.render(surface)

        # Draw floor items
        for item in self.items:
            item.render(surface)

        # Draw NPC if present
        if self.npc:
            self.npc.render(surface)
