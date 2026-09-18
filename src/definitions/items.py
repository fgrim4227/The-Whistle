"""
Render archetypes for GameObject (keyed by obj_type) and HidingSpot
(keyed by spot_type): one drawing function per type, so adding a new
item or hiding-spot look means adding an entry here instead of another
branch in GameObject.render()/HidingSpot.render(). These are placeholder
shapes, not real sprites -- swap a function's body for a blit once art
exists, the callers never need to change.
"""

import math
import os
from typing import Callable, Dict, Optional

import pygame

import settings

_SPRITESHEET_SURFACE: Optional[pygame.Surface] = None
_SPRITE_BATTERY: Optional[pygame.Surface] = None
_SPRITE_FUSE_KEY: Optional[pygame.Surface] = None
_SPRITE_CABINET: Optional[pygame.Surface] = None
_SPRITE_OLD_KEY: Optional[pygame.Surface] = None
_SPRITE_KEY: Optional[pygame.Surface] = None
_SPRITE_LOCKPICK: Optional[pygame.Surface] = None


def _get_item_sprites() -> None:
    global _SPRITESHEET_SURFACE, _SPRITE_BATTERY, _SPRITE_FUSE_KEY, _SPRITE_CABINET
    global _SPRITE_OLD_KEY, _SPRITE_KEY, _SPRITE_LOCKPICK
    if _SPRITESHEET_SURFACE is None:
        sheet_path = os.path.join(settings.BASE_DIR, "assets", "graphics", "environment", "spritesheet.png")
        if os.path.exists(sheet_path):
            try:
                _SPRITESHEET_SURFACE = pygame.image.load(sheet_path).convert_alpha()
                _SPRITE_BATTERY = _SPRITESHEET_SURFACE.subsurface(pygame.Rect(592, 48, 16, 16))
                _SPRITE_FUSE_KEY = _SPRITESHEET_SURFACE.subsurface(pygame.Rect(592, 64, 16, 16))
                _SPRITE_CABINET = _SPRITESHEET_SURFACE.subsurface(pygame.Rect(592, 80, 16, 16))
                # New item sprites authored by Francisco in spritesheet:
                # (592, 96): Master Bedroom key (Yellow)
                # (608, 96): Forest key (Green)
                # (624, 96): Lockpick / Ganzúa (Silver hook)
                _SPRITE_OLD_KEY = _SPRITESHEET_SURFACE.subsurface(pygame.Rect(592, 96, 16, 16))
                _SPRITE_KEY = _SPRITESHEET_SURFACE.subsurface(pygame.Rect(608, 96, 16, 16))
                _SPRITE_LOCKPICK = _SPRITESHEET_SURFACE.subsurface(pygame.Rect(624, 96, 16, 16))
            except Exception as e:
                print(f"Notice: Failed to load item sprites from {sheet_path}: {e}")


def _draw_battery(surface: pygame.Surface, rect: pygame.Rect) -> None:
    _get_item_sprites()
    if _SPRITE_BATTERY is not None:
        surface.blit(_SPRITE_BATTERY, rect.topleft)
    else:
        pygame.draw.rect(surface, (60, 180, 60), rect, border_radius=2)
        pygame.draw.rect(surface, (220, 220, 220), (rect.left + 4, rect.top - 2, 8, 3))


