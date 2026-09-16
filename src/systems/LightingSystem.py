"""
2D Atmospheric Lighting and Darkness System (LightingSystem).
Generates dynamic darkness and realistic directional flashlight cones with multi-layer
alpha diffusion, ambient personal glow, and eerie sine-wave pulsating monster eyes.
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import pygame

import settings


@dataclass
class Light:
    x: float
    y: float
    radius: float
    color: Tuple[int, int, int]
    intensity: float = 0.4
    reveal: float = 1.0


class LightingSystem:
    def __init__(self) -> None:
        size = (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.darkness_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.light_mask = pygame.Surface(size, pygame.SRCALPHA)

        # Base ambient darkness alpha: faint silhouettes of nearby walls/floors still visible
        self.base_ambient_alpha: float = 240.0
        # Monster ambient darkness alpha: suffocating 100% pitch-black darkness when El Silbón is in room
        self.monster_ambient_alpha: float = 255.0
        # Ambient darkness alpha while the "catching" capture animation
        # plays: clearer than normal so the animation itself is visible.
        self.catching_ambient_alpha: float = 200.0
        # Current active darkness alpha (dynamically tweenable via Timer.tween).
        self.darkness_alpha: float = self.base_ambient_alpha

        self.flicker_timer: float = 0.0

        # Multi-layer flashlight cone configuration: (length_px, spread_deg, subtract_alpha, arc_steps)
        # Tightly-spaced diffusion surfaces preserving the exact original cone width (68 deg to 20 deg)
        self.cone_layers = [
            (165.0, 68.0, 35, 14),
            (157.0, 62.0, 55, 14),
            (149.0, 56.0, 80, 12),
            (141.0, 50.0, 105, 12),
            (133.0, 44.0, 130, 10),
            (125.0, 39.0, 155, 10),
            (117.0, 34.0, 180, 8),
            (108.0, 29.0, 205, 8),
            (99.0,  24.0, 230, 6),
            (90.0,  20.0, 255, 6),
        ]

        # Single simple faint circular glow for the player (no multi-layer rings or stepped diffusion)
        self.player_ambient_radius: int = 18
        self.player_ambient_alpha: int = 70

    def update(self, dt: float) -> None:
        """Updates internal timers for sine wave light modulations."""
        self.flicker_timer += dt

    def render(
        self,
        target_surface: pygame.Surface,
        player_or_lights: Union[Any, List[Light]],
        monster: Optional[Any] = None,
        camera_offset: Tuple[int, int] = (0, 0),
        dt: float = 0.0,
    ) -> None:
        """
        Renders the darkness layer, carving out the player's flashlight cone / ambient halo
        and pulsating the eerie glowing eyes of El Silbón.
        """
        if dt > 0.0:
            self.flicker_timer += dt

        ox, oy = camera_offset
        alpha_val = max(0, min(255, int(self.darkness_alpha)))

        # 1. Fill darkness overlay and clear subtraction mask
        self.darkness_surface.fill((8, 8, 14, alpha_val))
        self.light_mask.fill((0, 0, 0, 0))

        # 2. Support both modern Entity-based rendering and legacy Light-list rendering
        if isinstance(player_or_lights, list):
            for light in player_or_lights:
                radius = int(light.radius)
                if radius <= 0:
                    continue
                lx = int(light.x - ox)
                ly = int(light.y - oy)
                alpha_cut = int(255 * light.reveal)
                pygame.draw.circle(self.light_mask, (0, 0, 0, alpha_cut), (lx, ly), radius)
        else:
            player = player_or_lights
            if player and not getattr(player, "is_hidden", False):
                px, py = player.get_center()
                spx = px - ox
                spy = py - oy

                # Single simple faint circular glow around player (no multi-layer rings or stepped diffusion)
                pygame.draw.circle(
                    self.light_mask,
                    (0, 0, 0, self.player_ambient_alpha),
                    (int(spx), int(spy)),
                    self.player_ambient_radius,
                )

                is_flashlight_on = getattr(player, "flashlight_on", False) and getattr(player, "battery", 0) > 0

                if is_flashlight_on:
                    # Directional cone facing player.direction
                    direction = getattr(player, "direction", "right")
                    self._carve_flashlight_cone(spx, spy, direction)

        # 3. El Silbón glowing eyes and sine-wave flicker
        if monster and not getattr(monster, "is_dead", False):
            self._render_monster_eyes(target_surface, monster, ox, oy)

        # 4. Subtract lights from darkness overlay and blit darkness onto target surface
        self.darkness_surface.blit(self.light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        target_surface.blit(self.darkness_surface, (0, 0))

    def _carve_flashlight_cone(self, spx: float, spy: float, direction: str) -> None:
        """Carves a smooth, multi-layer arched cone in the direction of the player."""
        dir_angles = {
            "right": 0.0,
            "down": 90.0,
            "left": 180.0,
            "up": 270.0,
        }
        base_angle = math.radians(dir_angles.get(direction, 0.0))

        for length, spread_deg, alpha, steps in self.cone_layers:
            half = math.radians(spread_deg / 2.0)
            pts = [(spx, spy)]
            for i in range(steps + 1):
                a = base_angle - half + i * (2.0 * half / steps)
                pts.append((spx + length * math.cos(a), spy + length * math.sin(a)))
            pygame.draw.polygon(self.light_mask, (0, 0, 0, alpha), pts)

    def _render_monster_eyes(
        self, target_surface: pygame.Surface, monster: Any, ox: float, oy: float
    ) -> None:
        """
        Renders El Silbón's eyes piercing through darkness with sine-wave pulsating intensity.
        When the sine wave dips low, the eyes flicker and fade out into blackness.
        """
        if hasattr(monster, "get_eye_position"):
            eye_x, eye_y = monster.get_eye_position()
            smx = eye_x - ox
            smy = eye_y - oy
        else:
            mx, my = monster.get_center()
            smx = mx - ox
            smy = my - oy - 39.0

        # Sine wave modulation: frequency faster when hunting/berserk
        freq = 8.0 if getattr(monster, "ai_state", "") == "berserk" else 4.5
        sine_val = math.sin(self.flicker_timer * freq)

        # Thresholding: below -0.15, eyes are completely shrouded in darkness
        if sine_val <= -0.15:
            return

        factor = (sine_val + 0.15) / 1.15
        factor = max(0.0, min(1.0, factor))

        # Carve a tiny pinhole in the light mask
        eye_radius = max(1, int(settings.MONSTER_EYE_LIGHT_RADIUS))
        cutout_alpha = int(90 * factor)
        pygame.draw.circle(self.light_mask, (0, 0, 0, cutout_alpha), (int(smx), int(smy)), eye_radius + 2)

        # Draw glowing red eye dots directly onto target_surface
        eye_col = (int(255 * factor), int(25 * factor), int(20 * factor))
        pygame.draw.circle(target_surface, eye_col, (int(smx - 4), int(smy)), eye_radius)
        pygame.draw.circle(target_surface, eye_col, (int(smx + 4), int(smy)), eye_radius)
