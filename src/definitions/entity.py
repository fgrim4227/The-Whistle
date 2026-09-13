"""
Sprite/animation specs for Player and Monster, plus build_animations, a
loader both of them call instead of each hand-rolling their own slicing
loop. Each animation names a texture (from settings.TEXTURES) and the
1-based frame indices to play from it (settings.FRAMES/settings.frame()
already sliced them), plus playback interval/loop count.
"""

from typing import Any, Dict, Tuple

import pygame
from gale.animation import Animation

import settings

PLAYER_SIZE = (16, 32)
PLAYER_FALLBACK_COLOR = (40, 90, 160)

PLAYER_ANIMATIONS: Dict[str, Dict[str, Any]] = {
    "walk-down": {"texture": "player_walk_down", "frames": list(range(1, 8)), "interval": 0.12},
    "walk-up": {"texture": "player_walk_up", "frames": list(range(1, 7)), "interval": 0.12},
    "walk-left": {"texture": "player_walk_left", "frames": list(range(1, 8)), "interval": 0.12},
    "walk-right": {"texture": "player_walk_right", "frames": list(range(1, 8)), "interval": 0.12},
    "idle-down": {"texture": "player_idle", "frames": list(range(1, 5)), "interval": 0.25},
    "idle-up": {"texture": "player_idle", "frames": list(range(1, 5)), "interval": 0.25},
    "idle-left": {"texture": "player_idle", "frames": list(range(1, 5)), "interval": 0.25},
    "idle-right": {"texture": "player_idle", "frames": list(range(1, 5)), "interval": 0.25},
    "dying": {"texture": "player_dying", "frames": list(range(1, 7)), "interval": 0.18, "loops": 1},
}

MONSTER_SIZE = (24, 44)
MONSTER_SPRITE_SIZE = (64, 64)
MONSTER_FALLBACK_COLOR = (160, 40, 40)
# render_sprite's own offset from the entity's x/y to the sprite's top-left.
MONSTER_SPRITE_OFFSET = (-20, -12)

# silbon_walk is one 10-col x 4-row sheet (up/left/right/down per row);
# silbon_idle is one 7-col x 4-row sheet (down/up/left/right per row).
# Frame indices below are 1-based, row-major across the whole sheet.
MONSTER_ANIMATIONS: Dict[str, Dict[str, Any]] = {
    "walk-up": {"texture": "silbon_walk", "frames": list(range(1, 11)), "interval": 0.10},
    "walk-left": {"texture": "silbon_walk", "frames": list(range(11, 21)), "interval": 0.10},
    "walk-right": {"texture": "silbon_walk", "frames": list(range(21, 31)), "interval": 0.10},
    "walk-down": {"texture": "silbon_walk", "frames": list(range(31, 41)), "interval": 0.10},
    "idle-down": {"texture": "silbon_idle", "frames": list(range(1, 8)), "interval": 0.16},
    "idle-up": {"texture": "silbon_idle", "frames": list(range(8, 15)), "interval": 0.16},
    "idle-left": {"texture": "silbon_idle", "frames": list(range(15, 22)), "interval": 0.16},
    "idle-right": {"texture": "silbon_idle", "frames": list(range(22, 29)), "interval": 0.16},
}


def _fallback_frame(frame_size: Tuple[int, int], color: Tuple[int, int, int]) -> pygame.Surface:
    fw, fh = frame_size
    dummy = pygame.Surface((fw, fh), pygame.SRCALPHA)
    pygame.draw.rect(dummy, color, (0, 0, fw, fh))
    return dummy


def build_animations(
    spec: Dict[str, Dict[str, Any]],
    fallback_color: Tuple[int, int, int],
    fallback_size: Tuple[int, int],
) -> Tuple[Dict[str, Animation], Dict[str, str]]:
    """
    :returns: (animations, textures) -- animations[name] plays back
    settings.FRAMES rects on settings.TEXTURES[textures[name]]; when
    that texture never loaded, animations[name] instead holds a single
    solid-color placeholder frame (a plain pygame.Surface, not a rect,
    sized fallback_size), and textures[name] is unset.
    """
    animations: Dict[str, Animation] = {}
    textures: Dict[str, str] = {}

    for name, entry in spec.items():
        texture_id = entry["texture"]
        interval = entry.get("interval", 0.15)

        if settings.TEXTURES.get(texture_id) is None:
            animations[name] = Animation([_fallback_frame(fallback_size, fallback_color)], interval)
            continue

        textures[name] = texture_id
        frame_rects = [settings.frame(texture_id, i) for i in entry["frames"]]
        animations[name] = Animation(frame_rects, interval, loops=entry.get("loops"))

    return animations, textures
