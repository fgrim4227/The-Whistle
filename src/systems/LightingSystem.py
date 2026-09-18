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
        #self.base_ambient_alpha: float = 0.0
        self.base_ambient_alpha: float = 253.0
        # Monster ambient darkness alpha: suffocating 100% pitch-black darkness when El Silbón is in room
        #self.monster_ambient_alpha: float = 0.0
        self.monster_ambient_alpha: float = 255.0
        # Ambient darkness alpha while the "catching" capture animation
        # plays: clearer than normal so the animation itself is visible.
        self.catching_ambient_alpha: float = 245.0
        # Current active darkness alpha (dynamically tweenable via Timer.tween).
        self.darkness_alpha: float = self.base_ambient_alpha

        self.flicker_timer: float = 0.0

        # Multi-layer flashlight cone configuration: (length_px, spread_deg, subtract_alpha, arc_steps)
        # Tightly-spaced diffusion surfaces preserving the exact original cone width (68 deg to 20 deg)
        self.lenght_cone = 10
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
                    direction = getattr(player, "direction", "right")
                    ox_dir, oy_dir = self.flashlight_origin_offset.get(direction, (0, 0))
                    self._carve_flashlight_cone(spx + ox_dir, spy + oy_dir, direction)


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
        inner_radius = self.flashlight_inner_radius.get(direction, 0.0)

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




