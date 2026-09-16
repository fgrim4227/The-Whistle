"""
Generic light-source darkness system, built on gale.stencil.

LightingSystem itself knows nothing about flashlights or monster eyes --
it just takes a list of Light (world position, radius, color, intensity)
every frame and carves each one, as a hard-edged circle of full
visibility, out of a solid darkness overlay; a light with intensity > 0
also casts its own color over that same circle. Whoever calls render()
(PlayState today) decides what counts as a light and builds that list --
the player's flashlight (colorless, intensity 0) and El Silbón's red
eyes are just two entries in it, and any future emitter (a thrown lit
lantern, say) is a third with no change needed here.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pygame
from gale.stencil import Stencil

import settings


@dataclass
class Light:
    x: float
    y: float
    radius: float
    color: Tuple[int, int, int]
    intensity: float = 0.4  # 0..1, max fraction of `color` added at the light's own center
    reveal: float = 1.0  # 0..1, how much of the ambient darkness this light removes -- 1 = fully lit like a real flashlight, lower = still dim inside its own circle. Flat, not a gradient.


class LightingSystem:
    def __init__(self) -> None:
        size = (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.darkness_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.glow_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.stencil = Stencil(size)

        # Base ambient darkness alpha: faint silhouettes of nearby geometry still show through.
        self.base_ambient_alpha: float = 240.0
        # Monster ambient darkness alpha: suffocating 100% pitch-black darkness when El Silbón enters.
        self.monster_ambient_alpha: float = 255.0
        # Current active darkness alpha (dynamically tweenable via Timer.tween).
        self.darkness_alpha: float = self.base_ambient_alpha

        self._reveal_cache: Dict[Tuple[int, float], pygame.Surface] = {}
        self._tint_cache: Dict[Tuple[int, Tuple[int, int, int], float], pygame.Surface] = {}

    def _reveal_circle(self, radius: int, reveal: float) -> pygame.Surface:
        """
        A cached white circle, one flat level of see-through-ness all
        the way across (no soft edge): clears the darkness inside its
        radius down to `1 - reveal` of its normal strength, and leaves
        everything outside untouched. A softer, fading edge was tried
        first, but the library we cut this shape out of the darkness
        with treats any pixel that was drawn at all -- even a barely
        visible one at the edge -- as fully drawn, so the edge came out
        as a ring darker than the darkness around it instead of fading
        smoothly. A flat, hard-edged circle sidesteps that.
        """
        key = (radius, round(reveal, 3))
        cached = self._reveal_cache.get(key)
        if cached is not None:
            return cached

        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        alpha = max(0, min(255, int(255 * reveal)))
        pygame.draw.circle(surface, (255, 255, 255, alpha), (radius, radius), radius)
        self._reveal_cache[key] = surface
        return surface

    def _tint_circle(self, radius: int, color: Tuple[int, int, int], strength: float) -> pygame.Surface:
        """
        A cached, flat colored circle, the same hard-edged shape as
        _reveal_circle: `color` dimmed by `strength` applies evenly
        across the whole circle, not just at its center. We dim the
        color itself instead of making it see-through, because this
        glow gets laid on top of the scene by brightening it directly --
        it adds the color's full brightness wherever it's drawn, no
        matter how transparent that pixel looks. A faint, see-through
        edge would still show up at full strength, so we dim the color
        instead of the transparency.
        """
        key = (radius, color, round(strength, 3))
        cached = self._tint_cache.get(key)
        if cached is not None:
            return cached

        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        r0, g0, b0 = color
        col = (int(r0 * strength), int(g0 * strength), int(b0 * strength), 255)
        pygame.draw.circle(surface, col, (radius, radius), radius)
        self._tint_cache[key] = surface
        return surface

    def render(
        self,
        target_surface: pygame.Surface,
        lights: List[Light],
        camera_offset: Tuple[int, int] = (0, 0),
    ) -> None:
        """Renders the darkness layer with every light in `lights` carved out of it."""
        ox, oy = camera_offset

        alpha_val = max(0, min(255, int(self.darkness_alpha)))
        self.darkness_surface.fill((8, 8, 14, alpha_val))
        self.glow_surface.fill((0, 0, 0, 0))
        self.stencil.clear()

        for light in lights:
            radius = int(light.radius)
            if radius <= 0:
                continue

            pos = (int(light.x - ox - radius), int(light.y - oy - radius))

            # Reveal: add this light's circle onto the shared cutout
            # shape, so overlapping lights combine into a wider revealed area.
            reveal = self._reveal_circle(radius, light.reveal)
            self.stencil.draw(lambda mask, g=reveal, p=pos: mask.blit(g, p, special_flags=pygame.BLEND_RGBA_ADD))

            # Tint: a much gentler color cast on its own layer, so the
            # room still reads normally inside the light instead of
            # being painted over solid.
            tint = self._tint_circle(radius, light.color, light.intensity)
            self.glow_surface.blit(tint, pos, special_flags=pygame.BLEND_RGBA_ADD)

        self.stencil.apply(self.darkness_surface, invert=True)
        target_surface.blit(self.darkness_surface, (0, 0))
        target_surface.blit(self.glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
