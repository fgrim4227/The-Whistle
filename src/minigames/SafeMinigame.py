"""
SafeMinigame: Acoustic combination safe dial minigame.
The player rotates the metallic safe dial and listens for distinct acoustic clicks.
Confirming the wrong number or turning violently jams the mechanism and alerts El Silbón.
"""

import math
import random
from typing import Any, Callable, Optional, Set
import pygame

import settings
from src.i18n import t
from src.minigames.BaseMinigame import BaseMinigame


class SafeMinigame(BaseMinigame):
    def __init__(
        self,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
        combination_numbers: Optional[Set[int]] = None,
    ) -> None:
        super().__init__(play_state, target_object, on_success, on_fail)

        self.max_number = 40  # Numbers 0 to 39
        # 3 random combination numbers if not provided
        if combination_numbers:
            self.targets: Set[int] = set(combination_numbers)
        else:
            nums = random.sample(range(2, self.max_number - 2), 3)
            self.targets = set(nums)

        self.original_target_count = len(self.targets)
        self.unlocked_numbers: Set[int] = set()

        self.current_value: float = 0.0
        self.rotation_speed: float = 8.0  # numbers per second when held
        self.last_clicked_number: int = 0
        self.turn_direction: int = 0  # -1 left, 1 right

        self.feedback_message: str = ""
        self.feedback_timer: float = 0.0
        self.feedback_color: tuple = (220, 220, 220)

    def handle_input(self, event: pygame.event.Event) -> bool:
        if super().handle_input(event):
            return True

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                self._attempt_lock_in()
                return True
        return False

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        if super().handle_action(input_id, input_data):
            return True

        if getattr(input_data, "pressed", True):
            if input_id in ("action", "enter", "interact"):
                self._attempt_lock_in()
                return True
        return False

    def _attempt_lock_in(self) -> None:
        current_num = int(round(self.current_value)) % self.max_number
        if current_num in self.targets and current_num not in self.unlocked_numbers:
            # Correct number discovered!
            self.unlocked_numbers.add(current_num)
            self.targets.remove(current_num)
            settings.play_sound("minigame_unlock_click", loops=0, volume=1.0, channel_name="minigame")
            self.feedback_message = f"¡Pestillo {len(self.unlocked_numbers)} fijado!"
            self.feedback_color = (80, 230, 80)
            self.feedback_timer = 2.0

            if len(self.targets) == 0:
                # All numbers unlocked!
                self.is_completed = True
                if self.on_success:
                    self.on_success()
                self.close()
        else:
            # Wrong number! Safe jams and creates loud metallic disturbance
            self.feedback_message = "¡Mecanismo trabado! ¡Ruido metálico!"
            self.feedback_color = (255, 60, 60)
            self.feedback_timer = 2.5
            self.alert_monster(radius=1000, sound_name="minigame_lock_forced", volume=1.0)
            if self.on_fail:
                self.on_fail()

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.is_active or self.is_completed:
            return

        if self.feedback_timer > 0.0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)

        # Polling rotation keys
        keys = pygame.key.get_pressed()
        rotate_dir = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            rotate_dir -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            rotate_dir += 1

        self.turn_direction = rotate_dir

        if rotate_dir != 0:
            prev_int = int(round(self.current_value)) % self.max_number
            self.current_value = (self.current_value + rotate_dir * self.rotation_speed * dt) % self.max_number
            new_int = int(round(self.current_value)) % self.max_number

            if new_int != prev_int:
                # Sound cue: distinct unlock click on target number, normal tick otherwise
                if new_int in self.targets:
                    settings.play_sound("minigame_unlock_click", loops=0, volume=0.85, channel_name="minigame")
                else:
                    settings.play_sound("minigame_normal_click", loops=0, volume=0.45, channel_name="minigame")
                self.last_clicked_number = new_int

    def render(self, surface: pygame.Surface) -> None:
        # 1. Semi-transparent backdrop overlay
        backdrop = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((10, 8, 12, 175))
        surface.blit(backdrop, (0, 0))

        center_x = settings.VIRTUAL_WIDTH // 2
        center_y = settings.VIRTUAL_HEIGHT // 2 + 6

        # 2. Outer Safe Frame
        panel_w, panel_h = 220, 160
        panel_rect = pygame.Rect(center_x - panel_w // 2, center_y - panel_h // 2, panel_w, panel_h)
        pygame.draw.rect(surface, (35, 33, 38), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (70, 68, 75), panel_rect, width=2, border_radius=8)

        # Header Title
        title_font = settings.FONTS.get("medium", settings.FONTS["small"])
        title_surf = title_font.render("CAJA FUERTE - COMBINACIÓN", True, (230, 210, 160))
        surface.blit(title_surf, (center_x - title_surf.get_width() // 2, panel_rect.top + 8))

        # 3. Dial Center
        dial_radius = 42
        dial_center = (center_x, center_y + 4)
        pygame.draw.circle(surface, (20, 20, 22), dial_center, dial_radius + 4)
        pygame.draw.circle(surface, (50, 48, 54), dial_center, dial_radius)
        pygame.draw.circle(surface, (80, 78, 86), dial_center, dial_radius, width=2)

        # Draw dial ticks
        current_num = int(round(self.current_value)) % self.max_number
        for num in range(self.max_number):
            # Angle relative to current value (0 at 12 o'clock)
            angle_deg = ((num - self.current_value) / self.max_number) * 360.0 - 90.0
            rad = math.radians(angle_deg)
            is_major = (num % 5 == 0)
            inner_r = dial_radius - (8 if is_major else 4)
            outer_r = dial_radius - 2
            x1 = dial_center[0] + inner_r * math.cos(rad)
            y1 = dial_center[1] + inner_r * math.sin(rad)
            x2 = dial_center[0] + outer_r * math.cos(rad)
            y2 = dial_center[1] + outer_r * math.sin(rad)
            tick_color = (200, 190, 160) if is_major else (120, 115, 110)
            pygame.draw.line(surface, tick_color, (x1, y1), (x2, y2), 2 if is_major else 1)

        # Center Knob
        pygame.draw.circle(surface, (75, 70, 65), dial_center, 18)
        pygame.draw.circle(surface, (110, 105, 95), dial_center, 18, width=2)
        # Indicator Pointer at top (red triangle pointing down at dial)
        pointer_top = dial_center[1] - dial_radius - 6
        pygame.draw.polygon(
            surface,
            (240, 50, 50),
            [
                (center_x, dial_center[1] - dial_radius + 2),
                (center_x - 5, pointer_top),
                (center_x + 5, pointer_top),
            ],
        )

        # Display current number in center knob
        num_font = settings.FONTS.get("dialogue", settings.FONTS["small"])
        num_surf = num_font.render(str(current_num), True, (245, 235, 210))
        surface.blit(num_surf, (dial_center[0] - num_surf.get_width() // 2, dial_center[1] - num_surf.get_height() // 2))

        # 4. Status LEDs (3 lights representing combination numbers locked in)
        led_y = panel_rect.top + 28
        total_leds = self.original_target_count
        unlocked_count = len(self.unlocked_numbers)
        led_spacing = 18
        start_led_x = center_x - ((total_leds - 1) * led_spacing) // 2

        for i in range(total_leds):
            lx = start_led_x + i * led_spacing
            is_lit = (i < unlocked_count)
            color = (60, 230, 60) if is_lit else (70, 20, 20)
            pygame.draw.circle(surface, color, (lx, led_y), 5)
            pygame.draw.circle(surface, (140, 140, 140), (lx, led_y), 5, width=1)

        # Feedback banner if active
        small_font = settings.FONTS.get("small", settings.FONTS["small"])
        if self.feedback_timer > 0.0 and self.feedback_message:
            fb_surf = small_font.render(self.feedback_message, True, self.feedback_color)
            surface.blit(fb_surf, (center_x - fb_surf.get_width() // 2, center_y + dial_radius + 8))
        else:
            hint_surf = small_font.render("Escucha el clic acústico al girar...", True, (160, 160, 150))
            surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, center_y + dial_radius + 8))

        # Bottom Controls Hint
        ctrl_surf = small_font.render("[A/D] Girar  |  [ESPACIO] Fijar número  |  [ESC] Salir", True, (210, 200, 170))
        surface.blit(ctrl_surf, (center_x - ctrl_surf.get_width() // 2, panel_rect.bottom - 16))
