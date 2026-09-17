"""
LockpickMinigame: Tension-based lockpicking minigame for cabinets and vintage locks.
The player aligns the pick angle and applies turning force with the tension wrench.
Forcing the lock at an incorrect angle strains the metal (lock_forced.mp3) and alerts El Silbón.
"""

import math
import random
from typing import Any, Callable, Optional
import pygame

import settings
from src.minigames.BaseMinigame import BaseMinigame


class LockpickMinigame(BaseMinigame):
    def __init__(
        self,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
        target_angle: Optional[float] = None,
    ) -> None:
        super().__init__(play_state, target_object, on_success, on_fail)

        # Angle range: -80 degrees (far left) to +80 degrees (far right)
        self.min_angle = -80.0
        self.max_angle = 80.0
        self.current_pick_angle: float = 0.0

        if target_angle is not None:
            self.sweet_spot_angle = target_angle
        else:
            self.sweet_spot_angle = random.uniform(-65.0, 65.0)

        self.tolerance: float = 12.0  # degrees of tolerance
        self.cylinder_rotation: float = 0.0  # 0 to 90 degrees
        self.is_turning: bool = False
        self.strain_timer: float = 0.0
        self.shake_offset: float = 0.0

        self.feedback_message: str = ""
        self.feedback_color: tuple = (220, 220, 220)
        self.feedback_timer: float = 0.0

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        if super().handle_action(input_id, input_data):
            return True

        if input_id in ("action", "interact", "move_up"):
            self.is_turning = getattr(input_data, "pressed", False)
            return True
        return False

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.is_active or self.is_completed:
            return

        if self.feedback_timer > 0.0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)

        keys = pygame.key.get_pressed()

        # 1. Adjust pick angle with A/D (only when not heavily turning)
        if not self.is_turning or self.cylinder_rotation < 10.0:
            pick_speed = 90.0  # deg / sec
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.current_pick_angle = max(self.min_angle, self.current_pick_angle - pick_speed * dt)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.current_pick_angle = min(self.max_angle, self.current_pick_angle + pick_speed * dt)

        # 2. Apply tension with W, SPACE, or UP
        turning_requested = self.is_turning or keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]

        # Distance from sweet spot
        angle_dist = abs(self.current_pick_angle - self.sweet_spot_angle)

        if turning_requested:
            # Maximum reachable rotation depends on proximity to sweet spot
            if angle_dist <= self.tolerance:
                max_turn = 90.0
            elif angle_dist <= self.tolerance * 2.5:
                ratio = 1.0 - ((angle_dist - self.tolerance) / (self.tolerance * 1.5))
                max_turn = ratio * 45.0
            else:
                max_turn = 5.0

            turn_speed = 120.0
            if self.cylinder_rotation < max_turn:
                self.cylinder_rotation = min(max_turn, self.cylinder_rotation + turn_speed * dt)
                self.shake_offset = 0.0
                self.strain_timer = 0.0
            else:
                # Cylinder reached maximum turn for this angle and is jammed under pressure!
                if max_turn < 90.0:
                    self.strain_timer += dt
                    self.shake_offset = math.sin(pygame.time.get_ticks() * 0.05) * min(5.0, self.strain_timer * 4.0)

                    # Sound feedback when straining the lock
                    if self.strain_timer > 0.35 and int(self.strain_timer * 10) % 6 == 0:
                        settings.play_sound("minigame_lock_forced", loops=0, volume=0.7, channel_name="minigame")

                    # If forced too long under strain: snap back and alert El Silbón!
                    if self.strain_timer > 1.2:
                        self.alert_monster(radius=1000, sound_name="minigame_lock_forced", volume=1.0)
                        self.feedback_message = "¡La ganzúa resbaló con fuerza! ¡Alerta!"
                        self.feedback_color = (255, 60, 60)
                        self.feedback_timer = 2.5
                        self.cylinder_rotation = 0.0
                        self.strain_timer = 0.0
                        if self.on_fail:
                            self.on_fail()

        else:
            # Releasing tension resets cylinder smoothly
            reset_speed = 180.0
            self.cylinder_rotation = max(0.0, self.cylinder_rotation - reset_speed * dt)
            self.strain_timer = 0.0
            self.shake_offset = 0.0

        # Check Unlock Condition
        if self.cylinder_rotation >= 90.0:
            self.is_completed = True
            settings.play_sound("minigame_unlock_click", loops=0, volume=1.0, channel_name="minigame")
            if self.on_success:
                self.on_success()
            self.close()

    def render(self, surface: pygame.Surface) -> None:
        # 1. Dark semi-transparent overlay
        backdrop = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((12, 10, 8, 175))
        surface.blit(backdrop, (0, 0))

        center_x = settings.VIRTUAL_WIDTH // 2
        center_y = settings.VIRTUAL_HEIGHT // 2 + 8

        # 2. Outer Wooden Cabinet Frame
        panel_w, panel_h = 220, 160
        panel_rect = pygame.Rect(center_x - panel_w // 2, center_y - panel_h // 2, panel_w, panel_h)
        pygame.draw.rect(surface, (45, 30, 20), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (85, 60, 40), panel_rect, width=2, border_radius=8)

        # Header Title
        #title_font = settings.FONTS.get("medium", settings.FONTS["small"])
        #title_surf = title_font.render("FORZAR CERRADURA - GANZÚA", True, (240, 215, 160))
        #surface.blit(title_surf, (center_x - title_surf.get_width() // 2, panel_rect.top + 8))

        # 3. Outer Brass Plate
        plate_radius = 45
        lock_center = (center_x, center_y + 4)
        pygame.draw.circle(surface, (80, 65, 30), lock_center, plate_radius + 4)
        pygame.draw.circle(surface, (150, 120, 50), lock_center, plate_radius)
        pygame.draw.circle(surface, (200, 170, 80), lock_center, plate_radius, width=2)

        # 4. Inner Rotating Keyhole Cylinder
        cylinder_radius = 28
        pygame.draw.circle(surface, (90, 75, 40), lock_center, cylinder_radius)
        pygame.draw.circle(surface, (60, 48, 25), lock_center, cylinder_radius, width=2)

        # Keyhole slot rotated by cylinder_rotation
        rot_rad = math.radians(self.cylinder_rotation)
        slot_w, slot_h = 6, 24
        # Create rotated keyhole slot
        slot_surf = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
        slot_surf.fill((20, 15, 10))
        pygame.draw.circle(slot_surf, (20, 15, 10), (slot_w // 2, 4), 4)
        rotated_slot = pygame.transform.rotate(slot_surf, -self.cylinder_rotation)
        slot_rect = rotated_slot.get_rect(center=lock_center)
        surface.blit(rotated_slot, slot_rect)

        # 5. Lockpick Wire (needle angled by current_pick_angle + shake_offset)
        effective_angle = self.current_pick_angle + self.shake_offset
        pick_rad = math.radians(effective_angle - 90.0)
        pick_len = 55
        px_end = lock_center[0] + pick_len * math.cos(pick_rad)
        py_end = lock_center[1] + pick_len * math.sin(pick_rad)
        pick_color = (210, 210, 220) if self.strain_timer < 0.3 else (255, 120, 120)
        pygame.draw.line(surface, pick_color, lock_center, (int(px_end), int(py_end)), 3)
        # Small handle / ring on pick end
        pygame.draw.circle(surface, (170, 170, 180), (int(px_end), int(py_end)), 4, width=2)

        # Tension Wrench at bottom
        wrench_rad = math.radians(self.cylinder_rotation + 90.0)
        wx_end = lock_center[0] + 35 * math.cos(wrench_rad)
        wy_end = lock_center[1] + 35 * math.sin(wrench_rad)
        pygame.draw.line(surface, (110, 110, 120), lock_center, (int(wx_end), int(wy_end)), 4)

        # 6. Status and Instructions
        small_font = settings.FONTS.get("small", settings.FONTS["small"])
        if self.feedback_timer > 0.0 and self.feedback_message:
            fb_surf = small_font.render(self.feedback_message, True, self.feedback_color)
            surface.blit(fb_surf, (center_x - fb_surf.get_width() // 2, center_y + plate_radius + 8))
        else:
            hint_surf = small_font.render("Busca el ángulo sin forzar...", True, (190, 180, 160))
            surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, center_y + plate_radius + 8))

        ctrl_surf = small_font.render("[A/D] Ángulo  |  [W / ESPACIO] Girar  |  [ESC] Salir", True, (210, 200, 170))
        surface.blit(ctrl_surf, (center_x - ctrl_surf.get_width() // 2, panel_rect.bottom - 16))
