"""
HidingSpot class for wardrobes, lockers, and tables where Andreas can conceal himself.
"""

from typing import Tuple
import pygame


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
        if self.spot_type == "wardrobe":
            # Dark wood double-door wardrobe
            pygame.draw.rect(surface, (70, 45, 25), rect, border_radius=2)
            pygame.draw.rect(surface, (40, 25, 15), rect, width=2, border_radius=2)
            # Center split line
            pygame.draw.line(surface, (40, 25, 15), (rect.centerx, rect.top + 2), (rect.centerx, rect.bottom - 2), 2)
            # Door handles
            pygame.draw.circle(surface, (200, 180, 70), (rect.centerx - 4, rect.centery), 2)
            pygame.draw.circle(surface, (200, 180, 70), (rect.centerx + 4, rect.centery), 2)
        else:
            # Wooden table
            pygame.draw.rect(surface, (110, 80, 50), rect, border_radius=3)
            pygame.draw.rect(surface, (60, 40, 20), rect, width=2, border_radius=3)
