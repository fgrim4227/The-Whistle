"""
HidingSpot class for wardrobes, lockers, and tables where Andreas can conceal himself.
"""

from typing import Tuple
import pygame

from src.definitions.items import HIDING_SPOT_ARCHETYPES


class HidingSpot:
    def __init__(
        self,
        spot_type: str,
        x: float,
        y: float,
        width: int = 32,
        height: int = 32,
        render_graphic: bool = True,
        is_solid: bool = True,
    ) -> None:
        self.spot_type = spot_type  # "wardrobe", "table"
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.is_occupied = False
        self.render_graphic = render_graphic
        self.is_solid = is_solid

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if not self.render_graphic:
            return

        rect = self.get_rect().move(-camera_offset[0], -camera_offset[1])
        draw = HIDING_SPOT_ARCHETYPES.get(self.spot_type, HIDING_SPOT_ARCHETYPES["table"])
        draw(surface, rect)
