"""
2D Lighting and Darkness System (LightingSystem).
Generates atmospheric darkness and dynamic flashlight cones using an independent light mask
combined with pygame.BLEND_RGBA_SUB for crisp subtraction and smooth visibility.
"""

import math
from typing import Tuple, Optional
import pygame

import settings


class LightingSystem:
    def __init__(self) -> None:
        self.darkness_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT),
            flags=pygame.SRCALPHA
        )
        self.light_mask = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT),
            flags=pygame.SRCALPHA
        )
        # Balanced darkness opacity
        self.ambient_darkness = (10, 10, 16, 255)
        self.cone_length = 145.0
        self.cone_angle_deg = 50.0

    def render(self, target_surface: pygame.Surface, player, monster, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Renders the darkness layer and flashlight cutouts over target_surface."""
        # 1. Reset darkness layer and light subtraction mask
        self.darkness_surface.fill(self.ambient_darkness)
        self.light_mask.fill((0, 0, 0, 0))

        ox, oy = camera_offset
        px, py = player.get_center()
        spx = px - ox
        spy = py - oy

        # 2. Build the light mask (light subtracts opacity from darkness)
        # When player is hidden inside wardrobe/table, NO halo or light is rendered
        if not player.is_hidden:
            if player.flashlight_on and player.battery > 0:
                self._carve_flashlight_cone(spx, spy, player.direction)
                # Ambient radius around player when holding flashlight
                pygame.draw.circle(self.light_mask, (0, 0, 0, 200), (int(spx), int(spy)), 30)
                pygame.draw.circle(self.light_mask, (0, 0, 0, 240), (int(spx), int(spy)), 18)
            else:
                # Faint residual visibility when flashlight is turned off (only when NOT hidden)
                pygame.draw.circle(self.light_mask, (0, 0, 0, 130), (int(spx), int(spy)), 22)

        # 3. Apply light cutout onto the darkness surface
        self.darkness_surface.blit(self.light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # 4. Blit darkness layer onto game surface
        target_surface.blit(self.darkness_surface, (0, 0))

        # 5. El Silbón glowing eyes piercing through darkness if lurking nearby
        if monster and not monster.is_dead:
            mx, my = monster.get_center()
            dist = math.hypot(mx - px, my - py)
            if dist < 240.0:
                smx = mx - ox
                smy = my - oy
                eye_color = (255, 30, 30) if monster.ai_state == "berserk" else (255, 215, 80)
                pygame.draw.circle(target_surface, eye_color, (int(smx - 4), int(smy - 14)), 2)
                pygame.draw.circle(target_surface, eye_color, (int(smx + 4), int(smy - 14)), 2)

    def _carve_flashlight_cone(self, px: float, py: float, direction: str) -> None:
        """Draws the flashlight beam onto the light mask."""
        dir_angles = {
            "right": 0.0,
            "down": 90.0,
            "left": 180.0,
            "up": 270.0,
        }
        base_angle = math.radians(dir_angles.get(direction, 90.0))
        half_spread = math.radians(self.cone_angle_deg / 2.0)

        p1 = (px, py)
        p2 = (
            px + self.cone_length * math.cos(base_angle - half_spread),
            py + self.cone_length * math.sin(base_angle - half_spread),
        )
        p3 = (
            px + self.cone_length * math.cos(base_angle + half_spread),
            py + self.cone_length * math.sin(base_angle + half_spread),
        )

        # Outer soft beam
        pygame.draw.polygon(self.light_mask, (0, 0, 0, 185), [p1, p2, p3])
        
        # Inner brighter beam
        p_mid = (
            px + (self.cone_length * 0.85) * math.cos(base_angle),
            py + (self.cone_length * 0.85) * math.sin(base_angle),
        )
        p2_mid = (px + (p2[0] - px) * 0.7, py + (p2[1] - py) * 0.7)
        p3_mid = (px + (p3[0] - px) * 0.7, py + (p3[1] - py) * 0.7)
        pygame.draw.polygon(self.light_mask, (0, 0, 0, 235), [p1, p2_mid, p_mid])
        pygame.draw.polygon(self.light_mask, (0, 0, 0, 235), [p1, p_mid, p3_mid])
