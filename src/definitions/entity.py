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
PLAYER_SPRITE_SIZE = (32, 48)
PLAYER_SPRITE_BOTTOM_MARGIN = 0
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
MONSTER_SPRITE_SIZE = (92, 92)
MONSTER_FALLBACK_COLOR = (160, 40, 40)
# render_sprite anchors the sprite's bottom this many px below the
# collision box's bottom edge (feet/shadow margin) and centers it
# horizontally computed from each frame's own size, so idle's smaller
# 64x64 sheet and walk/running's 92x92 sheets don't visually jump
# position when the animation changes.
MONSTER_SPRITE_BOTTOM_MARGIN = 8

# monster_walk/monster_running are each one 8-col x 4-row sheet, rows in
# down/left/up/right order. monster_idle is a single
# 4-frame row with no per-direction variants. Frame indices below are
# 1-based, row-major across the whole sheet.
MONSTER_ANIMATIONS: Dict[str, Dict[str, Any]] = {
    "walk-down": {"texture": "monster_walk", "frames": list(range(1, 9)), "interval": 0.10},
    "walk-left": {"texture": "monster_walk", "frames": list(range(9, 17)), "interval": 0.10},
    "walk-up": {"texture": "monster_walk", "frames": list(range(17, 25)), "interval": 0.10},
    "walk-right": {"texture": "monster_walk", "frames": list(range(25, 33)), "interval": 0.10},
    "idle": {"texture": "monster_idle", "frames": list(range(1, 5)), "interval": 0.20},
    "catching": {"texture": "monster_catching", "frames": list(range(1, 10)), "interval": 0.7, "loops": 1},
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
    :returns: (animations, textures) animations[name] plays back
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
