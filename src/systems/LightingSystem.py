"""
2D Atmospheric Lighting and Darkness System (LightingSystem).
Generates dynamic darkness and realistic directional flashlight cones with multi-layer
alpha diffusion and ambient personal glow.
"""

import math
from typing import Any, Dict, Optional, Tuple
import pygame
from gale.timer import Timer

import settings


class LightingSystem:
    def __init__(self) -> None:
        size = (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.darkness_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.light_mask = pygame.Surface(size, pygame.SRCALPHA)

        # Base ambient darkness alpha: faint silhouettes of nearby walls/floors still visible
        self.base_ambient_alpha: float = 253.0
        # Monster ambient darkness alpha: suffocating 100% pitch-black darkness when El Silbón is in room
        self.monster_ambient_alpha: float = 255.0
        # Ambient darkness alpha while the "catching" capture animation
        # plays: clearer than normal so the animation itself is visible.
        self.catching_ambient_alpha: float = 245.0
        # Current active darkness alpha (dynamically tweenable via Timer.tween).
        self.darkness_alpha: float = self.base_ambient_alpha

        self.flicker_timer: float = 0.0

        # Multi-layer flashlight cone configuration: (length_px, spread_deg, subtract_alpha, arc_steps)
        # Tightly-spaced diffusion surfaces preserving the exact original cone width (68 deg to 20 deg)
        self.cone_layers = [
            (233.0, 70.0, 130, 10),
            (195.0, 54.0, 155, 10),
            (187.0, 48.0, 180, 8),
            (178.0, 32.0, 205, 8),
            (169.0,  26.0, 230, 6),
            (160.0,  20.0, 255, 6),
        ]

        self.flashlight_inner_radius: Dict[str, float] = {
            "up": 20.0,
            "down": 0.0,
            "left": 0.0,
            "right": 0.0,
        }



        # Single simple faint circular glow for the player (no multi-layer rings or stepped diffusion)
        self.player_ambient_radius: int = 23
        self.player_ambient_alpha: int = 10

        self.flashlight_origin_offset: Dict[str, Tuple[int, int]] = {
            "up": (0, 0),
            "down": (-9, 6),
            "left": (-10, 5),
            "right": (0, 6),
        }

        self.direction_angles: Dict[str, float] = {
            "right": 0.0,
            "down": 90.0,
            "left": 180.0,
            "up": 270.0,
        }
        self.beam_turn_time: float = 0.12
        self.beam_angle: float = 0.0
        self.beam_offset_x: float = 0.0
        self.beam_offset_y: float = 0.0
        self.beam_inner_radius: float = 0.0
        self._beam_direction: Optional[str] = None
        self._beam_tween = None

        self.title_flash_timer: float = 0.0
        self.title_white_flash_timer: float = 0.0

    def update(self, dt: float) -> None:
        """Updates internal timers for sine wave light modulations."""
        self.flicker_timer += dt

    def render(
        self,
        target_surface: pygame.Surface,
        player: Optional[Any],
        monster: Optional[Any] = None,
        camera_offset: Tuple[int, int] = (0, 0),
        dt: float = 0.0,
    ) -> None:
        """
        Renders the darkness layer, carving out the player's flashlight cone / ambient halo.
        """
        if dt > 0.0:
            self.flicker_timer += dt

        ox, oy = camera_offset
        alpha_val = max(0, min(255, int(self.darkness_alpha)))

        # 1. Fill darkness overlay and clear subtraction mask
        self.darkness_surface.fill((8, 8, 14, alpha_val))
        self.light_mask.fill((0, 0, 0, 0))

        # 2. Carve player ambient halo and directional flashlight cone
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

            direction = getattr(player, "direction", "right")
            self._steer_beam(direction, animate=is_flashlight_on)

            if is_flashlight_on:
                self._carve_flashlight_cone(spx + self.beam_offset_x, spy + self.beam_offset_y)

        # 3. Subtract light mask and composite onto target surface
        self.darkness_surface.blit(self.light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        target_surface.blit(self.darkness_surface, (0, 0))

    def _steer_beam(self, direction: str, animate: bool) -> None:
        """Swings the cone around the player toward the way they now face."""
        if direction == self._beam_direction:
            return

        first_time = self._beam_direction is None
        self._beam_direction = direction

        target_angle = self.direction_angles.get(direction, 0.0)
        target_offset = self.flashlight_origin_offset.get(direction, (0, 0))
        target_inner = self.flashlight_inner_radius.get(direction, 0.0)

        if self._beam_tween and not self._beam_tween.to_remove:
            self._beam_tween.remove()
        self._beam_tween = None

        if first_time or not animate:
            self.beam_angle = target_angle
            self.beam_offset_x, self.beam_offset_y = float(target_offset[0]), float(target_offset[1])
            self.beam_inner_radius = target_inner
            return

        # Always the shorter way around, so turning from up to right doesn't spin three quarters of a circle.
        turn = (target_angle - self.beam_angle + 180.0) % 360.0 - 180.0
        self._beam_tween = Timer.tween(
            self.beam_turn_time,
            [(self, {
                "beam_angle": self.beam_angle + turn,
                "beam_offset_x": float(target_offset[0]),
                "beam_offset_y": float(target_offset[1]),
                "beam_inner_radius": target_inner,
            })],
            ease_function_name="out_quad",
        )

    def _carve_flashlight_cone(self, spx: float, spy: float) -> None:
        """Carves a smooth, multi-layer arched cone at the current beam angle."""
        base_angle = math.radians(self.beam_angle)
        inner_radius = self.beam_inner_radius

        for length, spread_deg, alpha, steps in self.cone_layers:
            half = math.radians(spread_deg / 2.0)
            angles = [base_angle - half + i * (2.0 * half / steps) for i in range(steps + 1)]
            near = [
                (spx + inner_radius * math.cos(a), spy + inner_radius * math.sin(a))
                for a in angles
            ]
            far = [(spx + length * math.cos(a), spy + length * math.sin(a)) for a in angles]
            pts = near + far[::-1]
            pygame.draw.polygon(self.light_mask, (0, 0, 0, alpha), pts)
    def trigger_thunder_flash(self) -> None:
        """The time for the clearer alpha surface"""
        self.title_white_flash_timer = 0.05
        self.title_flash_timer = 0.15

    def render_title_screen(self, target_surface: pygame.Surface, dt: float) -> None:
        """Decides if the darkness of the title screen should be rendered higher or lower"""
        if self.title_white_flash_timer > 0:
            self.title_white_flash_timer -= dt
            white_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            white_surface.fill(settings.COLOR_WHITE)
            target_surface.blit(white_surface, (0, 0))
            return
        if self.title_flash_timer > 0:
            self.title_flash_timer -= dt
            alpha_val = 130
        else:
            alpha_val = 230

        alpha_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        alpha_surface.fill((0, 0, 0, alpha_val))
        target_surface.blit(alpha_surface, (0, 0))



