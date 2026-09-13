"""
GameObject and ThrowableProjectile classes for items, tools, and interactable environmental objects.
"""

from typing import Optional, Tuple
import pygame

from src.definitions.items import ITEM_ARCHETYPES


class GameObject:
    def __init__(
        self,
        obj_type: str,
        x: float,
        y: float,
        width: int = 16,
        height: int = 16,
        is_collectible: bool = True,
        render_graphic: bool = True,
    ) -> None:
        self.obj_type = obj_type  # "key", "battery", "crowbar", "throwable", "cabinet", "safe", ...
        self.x = float(x)
        self.y = float(y)
        self.width = int(width)
        self.height = int(height)
        self.is_collectible = is_collectible
        self.render_graphic = render_graphic
        self.is_picked = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if self.is_picked or not self.render_graphic:
            return

        rect = self.get_rect().move(-camera_offset[0], -camera_offset[1])
        draw = ITEM_ARCHETYPES.get(self.obj_type)
        if draw:
            draw(surface, rect)


class ThrowableProjectile:
    """Projectile thrown by the player to stun or enrage El Silbón."""
    def __init__(self, x: float, y: float, direction: str, speed: float = 240.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.direction = direction
        self.radius = 4
        self.active = True
        self.distance_traveled = 0.0
        self.max_distance = 160.0

        dir_vectors = {
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
            "up": (0.0, -1.0),
            "down": (0.0, 1.0),
        }
        self.dx, self.dy = dir_vectors.get(direction, (0.0, 1.0))

    def update(self, dt: float) -> None:
        step = self.speed * dt
        self.x += self.dx * step
        self.y += self.dy * step
        self.distance_traveled += step

        if self.distance_traveled >= self.max_distance:
            self.active = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if self.active:
            sx = int(self.x - camera_offset[0])
            sy = int(self.y - camera_offset[1])
            pygame.draw.circle(surface, (220, 210, 190), (sx, sy), self.radius)
