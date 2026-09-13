"""
BaseEntity class for all movable entities (Player, Monster).
"""

from typing import Optional, Tuple
import pygame


class BaseEntity:
    def __init__(self, x: float, y: float, width: int, height: int, speed: float = 80.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = "down"  # "up", "down", "left", "right"
        self.vx = 0.0
        self.vy = 0.0
        self.is_dead = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def render(self, surface: pygame.Surface) -> None:
        # Geometric fallback rendering
        pygame.draw.rect(surface, (180, 180, 180), self.get_rect())