def _draw_key(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draws Forest Key (Green Key from safe)."""
    _get_item_sprites()
    if _SPRITE_KEY is not None:
        if rect.width != 16 or rect.height != 16:
            scaled = pygame.transform.scale(_SPRITE_KEY, (rect.width, rect.height))
            surface.blit(scaled, rect.topleft)
        else:
            surface.blit(_SPRITE_KEY, rect.topleft)
    else:
        pygame.draw.circle(surface, (20, 180, 50), (rect.centerx, rect.top + 5), 4)
        pygame.draw.line(surface, (20, 180, 50), (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 2), 2)
        pygame.draw.line(surface, (20, 180, 50), (rect.centerx, rect.bottom - 4), (rect.right - 2, rect.bottom - 4), 2)


def _draw_crowbar(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.line(surface, (180, 40, 40), (rect.left + 2, rect.bottom - 2), (rect.right - 4, rect.top + 2), 3)
    pygame.draw.arc(surface, (180, 40, 40), (rect.right - 8, rect.top, 8, 8), 0, math.pi, 2)


def _draw_throwable(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.circle(surface, (160, 150, 140), (rect.centerx, rect.centery), 5)


def _draw_lockpick(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draws Lockpick / Ganzúa."""
    _get_item_sprites()
    if _SPRITE_LOCKPICK is not None:
        if rect.width != 16 or rect.height != 16:
            scaled = pygame.transform.scale(_SPRITE_LOCKPICK, (rect.width, rect.height))
            surface.blit(scaled, rect.topleft)
        else:
            surface.blit(_SPRITE_LOCKPICK, rect.topleft)
    else:
        pygame.draw.line(surface, (200, 200, 210), (rect.left + 2, rect.bottom - 2), (rect.right - 2, rect.top + 2), 2)
        pygame.draw.circle(surface, (200, 200, 210), (rect.right - 3, rect.top + 3), 2)


def _draw_old_key(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draws Master Bedroom Key (Yellow/Gold key from dining cabinet)."""
    _get_item_sprites()
    if _SPRITE_OLD_KEY is not None:
        if rect.width != 16 or rect.height != 16:
            scaled = pygame.transform.scale(_SPRITE_OLD_KEY, (rect.width, rect.height))
            surface.blit(scaled, rect.topleft)
        else:
            surface.blit(_SPRITE_OLD_KEY, rect.topleft)
    else:
        pygame.draw.circle(surface, (230, 190, 40), (rect.centerx, rect.top + 5), 4, width=2)
        pygame.draw.line(surface, (230, 190, 40), (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 2), 2)


def _draw_cabinet(surface: pygame.Surface, rect: pygame.Rect) -> None:
    _get_item_sprites()
    if _SPRITE_CABINET is not None:
        if rect.width != 16 or rect.height != 16:
            scaled = pygame.transform.scale(_SPRITE_CABINET, (rect.width, rect.height))
            surface.blit(scaled, rect.topleft)
        else:
            surface.blit(_SPRITE_CABINET, rect.topleft)
    else:
        pygame.draw.rect(surface, (90, 60, 40), rect, border_radius=2)
        pygame.draw.rect(surface, (50, 32, 20), rect, width=2, border_radius=2)
        pygame.draw.circle(surface, (200, 180, 70), rect.center, 2)


def _draw_safe(surface: pygame.Surface, rect: pygame.Rect) -> None:
    #pygame.draw.rect(surface, (60, 60, 65), rect, border_radius=3)
    #pygame.draw.rect(surface, (30, 30, 34), rect, width=2, border_radius=3)
    #pygame.draw.circle(surface, (200, 190, 60), rect.center, 4, width=1)
    pass


def _draw_note(surface: pygame.Surface, rect: pygame.Rect) -> None:
    paper_rect = pygame.Rect(rect.left + 2, rect.top + 1, max(12, rect.width - 4), max(14, rect.height - 2))
    pygame.draw.rect(surface, (235, 225, 200), paper_rect, border_radius=1)
    pygame.draw.rect(surface, (150, 130, 95), paper_rect, width=1, border_radius=1)
    for ly in range(paper_rect.top + 3, paper_rect.bottom - 2, 3):
        pygame.draw.line(surface, (100, 85, 65), (paper_rect.left + 2, ly), (paper_rect.right - 3, ly), 1)


def _draw_fuse_box(surface: pygame.Surface, rect: pygame.Rect) -> None:
    # Handled dynamically in GameObject.render() based on power_restored state
    pass


def _draw_fuse_key(surface: pygame.Surface, rect: pygame.Rect) -> None:
    _get_item_sprites()
    if _SPRITE_FUSE_KEY is not None:
        surface.blit(_SPRITE_FUSE_KEY, rect.topleft)
    else:
        pygame.draw.circle(surface, (140, 190, 220), (rect.centerx, rect.top + 5), 4)
        pygame.draw.circle(surface, (40, 80, 120), (rect.centerx, rect.top + 5), 2)
        pygame.draw.line(surface, (200, 210, 220), (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 2), 2)
        pygame.draw.line(surface, (200, 210, 220), (rect.centerx, rect.bottom - 4), (rect.right - 2, rect.bottom - 4), 2)


ITEM_ARCHETYPES: Dict[str, Callable[[pygame.Surface, pygame.Rect], None]] = {
    "battery": _draw_battery,
    "key": _draw_key,
    "crowbar": _draw_crowbar,
    "throwable": _draw_throwable,
    "lockpick": _draw_lockpick,
    "old_key": _draw_old_key,
    "cabinet": _draw_cabinet,
    "safe": _draw_safe,
    "note": _draw_note,
    "fuse_box": _draw_fuse_box,
    "fuse_key": _draw_fuse_key,
}


def _draw_wardrobe(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, (70, 45, 25), rect, border_radius=2)
    pygame.draw.rect(surface, (40, 25, 15), rect, width=2, border_radius=2)
    pygame.draw.line(surface, (40, 25, 15), (rect.centerx, rect.top + 2), (rect.centerx, rect.bottom - 2), 2)
    pygame.draw.circle(surface, (200, 180, 70), (rect.centerx - 4, rect.centery), 2)
    pygame.draw.circle(surface, (200, 180, 70), (rect.centerx + 4, rect.centery), 2)


def _draw_table(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, (110, 80, 50), rect, border_radius=3)
    pygame.draw.rect(surface, (60, 40, 20), rect, width=2, border_radius=3)


HIDING_SPOT_ARCHETYPES: Dict[str, Callable[[pygame.Surface, pygame.Rect], None]] = {
    "wardrobe": _draw_wardrobe,
    "table": _draw_table,
}


# Data-oriented sound mapping for dropping items on the floor (G key or Granny swap)
ITEM_DROP_SOUNDS: Dict[str, str] = {
    "key": "drop_forest_key",
    "old_key": "drop_key",
    "fuse_key": "drop_key",
    "lockpick": "drop_lockpick",
    "crowbar": "drop_heavy",
    "throwable": "object_hit",
    "battery": "drop_key",
}


def get_item_drop_sound(item_type: str) -> str:
    """Returns the audio sound identifier associated with dropping this item on the floor."""
    return ITEM_DROP_SOUNDS.get(item_type, "drop_key")
