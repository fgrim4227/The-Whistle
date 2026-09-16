import os
from typing import Any, List, Optional, Tuple
import pygame

import settings
from src.definitions.items import ITEM_ARCHETYPES

_FUSE_BOX_SPRITES_LOADED = False
_SPRITE_FUSE_BOX_OPEN: Optional[pygame.Surface] = None
_SPRITE_FUSE_BOX_CLOSED: Optional[pygame.Surface] = None


def _load_fuse_box_sprites() -> None:
    global _FUSE_BOX_SPRITES_LOADED, _SPRITE_FUSE_BOX_OPEN, _SPRITE_FUSE_BOX_CLOSED
    if _FUSE_BOX_SPRITES_LOADED:
        return
    _FUSE_BOX_SPRITES_LOADED = True
    sheet_path = os.path.join(settings.BASE_DIR, "assets", "graphics", "environment", "spritesheet.png")
    if os.path.exists(sheet_path):
        try:
            sheet = pygame.image.load(sheet_path).convert_alpha()
            _SPRITE_FUSE_BOX_OPEN = sheet.subsurface(pygame.Rect(736, 32, 16, 32))
            _SPRITE_FUSE_BOX_CLOSED = sheet.subsurface(pygame.Rect(720, 32, 16, 32))
        except Exception as e:
            print(f"Notice: Failed to load fuse box sprites: {e}")


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
        note_id: Optional[str] = None,
        yields: Optional[str] = None,
    ) -> None:
        self.obj_type = obj_type  # "key", "battery", "crowbar", "throwable", "cabinet", "safe", "note", ...
        self.x = float(x)
        self.y = float(y)
        self.width = int(width)
        self.height = int(height)
        self.is_collectible = is_collectible
        self.render_graphic = render_graphic
        self.note_id = note_id
        self.yields = yields
        self.is_picked = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0), house: Optional[Any] = None) -> None:
        if self.is_picked:
            return

        # Special dynamic handling for fuse_box: swaps between closed and open sprite upon restoring power
        if self.obj_type == "fuse_box":
            _load_fuse_box_sprites()
            rect = self.get_rect().move(-camera_offset[0], -camera_offset[1])
            is_powered = getattr(house, "power_restored", False) if house else False
            if is_powered and _SPRITE_FUSE_BOX_OPEN is not None:
                surface.blit(_SPRITE_FUSE_BOX_OPEN, (rect.x, rect.y))
            elif not is_powered and not self.render_graphic:
                # Closed fuse box tile is already pre-baked into the room background
                pass
            elif _SPRITE_FUSE_BOX_CLOSED is not None:
                surface.blit(_SPRITE_FUSE_BOX_CLOSED, (rect.x, rect.y))
            return

        if not self.render_graphic:
            return

        rect = self.get_rect().move(-camera_offset[0], -camera_offset[1])
        draw = ITEM_ARCHETYPES.get(self.obj_type)
        if draw:
            draw(surface, rect)


class ThrowableProjectile:
    """Projectile thrown by the player to stun or enrage El Silbón, or distract him via sound impact."""
    def __init__(self, x: float, y: float, direction: str, speed: float = 240.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.direction = direction
        self.radius = 4
        self.active = True
        self.distance_traveled = 0.0
        self.max_distance = 1000

        dir_vectors = {
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
            "up": (0.0, -1.0),
            "down": (0.0, 1.0),
        }
        self.dx, self.dy = dir_vectors.get(direction, (0.0, 1.0))

    def update(self, dt: float, obstacles: Optional[List[pygame.Rect]] = None) -> bool:
        """
        Updates projectile position. Returns True if projectile impacted
        an obstacle or reached max distance on this frame (generating noise).
        """
        if not self.active:
            return False

        step = self.speed * dt
        self.x += self.dx * step
        self.y += self.dy * step
        self.distance_traveled += step

        # Check collision with solid room obstacles
        if obstacles and self.get_rect().collidelist(obstacles) != -1:
            self.active = False
            return True

        if self.distance_traveled >= self.max_distance:
            self.active = False
            return True

        return False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if self.active:
            sx = int(self.x - camera_offset[0])
            sy = int(self.y - camera_offset[1])
            pygame.draw.circle(surface, (220, 210, 190), (sx, sy), self.radius)
