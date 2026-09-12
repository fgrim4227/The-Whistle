"""
GameObject and ThrowableProjectile classes for items, tools, and interactable environmental objects.
"""

from typing import Optional, Tuple
import pygame
import math


class GameObject:
    def __init__(self, obj_type: str, x: float, y: float, name: str, is_collectible: bool = True) -> None:
        self.obj_type = obj_type  # "key", "battery", "crowbar", "throwable"
        self.x = float(x)
        self.y = float(y)
        self.width = 16
        self.height = 16
        self.name = name
        self.is_collectible = is_collectible
        self.is_picked = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface: pygame.Surface) -> None:
        if self.is_picked:
            return

        rect = self.get_rect()
        if self.obj_type == "battery":
            # Battery icon
            pygame.draw.rect(surface, (60, 180, 60), rect, border_radius=2)
            pygame.draw.rect(surface, (220, 220, 220), (rect.left + 4, rect.top - 2, 8, 3))
        elif self.obj_type == "key":
            # Golden key icon
            pygame.draw.circle(surface, (230, 190, 40), (rect.centerx, rect.top + 5), 4)
            pygame.draw.line(surface, (230, 190, 40), (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 2), 2)
            pygame.draw.line(surface, (230, 190, 40), (rect.centerx, rect.bottom - 4), (rect.right - 2, rect.bottom - 4), 2)
        elif self.obj_type == "crowbar":
            # Red iron crowbar
            pygame.draw.line(surface, (180, 40, 40), (rect.left + 2, rect.bottom - 2), (rect.right - 4, rect.top + 2), 3)
            pygame.draw.arc(surface, (180, 40, 40), (rect.right - 8, rect.top, 8, 8), 0, math.pi, 2)
        elif self.obj_type == "throwable":
            # Stone / Bottle projectile
            pygame.draw.circle(surface, (160, 150, 140), (rect.centerx, rect.centery), 5)


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

    def render(self, surface: pygame.Surface) -> None:
        if self.active:
            pygame.draw.circle(surface, (220, 210, 190), (int(self.x), int(self.y)), self.radius)
