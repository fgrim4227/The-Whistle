"""
Render archetypes for GameObject (keyed by obj_type) and HidingSpot
(keyed by spot_type): one drawing function per type, so adding a new
item or hiding-spot look means adding an entry here instead of another
branch in GameObject.render()/HidingSpot.render(). These are placeholder
shapes, not real sprites -- swap a function's body for a blit once art
exists, the callers never need to change.
"""

import math
from typing import Callable, Dict

import pygame


def _draw_battery(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, (60, 180, 60), rect, border_radius=2)
    pygame.draw.rect(surface, (220, 220, 220), (rect.left + 4, rect.top - 2, 8, 3))


def _draw_key(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.circle(surface, (230, 190, 40), (rect.centerx, rect.top + 5), 4)
    pygame.draw.line(surface, (230, 190, 40), (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 2), 2)
    pygame.draw.line(surface, (230, 190, 40), (rect.centerx, rect.bottom - 4), (rect.right - 2, rect.bottom - 4), 2)


def _draw_crowbar(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.line(surface, (180, 40, 40), (rect.left + 2, rect.bottom - 2), (rect.right - 4, rect.top + 2), 3)
    pygame.draw.arc(surface, (180, 40, 40), (rect.right - 8, rect.top, 8, 8), 0, math.pi, 2)


def _draw_throwable(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.circle(surface, (160, 150, 140), (rect.centerx, rect.centery), 5)


def _draw_lockpick(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.line(surface, (200, 200, 210), (rect.left + 2, rect.bottom - 2), (rect.right - 2, rect.top + 2), 2)
    pygame.draw.circle(surface, (200, 200, 210), (rect.right - 3, rect.top + 3), 2)


def _draw_old_key(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.circle(surface, (170, 140, 90), (rect.centerx, rect.top + 5), 4, width=2)
    pygame.draw.line(surface, (170, 140, 90), (rect.centerx, rect.top + 5), (rect.centerx, rect.bottom - 2), 2)


def _draw_cabinet(surface: pygame.Surface, rect: pygame.Rect) -> None:
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
    # Graphical tile is already drawn on tilemap layer
    pass


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
