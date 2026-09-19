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

PLAYER_SIZE = (20, 37)
PLAYER_SPRITE_SIZE = (17, 37)
PLAYER_SPRITE_BOTTOM_MARGIN = 0
PLAYER_FALLBACK_COLOR = (40, 90, 160)

PLAYER_ANIMATIONS: Dict[str, Dict[str, Any]] = {
    "walk-up": {"texture": "player", "frames": list(range(2, 12)), "interval": 0.12},
    "walk-left": {"texture": "player", "frames": list(range(13, 23)), "interval": 0.12},
    "walk-down": {"texture": "player", "frames": list(range(24, 34)), "interval": 0.12},
    "walk-right": {"texture": "player", "frames": list(range(35, 45)), "interval": 0.12},
    "idle-up": {"texture": "player", "frames": [1], "interval": 0.25},
    "idle-left": {"texture": "player", "frames": [12], "interval": 0.25},
    "idle-down": {"texture": "player", "frames": [23], "interval": 0.25},
    "idle-right": {"texture": "player", "frames": [34], "interval": 0.25},  

    "walk-up-flashlight": {"texture": "player_flashlight", "frames": list(range(2, 12)), "interval": 0.12},
    "walk-left-flashlight": {"texture": "player_flashlight", "frames": list(range(13, 23)), "interval": 0.12},
    "walk-down-flashlight": {"texture": "player_flashlight", "frames": list(range(24, 34)), "interval": 0.12},
    "walk-right-flashlight": {"texture": "player_flashlight", "frames": list(range(35, 45)), "interval": 0.12},
    "idle-up-flashlight": {"texture": "player_flashlight", "frames": [1], "interval": 0.25},
    "idle-left-flashlight": {"texture": "player_flashlight", "frames": [12], "interval": 0.25},
    "idle-down-flashlight": {"texture": "player_flashlight", "frames": [23], "interval": 0.25},
    "idle-right-flashlight": {"texture": "player_flashlight", "frames": [34], "interval": 0.25},
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
    "idle-down": {"texture": "monster_idle", "frames": [1], "interval": 0.20},
    "idle-left": {"texture": "monster_idle", "frames": [2], "interval": 0.20},
    "idle-up": {"texture": "monster_idle", "frames": [3], "interval": 0.20},
    "idle-right": {"texture": "monster_idle", "frames": [4], "interval": 0.20},
    "catching-down": {"texture": "monster_catching", "frames": list(range(1, 9)), "interval": 0.5, "loops": 1},
    "catching-left": {"texture": "monster_catching", "frames": list(range(9, 17)), "interval": 0.5, "loops": 1},
    "catching-up": {"texture": "monster_catching", "frames": list(range(17, 25)), "interval": 0.5, "loops": 1},
    "catching-right": {"texture": "monster_catching", "frames": list(range(25, 33)), "interval": 0.5, "loops": 1},
    "run-down":{"texture": "monster_running", "frames": list(range(1, 9)), "interval": 0.10},
    "run-left": {"texture": "monster_running", "frames": list(range(9, 17)), "interval": 0.10},
    "run-up": {"texture": "monster_running", "frames": list(range(17, 25)), "interval": 0.10},
    "run-right": {"texture": "monster_running", "frames": list(range(25, 33)), "interval": 0.10},
    "breathing-down": {"texture": "monster_breathing", "frames": list(range(1, 9)), "interval": 0.10},
    "breathing-left": {"texture": "monster_breathing", "frames": list(range(9, 17)), "interval": 0.10},
    "breathing-up": {"texture": "monster_breathing", "frames": list(range(17, 25)), "interval": 0.10},
    "breathing-right": {"texture": "monster_breathing", "frames": list(range(25, 33)), "interval": 0.10},
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
